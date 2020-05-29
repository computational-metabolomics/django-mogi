# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from django.contrib.auth.mixins import LoginRequiredMixin
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin

from django_tables2.export.views import ExportMixin

from mogi.models import models_compounds
from mogi.tables import tables_compounds
from mogi.filter import filter_compounds



class CompoundListView(LoginRequiredMixin, SingleTableMixin, FilterView):
    '''
    '''
    table_class = tables_compounds.CompoundTable
    model = models_compounds.Compound
    template_name = 'mogi/compound_list.html'
    filterset_class = filter_compounds.CompoundFilter





