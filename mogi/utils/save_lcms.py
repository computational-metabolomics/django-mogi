from django.contrib.auth.models import User

from mbrowse.utils.save_lcms import LcmsDataTransfer
from mogi.models import CPeakGroupMetaMOGI, CAnnotationMOGI, HistoryDataMOGI
from misa.models import Assay, AssayRun, AssayDetail, Investigation
from galaxy.models import History

from mogi.forms import HistoryMogiDataForm
from galaxy.utils.history_actions import get_history_status, history_data_save_form, init_history_data_save_form

class LcmsDataTransferMOGI(LcmsDataTransfer):
    cpeakgroupmeta_class = CPeakGroupMetaMOGI
    historydatamogi = ''
    assays = []

    def set_cpeakgroupmeta(self, celery_obj):

        cpgm = CPeakGroupMetaMOGI(metabinputdata=self.md, historydatamogi=self.historydatamogi)
        cpgm.save()

        ########################################
        # Check ISA has been created for files
        ########################################
        # if the files are not assigned to an assay we can't process properly as we can not reference to the correct
        # study sample
        for mfile in self.mfile_d.values():
            if not mfile.run.assayrun:
                if celery_obj:
                    celery_obj.update_state(state='FAILED',
                                                meta={'current': 0, 'total': 100,
                                                      'status': 'Data file {} used is not associated with any '
                                                                'Assay '.format(mfile.original_filename)})

                return 0

        ###########################################
        # Get relevant assays
        ###########################################

        assays = [Assay.objects.get(id=mfile.run.assayrun.assaydetail.assay_id) for mfile in set(self.mfile_d.values())]
        assays = list(set(assays))

        md_name = '|'

        for a in assays:
            md_name += '{} {} {}|'.format(a.study.investigation_id, a.study_id, a.name)
            cpgm.assay.add(a)

        self.md.name = md_name
        self.md.save()
        self.assays = assays
        self.cpgm = cpgm

        return cpgm


def get_data_from_galaxy(user_id, galaxy_name, galaxy_data_id, galaxy_history_id, investigation_name, celery_obj):
    if celery_obj:
        celery_obj.update_state(state='RUNNING',
                                meta={'current': 0.1, 'total': 100, 'status': 'Getting data from Galaxy instance'})

    user = User.objects.get(pk=user_id)

    get_history_status(user)

    internal_h = History.objects.filter(galaxy_id=galaxy_history_id, galaxyinstancetracking__name=galaxy_name)

    if not internal_h:
        error_msg = 'No data available please check galaxy connection'
        print(error_msg)
        if celery_obj:
            celery_obj.update_state(state='FAILED', meta={'current': 0, 'total': 100, 'status': error_msg})
        return 0, error_msg

    i_qs = Investigation.objects.filter(slug=investigation_name)

    if not i_qs:
        error_msg = 'No investigation with name {}'.format(investigation_name)
        print(error_msg)
        if celery_obj:
            celery_obj.update_state(state='FAILED', meta={'current': 0, 'total': 100, 'status': error_msg})
        return 0, error_msg

    hdm = HistoryDataMOGI(investigation = i_qs[0], history=internal_h[0])

    print(hdm)
    hdm = history_data_save_form(user, internal_h[0].id, galaxy_data_id, hdm)

    return hdm
