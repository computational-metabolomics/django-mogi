from __future__ import print_function

from django.contrib.auth import get_user_model

from mogi.models.models_isa import (
    PolarityType,
    MFile,
    MFileSuffix,
    Run,
)

from mogi.models.models_inputdata import (
    MetabInputData
)

from mogi.models.models_libraries import (
    LibrarySpectraMeta,
    LibrarySpectraSource,
)

from mogi.models.models_peaks import (
    SPeakMeta,
    SPeak,
    XCMSFileInfo,
    CPeak,
    CPeakGroup,
    CPeakGroupMeta,
    CPeakGroupCPeakLink,
    SPeakMetaCPeakFragLink,
    Eic,
    EicMeta,
    PrecursorIonPurity,
    CPeakGroupSPeakLink,
    SPeakMetaSPeakLink,
    SPeakSPeakLink,
    CombinedPeak

)
from mogi.models.models_annotations import (
    MetaboliteAnnotation,
    MetaboliteAnnotationApproach,
    MetaboliteAnnotationDetail,
    MetaboliteAnnotationScore,
    ScoreType,
    DetailType,
    CombinedAnnotation,
    CombinedAnnotationConcat,
    AdductRule,
    NeutralMass,
    Adduct,
    Isotope
)
from mogi.models.models_compounds import (
    Compound
)
from mogi.models.models_isa import Assay, Investigation
from galaxy.models import History
from galaxy.utils.history_actions import get_history_status, history_data_save_form

from bulk_update.helper import bulk_update
from django.db.models import Count, Avg, F, Max
import sqlite3
from django.db import connection
from mogi.utils.sql_utils import sql_column_names, check_table_exists_sqlite
from django.conf import settings

import re
import os
import six
try:
    xrange
except NameError:  # python3
    xrange = range

import sys
if sys.version_info[0] < 3:
    from urllib2 import URLError
else:
    from urllib.error import URLError

if hasattr(settings, 'TEST_MODE'):
    TEST_MODE = settings.TEST_MODE
else:
    TEST_MODE = False




def setup_results_file_from_galaxy(user_id, galaxy_name, galaxy_data_id,
                         galaxy_history_id, investigation_name, celery_obj):
    if celery_obj:
        celery_obj.update_state(state='RUNNING',
                                meta={'current': 0.1, 'total': 100,
                                      'status': 'Getting data from Galaxy instance'})
    User = get_user_model()
    user = User.objects.get(pk=user_id)

    print('get history status')
    get_history_status(user, galaxy_history_id)

    print('get internal history tracking')
    print(galaxy_history_id)
    print(galaxy_name)
    internal_h = History.objects.filter(galaxy_id=galaxy_history_id,
                                        galaxyinstancetracking__name=galaxy_name)

    # Get Galaxy histroy data
    print('INTERNAL HISTORY MODEL {}'.format(internal_h))

    if not internal_h:
        error_msg = 'No data available please check galaxy connection'
        print(error_msg)
        if celery_obj:
            celery_obj.update_state(state='FAILED',
                                    meta={'current': 0, 'total': 100, 'status': error_msg})
        return 0, error_msg

    i_qs = Investigation.objects.filter(slug=investigation_name)

    if not i_qs:
        error_msg = 'No investigation with name {}'.format(investigation_name)
        print(error_msg)
        if celery_obj:
            celery_obj.update_state(state='FAILED',
                                    meta={'current': 0, 'total': 100, 'status': error_msg})
        return 0, error_msg

    md = MetabInputData(galaxy_history=internal_h[0])
    md.save()
    
    
    md = history_data_save_form(user,
                                 internal_h[0].id,
                                 galaxy_data_id,
                                 md)
    
    return md

class UploadResults(object):
    def __init__(self, md_id, mfile_ids):
        self.cpgm = ''
        if mfile_ids:
            self.mfiles = MFile.objects.filter(pk__in=mfile_ids)
        else:
            self.mfiles = MFile.objects.all()

        self.md = MetabInputData.objects.get(pk=md_id)

        self.mfile_d = {}
        print(self.md)
        print(self.md.data_file)
        self.conn = sqlite3.connect(self.md.data_file.path)
        self.cursor = self.conn.cursor()

        # this means we can inherit in MOGI a
        self.cpeakgroupmeta_class = CPeakGroupMeta

    def set_isa(self, celery_obj):

        cpgm = CPeakGroupMeta(metabinputdata=self.md)
        cpgm.save()

        ########################################
        # Check ISA has been created for files
        ########################################
        # if the files are not assigned to an assay
        # we can't process properly as we can not reference to the correct
        # study sample
        for mfile in self.mfile_d.values():
            if not mfile.run:
                if celery_obj:
                    celery_obj.update_state(state='FAILED',
                                       meta={
                                       'current': 0, 'total': 100,
                                       'status': 'Data file {} has no Assay '.format(
                                           mfile.original_filename)
                                         })

                return 0

        ###########################################
        # Get relevant assays
        ###########################################
        assays = []
        for mfile in set(self.mfile_d.values()):
            if mfile.run.assaydetail:
                print(mfile)
                print(mfile.run.assaydetail)
                assays.append(Assay.objects.get(id=mfile.run.assaydetail.assay.id))

        # Add to the list provided by the user
        assays.extend(self.md.assay.all())
        print(self.md.assay.all())
        # Remove duplicates
        assays = list(set(assays))

        print(assays)
        print('POLARITY TYPE', self.md.polaritytype)

        md_name = '|'

        if assays:
            for a in assays:
                # Get concat name
                md_name += '{} {} {}|'.format(a.study.investigation_id, a.study_id, a.name)

                # Add assays not already defined
                if a not in self.md.assay.all():
                    self.md.assay.add(a)

        self.md.name = md_name
        self.md.assay_names = ', '.join(l.name for l in self.md.assay.all())
        self.md.study_names =  ', '.join(set(l['study__name'] for l in self.md.assay.all().values('study__name')))
        self.md.investigation_names = ', '.join(set(l['study__investigation__name'] for l in self.md.assay.all().values(
            'study__investigation__name')))
        self.md.save()
        self.assays = assays


        self.cpgm = cpgm

        return cpgm


    def upload(self, celery_obj=None):
        ###################################
        # Get map of filename-to-class
        ###################################
        if celery_obj:
            celery_obj.update_state(state='RUNNING',
                                    meta={'current': 1, 'total': 100, 'status': 'Get map of filename-to-class'})
        xfi_d, mfile_d = self.save_xcms_file_info()
        self.mfile_d = mfile_d

        ###################################
        # first set ISA details (and cpeakgroupmeta)
        ###################################
        print('Set ISA details')
        if not self.set_isa(celery_obj):
            # If we can't find the files then we can't proceed
            return 0
        self.set_polarity()

        ###################################
        # Get grouped peaklist
        ###################################
        print('Get grouped peaklist')
        if celery_obj:
            celery_obj.update_state(state='RUNNING',
                                    meta={'current': 5, 'total': 100, 'status': 'Get grouped peaks'})

        self.save_xcms_grouped_peaks()

        ###################################
        # Get scan meta info
        ###################################
        print('Get scan meta info')
        if celery_obj:
            celery_obj.update_state(state='RUNNING',
                                    meta={'current': 10, 'total': 100, 'status': 'Get map scan meta info'})

        runs = {k: v.run for k, v in six.iteritems(mfile_d)}

        self.save_s_peak_meta(runs, celery_obj)

        ###################################
        # Get precursor ion purity info
        ###################################
        if celery_obj:
            celery_obj.update_state(state='RUNNING',
                                    meta={'current': 12, 'total': 100, 'status': 'Get precursor ion purity info'})

        self.save_precursor_ion_purity(celery_obj)

        ###################################
        # Get scan peaks
        ###################################
        print('Get scan peaks')
        if celery_obj:
            celery_obj.update_state(state='RUNNING',
                                    meta={'current': 15, 'total': 100, 'status': 'Get scan peaks'})

        self.save_s_peaks(celery_obj)

        ###################################
        # Get individual peaklist
        ###################################
        print('Get individual peaklist')
        if celery_obj:
            celery_obj.update_state(state='RUNNING',
                                    meta={'current': 20, 'total': 100, 'status': 'Get chromatographic peaks (indiv)'})

        self.save_xcms_individual_peaks(xfi_d)

        ###################################
        # Save EIC
        ###################################
        print('Save EIC')
        if celery_obj:
            celery_obj.update_state(state='RUNNING',
                                    meta={'current': 25, 'total': 100, 'status': 'Get EICs'})

        self.save_eics()

        ###################################
        # Get xcms peak list link
        ###################################
        print('Get xcms peak list link')
        if celery_obj:
            celery_obj.update_state(state='RUNNING',
                                    meta={'current': 30, 'total': 100, 'status': 'Get peak links'})

        self.save_xcms_group_peak_link()

        ###################################
        # Get adduct and isotope annotations
        ###################################
        print('Get adduct and isotope annotations')
        if celery_obj:
            celery_obj.update_state(state='RUNNING',
                                    meta={'current': 35, 'total': 100, 'status': 'Get adduct and isotopes'})

        ruleset_d = self.save_adduct_rules()
        self.save_neutral_masses()
        self.save_adduct_annotations(ruleset_d)
        self.save_isotope_annotations()

        ###################################
        # Fragmentation link
        ###################################
        print('Fragmentation link')
        if celery_obj:
            celery_obj.update_state(state='RUNNING',
                                    meta={'current': 40, 'total': 100,
                                          'status': 'Get scan peaks to chrom peak frag links'})

        self.save_speakmeta_cpeak_frag_link()


        ###################################
        # Get CPeakGroupSPeakLink (e.g. peaks linked between LC-MS and fraction)
        ###################################
        print('Get CPeakGroup SPeak Link')
        if celery_obj:
            celery_obj.update_state(state='RUNNING',
                                    meta={'current': 41, 'total': 100, 'status': 'Get peak links'})

        self.save_cpeakgroup_speak_link()


        ###################################
        # Get SPeakMetaSPeakLink (e.g. linking precursors to fragmentation for DIMSn)
        ###################################
        print('Get SPeakMeta SPeak Link')
        if celery_obj:
            celery_obj.update_state(state='RUNNING',
                                    meta={'current': 42, 'total': 100, 'status': 'Get peak links'})

        self.save_speakmeta_speak_link()


        ###################################
        # Get SPeakSPeakLink (e.g. linking precursors a DIMS experiment to a DIMSn experiment)
        ###################################
        print('Get SPeak SPeak Link')
        if celery_obj:
            celery_obj.update_state(state='RUNNING',
                                    meta={'current': 43, 'total': 100, 'status': 'Get peak links'})

        self.save_speak_speak_link()


        ####################################
        # Save metab compound
        ####################################
        print('Save metab compound')
        if celery_obj:
            celery_obj.update_state(state='RUNNING',
                                    meta={'current': 44, 'total': 100,
                                          'status': 'Updating compounds'})

        self.save_metab_compound()


        ####################################
        # Save ms1 lookup results
        ####################################
        if celery_obj:
            celery_obj.update_state(state='RUNNING',
                                    meta={'current': 45, 'total': 100,
                                          'status': 'Get ms1 lookup results'})
        print('MS1 lookup')
        self.save_ms1_lookup(celery_obj)

        ####################################
        # spectral matching
        ####################################
        print('spectral matching')
        if celery_obj:
            celery_obj.update_state(state='RUNNING',
                                    meta={'current': 46, 'total': 100,
                                          'status': 'Get spectral matching annotations'})
        lib_ids = self.save_spectral_matching_annotations()

        if celery_obj:
            celery_obj.update_state(state='RUNNING',
                                    meta={'current': 47, 'total': 100,
                                          'status': 'Get spectral matching library spectra'})

        self.save_library_spectra(lib_ids)

        ####################################
        # MetFrag
        ####################################
        print('MetFrag')
        if celery_obj:
            celery_obj.update_state(state='RUNNING',
                                    meta={'current': 50, 'total': 100,
                                          'status': 'Get MetFrag annotations'})
        self.save_metfrag(celery_obj)


        ####################################
        # CSI:FingerID
        ####################################
        print('CSI:FingerID')
        if celery_obj:
            celery_obj.update_state(state='RUNNING',
                                    meta={'current': 80, 'total': 100,
                                          'status': 'Get CSI:FingerID annotations'})
        self.save_sirius_csifingerid(celery_obj)

        ####################################
        # Update "combined peaks" summarising the peaks across different approaches (e.g. Fractionation-DIMS and LC-MS)
        ####################################
        print('Update combined peaks')
        if celery_obj:
            celery_obj.update_state(state='RUNNING',
                                    meta={'current': 90, 'total': 100,
                                          'status': 'Update combined peaks'})
        self.save_combined_peaks(celery_obj)


        ####################################
        # Update "combined annotation"
        ####################################
        print('Update combined annotation')
        if celery_obj:
            celery_obj.update_state(state='RUNNING',
                                    meta={'current': 95, 'total': 100,
                                          'status': 'Update combined annotation'})
        self.save_combined_annotation(celery_obj)

        ####################################
        # Update "concat annotation"
        ####################################
        print('Update concat annotation')
        if celery_obj:
            celery_obj.update_state(state='RUNNING',
                                    meta={'current': 97, 'total': 100,
                                          'status': 'Update concat annotation'})
        self.save_concat_annotation(celery_obj)


        if celery_obj:
            celery_obj.update_state(state='SUCCESS',
                                        meta={'current': 100, 'total': 100,
                                              'status': 'Uploaded dataset'})
        return 1

    def set_polarity(self):

        polarities = []
        for id, m in six.iteritems(self.mfile_d):
            if m.run.polaritytype:
                polarities.append(m.run.polaritytype.type.upper())

        polarities = list(set(polarities))

        print(polarities)

        if 'COMBINATION' in polarities:
            p = PolarityType.objects.get(type='COMBINATION')
        elif 'UNKNOWN' in polarities:
            p = PolarityType.objects.get(type='UNKNOWN')
        elif 'POSITIVE' in polarities and 'NEGATIVE' in polarities:
            p = PolarityType.objects.get(type='COMBINATION')
        elif 'POSITIVE' in polarities:
            p = PolarityType.objects.get(type='POSITIVE')
        elif 'NEGATIVE' in polarities:
            p = PolarityType.objects.get(type='NEGATIVE')
        else:
            p = PolarityType.objects.get(type='UNKNOWN')


        self.cpgm.polaritytype = p
        self.cpgm.save()


    def save_xcms_file_info(self):
        md = self.md
        cursor = self.cursor
        mfiles = self.mfiles

        if check_table_exists_sqlite(cursor, 'xset_classes'):

            cursor.execute('SELECT * FROM  xset_classes')
            names = sql_column_names(cursor)
            xset_classes = {}
            for row in self.cursor:
                xset_classes[row[names['row_names']]] = row[names['class']]

        else:
            xset_classes = {}


        cursor.execute('SELECT * FROM  fileinfo')

        names = sql_column_names(cursor)

        xfi_d = {}
        mfile_d = {}

        for row in self.cursor:
            idi = row[names['fileid']]

            if row[names['nm_save']]:
                fn = row[names['nm_save']]
            else:
                fn = row[names['filename']]

            if xset_classes:
                sampleType = xset_classes[os.path.splitext(fn)[0]]
            else:
                # old database schema has this stored in the same table
                sampleType = row[names['class']]

            mfile_qs = mfiles.filter(original_filename=fn)

            if mfile_qs:
                mfile = mfile_qs[0]
            else:

                # add the file with the most basic of information
                prefix, suffix = os.path.splitext(fn)


                if re.match('.*(?:_POS_|_POSITIVE_).*', prefix):
                    polarity_qs = PolarityType.objects.filter(type='POSITIVE')
                elif re.match('.*(?:_NEG_|_NEGATIVE_).*', prefix):
                    polarity_qs = PolarityType.objects.filter(type='NEGATIVE')
                else:
                    polarity_qs = PolarityType.objects.filter(type='UNKNOWN')

                if polarity_qs:
                    run = Run(prefix=prefix, polaritytype=polarity_qs[0])
                else:
                    run = Run(prefix=prefix)

                run.save()
                print(fn, run, suffix)
                mfile = MFile(original_filename=fn, run=run, mfilesuffix=MFileSuffix.objects.filter(
                    suffix=suffix.lower())[0])
                mfile.save()

            xfi = XCMSFileInfo(idi=idi, filename=fn, classname=sampleType, mfile=mfile, metabinputdata=md)

            xfi.save()
            xfi_d[idi] = xfi
            mfile_d[idi] = mfile

        return xfi_d, mfile_d

    def save_s_peak_meta(self, runs, celery_obj):

        md = self.md
        cursor = self.cursor
        cpgm = self.cpgm

        cursor.execute('SELECT * FROM  s_peak_meta')
        names = sql_column_names(cursor)

        speakmetas = []
        pips = []

        cpeakgroups_d = {c.idi: c for c in CPeakGroup.objects.filter(cpeakgroupmeta=self.cpgm)}


        for row in cursor:

            # this needs to be update after SQLite update in msPurity
            # to stop ram memory running out
            if len(speakmetas) % 500 == 0:
                if celery_obj:
                    celery_obj.update_state(state='RUNNING',
                                            meta={'current': 10, 'total': 100,
                                                  'status': 'Upload scan {}'.format(row[names['pid']])
                                                  }
                                            )

                SPeakMeta.objects.bulk_create(speakmetas)
                speakmetas = []


            cpg = cpeakgroups_d[int(row[names['grpid']])] if row[names['grpid']] else None

            spm = SPeakMeta(
                run=runs[row[names['fileid']]] if row[names['fileid']] in runs else None,
                idi=row[names['pid']],
                precursor_mz=cpg.mzmed if cpg else row[names['precursorMZ']],
                precursor_i=row[names['precursorIntensity']],
                precursor_rt=cpg.rtmed if cpg else row[names['precursorRT']],
                precursor_scan_num=row[names['precursorScanNum']],
                precursor_nearest=row[names['precursorNearest']],
                scan_num=row[names['precursorScanNum']],
                spectrum_type=row[names['spectrum_type']] if 'spectrum_type' in names else None,
                spectrum_detail=row[names['name']] if 'name' in names else None,
                well=row[names['well']] if 'well' in names else None,
                well_rtmin=row[names['well_rtmin']] if 'well' in names else None,
                well_rtmax=row[names['well_rtmax']] if 'well' in names else None,
                well_rt=row[names['well_rtmax']] if 'well' in names else None,

                cpeakgroup_id=cpg.id if cpg else None,
                ms_level=2,
                metabinputdata=md,

            )
            # spm.save()
            # Add purity data (if available)
            if row[names['aPurity']] or row[names['inPurity']] or row[names['iPurity']]:
                pip = PrecursorIonPurity(a_mz=row[names['aMz']],
                                     a_purity=row[names['aPurity']],
                                     a_pknm=row[names['apkNm']],
                                     i_mz=row[names['iMz']],
                                     i_purity=row[names['iPurity']],
                                     i_pknm=row[names['ipkNm']],
                                     in_purity=row[names['inPurity']],
                                     in_pknm=row[names['inPkNm']],
                                     speakmeta=spm)
                # pip.save()
                # pips.append(pip)

            speakmetas.append(spm)


        speakmetas = SPeakMeta.objects.bulk_create(speakmetas)
        # PrecursorIonPurity.objects.bulk_create(pips)

    def save_precursor_ion_purity(self, celery_obj):
        md = self.md
        cursor = self.cursor
        cursor.execute('SELECT * FROM  s_peak_meta')
        names = sql_column_names(cursor)

        pips = []

        speakmeta = SPeakMeta.objects.filter(metabinputdata=md)
        speakmeta_d = {s.idi: s.pk for s in speakmeta}

        for row in cursor:

            # this needs to be update after SQLite update in msPurity
            # to stop ram memory running out
            if len(pips) % 500 == 0:
                if celery_obj:
                    celery_obj.update_state(state='RUNNING',
                                            meta={'current': 12, 'total': 100,
                                                  'status': 'Upload precursor ion {}'.format(row[names['pid']])
                                                  }
                                            )

                PrecursorIonPurity.objects.bulk_create(pips)
                pips = []


            if row[names['aPurity']] or row[names['inPurity']] or row[names['iPurity']]:
                pip = PrecursorIonPurity(a_mz=row[names['aMz']],
                                     a_purity=row[names['aPurity']],
                                     a_pknm=row[names['apkNm']],
                                     i_mz=row[names['iMz']],
                                     i_purity=row[names['iPurity']],
                                     i_pknm=row[names['ipkNm']],
                                     in_purity=row[names['inPurity']],
                                     in_pknm=row[names['inPkNm']],
                                     speakmeta_id=speakmeta_d[row[names['pid']]])

                pips.append(pip)

        PrecursorIonPurity.objects.bulk_create(pips)

    def save_s_peaks(self, celery_obj):
        md = self.md
        cursor = self.cursor


        if not check_table_exists_sqlite(cursor, 's_peaks'):
            return 0

        speakmeta = SPeakMeta.objects.filter(metabinputdata=md)
        speakmeta_d = {s.idi: s.pk for s in speakmeta}

        cursor.execute('SELECT * FROM  s_peaks')
        names = sql_column_names(cursor)
        speaks = []

        for row in cursor:

            speaks.append(
                SPeak(
                    idi=row[names['sid']],
                    speakmeta_id=speakmeta_d[row[names['pid']]],
                    mz=row[names['mz']],
                    i=row[names['i']],
                    adducts=row[names['adduct']] if 'adduct' in names else None,
                    isotopes=row[names['isotopes']] if 'isotopes' in names else None
                )
            )
            # to stop ram memory runnning out
            if len(speaks) > 1000:
                SPeak.objects.bulk_create(speaks)
                if celery_obj:
                    celery_obj.update_state(state='RUNNING',
                                            meta={'current': 20, 'total': 100,
                                                  'status': 'Scan peaks upload, {}'.format(len(speaks))})
                speaks = []

        if speaks:
            print('saving speak objects')
            SPeak.objects.bulk_create(speaks)

    def save_xcms_individual_peaks(self, xfid):
        cursor = self.cursor
        cursor.execute('SELECT * FROM  c_peaks')
        names = sql_column_names(cursor)

        cpeaks = []

        for row in cursor:

            if len(cpeaks) % 500 == 0:
                CPeak.objects.bulk_create(cpeaks)
                cpeaks = []

            cpeak = CPeak(idi=row[names['cid']],
                          mz=row[names['mz']],
                          mzmin=row[names['mzmin']],
                          mzmax=row[names['mzmax']],
                          rt=row[names['rt']],
                          rtmin=row[names['rtmin']],
                          rtmax=row[names['rtmax']],
                          rtminraw=row[names['rtminraw']] if 'rtminraw' in names else None,
                          rtmaxraw=row[names['rtmaxraw']] if 'rtmaxraw' in names else None,
                          intb=row[names['intb']] if 'intb' in names else None,
                          _into=row[names['_into']],
                          maxo=row[names['maxo']],
                          sn=row[names['sn']] if 'sn' in names else None,
                          xcmsfileinfo=xfid[row[names['fileid']]]
                          )
            cpeaks.append(cpeak)

        CPeak.objects.bulk_create(cpeaks)

    def save_xcms_grouped_peaks(self):
        md = self.md
        cursor = self.cursor

        cursor.execute('SELECT * FROM  c_peak_groups')
        names = sql_column_names(cursor)

        cpeakgroups = []
        cpeakgroup_d = {}

        for row in cursor:

            if len(cpeakgroups) % 500 == 0:
                CPeakGroup.objects.bulk_create(cpeakgroups)
                cpeakgroups = []

            cpeakgroup = CPeakGroup(idi=row[names['grpid']],
                                        mzmed=row[names['mz']],
                                        mzmin=row[names['mzmin']],
                                        mzmax=row[names['mzmax']],
                                        rtmed=row[names['rt']],
                                        rtmin=row[names['rtmin']],
                                        rtmax=row[names['rtmax']],
                                        npeaks=row[names['npeaks']],
                                        cpeakgroupmeta=self.cpgm,
                                        isotopes=row[names['isotopes']] if 'isotopes' in names else None,
                                        adducts=row[names['adduct']] if 'adduct' in names else None,
                                        pcgroup=row[names['pcgroup']] if 'pcgroup' in names else None,
                                        )
            cpeakgroups.append(cpeakgroup)
            cpeakgroup_d[row[names['grpid']]] = cpeakgroup

        CPeakGroup.objects.bulk_create(cpeakgroups)

    def save_eics(self):
        md = self.md
        cursor = self.cursor

        if not check_table_exists_sqlite(cursor, 'eics'):
            return 0

        cursor.execute('SELECT * FROM  eics')
        names = sql_column_names(cursor)

        eicmeta = EicMeta(metabinputdata=md)
        eicmeta.save()

        cpeaks_d = {c.idi: c.pk for c in CPeak.objects.filter(xcmsfileinfo__metabinputdata=md)}
        cpeakgroups_d = {c.idi: c.pk for c in CPeakGroup.objects.filter(cpeakgroupmeta=self.cpgm)}

        eics = []
        c = 0
        for row in cursor:
            if c >= 1000:
                # to save memory
                Eic.objects.bulk_create(eics)
                eics = []
                c = 0

            eic = Eic(idi=row[names['eicidi']],
                      scan=row[names['scan']],
                      intensity=row[names['intensity']],
                      rt_raw=row[names['rt_raw']],
                      rt_corrected=row[names['rt_corrected']] if 'rt_corrected' in names else None,
                      purity=row[names['purity']] if 'purity' in names else None,
                      cpeak_id=cpeaks_d[row[names['c_peak_id']]],
                      cpeakgroup_id=cpeakgroups_d[row[names['grpid']]],
                      eicmeta_id=eicmeta.id
                      )
            eics.append(eic)
            c += 1

        Eic.objects.bulk_create(eics)

    def save_xcms_group_peak_link(self):
        md = self.md
        cursor = self.cursor


        cursor.execute('SELECT * FROM  c_peak_X_c_peak_group')
        names = sql_column_names(cursor)

        cpeakgrouplink = []

        cpeakgroups_d = {c.idi: c.pk for c in CPeakGroup.objects.filter(cpeakgroupmeta=self.cpgm)}
        cpeaks_d = {c.idi: c.pk for c in CPeak.objects.filter(xcmsfileinfo__metabinputdata=md)}

        for row in cursor:

            if len(cpeakgrouplink) % 500 == 0:
                CPeakGroupCPeakLink.objects.bulk_create(cpeakgrouplink)
                cpeakgrouplink = []

            cpeakgrouplink.append(
                CPeakGroupCPeakLink(
                    cpeak_id=cpeaks_d[row[names['cid']]],
                    cpeakgroup_id=cpeakgroups_d[row[names['grpid']]],
                    best_feature=row[names['bestpeak']] if 'bestpeak' in names else None,
                )
            )

        CPeakGroupCPeakLink.objects.bulk_create(cpeakgrouplink)

        return cpeakgrouplink

    def save_cpeakgroup_speak_link(self):
        md = self.md
        cursor = self.cursor
        if not check_table_exists_sqlite(cursor, 'c_peak_groups_X_s_peaks'):
            return 0        
        
        cursor.execute('SELECT * FROM  c_peak_groups_X_s_peaks')
        names = sql_column_names(cursor)

        cpeakgrouplink = []

        cpeakgroups_d = {c.idi: c.pk for c in CPeakGroup.objects.filter(cpeakgroupmeta=self.cpgm)}
        speaks_d = {c.idi: c.pk for c in SPeak.objects.filter(speakmeta__metabinputdata=md)}

        for row in cursor:

            if len(cpeakgrouplink) % 500 == 0:
                CPeakGroupSPeakLink.objects.bulk_create(cpeakgrouplink)
                cpeakgrouplink = []

            cpeakgrouplink.append(
                CPeakGroupSPeakLink(
                    speak_id=speaks_d[row[names['sid']]],
                    cpeakgroup_id=cpeakgroups_d[row[names['grpid']]],
                    mzdiff=row[names['mzdiff']]
                )
            )

        CPeakGroupSPeakLink.objects.bulk_create(cpeakgrouplink)

        return cpeakgrouplink

    def save_speakmeta_speak_link(self):
        md = self.md
        cursor = self.cursor

        if not check_table_exists_sqlite(cursor, 's_peak_meta_X_s_peaks'):
            return 0


        cursor.execute('SELECT * FROM  s_peak_meta_X_s_peaks')
        names = sql_column_names(cursor)

        links = []

        speakmeta_d = {c.idi: c.pk for c in SPeakMeta.objects.filter(metabinputdata=md)}
        speaks_d = {c.idi: c.pk for c in SPeak.objects.filter(speakmeta__metabinputdata=md)}

        for row in cursor:

            if len(links) % 500 == 0:
                SPeakMetaSPeakLink.objects.bulk_create(links)
                links = []

            links.append(
                SPeakMetaSPeakLink(
                    speak_id=speaks_d[row[names['sid']]],
                    speakmeta_id=speakmeta_d[row[names['pid']]],
                    mzdiff=row[names['mzdiff']],
                    linktype = row[names['link_type']]
                )
            )

        SPeakMetaSPeakLink.objects.bulk_create(links)

    def save_speak_speak_link(self):
        md = self.md
        cursor = self.cursor
        
        if not check_table_exists_sqlite(cursor, 's_peaks_X_speaks'):
            return 0

        cursor.execute('SELECT * FROM  s_peaks_X_s_peaks')
        names = sql_column_names(cursor)

        links = []

        speaks_d = {c.idi: c.pk for c in SPeak.objects.filter(speakmeta__metabinputdata=md)}

        for row in cursor:

            if len(links) % 500 == 0:
                SPeakSPeakLink.objects.bulk_create(links)
                links = []

            links.append(
                SPeakSPeakLink(
                    speak1_id=speaks_d[row[names['sid1']]],
                    speak2_id=speaks_d[row[names['sid2']]],
                    mzdiff=row[names['mzdiff']],
                    linktype=row[names['link_type']]
                )
            )

        SPeakSPeakLink.objects.bulk_create(links)


    def save_adduct_rules(self):
        md = self.md
        cursor = self.cursor

        if not check_table_exists_sqlite(cursor, 'adduct_rules'):
            return 0

        # update adduct rules
        cursor.execute('SELECT * FROM adduct_rules')
        names = sql_column_names(cursor)
        addr = list(AdductRule.objects.filter().values('adduct_type', 'id'))
        if len(addr) > 0:
            addrd = {a['adduct_type']: a['id'] for a in addr}
        else:
            addrd = {}

        ruleset_d = {}

        for row in cursor:
            if row[names['name']] not in addrd:
                arulei = AdductRule(adduct_type=row[names['name']],
                                    nmol=row[names['nmol']],
                                    charge=row[names['charge']],
                                    massdiff=row[names['massdiff']],
                                    oidscore=row[names['oidscore']],
                                    quasi=row[names['quasi']],
                                    ips=row[names['ips']],
                                    frag_score=row[names['frag_score']] if 'frag_score' in names else None
                                    )
                arulei.save()
                ruleset_d[row[names['rule_id']]] = arulei.id
            else:
                ruleset_d[row[names['rule_id']]] = addrd[row[names['name']]]

        return ruleset_d

    def save_neutral_masses(self):
        md = self.md
        cursor = self.cursor
        if not check_table_exists_sqlite(cursor, 'neutral_masses'):
            return 0
        # update neutral mass
        cursor.execute('SELECT * FROM neutral_masses')
        names = sql_column_names(cursor)

        nms = []
        for row in cursor:
            if len(row) % 500 == 0:
                NeutralMass.objects.bulk_create(nms)
                nms = []

            nm = NeutralMass(idi=row[names['nm_id']],
                             nm=row[names['mass']],
                             ips=row[names['ips']],
                             metabinputdata=md)
            nms.append(nm)

        NeutralMass.objects.bulk_create(nms)

    def save_adduct_annotations(self, ruleset_d):
        md = self.md
        cursor = self.cursor

        if not check_table_exists_sqlite(cursor, 'adduct_annotations'):
            return 0

        nm_d = {n.idi: n.id for n in NeutralMass.objects.filter(metabinputdata=md)}
        cpeakgroups_d = {c.idi: c.pk for c in CPeakGroup.objects.filter(cpeakgroupmeta=self.cpgm)}
        cursor.execute('SELECT * FROM adduct_annotations')
        names = sql_column_names(cursor)
        ads = []
        for row in cursor:
            if len(row) % 500 == 0:
                Adduct.objects.bulk_create(ads)
                ads = []

            ad = Adduct(idi=row[names['add_id']],
                        adductrule_id=ruleset_d[row[names['rule_id']]],
                        cpeakgroup_id=cpeakgroups_d[row[names['grpid']]],
                        neutralmass_id=nm_d[row[names['nm_id']]]
                        )
            ads.append(ad)

        Adduct.objects.bulk_create(ads)

    def save_isotope_annotations(self):
        md = self.md
        cursor = self.cursor


        if not check_table_exists_sqlite(cursor, 'isotope_annotations'):
            return 0

        cpeakgroups_d = {c.idi: c.pk for c in CPeakGroup.objects.filter(cpeakgroupmeta=self.cpgm)}
        cursor.execute('SELECT * FROM isotope_annotations')
        names = sql_column_names(cursor)
        isos = []
        for row in cursor:
            if len(row) % 500 ==0:
                Isotope.objects.bulk_create(isos)
                isos = []

            iso = Isotope(idi=row[names['iso_id']],
                          iso=row[names['iso']],
                          charge=row[names['charge']],
                          cpeakgroup1_id=cpeakgroups_d[row[names['c_peak_group1_id']]],
                          cpeakgroup2_id=cpeakgroups_d[row[names['c_peak_group2_id']]],
                          metabinputdata=md
                          )
            isos.append(iso)

        Isotope.objects.bulk_create(isos)

    def save_speakmeta_cpeak_frag_link(self):
        md = self.md
        cursor = self.cursor


        if not check_table_exists_sqlite(cursor, 'c_peak_X_s_peak_meta'):
            return 0

        cursor.execute('SELECT * FROM  c_peak_X_s_peak_meta')
        names = sql_column_names(cursor)

        speakmeta = SPeakMeta.objects.filter(metabinputdata=md)
        speakmeta_d = {s.idi: s.pk for s in speakmeta}

        cpeaks = CPeak.objects.filter(xcmsfileinfo__metabinputdata=md)
        cpeak_d = {s.idi: s.pk for s in cpeaks}

        speakmeta_cpeak_frag_links = []

        for row in cursor:
            if len(speakmeta_cpeak_frag_links) % 500 == 0:
                SPeakMetaCPeakFragLink.objects.bulk_create(speakmeta_cpeak_frag_links)
                speakmeta_cpeak_frag_links = []

            # this needs to be update after SQLite update in msPurity
            speakmeta_cpeak_frag_links.append(
                SPeakMetaCPeakFragLink(
                    speakmeta_id=speakmeta_d[row[names['pid']]],
                    cpeak_id=cpeak_d[row[names['cid']]],
                )
            )

        SPeakMetaCPeakFragLink.objects.bulk_create(speakmeta_cpeak_frag_links)

        # Add the number of msms events for grouped feature (not possible with django sql stuff) - this fails on
        # SQLite testing. This is not essential information so we can skip if using sqlite
        if settings.DATABASES['default']['ENGINE'] == 'django.db.backends.mysql':
            sqlstmt = '''UPDATE mogi_cpeakgroup AS t
                                    INNER JOIN (
                                            (SELECT cpg.id, COUNT(cpgl.id) AS counter FROM mogi_cpeakgroup as cpg 
                	                          LEFT JOIN mogi_cpeakgroupcpeaklink as cpgl 
                                                ON cpgl.cpeakgroup_id=cpg.id
                                              LEFT JOIN mogi_speakmetacpeakfraglink as scfl 
                                                ON cpgl.cpeak_id=scfl.cpeak_id
                                                WHERE scfl.id is not NULL AND cpg.cpeakgroupmeta_id={}
                                              group by cpg.id)
                                              ) m ON t.id = m.id
                                            SET t.msms_count = m.counter'''.format(self.cpgm.id)

            with connection.cursor() as cursor:
                cursor.execute(sqlstmt)


    def save_metab_compound(self):
        cursor = self.cursor

        if not check_table_exists_sqlite(cursor, 'metab_compound'):
            return 0

        cursor.execute('SELECT * FROM  metab_compound')
        names = sql_column_names(cursor)
        cmps = []
        for  i, row in enumerate(cursor):
            if i % 100 == 0:
                Compound.objects.bulk_create(cmps)
                cmps = []

            if 'inchikey' in names:
                inchikey = row[names['inchikey']]
            elif 'inchikey_id' in names:
                inchikey = row[names['inchikey_id']]
            else:
                break
            cmp = Compound.objects.filter(inchikey=inchikey)

            if not cmp:
                cmp = Compound(inchikey=inchikey,
                               inchikey1=row[names['inchikey1']],
                               inchikey2=row[names['inchikey2']],
                               inchikey3=row[names['inchikey3']],
                               name=row[names['name']],
                               inchi=row[names['inchi']],
                               smiles_canonical=row[names['smiles_canonical']],
                               exact_mass=row[names['exact_mass']],
                               molecular_formula=row[names['molecular_formula']],
                               pubchem_cids=row[names['pubchem_cids']],
                               kegg_drugs=row[names['kegg_drugs']],
                               kegg_brite=row[names['kegg_brite']],
                               hmdb_ids=row[names['hmdb_ids']],
                               hmdb_bio_custom_flag=row[names['hmdb_bio_custom_flag']],
                               hmdb_drug_flag=row[names['hmdb_drug_flag']],
                               biosim_max_score=row[names['biosim_max_score']],
                               biosim_max_count=row[names['biosim_max_count']],
                               biosim_hmdb_ids=row[names['biosim_hmdb_ids']],
                               )
                cmps.append(cmp)

        Compound.objects.bulk_create(cmps)


    def save_library_spectra(self, lib_ids):
        cursor = self.cursor

        if not check_table_exists_sqlite(cursor, 'l_s_peaks'):
            return 0

        cursor.execute('SELECT * FROM  l_s_peaks WHERE library_spectra_meta_id IN ({})'.
                       format(','.join([str(i) for i in lib_ids.keys()])))

        names = sql_column_names(cursor)

        lsps = []

        for row in cursor:
            if len(lsps) % 500 == 0:
                SPeak.objects.bulk_create(lsps)
                lsps = []

            lsp = SPeak(mz=row[names['mz']],
                        i=row[names['i']],
                        speakmeta_id=lib_ids[row[names['library_spectra_meta_id']]])

            lsps.append(lsp)

        SPeak.objects.bulk_create(lsps)

    def update_details_or_scores(self, sd_d, mas_d):
        out = []
        for idi, sd in sd_d.items():

            ma_idi = mas_d[idi]

            for i in sd:
                i.metaboliteannotation = ma_idi
                out.append(i)
        return out

    def save_metabolite_annotation(self, mas, scores, details=None):

        if not mas:
            return 0

        MetaboliteAnnotation.objects.bulk_create(mas)

        mas = MetaboliteAnnotation.objects.filter(metabinputdata=self.md)
        mas_d = {m.idi: m for m in mas}

        scores_l = self.update_details_or_scores(scores, mas_d)

        MetaboliteAnnotationScore.objects.bulk_create(scores_l)

        if details:
            details_l = self.update_details_or_scores(details, mas_d)
            MetaboliteAnnotationDetail.objects.bulk_create(details_l)


    def save_spectral_matching_annotations(self):
        md = self.md
        cursor = self.cursor

        maa = MetaboliteAnnotationApproach.objects.filter(name='Spectral matching').first()

        if not check_table_exists_sqlite(cursor, 'xcms_match'):
            return 0

        # Make sure column name is compatible (older version uses id
        cursor.execute('PRAGMA table_info(l_s_peak_meta)')
        cnames = [row[1] for row in cursor]
        if 'pid' in cnames:
            l_s_peak_meta_id_cn = 'pid'
        else:
            l_s_peak_meta_id_cn = 'id'

        cursor.execute('SELECT * FROM  xcms_match LEFT JOIN l_s_peak_meta ON xcms_match.lpid=l_s_peak_meta.{}'.
                       format(l_s_peak_meta_id_cn))

        names = sql_column_names(cursor)

        speakmeta_d = {c.idi: c.pk for c in SPeakMeta.objects.filter(metabinputdata=md)}

        library_d = {c.accession: c.pk for c in LibrarySpectraMeta.objects.all()}
        cpeakgroups_d = {c.idi: c.pk for c in CPeakGroup.objects.filter(cpeakgroupmeta=self.cpgm)}

        # keep track of the new librarymetaids
        new_lib_ids = {}

        mas = []
        scores = {}
        idi = 1
        for idi, row in enumerate(cursor):
            if TEST_MODE:
                if idi > 500:
                    break
            if len(mas) % 500 == 0:
                self.save_metabolite_annotation(mas, scores)
                mas = []
                scores = {}

            if names['accession'] in library_d:
                lsm_id = library_d[row[names['accession']]]
            else:

                lsm = LibrarySpectraMeta(idi=row[names['mid']],
                                   spectrum_type='library_spectra',
                                   ms_level=row[names['ms_level']],

                                   name=row[names['name']],
                                   accession=row[names['accession']],
                                   collision_energy=row[names['collision_energy']],
                                   resolution=row[names['resolution']],
                                   polarity=row[names['polarity']],
                                   fragmentation_type=row[names['fragmentation_type']],
                                   precursor_mz=row[names['precursor_mz']],
                                   precursor_type=row[names['precursor_type']],
                                   instrument_type=row[names['instrument_type']],
                                   instrument=row[names['instrument']],
                                   copyright=row[names['copyright']],
                                   column=row[names['column']],
                                   mass_accuracy=row[names['mass_accuracy']],
                                   mass_error=row[names['mass_error']],
                                   origin=row[names['origin']],
                                   splash=row[names['splash']],
                                   retention_index=row[names['retention_index']],
                                   retention_time=row[names['retention_time']],
                                   inchikey=row[names['inchikey_id']])

                lsm.save()
                lsm_id = lsm.id
                new_lib_ids[row[names['lpid']]] = lsm_id

            ma = MetaboliteAnnotation(metabinputdata=md,
                                      idi=idi,
                                      speakmeta_id=speakmeta_d[row[names['pid']]],
                                      cpeakgroup_id=cpeakgroups_d[row[names['grpid']]],
                                      metaboliteannotationapproach=maa,
                                      libraryspectrameta_id=lsm_id)

            # Add the scores
            scores_idi = self.create_scores_idi(['dpc', 'cdpc', 'rdpc', 'mcount', 'allcount', 'rtdiff'], row, names,
                                                maa)

            scores[idi] = scores_idi
            mas.append(ma)
            idi += 1

        self.save_metabolite_annotation(mas, scores)

        return new_lib_ids

    def create_scores_idi(self, score_names, row, colnames, maa):
        scores_idi = []
        for score_name in score_names:
            if row[colnames[score_name]]:
                st = ScoreType.objects.filter(name=score_name,
                                              metaboliteannotationapproach=maa
                                              ).first()
                scores_idi.append(MetaboliteAnnotationScore(scoretype=st,
                                                            score_value=row[colnames[score_name]]))
        return scores_idi

    def create_details_idi(self, detail_names, row, colnames, maa):
        details_idi = []
        for detail_name in detail_names:
            if row[colnames[detail_name]]:
                dt = DetailType.objects.filter(name=detail_name,
                                          metaboliteannotationapproach=maa).first()
                details_idi.append(MetaboliteAnnotationDetail(detailtype=dt,
                                                               detail_value=row[colnames[detail_name]]))
        return details_idi


    def save_metfrag(self, celery_obj):

        maa = MetaboliteAnnotationApproach.objects.filter(name='Metfrag').first()

        md = self.md
        cursor = self.cursor
        cpgm = self.cpgm

        if not check_table_exists_sqlite(cursor, 'metfrag_results'):
            return 0

        cursor.execute('SELECT * FROM  metfrag_results')
        names = sql_column_names(cursor)

        mas = []
        scores = {}
        details = {}
        cpeakgroups_d = {c.idi: c.pk for c in CPeakGroup.objects.filter(cpeakgroupmeta=cpgm)}
        speakmeta_d = {c.idi: c.pk for c in SPeakMeta.objects.filter(metabinputdata=md)}

        for idi, row in enumerate(cursor):
            if not row[names['grpid']].is_integer():
                # ignore rows where we can't get a real grpid
                continue
            
            if TEST_MODE:
                if idi > 500:
                    break
            if not row[names['InChIKey']]:
                # currently only add compounds we can have a name for (should be all cases if PubChem was used)
                continue

            try:
                score = float(row[names['Score']])
            except ValueError as e:
                print(e)
                continue

            if celery_obj and len(mas) % 100 == 0:
                celery_obj.update_state(state='RUNNING',
                                        meta={'current': 50, 'total': 100,
                                              'status': 'Metfrag upload, annotation {}'.format(idi)})

            if len(mas) % 100 == 0:

                self.save_metabolite_annotation(mas, scores, details)
                mas = []
                scores = {}
                details = {}

            ma = MetaboliteAnnotation(metabinputdata=md,
                                      idi=idi,
                                      metaboliteannotationapproach=maa,
                                      cpeakgroup_id=cpeakgroups_d[
                                          row[names['grpid']]] if 'grpid' in names and \
                                                                  row[names['grpid']] else None,
                                      speakmeta_id=speakmeta_d[
                                          row[names['pid']]] if 'pid' in names and \
                                                                    row[names['pid']] else None,
                                      inchikey=row[names['InChIKey']])

            mas.append(ma)
            score_names = ['OfflineMetFusionScore', 'SuspectListScore', 'FragmenterScore', 'Score',
                           'NoExplPeaks', 'NumberPeaksUsed', 'MaximumTreeDepth']
            scores_idi = self.create_scores_idi(score_names, row, names, maa)
            scores[idi] = scores_idi

            detail_names = ['adduct', 'ExplPeaks', 'FormulasOfExplPeaks', 'FragmenterScore_Values',
                            'MaximumTreeDepth', 'MolecularFormula', 'MonoisotopicMass']

            details_idi = self.create_details_idi(detail_names, row, names, maa)
            details[idi] = details_idi

        self.save_metabolite_annotation(mas, scores, details)


    def save_sirius_csifingerid(self, celery_obj):

        maa = MetaboliteAnnotationApproach.objects.filter(name='SIRIUS CSI:FingerID').first()

        md = self.md
        cursor = self.cursor

        if not check_table_exists_sqlite(cursor, 'sirius_csifingerid_results'):
            return 0

        cursor.execute('SELECT * FROM  sirius_csifingerid_results')
        names = sql_column_names(cursor)

        cpeakgroups_d = {c.idi: c.pk for c in CPeakGroup.objects.filter(cpeakgroupmeta=self.cpgm)}
        speakmeta_d = {c.idi: c.pk for c in SPeakMeta.objects.filter(metabinputdata=md)}

        mas = []
        scores = {}
        details = {}

        for idi, row in enumerate(cursor):


            try:
                rank = int(row[names['rank']])
            except ValueError as e:
                print(e)
                continue


            # if int(row[names['rank']])<=50:
            #     continue

            if TEST_MODE:
                if idi > 500:
                    break

            if celery_obj and idi % 500 == 0:
                celery_obj.update_state(state='RUNNING',
                                        meta={'current': 80, 'total': 100,
                                              'status': 'SIRIUS CSI-FingerID upload, annotation {}'.format(idi)})

            if len(mas) % 500 == 0:
                print(idi, row[names['rank']])
                self.save_metabolite_annotation(mas, scores, details)
                mas = []
                scores = {}
                details = {}

            ma = MetaboliteAnnotation(metabinputdata=md,
                                      idi=idi,
                                      metaboliteannotationapproach=maa,
                                      cpeakgroup_id=cpeakgroups_d[
                                          row[names['grpid']]] if 'grpid' in names and \
                                                               row[names['grpid']] else None,
                                      speakmeta_id=speakmeta_d[
                                          row[names['pid']]] if 'pid' in names and \
                                                              row[names['pid']] else None,
                                      inchikey1=row[names['inchikey2D']])

            mas.append(ma)
            score_names = ['rank', 'score', 'bounded_score']
            scores_idi = self.create_scores_idi(score_names, row, names, maa)
            scores[idi] = scores_idi

            detail_names = ['links', 'adduct']

            details_idi = self.create_details_idi(detail_names, row, names, maa)
            details[idi] = details_idi

        self.save_metabolite_annotation(mas, scores, details)

    def save_ms1_lookup(self, celery_obj):

        maa = MetaboliteAnnotationApproach.objects.filter(name='MS1 Lookup').first()

        md = self.md
        cursor = self.cursor

        if not check_table_exists_sqlite(cursor, 'ms1_lookup_results'):
            return 0


        cursor.execute('SELECT * FROM  ms1_lookup_results')
        names = sql_column_names(cursor)

        cpeakgroups_d = {c.idi: c.pk for c in CPeakGroup.objects.filter(cpeakgroupmeta=self.cpgm)}
        speak_d = {c.idi: c.pk for c in SPeak.objects.filter(speakmeta__metabinputdata=md)}

        mas = []
        scores = {}
        details = {}

        for idi, row in enumerate(cursor):

            if TEST_MODE:
                if idi > 500:
                    break

            if celery_obj and idi % 500 == 0:

                celery_obj.update_state(state='RUNNING',
                                        meta={'current': 80, 'total': 100,
                                              'status': 'MS1 lookup upload, annotation {}'.format(idi)})

            if len(mas) % 100 == 0:

                self.save_metabolite_annotation(mas, scores, details)
                mas = []
                scores = {}
                details = {}

            ma = MetaboliteAnnotation(metabinputdata=md,
                                      idi=idi,
                                      metaboliteannotationapproach=maa,
                                      cpeakgroup_id=cpeakgroups_d[
                                          row[names['grpid']]] if 'grpid' in names and \
                                                           row[names['grpid']] else None,
                                      speak_id=speak_d[
                                          row[names['sid']]] if 'sid' in names and \
                                                            row[names['sid']] else None,
                                      inchikey=row[names['inchikey']])


            mas.append(ma)

            # defaults to 1 for ms1 lookup (e.g. if the Null value given for score)
            scores[idi] = [
                MetaboliteAnnotationScore(
                    scoretype=ScoreType.objects.filter(
                        name='score').first(),
                    score_value=row[names['score']] if 'score' in names else 1)]

            details[idi] = self.create_details_idi(['adduct'], row, names, maa)

        self.save_metabolite_annotation(mas, scores, details)


    def save_combined_peaks(self, celery_obj):
        md = self.md
        cursor = self.cursor

        # Get summary of LC-MS/MS peaks
        combinedps = []
        for i, cpeakgroup in enumerate(CPeakGroup.objects.filter(cpeakgroupmeta=self.cpgm)):
            if TEST_MODE:
                if i > 500:
                    break

            if i % 100 == 0:
                if celery_obj:
                    celery_obj.update_state(state='RUNNING',
                                        meta={'current': 95, 'total': 100,
                                              'status': 'Creating combined peak table LC-MS(/MS) peak {}'.format(i)})

                CombinedPeak.objects.bulk_create(combinedps)
                combinedps = []

            fract_match = True if CPeakGroupSPeakLink.objects.filter(cpeakgroup=cpeakgroup) else False

            frag_match = True if SPeakMeta.objects.filter(speakmetacpeakfraglink__cpeak__cpeakgroup=cpeakgroup) else False


            intensity = max([i._into for i in cpeakgroup.cpeak.all()])

            combinedp = CombinedPeak(metabinputdata=md,
                                     cpeakgroup=cpeakgroup,
                                     speak=None,
                                     rtmin=cpeakgroup.rtmin,
                                     rtmax=cpeakgroup.rtmax,
                                     rt=cpeakgroup.rtmed,
                                     mz=cpeakgroup.mzmed,
                                     intensity=intensity,
                                     well=None,
                                     ms_type='LC-MS(/MS)',
                                     fraction_match=fract_match,
                                     camera_adducts=cpeakgroup.adducts,
                                     camera_isotopes=cpeakgroup.isotopes,
                                     frag_match=frag_match)

            combinedps.append(combinedp)

        CombinedPeak.objects.bulk_create(combinedps)
        combinedps = []

        # Get summary for fractionation peaks
        for i, sp in enumerate(SPeak.objects.filter(speakmeta__metabinputdata=md, speakmeta__spectrum_type='dimspy0')):
            if i % 100 == 0:
                if celery_obj:
                    celery_obj.update_state(state='RUNNING',
                                        meta={'current': 96, 'total': 100,
                                              'status': 'Creating combined peak table fractionation peaks {}'.format(
                                                  i)})

                CombinedPeak.objects.bulk_create(combinedps)
                combinedps = []

            if sp.mz<=0:
                # these peaks are from the blank subtraction and have been removed
                continue

            fract_match = True if CPeakGroupSPeakLink.objects.filter(speak=sp) else False

            with connection.cursor() as cursor:
                sqlstmt = """SELECT spm.id FROM mogi_speakmeta AS spm
                        LEFT JOIN mogi_speakmetaspeaklink AS smxs ON smxs.speakmeta_id=spm.id 
                        LEFT JOIN mogi_speak AS sp ON sp.id=smxs.speak_id
                        LEFT JOIN mogi_speakspeaklink AS spXsp ON spXsp.speak2_id=sp.id
                        WHERE spXsp.speak1_id={}
                """.format(sp.id)

                frag_match = True if cursor.execute(sqlstmt) else False

            combinedp = CombinedPeak(metabinputdata=md,
                                     cpeakgroup=None,
                                     speak=sp,
                                     rtmin=sp.speakmeta.well_rtmin,
                                     rtmax=sp.speakmeta.well_rtmax,
                                     rt=sp.speakmeta.well_rt,
                                     mz=sp.mz,
                                     intensity=sp.i,
                                     ms_type='Fractionation',
                                     well=sp.speakmeta.well,
                                     fraction_match=fract_match,
                                     camera_adducts=sp.adducts,
                                     camera_isotopes=sp.isotopes,
                                     frag_match=frag_match)

            combinedps.append(combinedp)
        CombinedPeak.objects.bulk_create(combinedps)

    def save_combined_annotation(self, celery_obj):

        cpgm = self.cpgm
        md = self.md
        cursor = self.cursor

        if not check_table_exists_sqlite(cursor, 'combined_annotations'):
            return 0

        cursor.execute('SELECT * FROM  combined_annotations')
        names = sql_column_names(cursor)

        cpeakgroups_d = {c.idi: c.pk for c in CPeakGroup.objects.filter(cpeakgroupmeta=cpgm)}
        speaks_d = {c.idi: c.pk for c in SPeak.objects.filter(speakmeta__metabinputdata=md,
                                                              speakmeta__spectrum_type='dimspy0')}

        # Get summary of LC-MS/MS peaks
        cas = []
        for i, row in enumerate(cursor):
            if TEST_MODE:
                if i > 500:
                    break

            if i % 100 == 0:
                if celery_obj:
                    celery_obj.update_state(state='RUNNING',
                                        meta={'current': 95, 'total': 100,
                                              'status': 'Creating combined peak table LC-MS(/MS) peak {}'.format(i)})

                CombinedAnnotation.objects.bulk_create(cas)
                cas = []

            if 'grpid' in names and row[names['grpid']]:
                combinedp = CombinedPeak.objects.filter(cpeakgroup_id=cpeakgroups_d[row[names['grpid']]]).first()

            if 'sid' in names and row[names['sid']]:
                combinedp = CombinedPeak.objects.filter(speak_id=speaks_d[row[names['sid']]]).first()

            ca = CombinedAnnotation(combinedpeak=combinedp,
                                    compound=Compound.objects.filter(inchikey=row[names['inchikey']]).first(),
                                    compound_annotated_adduct=row[names['adduct_overall']],
                                    ms1_lookup_score=row[names['ms1_lookup_score']],
                                    ms1_lookup_wscore=row[names['ms1_lookup_wscore']],
                                    spectral_matching_score=row[names['sm_score']],
                                    spectral_matching_wscore=row[names['sm_wscore']],
                                    metfrag_score=row[names['metfrag_score']],
                                    metfrag_wscore=row[names['metfrag_wscore']],
                                    sirius_csifingerid_score=row[names['sirius_score']],
                                    sirius_csifingerid_wscore=row[names['sirius_wscore']],
                                    biosim_max_score=row[names['biosim_max_score']],
                                    biosim_wscore=row[names['biosim_wscore']],
                                    total_wscore=row[names['wscore']],
                                    rank=row[names['rank']])

            cas.append(ca)

        CombinedAnnotation.objects.bulk_create(cas)

    def save_concat_annotation(self, celery_obj):

        cacs = []
        for i, cp in enumerate(CombinedPeak.objects.filter(metabinputdata=self.md)):
            if TEST_MODE:
                if i > 500:
                    break

            if i % 100 == 0:
                if celery_obj:
                    celery_obj.update_state(state='RUNNING',
                                        meta={'current': 95, 'total': 100,
                                              'status': 'Concat annotations {}'.format(i)})

                CombinedAnnotationConcat.objects.bulk_create(cacs)
                cacs = []

            # get top ranked annotations
            ca = CombinedAnnotation.objects.filter(
                combinedpeak=cp, rank=1,
            ).order_by(
                '-total_wscore'
            ).values(
                'total_wscore', 'compound__inchikey', 'compound_annotated_adduct',
                'compound__name'
            )

            top_score = ca.aggregate(Max('total_wscore'))['total_wscore__max']

            print(top_score)

            if isinstance(top_score, float):
                top_score = round(top_score, 2)

            concat_score = '|'.join([str(round(i['total_wscore'], 2)) for i in ca][:5])
            concat_inchikey = '|'.join([str(i['compound__inchikey']) for i in ca][:5])
            concat_name = '|'.join([str(i['compound__name']) for i in ca][:5])
            concat_adduct = '|'.join([str(i['compound_annotated_adduct']) for i in ca][:5])

            cac = CombinedAnnotationConcat(combinedpeak=cp,
                                           top_score=top_score,
                                           concat_score=concat_score,
                                           concat_adduct=concat_adduct,
                                           concat_inchikey=concat_inchikey,
                                           concat_name=concat_name[:1000], # limit 4 readability
                                           )

            cacs.append(cac)

        CombinedAnnotationConcat.objects.bulk_create(cacs)


