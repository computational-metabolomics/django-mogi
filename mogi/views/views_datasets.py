# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from django.db.models import Q
from django.views.generic import CreateView, ListView
from django_tables2.views import SingleTableMixin
from django.views.generic import CreateView, UpdateView, View
from django.shortcuts import render
from django.urls import reverse_lazy

from mogi.models import models_datasets
from mogi.tables import tables_datasets
from mogi.forms import forms_datasets
from mogi.tasks import upload_dataset_task
from mogi.views import views_isa


class DatasetListView(SingleTableMixin, ListView):
    '''
    '''
    table_class = tables_datasets.ResultsDataTable
    model = models_datasets.Dataset
    template_name = 'mogi/results_summary.html'




class UploadDatasetsView(views_isa.ISAOperatorMixin, CreateView):


    redirect_string = 'data_and_results_summary'
    task_string = 'create'
    permission_required = 'mogi.add_dataset'
    success_message = 'Upload started'
    permission_denied_message = 'Permission Denied'
    success_url = 'data_and_results_summary'
    model = models_datasets.UploadDatasets
    form_class = forms_datasets.UploadDatasetsForm

    def form_valid(self, form):
        # The user is automatically added to the model based on whoever is logged in at the time
        i = form.save(commit=False)
        i.user = self.request.user
        ofn = self.request.FILES['data_file'].name
        i.original_filename = ofn
        i.save()
        
        form.save_m2m()
        
        result = upload_dataset_task.delay(i.pk, self.request.user.id)
        self.request.session['result'] = result.id


        return render(self.request, 'gfiles/status.html', {'s': 0, 'progress': 0})
