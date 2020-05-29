# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
from django.views.generic import CreateView, ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django_tables2.views import SingleTableMixin


from mogi.models import models_search
from mogi.forms import forms_search
from mogi.tables import tables_search
from mogi.tasks import search_mz_task, search_nm_task, search_frag_task

class SearchNmParamCreateView(LoginRequiredMixin, CreateView):
    model = models_search.SearchNmParam
    form_class = forms_search.SearchNmParamForm
    success_url = '/mogi/success'

    def form_valid(self, form):
        form.instance.user = self.request.user
        snp = form.save()
        result = search_nm_task.delay(snp.id, self.request.user.id)
        self.request.session['result'] = result.id
        return render(self.request, 'gfiles/status.html', {'s': 0, 'progress': 0})


class SearchMzParamCreateView(LoginRequiredMixin, CreateView):
    model = models_search.SearchMzParam
    form_class = forms_search.SearchMzParamForm
    success_url = '/mogi/success'

    def form_valid(self, form):
        form.instance.user = self.request.user
        smp = form.save()
        result = search_mz_task.delay(smp.id, self.request.user.id)
        self.request.session['result'] = result.id
        return render(self.request, 'gfiles/status.html', {'s': 0, 'progress': 0})


class SearchFragParamCreateView(LoginRequiredMixin, CreateView):
    model = models_search.SearchFragParam
    form_class = forms_search.SearchFragParamForm
    success_url = '/mogi/success'

    def get_initial(self):
        initial = super(SearchFragParamCreateView, self).get_initial()
        initial['products'] = "60.0827,201.2\n104.1075,2115"
        initial['mz_precursor'] = 104.10751
        initial['description'] = 'Choline [M+H]+'
        return initial

    def form_valid(self, form):
        form.instance.user = self.request.user
        sp = form.save()
        # result = search_frag(sp.id)
        result = search_frag_task.delay(sp.id, self.request.user.id)
        self.request.session['result'] = result.id
        # self.request.session['result'] = result.id
        return render(self.request, 'gfiles/status.html', {'s': 0, 'progress': 0})



class SearchResultListView(LoginRequiredMixin, SingleTableMixin, ListView):
    model = models_search.SearchResult
    table_class = tables_search.SearchResultTable
    template_name = 'mogi/searchresult_list.html'





