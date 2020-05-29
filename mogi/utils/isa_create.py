# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import zipfile
import copy
import os
import six
import csv
from django.template.defaultfilters import slugify
from io import TextIOWrapper
from django.contrib.auth import get_user_model
from django import forms
from mogi.utils.sample_batch_create import sample_batch_create
from mogi.utils.mfile_upload import upload_files_from_zip, add_mfiles, add_runs, add_runs_mfiles_filelist
from mogi.models import models_isa



def isa_batch_create(sample_list, user_id, save_as_link=True,
                     root_dir = '', celery_obj = '', delimiter=','):
    reader = csv.DictReader(TextIOWrapper(
        sample_list, encoding='ascii', errors='replace'), delimiter=delimiter)

    sample_list_l = list(reader)
    
    User = get_user_model()
    user = User.objects.get(pk=user_id)

    # Check each row if investigation, study and assay
    for row in sample_list_l:
        i = models_isa.Investigation.objects.filter(name=row['investigation']).first()
        if not i:
            i = models_isa.Investigation(name=row['investigation'],
                                     description='',
                                     slug=slugify(row['investigation']),
                                     owner=user,
                                     public=True)
            i.save()

        s = models_isa.Study.objects.filter(name=row['study'], investigation=i).first()

        if not s:
            s = models_isa.Study(name=row['study'],
                             description='',
                             investigation=i,
                             owner=user,
                             public=True
                                 )
            s.save()

        a = models_isa.Assay.objects.filter(name=row['assay'], study=s).first()

        if not a:
            a = models_isa.Assay(name=row['assay'],
                                 description='',
                                 study=s,
                                 owner=user,
                                 public=True
                                 )
            a.save()


    # Create samples (if not already created)
    sample_list.seek(0)
    sample_batch_create(sample_list, study_default='',
                        replace_duplicates=False, delimiter=delimiter)

    # create assay details
    mapping_d = {}
    allfiles = []
    for row in sample_list_l:
        
        a = models_isa.Assay.objects.filter(name=row['assay'], study=s).first()

        mapping_d.update(get_mapping_d([row], a.id, create_assay_details=True))
        allfiles.extend(get_files(row, bn=False))

    # Add the runs
    runs = {}
    for p, d in mapping_d.items():
        r = models_isa.Run(
                prefix=p,
                polaritytype=models_isa.PolarityType.objects.get(
                    type=d['rowdetails']['polarity'].upper()
                )
        )
        r.save()
        runs[p] = r

    # Add all files to runs
    allfiles = [os.path.join(root_dir, i) for i in allfiles]
    mfiles = add_mfiles(allfiles, runs, user, save_as_link, celery_obj='')

    # Map the assay details to the files
    map_run_to_assaydetail(runs, mapping_d, use_prefix=True)


def upload_assay_data_files_zip(assayid, data_zipfile, data_mappingfile, user,
                                create_assay_details):

    # Upload the files
    if zipfile.is_zipfile(data_zipfile):
        runs, mfiles = upload_files_from_zip(data_zipfile, user)
    else:
        print('data needs to be in zip file format')
        return 0

    mappingd = get_mapping_d(data_mappingfile, assayid=assayid,
                             create_assay_details=create_assay_details)
    # then go through the mapping file and upload to relevant assay_run
    #section adding replicates if present
    map_run_to_assaydetail(runs, mappingd)


def map_run_to_assaydetail(runs, mappingd, use_prefix=False):
    # get the unique runs we need
    unique_runs = list(set([run for filename, run in six.iteritems(runs)]))

    # loop through the runs
    for run in unique_runs:
        ## we presume that the correct checks have been performed before
        ##  so that all files from the same
        ## run will have the same assay details

        if use_prefix:
            md = mappingd[run.prefix]
        else:
            mfile = run.mfile_set.all()
            fn = mfile[0].original_filename
            md = mappingd[fn]
        run.assaydetail = md['assaydetails']
        run.technical_replicate = md['rowdetails']['technical_replicate'] if 'technical_replicate' in md[
            'rowdetails'] else 1

        run.polaritytype = models_isa.PolarityType.objects.get(type=md['rowdetails']['polarity'].upper())
        run.save()


def get_mapping_d(mapping_l, assayid, create_assay_details=False):

    mapping_d = {}
    for row in mapping_l:
        # update each time
        qs = models_isa.AssayDetail.objects.filter(assay_id=assayid)
        fns = get_files(row)

        if not fns:
            continue

        ad = search_assay_detail(row, qs)

        if create_assay_details and not ad:
            ad = create_assay_detail(row, assayid)

        # mapping directory of array details per "file prefix"
        # e.g. Run. Not The fns list should be all the same data
        # but different file formats e.g. mzML and RAW.
        # So can just get the first element of the list
        mapping_d[os.path.splitext(fns[0])[0]] = {'assaydetails': ad, 'rowdetails':row}


    return mapping_d

def search_assay_detail(row, qs):

    code_field = row_2_codefield(row)
    match = qs.filter(code_field=code_field)

    if match:
        return match[0]
    else:
        return ''


def create_assay_detail(row, assayid):
    # import here to prevent circular imports
    from mogi.forms.forms_isa import AssayDetailForm
    sc = models_isa.SampleCollectionProcess(
        samplecollectionprotocol=models_isa.SampleCollectionProtocol.objects.get(
           code_field=row['sample_collection']
        )
    )
    sc.save()

    cfrac, spefrac = frac2numbers(row)

    print(cfrac, spefrac)
    ei = models_isa.ExtractionProcess(
        extractionprotocol=models_isa.ExtractionProtocol.objects.get(
            code_field=row['extraction'])
    )
    ei.save()

    # Create SPE process

    spei = models_isa.SpeProcess(
        spefrac=spefrac,
        speprotocol=models_isa.SpeProtocol.objects.get(
            code_field=row['spe']
        )
    )
    spei.save()

    # Create chromtography process
    ci = models_isa.ChromatographyProcess(
        chromatographyfrac=cfrac,
        chromatographyprotocol=models_isa.ChromatographyProtocol.objects.get(
            code_field=row['chromatography']
        )
    )
    ci.save()

    # create measurement process
    mi = models_isa.MeasurementProcess(
        measurementprotocol=models_isa.MeasurementProtocol.objects.get(
            code_field=row['measurement']
        ),
        polaritytype=models_isa.PolarityType.objects.get(
            type=row['polarity'].upper()
        ),
    )
    mi.save()

    ss = models_isa.StudySample.objects.get(
        sample_name=row['sample_name'],
        study=models_isa.Study.objects.get(
            assay__id=assayid
        )
    )

    data_in = {'assay': assayid,
               'studysample': ss.id,
               'samplecollectionprocess': sc.id,
               'extractionprocess': ei.id,
               'speprocess': spei.id,
               'chromatographyprocess': ci.id,
               'measurementprocess': mi.id}

    form = AssayDetailForm(data_in)
    form.is_valid()
    ad = form.save()

    return ad


def frac2numbers(row):
    if row['chromatography_frac'] == 'NA':
        cfrac = 0
    else:
        cfrac = row['chromatography_frac']

    if row['spe_frac'] == 'NA':
        spefrac = 0
    else:
        spefrac = row['spe_frac']

    return cfrac, spefrac

def row_2_codefield(row):
    cfrac, spefrac = frac2numbers(row)

    return '{}_{}_{}_{}_{}_{}_{}_{}_{}'.format(row['sample_name'],
                                               row['sample_collection'],
                                               row['extraction'],
                                               row['spe'],
                                               spefrac,
                                               row['chromatography'],
                                               cfrac,
                                               row['measurement'],
                                               row['polarity'].upper())


def file_upload_mapping_match(filenames, mapping_l):
    missing_files = []
    for fn in filenames:

        matched = False
        for row in mapping_l:

            map_filename = row['filename']
            if os.path.basename(fn) == map_filename:
                matched = True

        if not matched:
            missing_files.append(fn)

    return missing_files


def get_files(row, bn=True):
    fns = []
    if 'filename' in row:
        fns.append(row['filename'])

    if 'raw_filepth' in row:
        fns.append(row['raw_filepth'])

    if 'mzml_filepth' in row:
        fns.append(row['mzml_filepth'])

    if bn:
        fns = [os.path.basename(fn) for fn in fns]

    return fns

def check_mapping_details(mapping_l, assayid):

    qs = models_isa.AssayDetail.objects.filter(assay_id=assayid)

    missing_inf = []
    for row in mapping_l:
        fns = get_files(row)

        if not fns:
            continue

        if not check_frac(row['spe_frac']) or not check_frac(row['chromatography_frac']):

            msg = 'Fraction columns (spe_frac & chromatography_frac) can only be integers or NA, please check these columns' \
                  'in the mapping file'
            raise forms.ValidationError(msg)

        if not search_assay_detail(row, qs):
            missing_inf.extend(fns)

    return missing_inf



def check_frac(frac):
    if frac == 'NA':
        return True
    else:
        try:
            int(frac)
        except ValueError:
            return False
        else:
            return True



def upload_assay_data_files_dir(filelist, user_id, mapping_l, assayid,
                                create_assay_details, save_as_link, celery_obj):
    """
    """
    users = get_user_model()
    user = users.objects.get(pk=user_id)

    runs, mfiles = add_runs_mfiles_filelist(filelist, user, save_as_link, celery_obj)

    mappingd = get_mapping_d(mapping_l, assayid=assayid,
                             create_assay_details=create_assay_details)

    if celery_obj:
        celery_obj.update_state(state='RUNNING',
                meta={'current': 99, 'total': 100, 'status': 'Mapping files to assay details'})

    # then go through the mapping file and upload to relevant
    # assay_run section adding replicates if present
    map_run_to_assaydetail(runs, mappingd)
