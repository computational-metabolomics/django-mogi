# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# -*- coding: utf-8 -*-
from rest_framework import viewsets

from django_tables2.views import SingleTableMixin
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, AccessMixin
from django.views.generic import View, ListView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
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
from mogi.tasks import galaxy_isa_upload_datalib_task
from mogi.serializers import IncomingGalaxyDataSerializer
from .views_isa import InvestigationListView



##############################################################################################
# REST
#############################################################################################
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




##############################################################################################
# Galaxy ISA uploads and workflows
##############################################################################################
class GalaxyISAupload(PermissionRequiredMixin, AccessMixin, TableFileSelectMixin, InvestigationListView):
    '''
    '''
    success_msg = "Run started"
    # template_name = 'misa/investigation_list.html'
    table_class = tables_isa.InvestigationTableUpload
    form_class = forms_galaxy.ISAtoGalaxyParamForm
    template_name = 'mogi/isa_files_to_galaxy.html'
    initial_context = {'library': True, 'django_url': 'galaxy_isa_upload_datalib/'}

    task_string = 'upload ISA projects to Galaxy'
    permission_required = 'mogi.galaxyisaupload'  # would need to manually create this permission to use
    redirect_string = 'galaxy_summary'

    def handle_no_permission(self):
        messages.error(self.request, 'User has insufficient privileges to {}'.format(self.task_string))
        return redirect(self.redirect_string)

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
    redirect_to = 'history'


class ISAFileSelectToGalaxyDataLib(FilesToGalaxyDataLib):
    task_string = 'upload ISA projects to Galaxy'
    permission_required = 'mogi.galaxyisaupload'  # would need to manually create this permission to use
    redirect_string = 'galaxy_summary'

    table_class = tables_isa.ISAFileSelectTableWithCheckBox
    filterset_class = filter_isa.ISAFileFilter


class ISAFileSelectToGalaxyHist(GenericFilesToGalaxyHistory):
    table_class = tables_isa.ISAFileSelectTableWithCheckBox
    filterset_class = filter_isa.ISAFileFilter


class ISAWorkflowListView(WorkflowListView):
    table_class = tables_galaxy.WorkflowTableISA
    redirect_to = 'isa_workflow_summary'





