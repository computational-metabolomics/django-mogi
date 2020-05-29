# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import collections
import numpy as np
import seaborn as sns
import plotly.offline as opy
import plotly.graph_objs as go
import six

from django.db.models import Q
from django.views.generic import CreateView, ListView
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from django.db import connection
from django.http import HttpResponseRedirect
from django.contrib import messages

from mogi.models import models_peaks, models_inputdata
from mogi.tables import tables_peaks
from mogi.filter import filter_peaks

from django.contrib import messages


def metabinput_permissions_check(request, model):
    if request.user.is_superuser:
        return model.objects.all()
    elif request.user.is_authenticated:
        return model.objects.filter(Q(metabinputdata__public=True) | Q(metabinputdata__user=request.user))
    else:
        return model.objects.filter(metabinputdata__public=True)



#################################################################################
# Combined peaks (includes both CPeakGroups and SPeaks (from fractionation)
#################################################################################
class CombinedPeakAllListView(LoginRequiredMixin, SingleTableMixin, FilterView):
    '''
    '''
    table_class = tables_peaks.CombinedPeakTable
    filterset_class = filter_peaks.CombinedPeakFilter
    model = models_peaks.CombinedPeak
    template_name = 'mogi/combinedpeak_summary_all.html'

    def get_queryset(self):
        return metabinput_permissions_check(self.request, self.model)

class CombinedPeakListView(LoginRequiredMixin, SingleTableMixin, FilterView):
    '''
    '''
    table_class = tables_peaks.CombinedPeakTable
    filterset_class = filter_peaks.CombinedPeakFilter
    model = models_peaks.CombinedPeak
    template_name = 'mogi/combinedpeak_summary.html'

    def get_queryset(self):
        combinedpeaks = metabinput_permissions_check(self.request, self.model)
        return combinedpeaks.filter(metabinputdata_id=self.kwargs.get('mid'))


class Frag4CombinedPeakListView(LoginRequiredMixin, SingleTableMixin, ListView):
    table_class = tables_peaks.SPeakMetaTable
    model = models_peaks.SPeakMeta
    template_name = 'mogi/frag4combinedpeak.html'

    def get_context_data(self, **kwargs):
        context = super(Frag4CombinedPeakListView, self).get_context_data(**kwargs)
        mid = models_inputdata.MetabInputData.objects.filter(combinedpeak__id=self.kwargs.get('cid')).last()
        context['mid_id'] = mid.id
        context['cid_id'] = self.kwargs.get('cid')
        return context

    def get_queryset(self):
        combinedpeaks = metabinput_permissions_check(self.request, models_peaks.CombinedPeak)
        combinedpeak = combinedpeaks.filter(id=self.kwargs.get('cid')).first()

        frag = ''

        if combinedpeak.cpeakgroup:
            # Fragmentation (individual scans - LC-MS/MS)
            frag_lcmsms_scans = models_peaks.SPeakMeta.objects.filter(
                speakmetacpeakfraglink__cpeak__cpeakgroupcpeaklink__cpeakgroup_id=combinedpeak.cpeakgroup_id
            )

            # Fragmentation (averaged scans - LC-MS/MS)
            frag_lcmsms_average = models_peaks.SPeakMeta.objects.filter(
                cpeakgroup_id=combinedpeak.cpeakgroup_id
            )
            frag = frag_lcmsms_scans | frag_lcmsms_average

        if combinedpeak.speak:

            # Fragmentation for fracationataion.
            # Three different types of spectra
            #   - Each energy merged (non adjusted MS/MS data) - e.g. 20, 40, 80
            #   - Each energy merged (adjust MS/MS data) Adjust for each MF annotation e.g. 20 MF1, 20 MF2, 40 MF1 ...
            #   - All merged and adjusted - all levels are merged and mz adjusted for each MF

            sqlstmt = """SELECT spm.id FROM mogi_speakmeta AS spm
                    LEFT JOIN mogi_speakmetaspeaklink AS smxs ON smxs.speakmeta_id=spm.id 
                    LEFT JOIN mogi_speak AS sp ON sp.id=smxs.speak_id
                    LEFT JOIN mogi_speakspeaklink AS spXsp ON spXsp.speak2_id=sp.id
                    WHERE spXsp.speak1_id={}
            """.format(combinedpeak.speak.id)

            with connection.cursor() as cursor:
                cursor.execute(sqlstmt)
                speakmeta_ids = [i[0] for i in cursor.fetchall()]
                print(speakmeta_ids)

            frag_fract = models_peaks.SPeakMeta.objects.filter(id__in=speakmeta_ids)

            if frag:
                frag = frag | frag_fract
            else:
                frag = frag_fract

        return frag


class SPeakPlotView(LoginRequiredMixin, SingleTableMixin, ListView):
    '''
    '''
    table_class = tables_peaks.SPeakTable
    model = models_peaks.SPeak
    template_name = 'mogi/speak_plot.html'

    def sid2sids(self):
        return [int(x) for x in self.kwargs.get('sid').split('/') if x]

    def get_queryset(self):
        return models_peaks.SPeak.objects.filter(speakmeta__id__in=self.sid2sids())

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(SPeakPlotView, self).get_context_data(**kwargs)

        values = models_peaks.SPeak.objects.filter(
            speakmeta__id__in=self.sid2sids()
        ).values(
            'mz',
            'i',
            'speakmeta__scan_num',
            'speakmeta__spectrum_type',
            'speakmeta__spectrum_detail',
            'speakmeta__id',
        )

        print(values)

        values4plot = collections.defaultdict(list)


        for d in values:
            spmid = d['speakmeta__id']

            if not values4plot[spmid]:
                values4plot[spmid] = collections.defaultdict(list)

            values4plot[spmid]['mz'].append(d['mz'])
            values4plot[spmid]['i'].append(d['i'])
            values4plot[spmid]['scan_num'].append(d['speakmeta__scan_num'])
            values4plot[spmid]['spectrum_type'].append(d['speakmeta__spectrum_type'])
            values4plot[spmid]['spectrum_detail'].append(d['speakmeta__spectrum_detail'])
            values4plot[spmid]['speakmeta_id'].append(d['speakmeta__id'])

        np.random.seed(sum(map(ord, "palettes")))
        c = 0
        current_palette = sns.color_palette('colorblind', len(values4plot))
        colour = current_palette.as_hex()

        data = []


        for k, v in six.iteritems(values4plot):

            mzs = v['mz']
            intens = v['i']
            spectrum_type = v['spectrum_type']
            spectrum_detail = v['spectrum_detail']
            spectrum_id = v['speakmeta_id']

            scan_num = v['scan_num']

            for i in range(0, len(mzs)):
                if i==0:
                    showLegend = True
                else:
                    showLegend = False
                name = '{} {} {}'.format(spectrum_id[i], spectrum_type[i], spectrum_detail[i])

                trace = go.Scatter(x=[mzs[i], mzs[i]],
                                   y=[0, intens[i]],
                                mode='lines+markers',
                                name=name,
                                legendgroup=name,
                                showlegend = showLegend,
                                line=dict(color=(str(colour[c]))))

                data.append(trace)
            c += 1

        layout = dict(title='Spectra',
                      xaxis=dict(title='scan'),
                      yaxis=dict(title='intensity'),
                      )
        figure = go.Figure(data=data, layout=layout)
        div = opy.plot(figure, auto_open=False, output_type='div')

        context['graph'] = div

        context['data'] = ''


        return context




#################################################################################
# Extracted ion chromatogram
#################################################################################
class EicListView(LoginRequiredMixin, SingleTableMixin, ListView):
    '''
    '''
    table_class = tables_peaks.EicTable
    model = models_peaks.Eic
    template_name = 'mogi/eics.html'

    def get(self, *args, **kwargs):
        if self.kwargs.get('cgid') == 'None':
            messages.info(self.request, 'EIC not applicable for chosen feature')
            return HttpResponseRedirect(self.request.META.get('HTTP_REFERER', '/'))
        else:
            return super(EicListView, self).get(*args, **kwargs)

    def get_queryset(self):
        return models_peaks.Eic.objects.filter(cpeakgroup_id=self.kwargs.get('cgid'))

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(EicListView, self).get_context_data(**kwargs)

        if self.kwargs.get('cgid') == 'None':
            return context

        values = models_peaks.Eic.objects.filter(
            cpeakgroup_id=self.kwargs.get('cgid')
        ).values(
            'rt_corrected',
            'intensity',
            'cpeak__xcmsfileinfo__mfile__original_filename',
            'cpeak__xcmsfileinfo__classname'
        )

        values4plot = collections.defaultdict(list)


        for d in values:
            filename = d['cpeak__xcmsfileinfo__mfile__original_filename']
            if not values4plot[filename]:
                values4plot[filename] = collections.defaultdict(list)

            values4plot[filename]['intensity'].append(d['intensity'])
            values4plot[filename]['rt'].append(d['rt_corrected'])

        np.random.seed(sum(map(ord, "palettes")))
        c = 0
        current_palette = sns.color_palette('colorblind', len(values4plot))
        colour = current_palette.as_hex()

        data = []
        for k, v in six.iteritems(values4plot):
            trace = go.Scatter(
                x=v['rt'],
                y=v['intensity'],
                name=k,
                line=dict(
                    color=(str(colour[c])),
                    width=2)
                )

            data.append(trace)
            c += 1

        layout = dict(title='Extracted Ion Chromatgrams for individual peaks grouped between multiple files',
                      xaxis=dict(title='retention time'),
                      yaxis=dict(title='intensity'),
                      )

        # layout = go.Layout(title="Meine Daten", xaxis={'title': 'x1'}, yaxis={'title': 'x2'})
        figure = go.Figure(data=data, layout=layout)
        div = opy.plot(figure, auto_open=False, output_type='div')

        context['graph'] = div

        context['data'] = ''

        mid = models_peaks.MetabInputData.objects.get(combinedpeak__cpeakgroup__id=self.kwargs.get('cgid'))
        context['mid_id'] = mid.id



        return context




#################################################################################
# LC-MS stuff only (deprecated)
#################################################################################
# class CPeakGroupAllListView(LoginRequiredMixin, SingleTableMixin, ListView):
#     '''
#     '''
#     table_class = tables_peaks.CPeakGroupTable
#     model = models_peaks.CPeakGroup
#     template_name = 'mogi/cpeakgroup_summary_all.html'
#
#
# class CPeakGroupListView(LoginRequiredMixin, SingleTableMixin, FilterView):
#     '''
#     '''
#     table_class = tables_peaks.CPeakGroupTable
#     model = models_peaks.CPeakGroup
#     filterset_class = filter_peaks.CPeakGroupFilter
#     template_name = 'mogi/cpeakgroup_summary.html'
#
#     def get_queryset(self):
#
#         return models_peaks.CPeakGroup.objects.filter(cpeakgroupmeta_id= self.kwargs.get('cid'))
#
#
# class CPeakGroupMetaListView(LoginRequiredMixin, SingleTableMixin, ListView):
#     '''
#     '''
#     table_class = tables_peaks.CPeakGroupMetaTable
#     model = models_peaks.CPeakGroupMeta
#     template_name = 'mogi/cpeakmeta_summary.html'
#
#     def get_queryset(self):
#         # To get django-tables2 to play nicely with properties need to run queryset into list!
#         # https://stackoverflow.com/questions/26985132/django-tables2-how-to-order-by-accessor
#         qs = super(CPeakGroupMetaListView, self).get_queryset()
#         return list(qs)
#
#
# class Frag4FeatureListView(LoginRequiredMixin, SingleTableMixin, ListView):
#     '''
#     '''
#     table_class = tables_peaks.SPeakTable
#     model = models_peaks.SPeak
#     template_name = 'mogi/frag4feature.html'
#
#
#     def get_queryset(self):
#         return models_peaks.SPeak.objects.filter(
#             speakmeta__speakmetacpeakfraglink__cpeak__cpeakgrouplink__cpeakgroup_id=self.kwargs.get('cgid'))
#
#     def get_context_data(self, **kwargs):
#         # Call the base implementation first to get a context
#         context = super(Frag4FeatureListView, self).get_context_data(**kwargs)
#
#         values = models_peaks.SPeak.objects.filter(
#             speakmeta__speakmetacpeakfraglink__cpeak__cpeakgrouplink__cpeakgroup_id=self.kwargs.get('cgid')
#         ).values(
#             'mz',
#             'i',
#             'speakmeta__scan_num',
#             'speakmeta_id',
#             'speakmeta__run__mfile__original_filename',
#             'speakmeta__cpeak__xcmsfileinfo__classname',
#         )
#
#         values4plot = collections.defaultdict(list)
#
#
#         for d in values:
#             spmid = d['speakmeta_id']
#
#             filename = d['speakmeta__run__mfile__original_filename']
#             if not values4plot[spmid]:
#                 values4plot[spmid] = collections.defaultdict(list)
#
#             values4plot[spmid]['mz'].append(d['mz'])
#             values4plot[spmid]['i'].append(d['i'])
#             values4plot[spmid]['class'].append(d['speakmeta__cpeak__xcmsfileinfo__classname'])
#             values4plot[spmid]['filename'].append(d['speakmeta__run__mfile__original_filename'])
#             values4plot[spmid]['scan_num'].append(d['speakmeta__scan_num'])
#
#         np.random.seed(sum(map(ord, "palettes")))
#         c = 0
#         current_palette = sns.color_palette('colorblind', len(values4plot))
#         colour = current_palette.as_hex()
#
#         data = []
#
#
#         for k, v in six.iteritems(values4plot):
#
#             mzs = v['mz']
#             intens = v['i']
#             intens = [i/max(intens)*100 for i in intens]
#             filename = v['filename']
#             scan_num = v['scan_num']
#             peakclass = v['class']
#
#             for i in range(0, len(mzs)):
#                 if i==0:
#                     showLegend = True
#                 else:
#                     showLegend = False
#                 name = '{f} {s}'.format(f=filename[i], s=scan_num[i])
#
#                 trace = go.Scatter(x=[mzs[i], mzs[i]],
#                                 y=[0, intens[i]],
#                                 mode='lines+markers',
#                                 name=name,
#                                 legendgroup=name,
#                                 showlegend = showLegend,
#                                 line=dict(color=(str(colour[c]))))
#                 # trace =  dict(name=k,
#                 #               legendgroup=str(k),
#                 #               x=[mzs[i], mzs[i]],
#                 #               y=[0, intens[i]],
#                 #               mode = 'lines+markers',
#                 #
#                 #               line=dict(color=(str(colour[c]))))
#
#                 data.append(trace)
#             c += 1
#
#         layout = dict(title='Fragmentation spectra assoicated with a chromatographic grouped feature',
#                       xaxis=dict(title='scan'),
#                       yaxis=dict(title='intensity'),
#                       )
#
#         # layout = go.Layout(title="Meine Daten", xaxis={'title': 'x1'}, yaxis={'title': 'x2'})
#         figure = go.Figure(data=data, layout=layout)
#         div = opy.plot(figure, auto_open=False, output_type='div')
#
#         context['graph'] = div
#
#         context['data'] = ''
#
#         cpgm = CPeakGroupMeta.objects.get(cpeakgroup__id=self.kwargs.get('cgid'))
#         context['cpgm_id'] = cpgm.id
#
#         return context



