# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, AccessMixin
from django.shortcuts import render, redirect
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from mogi.models import models_datasets
from django.http import HttpResponseRedirect

import numpy as np
import collections
import seaborn as sns
import plotly.offline as opy
import plotly.graph_objs as go
import sqlite3

class EicView(LoginRequiredMixin, SuccessMessageMixin, TemplateView):
    '''
    '''

    template_name = 'mogi/eics.html'

    def get(self, *args, **kwargs):
        if self.kwargs.get('grpid') == 'None' or self.kwargs.get('did') == 'None':
            messages.info(self.request, 'EIC not applicable for chosen feature')
            return HttpResponseRedirect(self.request.META.get('HTTP_REFERER', '/'))
        else:
            return super(EicView, self).get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(EicView, self).get_context_data(**kwargs)

        if self.kwargs.get('grpid') == 'None' or self.kwargs.get('did') == 'None':
            return context

        grpid = self.kwargs.get('grpid')
        dataset_id = self.kwargs.get('did')
        dqs = models_datasets.Dataset.objects.filter(id=dataset_id )
        if dqs:
            print(dqs[0].sqlite.path)
            conn = sqlite3.connect(dqs[0].sqlite.path)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            sql_stmt = """SELECT rt_corrected, intensity, filename
                            FROM eics AS e        
                            LEFT JOIN
                                c_peaks AS c ON e.c_peak_id = c.cid
                            LEFT JOIN
                            fileinfo AS f ON f.fileid = c.fileid
                            WHERE e.grpid=={};
                        """.format(grpid)
        print(sql_stmt)
        r = c.execute(sql_stmt)

        values4plot = collections.defaultdict(list)

        for row in r:
            filename = row['filename']

            if not values4plot[filename]:
                values4plot[filename] = collections.defaultdict(list)

            values4plot[filename]['intensity'].append(row['intensity'])
            values4plot[filename]['rt'].append(row['rt_corrected'])

        np.random.seed(sum(map(ord, "palettes")))
        c = 0
        current_palette = sns.color_palette('colorblind', len(values4plot))
        colour = current_palette.as_hex()

        data = []
        for k, v in values4plot.items():
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

        layout = dict(title='Extracted Ion Chromatograms for individual peaks grouped between multiple files',
                      xaxis=dict(title='retention time'),
                      yaxis=dict(title='intensity'),
                      )

        # layout = go.Layout(title="Meine Daten", xaxis={'title': 'x1'}, yaxis={'title': 'x2'})
        figure = go.Figure(data=data, layout=layout)
        div = opy.plot(figure, auto_open=False, output_type='div')

        context['graph'] = div

        print(div)

        context['data'] = ''

        return context


class SPeakView(LoginRequiredMixin, SuccessMessageMixin, TemplateView):
    '''
    '''
    template_name = 'mogi/speak_plot.html'

    def get(self, *args, **kwargs):
        if self.kwargs.get('did') == 'None':
            messages.info(self.request, 'Fragmentation spectral not available for chosen feature')
            return HttpResponseRedirect(self.request.META.get('HTTP_REFERER', '/'))
        else:
            return super(SPeakView, self).get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(SPeakView, self).get_context_data(**kwargs)

        if self.kwargs.get('did') == 'None':
            return context

        grpid = self.kwargs.get('grpid')
        sid = self.kwargs.get('sid')
        dataset_id = self.kwargs.get('did')

        dqs = models_datasets.Dataset.objects.filter(id=dataset_id)
        if not dqs:
            return context

        print(dqs[0].sqlite.path)
        conn = sqlite3.connect(dqs[0].sqlite.path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        allpeaks = []
        if grpid != 'None':
            sql_stmt = """SELECT spm.pid, spm.acquisitionNum, sp.mz, sp.i, spm.spectrum_type, spm.name, '' AS filename
                               FROM s_peaks AS sp 
                                LEFT JOIN s_peak_meta AS spm ON sp.pid=spm.pid
                                WHERE sp.grpid=={};
                            """.format(grpid)
            print(sql_stmt)
            r = c.execute(sql_stmt)
            averaged_peaks = [row for row in r]

            sql_stmt = """SELECT spm.pid, spm.acquisitionNum, sp.mz, sp.i, spm.spectrum_type, spm.name, f.filename
                          FROM s_peaks AS sp
                               LEFT JOIN
                               s_peak_meta AS spm ON sp.pid = spm.pid
                               LEFT JOIN
                               c_peak_X_s_peak_meta AS cXspm ON cXspm.pid = spm.pid
                               LEFT JOIN
                               c_peak_X_c_peak_group AS cXcpg ON cXcpg.cid = cXspm.cid
                               LEFT JOIN
                               fileinfo AS f ON f.fileid = spm.fileid
                         WHERE cXcpg.grpid =={};
                            """.format(grpid)
            print(sql_stmt)
            r = c.execute(sql_stmt)
            individual_peaks = [row for row in r]

            allpeaks = allpeaks + averaged_peaks + individual_peaks

        if sid != 'None':
            sql_stmt = """SELECT spXsp.sid2
            FROM s_peaks AS sp 
              LEFT JOIN
                s_peaks_X_s_peaks AS spXsp ON spXsp.sid2 = sp.sid       
            WHERE spXsp.sid1={};
                            """.format(sid)
            # print(sql_stmt)
            r = c.execute(sql_stmt)
            sid2s = [str(row['sid2']) for row in r]
            print(sid2s)

            sql_stmt = """SELECT spm.pid, spm.acquisitionNum, sp.mz, sp.i, spm.spectrum_type, spm.name, '' AS filename
                            FROM s_peaks AS sp
                            LEFT JOIN
                                s_peak_meta AS spm ON spm.pid = sp.pid
                            LEFT JOIN
                                s_peak_meta_X_s_peaks AS sxs ON sxs.pid = spm.pid
                            WHERE sxs.sid IN ('{}')
                            """.format("','".join(sid2s))
            print(sql_stmt)
            r = c.execute(sql_stmt)
            dimspeaks = [row for row in r]
            allpeaks = allpeaks + dimspeaks

            print(dimspeaks)

        values4plot = collections.defaultdict(list)

        if not allpeaks:
            messages.info(self.request, 'Fragmentation spectral not available for chosen feature')

        for row in allpeaks:
            spmid = row['pid']

            if not values4plot[spmid]:
                values4plot[spmid] = collections.defaultdict(list)

            values4plot[spmid]['mz'].append(row['mz'])
            values4plot[spmid]['i'].append(row['i'])
            values4plot[spmid]['scan_num'].append(row['acquisitionNum'])
            values4plot[spmid]['spectrum_type'].append(row['spectrum_type'])
            if row['name']:
                values4plot[spmid]['spectrum_detail'].append(row['name'])
            elif row['filename']:
                values4plot[spmid]['spectrum_detail'].append(row['filename'])
            else:
                values4plot[spmid]['spectrum_detail'].append('')
            values4plot[spmid]['pid'].append(row['pid'])

        np.random.seed(sum(map(ord, "palettes")))
        c = 0
        current_palette = sns.color_palette('colorblind', len(values4plot))
        colour = current_palette.as_hex()

        data = []
        print(values4plot)

        for k, v in values4plot.items():

            mzs = v['mz']
            intens = v['i']
            spectrum_type = v['spectrum_type']
            spectrum_detail = v['spectrum_detail']
            spectrum_id = v['pid']

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
                      height=700,
                      xaxis=dict(title='scan'),
                      yaxis=dict(title='intensity'),
                      legend=dict(
                          orientation="v",
                          yanchor="bottom",
                          y=-1.1,
                          xanchor="left",
                          x=0)
                      )
        figure = go.Figure(data=data, layout=layout)
        div = opy.plot(figure, auto_open=False, output_type='div')

        context['graph'] = div

        context['data'] = ''


        return context



