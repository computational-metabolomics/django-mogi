# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task

from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import InMemoryUploadedFile

from galaxy.models import FilesToGalaxyDataLibraryParam
from gfiles.models import TrackTasks, GenericFile

from mogi.models.models_isa import MFile
from mogi.models.models_inputdata import MetabInputData
from mogi.models.models_annotations import CombinedAnnotation
from mogi.tables.tables_annotations import CombinedAnnotationTable

from mogi.utils.isa_create import upload_assay_data_files_dir
from mogi.utils.mfile_upload import add_runs_mfiles_filelist
from mogi.utils.msp2db import LibraryData
from mogi.utils.search_mz_nm import search_mz, search_nm
from mogi.utils.search_frag import search_frag
from mogi.utils.download_annotations import DownloadAnnotations
from mogi.utils.upload_results import UploadResults, setup_results_file_from_galaxy
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
def search_nm_task(self, sp, userid):
    # track tasks in db
    tt = TrackTasks(taskid=self.request.id, state='RUNNING', name='Search nm values', user_id=userid)
    tt.save()

    search_nm(sp, self)

    # save successful result
    tt.result = reverse('search_nm_result')
    tt.state = 'SUCCESS'
    tt.save()


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
def search_frag_task(self, sp, userid):
    # track tasks in db
    tt = TrackTasks(taskid=self.request.id, state='RUNNING', name='Search nm values', user_id=userid)
    tt.save()

    # run function
    search_frag(sp, self)

    # save successful result
    tt.result = reverse('search_frag_result')
    tt.state = 'SUCCESS'
    tt.save()


@shared_task(bind=True)
def upload_metab_results_task(self, pk, userid):
    # track tasks in db
    tt = TrackTasks(taskid=self.request.id, state='RUNNING', name='Data upload', user_id=userid)
    tt.save()

    # upload file
    results = UploadResults(pk, None)
    
    # run function  
    results.upload(celery_obj=self)

    # save successful result
    tt.result = reverse('metabinputdata_summary')
    tt.state = 'SUCCESS'
    tt.save()


@shared_task(bind=True)
def download_cannotations_task(self, pk, userid):
    # track tasks in db
    tt = TrackTasks(taskid=self.request.id,
                    state='RUNNING',
                    name='Downloading annotations',
                    user_id=userid)
    tt.save()

    # perform function
    dam = DownloadAnnotations()
    dam.download_cannotations(pk, self)

    # save successful result
    tt.result = reverse('canns_download_result')
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

    result_out = galaxy_isa_uplofad_datalib(pks, galaxy_isa_upload_param,
                                           galaxy_pass, user_id, self)

    if result_out:
        self.update_state(state='SUCCESS',
                          meta={'current': 100, 'total': 100, 'status': 'completed'})

    # save successful result
    tt.result = reverse('galaxy_summary')
    tt.state = 'SUCCESS'
    tt.save()


@shared_task(bind=True)
def upload_metab_results_galaxy_task(self, userid, galaxy_name,
                                     galaxy_data_id, galaxy_history_id, investigation_name):
    tt = TrackTasks(taskid=self.request.id, state='RUNNING', name='Data upload', user_id=userid)
    tt.save()

    md = setup_results_file_from_galaxy(userid,
                                        galaxy_name,
                                        galaxy_data_id,
                                        galaxy_history_id,
                                        investigation_name,
                                        self)
    print('MD {}'.format(md))
    
    if not md:
        tt.result = reverse('metabinputdata_summary')
        tt.state = 'FAILURE'
        tt.save()
        return 0


    results = UploadResults(md.id, None)
    results.upload(celery_obj=self)


    # save successful result
    tt.result = reverse('metabinputdata_summary')
    tt.state = 'SUCCESS'
    tt.save()



    

class DownloadAnnotationsMogi(DownloadAnnotations):
    annotation_model_class = CombinedAnnotation
    annotation_table_class = CombinedAnnotationTable

    def get_items(self, cann_down):
        if cann_down.rank:
            canns = self.annotation_model_class.objects.filter(cannotation__rank__lte=cann_down.rank)
        else:
            canns = self.annotation_model_class.objects.all()

        return canns


@shared_task(bind=True)
def download_cannotations_mogi_task(self, pk, userid):
    # track tasks in db
    tt = TrackTasks(taskid=self.request.id,
                    state='RUNNING',
                    name='Downloading LC-MSMS annotations',
                    user_id=userid)
    tt.save()

    # perform function
    dam = DownloadAnnotationsMogi()
    dam.download_cannotations(pk, self)


    # save successful result
    tt.result = reverse('canns_download_result')
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

