# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from mogi.utils.upload_isa_to_galaxy import galaxy_isa_upload_datalib
from galaxy.models import FilesToGalaxyDataLibraryParam
from metab.models import MFile, MetabInputData
from metab.utils.save_lcms import LcmsDataTransfer

@shared_task(bind=True)
def galaxy_isa_upload_datalib_task(self, pks, param_pk, galaxy_pass, user_id):
    """

    """

    print 'CHECK1'
    self.update_state(state='Uploading ISA projects to Galaxy', meta={'current': 0.1, 'total': 100})
    galaxy_isa_upload_param = FilesToGalaxyDataLibraryParam.objects.get(pk=param_pk)
    galaxy_isa_upload_datalib(pks, galaxy_isa_upload_param, galaxy_pass, user_id, self)



@shared_task(bind=True)
def save_lcms(self, invest_id, gfile_id):
    mfiles = MFile.objects.filter(run__assayrun__assaydetail__assay__study__investigation=invest_id)
    mfiles_ids = [m.id for m in mfiles]
    md = MetabInputData(gfile_id=gfile_id)
    md.save()
    lcms_data_transfer = LcmsDataTransfer(md.id, mfiles_ids)
    lcms_data_transfer.transfer(celery_obj=self)

