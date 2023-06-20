# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task

from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.conf import settings

from galaxy.models import FilesToGalaxyDataLibraryParam
from gfiles.models import TrackTasks, GenericFile

from mogi.models.models_isa import MFile, ExportISA
from mogi.models.models_datasets import UploadDatasets
from mogi.models.models_compounds import UploadCompounds



from mogi.utils.isa_export import export_isa_files
from mogi.utils.isa_create import upload_assay_data_files_dir
from mogi.utils.mfile_upload import add_runs_mfiles_filelist
from mogi.utils.msp2db import LibraryData
from mogi.utils.search_mass import search_mz, search_mono
from mogi.utils.search_frag import search_frag
from mogi.utils.upload_compounds import upload_compounds
from mogi.utils.upload_datasets import upload_datasets
from mogi.utils.upload_isa_to_galaxy import galaxy_isa_upload_datalib


@shared_task(bind=True)
def upload_files_from_dir_task(self, filelist, username, save_as_link):
    user = User.objects.get(username=username)
    add_runs_mfiles_filelist(filelist, user, save_as_link, self)

@shared_task(bind=True)
def upload_library(self, msp_pth, name):

    self.update_state(state='Uploading library spectra (no progress bar)', meta={'current': 0, 'total': 100})
    libdata = LibraryData(msp_pth=msp_pth, name=name, db_pth=None, db_type='django_mysql',
                          source=name, d_form=False, chunk=200, celery_obj=self)


@shared_task(bind=True)
def search_mz_task(self, sp, userid):
    # track tasks in db
    tt = TrackTasks(taskid=self.request.id, state='RUNNING', name='Search mz values', user_id=userid)
    tt.save()

    # run function
    search_mz(sp, self)

    # save successful result
    tt.result = reverse('search_mz_result')
    tt.state = 'SUCCESS'
    tt.save()



@shared_task(bind=True)
def search_mono_task(self, sp, userid):
    # track tasks in db
    tt = TrackTasks(taskid=self.request.id, state='RUNNING', name='Search monoisotopic exact mass values', user_id=userid)
    tt.save()

    # run function
    search_mono(sp, self)

    # save successful result
    tt.result = reverse('search_mono_param')
    tt.state = 'SUCCESS'
    tt.save()

@shared_task(bind=True)
def search_frag_task(self, sp, userid):
    # track tasks in db
    tt = TrackTasks(taskid=self.request.id, state='RUNNING', name='Search frag values', user_id=userid)
    tt.save()

    # run function
    search_frag(sp, self)

    # save successful result
    tt.result = reverse('search_frag_param')
    tt.state = 'SUCCESS'
    tt.save()


@shared_task(bind=True)
def upload_dataset_task(self, pk, userid):
    # track tasks in db
    tt = TrackTasks(taskid=self.request.id, state='RUNNING', name='Data upload', user_id=userid)
    tt.save()

    # upload file
    ud = UploadDatasets.objects.get(pk=pk)
    print(ud)
    upload_datasets(ud.data_file.path)
    # save successful result
    tt.result = reverse('dataset_summary')
    tt.state = 'SUCCESS'
    tt.save()


@shared_task(bind=True)
def upload_compounds_task(self, pk, userid):
    # track tasks in db
    tt = TrackTasks(taskid=self.request.id, state='RUNNING', name='Data upload', user_id=userid)
    tt.save()

    # upload file
    uc = UploadCompounds.objects.get(pk=pk)

    upload_compounds(uc.data_file.path, settings.ANNOTATION_DETAILS, True, self)

    # save successful result
    tt.result = reverse('compounds')
    tt.state = 'SUCCESS'
    tt.save()

@shared_task(bind=True)
def galaxy_isa_upload_datalib_task(self, pks, param_pk, galaxy_pass, user_id):
    """

    """
    tt = TrackTasks(taskid=self.request.id, state='RUNNING',
                    name='Uploading ISA projects to Galaxy', user_id=user_id)
    tt.save()

    self.update_state(state='RUNNING',
                      meta={'current': 0.1, 'total': 100,
                            'status': 'Uploading ISA projects to Galaxy'})
    galaxy_isa_upload_param = FilesToGalaxyDataLibraryParam.objects.get(pk=param_pk)

    result_out = galaxy_isa_upload_datalib(pks, galaxy_isa_upload_param,
                                           galaxy_pass, user_id, self)

    if result_out:
        self.update_state(state='SUCCESS',
                          meta={'current': 100, 'total': 100, 'status': 'completed'})

    # save successful result
    tt.result = reverse('galaxy_summary')
    tt.state = 'SUCCESS'
    tt.save()


@shared_task(bind=True)
def upload_assay_data_files_dir_task(self, filelist, user_id, mapping_l, assayid, save_as_link, create_assay_details):
    """
    """
    users = get_user_model()
    tt = TrackTasks(taskid=self.request.id,
                    state='RUNNING',
                    name='Upload assay data file',
                    user=users.objects.get(pk=user_id))
    tt.save()

    upload_assay_data_files_dir(filelist, user_id, mapping_l, assayid, create_assay_details, save_as_link, self)

    tt.result = reverse('assayfile_summary', kwargs={'assayid': assayid})
    tt.state = 'SUCCESS'
    tt.save()


@shared_task(bind=True)
def export_isa_files_task(self, exportisa_id, user_id):
    """
    """
    users = get_user_model()
    expisa = ExportISA.objects.get(id=exportisa_id)
    tt = TrackTasks(taskid=self.request.id,
                    state='RUNNING',
                    name='Export ISA files',
                    user=users.objects.get(pk=user_id))
    tt.save()

    export_isa_files(expisa.investigation_id,
                     metabolights_compat=expisa.metabolights_compat, 
                     extract_mzml_info=expisa.mzml_parse,
                     export_json=expisa.json,
                     export_isatab=expisa.isatab,
                     celery_obj=self)

    tt.result = reverse('ilist')
    tt.state = 'SUCCESS'
    tt.save()

