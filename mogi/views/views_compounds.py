# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from django.contrib.auth.mixins import LoginRequiredMixin
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from django.views.generic import CreateView, UpdateView, View
from django_tables2.export.views import ExportMixin
from django.shortcuts import render

from mogi.models import models_compounds
from mogi.tables import tables_compounds
from mogi.filter import filter_compounds
from mogi.views import views_isa
from mogi.forms import forms_compounds
from mogi.tasks import upload_compounds_task
from django_tables2.export.views import ExportMixin

class CompoundListView(ExportMixin, SingleTableMixin, FilterView):
    '''
    '''
    table_class = tables_compounds.CompoundTable
    model = models_compounds.Compound
    template_name = 'mogi/compound_list.html'
    filterset_class = filter_compounds.CompoundFilter
    export_formats = ['csv']
    export_name = 'compounds'

    def get_filterset_kwargs(self, filterset_class):
        kwargs = super(CompoundListView, self).get_filterset_kwargs(filterset_class)
        if kwargs["data"] is None:
            kwargs["data"] = {"smbool": 'true', "metfragbool": 'true', "siriusbool": 'true'}
        elif "smbool" not in kwargs["data"]:
            kwargs["data"] = kwargs["data"].copy()
            kwargs["data"]["smbool"] = 'true'
            kwargs["data"]["metfragbool"] = 'true'
            kwargs["data"]["siriusbool"] = 'true'

        return kwargs

class UploadCompounds(views_isa.ISAOperatorMixin, CreateView):
    redirect_string = 'data_and_results_summary'
    task_string = 'create'
    permission_required = 'mogi.add_uploadcompounds'
    success_message = 'Upload started'
    permission_denied_message = 'Permission Denied'
    success_url = 'data_and_results_summary'
    model = models_compounds.UploadCompounds
    form_class = forms_compounds.UploadCompoundsForm


    def form_valid(self, form):
        # The user is automatically added to the model based on whoever is logged in at the time
        i = form.save(commit=False)
        i.user = self.request.user
        ofn = self.request.FILES['data_file'].name
        i.original_filename = ofn
        i.save()

        form.save_m2m()

        result = upload_compounds_task.delay(i.pk, self.request.user.id)
        self.request.session['result'] = result.id

        return render(self.request, 'gfiles/status.html', {'s': 0, 'progress': 0})

