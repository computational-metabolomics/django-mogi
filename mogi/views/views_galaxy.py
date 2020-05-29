# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# -*- coding: utf-8 -*-
from rest_framework import viewsets

from django_tables2.views import SingleTableMixin
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View, ListView

from galaxy.models import History
from galaxy.utils.history_actions import get_history_data, init_history_data_save_form, history_data_save_form
from galaxy.views import (
    FilesToGalaxyDataLib,
    HistoryDataCreateView,
    WorkflowRunView,
    TableFileSelectMixin,
    GenericFilesToGalaxyHistory,
    WorkflowListView,
    HistoryListView
)
from galaxy.utils.history_actions import get_history_status

from mogi.models import models_galaxy
from mogi.tables import tables_isa, tables_galaxy
from mogi.filter import filter_isa
from mogi.forms import forms_galaxy
from mogi.tasks import galaxy_isa_upload_datalib_task, upload_metab_results_galaxy_task
from mogi.serializers import IncomingGalaxyDataSerializer
from .views_isa import InvestigationListView



#################################################################################################
# REST
#################################################################################################
class IncomingGalaxyDataViewSet(viewsets.ModelViewSet):
    """
    """
    queryset = models_galaxy.IncomingGalaxyData.objects.all()
    serializer_class = IncomingGalaxyDataSerializer


class IncomingGalaxyDataListView(LoginRequiredMixin, SingleTableMixin, ListView):
    '''
    '''
    table_class = tables_galaxy.IncomingGalaxyDataTable
    model = models_galaxy.IncomingGalaxyData
    template_name = 'mogi/incoming_galaxy_data.html'




#################################################################################################
# Galaxy ISA uploads and workflows
#################################################################################################
class GalaxyISAupload(TableFileSelectMixin, InvestigationListView):
    '''
    '''
    success_msg = "Run started"
    # template_name = 'misa/investigation_list.html'
    table_class = tables_isa.InvestigationTableUpload
    form_class = forms_galaxy.ISAtoGalaxyParamForm
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
    table_class = tables_isa.ISAFileSelectTable
    filter_class = filter_isa.ISAFileFilter
    form_class = forms_galaxy.ISAWorkflowRunForm
    redirect_to = 'history_mogi'


class ISAFileSelectToGalaxyDataLib(FilesToGalaxyDataLib):
    table_class = tables_isa.ISAFileSelectTableWithCheckBox
    filterset_class = filter_isa.ISAFileFilter


class ISAFileSelectToGalaxyHist(GenericFilesToGalaxyHistory):
    table_class = tables_isa.ISAFileSelectTableWithCheckBox
    filterset_class = filter_isa.ISAFileFilter


class ISAWorkflowListView(WorkflowListView):
    table_class = tables_galaxy.WorkflowTableISA
    redirect_to = 'isa_workflow_summary'


########################################################################################################################
# Galaxy History data upload to django-metab
########################################################################################################################
class HistoryDataMogiListView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        data = get_history_data(self.kwargs['pk'], request.user, data_type=['sqlite'])

        table = tables_galaxy.HistoryMogiDataTable(data)

        return render(request, 'galaxy/history_data_bioblend_list.html', {'table': table})
        # return render(request, 'galaxy/history_status.html', {'table': table})

class HistoryMogiListView(HistoryListView):

    template_name = 'galaxy/history_status.html'
    table_class = tables_galaxy.HistoryMogiTable


class HistoryDataMogiCreateView(HistoryDataCreateView):
    model = models_galaxy.HistoryDataMOGI
    form_class = forms_galaxy.HistoryMogiDataForm
    template_name = 'galaxy/historydata_form.html'

    def form_valid(self, form):
        obj = self.save_form(form)
        # first get all the mfiles associated with the investigation

        result = save_lcms_mogi.delay(obj.pk, self.request.user.id)
        self.request.session['result'] = result.id
        return render(self.request, 'gfiles/status.html', {'s': 0, 'progress': 0})


class HistoryDataMogiFromRestCreateView(HistoryDataMogiCreateView):

    def get_initial(self):
        user = self.request.user
        get_history_status(user)

        galaxy_name = self.kwargs.get('galaxy_name')
        galaxy_data_id = self.kwargs.get('galaxy_data_id')
        galaxy_history_id = self.kwargs.get('galaxy_history_id')

        internal_h = History.objects.filter(galaxy_id=galaxy_history_id, galaxyinstancetracking__name=galaxy_name)

        if internal_h:
            history_d = init_history_data_save_form(user=user, history_internal_id=internal_h[0].id, galaxy_dataset_id=galaxy_data_id)

            return {'history': internal_h[0].id,
                    'name': history_d['name']}
        else:
            return {'history': 'NO DATA AVAILABLE (PLEASE CHECK CONNECTION)',
                    'name': 'NO DATA AVAILABLE (PLEASE CHECK CONNECTION)'}

    def save_form(self, form):
        history_data_obj = form.save(commit=False)
        history_data_obj.user = self.request.user

        galaxy_name = self.kwargs.get('galaxy_name')
        galaxy_data_id = self.kwargs.get('galaxy_data_id')
        galaxy_history_id = self.kwargs.get('galaxy_history_id')

        internal_h = History.objects.filter(galaxy_id=galaxy_history_id, galaxyinstancetracking__name=galaxy_name)

        return history_data_save_form(self.request.user, internal_h[0].id, galaxy_data_id, history_data_obj)


class SaveLcmsFromFromRest(LoginRequiredMixin, View):


    def get(self, request, *args, **kwargs):
        return render(request, 'mogi/confirm_submission.html')

    def post(self, request, *args, **kwargs):
        galaxy_name = self.kwargs.get('galaxy_name')
        galaxy_data_id = self.kwargs.get('galaxy_data_id')
        galaxy_history_id = self.kwargs.get('galaxy_history_id')
        investigation_name = self.kwargs.get('investigation_name')

        result = upload_metab_results_galaxy_task.delay(request.user.id,
                                      galaxy_name,
                                      galaxy_data_id,
                                      galaxy_history_id,
                                      investigation_name)

        self.request.session['result'] = result.id
        return render(self.request, 'gfiles/status.html', {'s': 0, 'progress': 0})






