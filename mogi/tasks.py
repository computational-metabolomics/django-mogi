# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task

from mogi.utils.upload_isa_to_galaxy import galaxy_isa_upload_datalib
from galaxy.models import FilesToGalaxyDataLibraryParam
from mbrowse.models import MFile, MetabInputData, CAnnotation
from mogi.utils.save_lcms import LcmsDataTransferMOGI, get_data_from_galaxy
from mogi.models import HistoryDataMOGI, CAnnotationMOGI
from gfiles.models import TrackTasks
from django.urls import reverse


@shared_task(bind=True)
def galaxy_isa_upload_datalib_task(self, pks, param_pk, galaxy_pass, user_id):
    """

    """
    tt = TrackTasks(taskid=self.request.id, state='RUNNING', name='Uploading ISA projects to Galaxy', user_id=user_id)
    tt.save()

    self.update_state(state='RUNNING', meta={'current': 0.1, 'total': 100, 'status': 'Uploading ISA projects to Galaxy'})
    galaxy_isa_upload_param = FilesToGalaxyDataLibraryParam.objects.get(pk=param_pk)

    result_out = galaxy_isa_upload_datalib(pks, galaxy_isa_upload_param, galaxy_pass, user_id, self)

    if result_out:
        self.update_state(state='SUCCESS', meta={'current': 100, 'total': 100, 'status': 'completed'})

    # save successful result
    tt.result = reverse('galaxy_summary')
    tt.state = 'SUCCESS'
    tt.save()



@shared_task(bind=True)
def save_lcms_mogi(self, userid, galaxy_name, galaxy_data_id, galaxy_history_id, investigation_name):
    ###################
    # Save task
    ###################
    tt = TrackTasks(taskid=self.request.id, state='RUNNING', name='LC-MSMS data upload', user_id=userid)
    tt.save()

    ####################
    # Perform operation
    ####################
    hdm = get_data_from_galaxy(userid, galaxy_name, galaxy_data_id, galaxy_history_id, investigation_name, self)

    if not hdm:
        tt.result = reverse('cpeakgroupmeta_summary_mogi')
        tt.state = 'FAILURE'
        tt.save()
        return 0

    mfiles = MFile.objects.filter(run__assayrun__assaydetail__assay__study__investigation=hdm.investigation.pk)
    mfiles_ids = [m.id for m in mfiles]
    md = MetabInputData(gfile_id=hdm.genericfile_ptr_id)
    md.save()
    lcms_data_transfer = LcmsDataTransferMOGI(md.id, mfiles_ids)
    lcms_data_transfer.historydatamogi = hdm

    if not lcms_data_transfer.transfer(celery_obj=self):
        # something wen't wrong don't perform the remaining analysis
        return 0

    self.update_state(state='RUNNING', meta={'current': 98, 'total': 100, 'status': 'Updating ISA links '})
    cans_mogi = []
    for i, cann in enumerate(CAnnotation.objects.filter(cpeakgroup__cpeakgroupmeta__metabinputdata=md).all()):
        if i % 5000 == 0:

            CAnnotationMOGI.objects.bulk_create(cans_mogi)
            cans_mogi = []
        cans_mogi.append(CAnnotationMOGI(cannotation=cann))

    CAnnotationMOGI.objects.bulk_create(cans_mogi)


    ####################
    # Save data
    ####################
    tt.result = reverse('cpeakgroupmeta_summary_mogi')
    tt.state = 'SUCCESS'
    tt.save()





@shared_task(bind=True)
def save_lcms_mogiOLD(self, hdm_id, userid):
    ###################
    # Save task
    ###################
    tt = TrackTasks(taskid=self.request.id, state='RUNNING', name='LC-MSMS data upload', user_id=userid)
    tt.save()

    ####################
    # Perform operation
    ####################
    hdm = HistoryDataMOGI.objects.get(pk=hdm_id)

    mfiles = MFile.objects.filter(run__assayrun__assaydetail__assay__study__investigation=hdm.investigation.pk)
    mfiles_ids = [m.id for m in mfiles]
    md = MetabInputData(gfile_id=hdm.genericfile_ptr_id)
    md.save()
    lcms_data_transfer = LcmsDataTransferMOGI(md.id, mfiles_ids)
    lcms_data_transfer.historydatamogi = hdm


    ####################
    # Save data
    ####################
    tt.result = reverse('cpeakgroupmeta_summary_mogi')
    tt.state = 'SUCCESS'
    tt.save()







