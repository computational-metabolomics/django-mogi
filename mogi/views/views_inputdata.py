# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from django.db.models import Q
from django.views.generic import CreateView, ListView
from django_tables2.views import SingleTableMixin
from django.views.generic import CreateView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy

from mogi.models import models_inputdata
from mogi.tables import tables_inputdata
from mogi.forms import forms_inputdata
from mogi.tasks import upload_metab_results_task
from mogi.views import views_isa


class MetabInputDataListView(LoginRequiredMixin, SingleTableMixin, ListView):
    '''
    '''
    table_class = tables_inputdata.MetabInputDataTable
    model = models_inputdata.MetabInputData
    template_name = 'mogi/metabinputdata_summary.html'

    def get_queryset(self):
        if self.request.user.is_superuser:
            return self.model.objects.all()
        elif self.request.user.is_authenticated:
            return self.model.objects.filter(Q(public=True) | Q(user=self.request.user))
        else:
            return self.model.objects.filter(public=True)



class UploadMetabResults(views_isa.ISAOperatorMixin, CreateView):


    redirect_string = 'data_and_results_summary'
    task_string = 'create'
    permission_required = 'mogi.metabinputdata'
    success_message = 'Upload started'
    permission_denied_message = 'Permission Denied'
    success_url = 'data_and_results_summary'
    model = models_inputdata.MetabInputData
    form_class = forms_inputdata.MetabInputDataForm

    def form_valid(self, form):
        # The user is automatically added to the model based on whoever is logged in at the time
        i = form.save(commit=False)
        i.user = self.request.user
        ofn = self.request.FILES['data_file'].name
        i.original_filename = ofn
        i.save()
        
        form.save_m2m()
        
        result = upload_metab_results_task.delay(i.pk, self.request.user.id)
        self.request.session['result'] = result.id


        return render(self.request, 'gfiles/status.html', {'s': 0, 'progress': 0})



class MetabInputDataUpdateView(views_isa.ISAOperatorMixin, UpdateView):

    redirect_string = 'metabinputdata_summary'
    task_string = 'update'
    permission_required = 'mogi.metabinputdata'
    success_message = 'Metabolomics experimental data updated'
    permission_denied_message = 'Permission Denied'
    success_url = reverse_lazy('metabinputdata_summary')
    model = models_inputdata.MetabInputData
    form_class = forms_inputdata.MetabInputDataForm

