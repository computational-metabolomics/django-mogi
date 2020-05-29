# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from django.views.generic import CreateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render


from galaxy.models import Workflow
from mogi.models import models_isa, models_compounds, models_inputdata


########################################################################################################################
# Generic
########################################################################################################################
def index(request):
    summary_d = {}
    summary_d['dataset_nm'] = len(models_inputdata.MetabInputData.objects.all())

    summary_d['isa_nm'] = len(models_isa.Investigation.objects.all())

    summary_d['workflow_nm'] = len(Workflow.objects.all())

    # we only have compounds detailed where we have some form of annotation
    summary_d['ann_nm'] = len(models_compounds.Compound.objects.all())


    return render(request, 'gfiles/index.html', summary_d)


def about(request):
    return render(request, 'mogi/about.html')


def submitted(request):
    return render(request, 'mogi/submitted.html')


def success(request):
    return render(request, 'mogi/success.html')


class DataAndResultsSummaryView(LoginRequiredMixin, View):
    # initial = {'key': 'value'}
    template_name = 'mogi/data_and_results_summary.html'

    def get(self, request, *args, **kwargs):

        return render(request, self.template_name)





