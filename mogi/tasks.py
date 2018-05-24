# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from mogi.utils.upload_isa_to_galaxy import galaxy_isa_upload_datalib
from galaxy.models import FilesToGalaxyDataLibraryParam

@shared_task(bind=True)
def galaxy_isa_upload_datalib_task(self, pks, param_pk, galaxy_pass, user_id):
    """

    """

    print 'CHECK1'
    self.update_state(state='Uploading ISA projects to Galaxy', meta={'current': 0.1, 'total': 100})
    galaxy_isa_upload_param = FilesToGalaxyDataLibraryParam.objects.get(pk=param_pk)
    galaxy_isa_upload_datalib(pks, galaxy_isa_upload_param, galaxy_pass, user_id, self)

