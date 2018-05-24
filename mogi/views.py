# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View

from galaxy.views import WorkflowRunView, TableFileSelectMixin
from misa.views import InvestigationListView
from misa.tables import ISAFileSelectTable, ISAFileSelectTableWithCheckBox
from misa.filter import ISAFileFilter

from mogi.tables import InvestigationTableUpload, WorkflowTableISA, HistoryMogiTable, HistoryMogiDataTable
from mogi.forms import ISAtoGalaxyParamForm, HistoryMogiDataForm, ISAWorkflowRunForm
from mogi.tasks import galaxy_isa_upload_datalib_task
from metab.utils.save_lcms import save_lcms_data
from metab.models import MFile, MetabInputData
from mogi.models import HistoryDataMOGI

from galaxy.utils.history_actions import get_history_data
from galaxy.views import FilesToGalaxyDataLib, GenericFilesToGalaxyHistory, WorkflowListView, HistoryListView, HistoryDataCreateView

class GalaxyISAupload(TableFileSelectMixin, InvestigationListView):
    '''
    '''
    success_msg = "Run started"
    # template_name = 'misa/investigation_list.html'
    table_class = InvestigationTableUpload
    form_class = ISAtoGalaxyParamForm
    template_name = 'mogi/isa_files_to_galaxy.html'
    initial_context = {'library': True, 'django_url': 'galaxy_isa_upload_datalib/'}

    def form_valid(self, request, form):
        user = self.request.user
        galaxy_isa_upload_param = form.save(commit=False)
        galaxy_isa_upload_param.added_by = user
        galaxy_isa_upload_param.save()

        pks = request.POST.getlist("check")

        result = galaxy_isa_upload_datalib_task.delay(pks, galaxy_isa_upload_param.id,
                                                      galaxy_pass=form.cleaned_data['galaxy_password'],
                                                      user_id=user.id)
        request.session['result'] = result.id
        return render(request, 'gfiles/status.html', {'s': 0, 'progress': 0})





class ISAWorkflowRunView(WorkflowRunView):
    '''
    Run a registered workflow
    '''
    success_msg = "Run started"
    success_url = '/galaxy/success'
    template_name = 'galaxy/workflow_run.html'
    table_class = ISAFileSelectTable
    filter_class = ISAFileFilter
    form_class = ISAWorkflowRunForm
    redirect_to = 'history_mogi'




class ISAFileSelectToGalaxyDataLib(FilesToGalaxyDataLib):
    table_class = ISAFileSelectTableWithCheckBox
    filterset_class = ISAFileFilter








class ISAFileSelectToGalaxyHist(GenericFilesToGalaxyHistory):
    table_class = ISAFileSelectTableWithCheckBox
    filterset_class = ISAFileFilter


class ISAWorkflowListView(WorkflowListView):
    table_class = WorkflowTableISA




def index(request):
    return render(request, 'mogi/index.html')

def about(request):
    return render(request, 'mogi/about.html')

def submitted(request):
    return render(request, 'galaxy/submitted.html')

def success(request):
    return render(request, 'dma/success.html')



class HistoryDataMogiListView(LoginRequiredMixin, View):


    def get(self, request, *args, **kwargs):
        data = get_history_data(self.kwargs['pk'], request.user, name_filter=['alldata.sqlite',
                                                                              'frag4feature_sqlite',
                                                                              'spectral_matching_sqlite'])

        table = HistoryMogiDataTable(data)

        return render(request, 'galaxy/history_data_bioblend_list.html', {'table': table})
        # return render(request, 'galaxy/history_status.html', {'table': table})

class HistoryMogiListView(HistoryListView):

    template_name = 'galaxy/history_status.html'
    table_class = HistoryMogiTable


class HistoryDataMogiCreateView(HistoryDataCreateView):
    model = HistoryDataMOGI
    form_class = HistoryMogiDataForm
    template_name = 'galaxy/historydata_form.html'

    def form_valid(self, form):
        obj = self.save_form(form)
        # first get all the mfiles associated with the investigation

        mfiles = MFile.objects.filter(run__assayrun__assaydetail__assay__study__investigation=obj.investigation.pk)
        md = MetabInputData(gfile_id=obj.genericfile_ptr_id)
        md.save()
        save_lcms_data(md.id, mfiles)


        return render(self.request, 'dma/submitted.html')
