# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import six
import collections
import numpy as np
import seaborn as sns
import plotly.offline as opy
import plotly.graph_objs as go

from django.db.models import Q
from django.db import connection
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from django.views.generic import CreateView, ListView, View
from django.urls import reverse_lazy
from django.db.models import Q

from mogi.models import models_annotations, models_peaks, models_libraries, models_inputdata
from mogi.tables import tables_annotations, tables_peaks
from mogi.filter import filter_annotations
from mogi.forms import forms_annotations
from mogi.tasks import download_cannotations_mogi_task
from mogi.views import views_peaks
from mogi.utils.upload_adduct_rules import upload_adduct_rules







class CombinedAnnotationListView(LoginRequiredMixin, SingleTableMixin, FilterView):
    '''
    '''
    table_class = tables_annotations.CombinedAnnotationTable
    model = models_annotations.CombinedAnnotation
    template_name = 'mogi/combinedpeak_annotations.html'
    filterset_class = filter_annotations.CombinedAnnotationFilter


    def get_queryset(self):
        # return self.model.objects.filter(cpeakgroup_id= self.kwargs.get('cid')).order_by('-weighted_score')
        if self.request.user.is_superuser:
            cp = self.model.objects.filter().order_by('-rank')
        elif self.request.user.is_authenticated:
            cp = self.model.objects.filter(Q(combinedpeak__metabinputdata__public=True) |
                                           Q(combinedpeak__metabinputdata__user=self.request.user)).order_by('-rank')
        else:
            cp = self.model.objects.filter(combinedpeak__metabinputdata=True).order_by('-rank')

        return cp.filter(combinedpeak_id=self.kwargs.get('cid'))

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(CombinedAnnotationListView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['cid'] = self.kwargs.get('cid')
        context['mid'] = models_peaks.MetabInputData.objects.get(combinedpeak__id=self.kwargs.get('cid')).id
        return context

class MetaboliteAnnotationListView(LoginRequiredMixin, SingleTableMixin, ListView):
    '''
    '''
    table_class = tables_annotations.MetaboliteAnnotationTable
    model = models_annotations.MetaboliteAnnotation
    template_name = 'mogi/metabolite_annotations.html'

    def get_queryset(self):
        # Get CPeakGroup Annotations (filtered by inchikey)
        print(self.kwargs.get('cid'))

        cp = views_peaks.metabinput_permissions_check(self.request, models_peaks.CombinedPeak)
        cp = cp.filter(id=self.kwargs.get('cid')).first()
        print(cp)
        qs = ''

        if not cp:
            return qs

        if cp.cpeakgroup:
            qs = self.model.objects.filter(cpeakgroup_id=cp.cpeakgroup.id)

        if cp.speak:
            # Get SPeak (fractionation) annotations filtered by inchikey
            qs_speak = self.model.objects.filter(speak_id=cp.speak.id)
            if qs:
                qs = qs | qs_speak
            else:
                qs = qs_speak

            with connection.cursor() as cursor:
                sqlstmt = """SELECT spm.id FROM mogi_speakmeta AS spm
                        LEFT JOIN mogi_speakmetaspeaklink AS smxs ON smxs.speakmeta_id=spm.id 
                        LEFT JOIN mogi_speak AS sp ON sp.id=smxs.speak_id
                        LEFT JOIN mogi_speakspeaklink AS spXsp ON spXsp.speak2_id=sp.id
                        WHERE spXsp.speak1_id={}
                """.format(cp.speak.id)
                cursor.execute(sqlstmt)
                spms_id = [i[0] for i in cursor.fetchall()]
                print(spms_id)

                qs_speakmeta = self.model.objects.filter(speakmeta__id__in=spms_id)
                if qs:
                    qs = qs | qs_speakmeta
                else:
                    qs = qs_speakmeta

        if qs:
            inchikey = self.kwargs.get('inchikey')
            inchikey1 = inchikey.split('-')[0]
            qs = qs.filter(Q(inchikey1=inchikey1) | Q(inchikey=inchikey) | Q(
                libraryspectrameta__inchikey=inchikey))


        return qs

    # def get_context_data(self, **kwargs):
    #     # Call the base implementation first to get a context
    #     context = super(CombinedAnnotationListView, self).get_context_data(**kwargs)
    #     # Add in a QuerySet of all the books
    #     context['cid'] = self.kwargs.get('cid')
    #     context['mid'] = models_peaks.MetabInputData.objects.get(combinedpeak__id=self.kwargs.get('cid')).id
    #     return context

class MetaboliteAnnotationDetailsListView(LoginRequiredMixin, SingleTableMixin, ListView):
    '''
    '''
    table_class = tables_annotations.MetaboliteAnnotationDetailTable
    model = models_annotations.MetaboliteAnnotationDetail
    template_name = 'mogi/metabolite_annotation_details.html'

    def get_queryset(self):
        if self.request.user.is_superuser:
            mad = self.model.objects.all()
        elif self.request.user.is_authenticated:
            mad = self.model.objects.filter(Q(metaboliteannotation__metabinputdata__public=True) |
                                          Q(metaboliteannotation__metabinputdata__user=self.request.user))
        else:
            mad = self.model.objects.filter(metaboliteannotation__metabinputdata__public=True)
        return mad.filter(metaboliteannotation__id = self.kwargs.get('maid'))



    def get_context_data(self, **kwargs):
        context = super(MetaboliteAnnotationDetailsListView, self).get_context_data(**kwargs)
        context['table_scores'] = tables_annotations.MetaboliteAnnotationScoreTable(
                                                        models_annotations.MetaboliteAnnotationScore.objects.filter(
                                                            metaboliteannotation__id=self.kwargs.get('maid')
                                                        ))

        mad = models_annotations.MetaboliteAnnotation.objects.filter(id=self.kwargs.get('maid')).first()


        mid = models_inputdata.MetabInputData.objects.filter(metaboliteannotation__id=mad.id).first()
        cp = models_peaks.CombinedPeak.objects.filter(Q(cpeakgroup__id=mad.cpeakgroup_id) |
                                                      Q(speak=mad.speak_id)).first()

        context['mid_id'] = mid.id
        context['cp_id'] = cp.id


        ma = models_annotations.MetaboliteAnnotation.objects.filter(id=self.kwargs.get('maid')).first()

        if ma.libraryspectrameta:
            context = sm_plot(ma.speakmeta.id, ma.libraryspectrameta.id, context)

        return context


class CombinedAnnotationListAllView(LoginRequiredMixin, SingleTableMixin, FilterView):
    '''
    '''
    table_class = tables_annotations.CombinedAnnotationTable
    model = models_annotations.CombinedAnnotation
    template_name = 'mogi/combinedpeak_annotations_all.html'
    filterset_class = filter_annotations.CombinedAnnotationFilter

    def get_queryset(self):
        if self.request.user.is_superuser:
            return self.model.objects.all().order_by('-rank')
        elif self.request.user.is_authenticated:
            return self.model.objects.filter(Q(combinedpeak__metabinputdata__public=True) |
                                             Q(combinedpeak__metabinputdata__user=self.request.user)).order_by('-rank')
        else:
            return self.model.objects.filter(combinedpeak__metabinputdata=True).order_by('-rank')



class CombinedAnnotationDownloadView(LoginRequiredMixin, CreateView):
    template_name = 'mogi/canns_download.html'
    model = models_annotations.CombinedAnnotationDownload
    success_url = reverse_lazy('canns_download_result')

    form_class = forms_annotations.CombinedAnnotationDownloadForm

    def form_valid(self, form):
        obj = form.save()
        obj.user = self.request.user
        obj.save()

        result = download_cannotations_mogi_task.delay(obj.pk, self.request.user.id)
        self.request.session['result'] = result.id

        return render(self.request, 'gfiles/status.html', {'s': 0, 'progress': 0})

    # def form_valid(self, form):
    #     rank = form.cleaned_data['rank']
    #     if rank:
    #         canns = CAnnotation.objects.filter(rank_lte=rank)
    #     else:
    #         canns = CAnnotation.objects.all()
    #
    #     canns_table = CAnnotationTable(canns)
    #
    #     form.instance.user = self.request.user
    #     obj = form.save()
    #     canns_download_result = CAnnotationDownloadResult()
    #     canns_download_result.cannotationdownload = obj
    #     canns_download_result.save()
    #
    #     dirpth = tempfile.mkdtemp()
    #     fnm = 'c_peak_group_annotations.csv'
    #     tmp_pth = os.path.join(dirpth, fnm)
    #
    #     print(canns_table)
    #     # django-tables2 table to csv
    #     with open(tmp_pth, 'w', newline='') as csvfile:
    #         writer = csv.writer(csvfile, delimiter=',')
    #         for row in canns_table.as_values():
    #             print(row)
    #             writer.writerow(row)
    #
    #     canns_download_result.annotation_file.save(fnm, File(open(tmp_pth)))
    #
    #     return super(CAnnotationDownloadView, self).form_valid(form)



class CombinedAnnotationDownloadResultView(LoginRequiredMixin, SingleTableMixin, FilterView):
    '''
    '''
    table_class = tables_annotations.CombinedAnnotationDownloadResultTable
    model = models_annotations.CombinedAnnotationDownloadResult
    template_name = 'mogi/cannotation_download_result.html'
    filterset_class = filter_annotations.CombinedAnnotationDownloadResultFilter

    def get_queryset(self):
        return self.model.objects.filter(cannotationdownload__user=self.request.user)




def sm_plot(spm_id, lsm_id, context):
    #sm = models_annotations.MetaboliteAnnotation.objects.get(id=spm_id)
    spm = models_peaks.SPeakMeta.objects.get(id=spm_id)

    # Get experimental spectra

    values = models_peaks.SPeak.objects.filter(
        speakmeta_id=spm_id
    ).values(
        'mz',
        'i',
        'speakmeta_id',
        'speakmeta__spectrum_type'
    )

    values4plot = collections.defaultdict(list)

    for d in values:
        spmid = d['speakmeta_id']

        if not values4plot[spmid]:
            values4plot[spmid] = collections.defaultdict(list)

        values4plot[spmid]['mz'].append(d['mz'])
        values4plot[spmid]['i'].append(d['i'])
        values4plot[spmid]['spmid'].append(d['speakmeta_id'])
        values4plot[spmid]['spectrum_type'].append(d['speakmeta__spectrum_type'])

    np.random.seed(sum(map(ord, "palettes")))
    c = 0
    current_palette = sns.color_palette('colorblind', 2)
    colour = current_palette.as_hex()

    data = []

    # Experimental
    for k, v in six.iteritems(values4plot):

        mzs = v['mz']
        intens = v['i']
        intens = [i / max(intens) * 100 for i in intens]
        spmids = v['spmid']
        stype = v['spectrum_type']


        for i in range(0, len(mzs)):
            if i == 0:
                showLegend = True
            else:
                showLegend = False

            name = 'spm_id = {i}, spec type = {t}'.format(i=spmids[i], t=stype[i])

            trace = go.Scatter(x=[mzs[i], mzs[i]],
                               y=[0, intens[i]],
                               mode='lines+markers',
                               name=name,
                               legendgroup=name,
                               showlegend=showLegend,
                               line=dict(color=(str(colour[0]))))

            data.append(trace)

    # library
    libm = models_libraries.LibrarySpectraMeta.objects.get(pk=lsm_id)

    ls = models_peaks.SPeak.objects.filter(speakmeta__id=lsm_id)
    showLegend = True


    for i in ls:

        trace = go.Scatter(x=[i.mz, i.mz],
                           y=[0, -i.i],
                           mode='lines+markers',
                           name=libm.name,
                           legendgroup=libm.name,
                           showlegend=showLegend,
                           line=dict(color=(str(colour[1]))))

        data.append(trace)
        if showLegend:
            showLegend = False

    layout = dict(title='Spectral match',
                  xaxis=dict(title='m/z'),
                  yaxis=dict(title='Relative abundance'),
                  )

    # layout = go.Layout(title="Meine Daten", xaxis={'title': 'x1'}, yaxis={'title': 'x2'})
    figure = go.Figure(data=data, layout=layout)
    div = opy.plot(figure, auto_open=False, output_type='div')

    context['graph'] = div

    context['data'] = ''


    # if spm.spectrum_type == 'scan':
    #
    #     cpgm_id = models_peaks.CPeakGroupMeta.objects.get(
    #         cpeakgroup__cpeak__speakmeta_frag=values[0]['speakmeta_id']).id
    #     cpg_id = models_peaks.CPeakGroup.objects.get(cpeak__speakmeta_frag=values[0]['speakmeta_id']).id
    #     context['cpgm_id'] = cpgm_id
    #     context['cpg_id'] = cpg_id
    # else:
    #
    #     cpgm_id = models_peaks.CPeakGroupMeta.objects.get(cpeakgroup__id=spm.cpeakgroup_id).id
    #     context['cpgm_id'] = cpgm_id
    #     context['cpg_id'] = spm.cpeakgroup_id

    return context


class SMatchView(LoginRequiredMixin, SingleTableMixin, ListView):
    '''
    '''
    table_class = tables_peaks.SPeakTable
    model = models_peaks.SPeak
    template_name = 'mogi/spectral_matching.html'

    def get_queryset(self):

        return models_peaks.SPeak.objects.filter(
            speakmeta__spectralmatching=self.kwargs.get('spmid'))

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(SMatchView, self).get_context_data(**kwargs)

        context = sm_plot(self.kwargs.get('spmid'))




        return context


class UploadAdductRules(LoginRequiredMixin, View):

    success_msg = ""
    success_url = '/dma/success'
    # initial = {'key': 'value'}
    template_name = 'mogi/upload_adduct_rules.html'

    def get(self, request, *args, **kwargs):

        form = forms_general.UploadAdductsForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = UploadAdductsForm(request.POST, request.FILES)

        if form.is_valid():
            adduct_rules = form.cleaned_data['adduct_rules']
            upload_adduct_rules(adduct_rules)
            return render(request, 'dma/success.html')
        else:
            print(form.errors)

        return render(request, self.template_name, {'form': form})

########################
# Depcrecated
########################
class CPeakGroupSpectralMatchingListView(LoginRequiredMixin, SingleTableMixin, ListView):
    '''
    '''
    table_class = tables_annotations.SpectralMatchingTable
    model = models_annotations.MetaboliteAnnotation
    template_name = 'mogi/cpeakgroup_spectral_matching_summary.html'
    def get_queryset(self):
        return SpectralMatching.objects.filter(cpeakgroup=self.kwargs.get('cgid')).order_by('-dpc')

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(CPeakGroupSpectralMatchingListView, self).get_context_data(**kwargs)
        context['cpg_id'] = self.kwargs.get('cgid')
        context['cpgm_id'] = models_peaks.CPeakGroupMeta.objects.get(cpeakgroup__id=self.kwargs.get('cgid')).id
        return context
