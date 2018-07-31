# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task

from mogi.utils.upload_isa_to_galaxy import galaxy_isa_upload_datalib
from galaxy.models import FilesToGalaxyDataLibraryParam
from mbrowse.models import MFile, MetabInputData, CAnnotation
from mogi.utils.save_lcms import LcmsDataTransferMOGI
from mogi.models import HistoryDataMOGI, CAnnotationMOGI

@shared_task(bind=True)
def galaxy_isa_upload_datalib_task(self, pks, param_pk, galaxy_pass, user_id):
    """

    """


    self.update_state(state='Uploading ISA projects to Galaxy', meta={'current': 0.1, 'total': 100})
    galaxy_isa_upload_param = FilesToGalaxyDataLibraryParam.objects.get(pk=param_pk)
    result_out = galaxy_isa_upload_datalib(pks, galaxy_isa_upload_param, galaxy_pass, user_id, self)
    if result_out:
        self.update_state(state='SUCCESS', meta={'current': 100, 'total': 100})

@shared_task(bind=True)
def save_lcms_mogi(self, hdm_id):
    hdm = HistoryDataMOGI.objects.get(pk=hdm_id)

    mfiles = MFile.objects.filter(run__assayrun__assaydetail__assay__study__investigation=hdm.investigation.pk)
    mfiles_ids = [m.id for m in mfiles]
    md = MetabInputData(gfile_id=hdm.genericfile_ptr_id)
    md.save()
    lcms_data_transfer = LcmsDataTransferMOGI(md.id, mfiles_ids)
    lcms_data_transfer.historydatamogi = hdm
    lcms_data_transfer.transfer(celery_obj=self)

    cans_mogi = []
    for i, cann in enumerate(CAnnotation.objects.filter(cpeakgroup__cpeakgroupmeta__metabinputdata=md).all()):
        if i % 1000 == 0:
            CAnnotationMOGI.objects.bulk_create(cans_mogi)
            cans_mogi = []
        cans_mogi.append(CAnnotationMOGI(cannotation=cann))

    CAnnotationMOGI.objects.bulk_create(cans_mogi)





