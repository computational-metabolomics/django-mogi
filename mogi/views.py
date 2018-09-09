# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View, ListView

from django_tables2.export.views import ExportMixin
from django_tables2.views import SingleTableMixin

from misa.models import Investigation
from misa.views import InvestigationListView
from misa.tables import ISAFileSelectTable, ISAFileSelectTableWithCheckBox
from misa.filter import ISAFileFilter

from mogi.tables import InvestigationTableUpload, WorkflowTableISA, HistoryMogiTable, HistoryMogiDataTable, CPeakGroupMetaMogiTable, CAnnotationMogiTable, IncomingGalaxyDataTable
from mogi.models import CAnnotationMOGI, CPeakGroupMetaMOGI, IncomingGalaxyData
from mogi.forms import ISAtoGalaxyParamForm, HistoryMogiDataForm, ISAWorkflowRunForm
from mogi.tasks import galaxy_isa_upload_datalib_task, save_lcms_mogi, download_cannotations_mogi_task
from mbrowse.utils.save_lcms import LcmsDataTransfer
from mbrowse.models import MFile, MetabInputData, CAnnotation
from mbrowse.views import CPeakGroupMetaListView, CAnnotationListAllView, CAnnotationDownloadView
from django.db.models import Q

from galaxy.models import Workflow, History
from galaxy.utils.history_actions import get_history_data,init_history_data_save_form, history_data_save_form
from galaxy.views import FilesToGalaxyDataLib, GenericFilesToGalaxyHistory, WorkflowListView, HistoryListView, HistoryDataCreateView
from galaxy.views import WorkflowRunView, TableFileSelectMixin
from galaxy.utils.history_actions import get_history_status
from mogi.models import HistoryDataMOGI
from mogi.filter import CAnnotationMOGIFilter

from rest_framework import viewsets
from mogi.serializers import IncomingGalaxyDataSerializer


########################################################################################################################
# REST
########################################################################################################################
class IncomingGalaxyDataViewSet(viewsets.ModelViewSet):
    """
    """
    queryset = IncomingGalaxyData.objects.all()
    serializer_class =  IncomingGalaxyDataSerializer


class IncomingGalaxyDataListView(LoginRequiredMixin, SingleTableMixin, ListView):
    '''
    '''
    table_class = IncomingGalaxyDataTable
    model = IncomingGalaxyData
    template_name = 'mogi/incoming_galaxy_data.html'




########################################################################################################################
# Galaxy ISA uploads and workflows
########################################################################################################################
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
    redirect_to = 'isa_workflow_summary'


########################################################################################################################
# Galaxy History data upload to django-metab
########################################################################################################################
class HistoryDataMogiListView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        data = get_history_data(self.kwargs['pk'], request.user, data_type=['sqlite'])

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

        result = save_lcms_mogi.delay(request.user.id,
                                      galaxy_name,
                                      galaxy_data_id,
                                      galaxy_history_id,
                                      investigation_name)

        self.request.session['result'] = result.id
        return render(self.request, 'gfiles/status.html', {'s': 0, 'progress': 0})







########################################################################################################################
# django-metab Peak and annotation summary
########################################################################################################################
class CPeakGroupMetaListMogiView(CPeakGroupMetaListView):
    table_class =CPeakGroupMetaMogiTable
    model = CPeakGroupMetaMOGI

    def get_queryset(self):
        # To get django-tables2 to play nicely with properties need tot trun queryset into list!
        # https://stackoverflow.com/questions/26985132/django-tables2-how-to-order-by-accessor
        qs = super(CPeakGroupMetaListMogiView, self).get_queryset()
        return list(qs)


class CAnnotationListAllMogiView(CAnnotationListAllView):
    table_class = CAnnotationMogiTable
    model = CAnnotationMOGI
    filterset_class = CAnnotationMOGIFilter
    template_name = 'mogi/cpeakgroup_annotations_all_mogi.html'

    def get_queryset(self):
        return self.model.objects.all().order_by('-cannotation__weighted_score')



class CAnnotationDownloadMogiView(CAnnotationDownloadView):

    def form_valid(self, form):
        obj = form.save()
        obj.user = self.request.user
        obj.save()

        result = download_cannotations_mogi_task.delay(obj.pk, self.request.user.id)
        self.request.session['result'] = result.id

        return render(self.request, 'gfiles/status.html', {'s': 0, 'progress': 0})


########################################################################################################################
# Generic
########################################################################################################################
def index(request):
    summary_d = {}
    summary_d['dataset_nm'] = len(MetabInputData.objects.all())

    summary_d['isa_nm'] = len(Investigation.objects.all())

    summary_d['workflow_nm'] = len(Workflow.objects.all())


    summary_d['ann_nm'] = len(CAnnotation.objects.filter(Q(spectral_matching_average_score__gt=0.6) |
                                                         Q(ms1_average_score__gt=0.0) |
                                                         Q(metfrag_average_score__gt=0.0) |
                                                         Q(sirius_csifingerid_average_score__gt=0.0) |
                                                         Q(mzcloud_average_score__gt=0.6)
                                                         ).values('cpeakgroup').distinct())


    return render(request, 'gfiles/index.html', summary_d)

def about(request):
    return render(request, 'mogi/about.html')

def submitted(request):
    return render(request, 'galaxy/submitted.html')

def success(request):
    return render(request, 'dma/success.html')





