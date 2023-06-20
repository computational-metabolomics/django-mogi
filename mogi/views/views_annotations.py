# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, AccessMixin
from django.shortcuts import render, redirect
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.http import HttpResponseRedirect
from django_tables2.export.views import ExportMixin
from django_tables2.views import SingleTableMixin, MultiTableMixin
from django_filters.views import FilterView
from django.conf import settings

from mogi.models import models_annotations, models_datasets
from mogi.tables import tables_annotations
from mogi.filter import filter_annotations
from mogi.utils.sql_utils import filterset_to_sql_stmt
import numpy as np
import collections
import seaborn as sns
import plotly.offline as opy
import plotly.graph_objs as go
import sqlite3


class CombinedAnnotationListView(ExportMixin, LoginRequiredMixin, SingleTableMixin, FilterView):
    model = models_annotations.CombinedAnnotation
    table_class = tables_annotations.CombinedAnnotationTable
    filterset_class = filter_annotations.CombinedAnnotationFilter
    template_name = 'mogi/combinedannotation_list.html'
    task_string = 'view combined annotation results'
    success_message = 'view combined annotation results'
    redirect_string = 'data_and_results_summary'
    export_formats = ['csv']
    export_name = 'combined_annotations'

    def handle_no_permission(self):
        messages.error(self.request, 'User has insufficient privileges to {}'.format(self.task_string))
        return redirect(self.redirect_string)

    # def get_queryset(self):
        # smr = models_annotations.CombinedAnnotation.objects.filter(id=self.kwargs.get('spid'))
        # smr = get_combined_annotation_table(self.kwargs.get('did'))
        # return smr

    def get_table_data(self):

        sql_filter_stmt = filterset_to_sql_stmt(self.filterset)
        self.table_data = get_combined_annotation_table(self.kwargs.get('did'), sql_filter_stmt)
        return super().get_table_data()

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(CombinedAnnotationListView, self).get_context_data(**kwargs)

        return context


def get_combined_annotation_table(dataset_id, sql_filter_stmt):
    dataset = models_datasets.Dataset.objects.get(id=dataset_id)
    print(dataset.sqlite.path)
    conn = sqlite3.connect(dataset.sqlite.path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    sql_stmt = """ 
                                       SELECT 
                                          ROW_NUMBER() OVER() AS id, 
                                          'lcms' AS ms_type,
                                          {} AS dataset_id,
                                          ca.grpid, 
                                          NULL AS sid,
                                          ROUND(cpg.mz,5) AS mz,
                                          ROUND(cpg.rt,2) AS rt,
                                          NULL AS well,
                                          cpg.grp_name, 
                                          ca.inchikey, mc.inchikey1, mc.name AS compound_name,  mc.pubchem_cids, 
                                          ROUND(ca.sirius_score,2) AS sirius_score,
                                          ROUND(ca.sirius_wscore,2) AS sirius_wscore,
                                          ROUND(ca.metfrag_score,2) AS metfrag_score,
                                          ROUND(ca.metfrag_wscore,2) AS metfrag_wscore,
                                          ca.sm_lpid,
                                          ROUND(ca.sm_score,2) AS sm_score,
                                          ROUND(ca.sm_wscore,2) AS sm_wscore,
                                          ROUND(ca.ms1_lookup_score,2) AS ms1_lookup_score,
                                          ROUND(ca.ms1_lookup_wscore,2) AS ms1_lookup_wscore,
                                          ROUND(ca.biosim_max_score,2) AS biosim_max_score,
                                          ROUND(ca.biosim_wscore,2) AS biosim_wscore,
                                          ROUND(ca.wscore,2) AS wscore, 
                                          ca.adduct_overall, ca.rank    
                                       FROM combined_annotations AS ca 
                                       LEFT JOIN metab_compound as mc ON mc.inchikey=ca.inchikey 
                                       LEFT JOIN c_peak_groups as cpg ON cpg.grpid=ca.grpid
                                       WHERE ca.rank<=5 {} AND ca.grpid NOT NULL
                                       """.format(dataset_id, sql_filter_stmt)

    print(sql_stmt)
    r = c.execute(sql_stmt)
    summary = [row for row in r]

    if dataset.fractionation:

        sql_stmt = """ 
                                       SELECT 
                                          ROW_NUMBER() OVER() AS id, 
                                          'dims' AS ms_type,
                                          {} AS dataset_id,
                                          NULL AS grpid, 
                                          ca.sid AS sid,
                                          ROUND(sp.mz,5) AS mz,
                                          ROUND(spm.well_rt,2) AS rt,
                                          spm.well,
                                          NULL AS grp_name, 
                                          ca.inchikey, mc.inchikey1, mc.name AS compound_name,  mc.pubchem_cids, 
                                          ROUND(ca.sirius_score,2) AS sirius_score,
                                          ROUND(ca.sirius_wscore,2) AS sirius_wscore,
                                          ROUND(ca.metfrag_score,2) AS metfrag_score,
                                          ROUND(ca.metfrag_wscore,2) AS metfrag_wscore,
                                          ca.sm_lpid,
                                          ROUND(ca.sm_score,2) AS sm_score,
                                          ROUND(ca.sm_wscore,2) AS sm_wscore,
                                          ROUND(ca.ms1_lookup_score,2) AS ms1_lookup_score,
                                          ROUND(ca.ms1_lookup_wscore,2) AS ms1_lookup_wscore,
                                          ROUND(ca.biosim_max_score,2) AS biosim_max_score,
                                          ROUND(ca.biosim_wscore,2) AS biosim_wscore,
                                          ROUND(ca.wscore,2) AS wscore, 
                                          ca.adduct_overall, ca.rank    
                                       FROM combined_annotations AS ca 
                                       LEFT JOIN metab_compound as mc ON mc.inchikey=ca.inchikey 
                                       LEFT JOIN s_peaks as sp ON sp.sid=ca.sid
                                       LEFT JOIN s_peak_meta as spm ON spm.pid=sp.pid
                                       WHERE ca.rank<=5 {} AND ca.sid NOT NULL
                                       """.format(dataset_id, sql_filter_stmt)

        r = c.execute(sql_stmt)
        summary.extend([row for row in r])

    return summary


class SpectralMatchingListView(ExportMixin, LoginRequiredMixin, SingleTableMixin, FilterView):
    model = models_annotations.SpectralMatching
    table_class = tables_annotations.SpectralMatchingTable
    filterset_class = filter_annotations.SpectralMatchingFilter
    template_name = 'mogi/spectralmatching_list.html'
    task_string = 'view spectral matching results'
    success_message = 'view spectral matching results'
    redirect_string = 'data_and_results_summary'
    export_formats = ['csv']
    export_name = 'spectral_matching'

    def handle_no_permission(self):
        messages.error(self.request, 'User has insufficient privileges to {}'.format(self.task_string))
        return redirect(self.redirect_string)

    # def get_queryset(self):
        # smr = models_annotations.CombinedAnnotation.objects.filter(id=self.kwargs.get('spid'))
        # smr = get_combined_annotation_table(self.kwargs.get('did'))
        # return smr

    def get_table_data(self):
        sql_filter_stmt = filterset_to_sql_stmt(self.filterset)
        self.table_data = get_spectral_matching_table(self.kwargs.get('did'),
                                                      self.kwargs.get('grpid'),
                                                      self.kwargs.get('sid'),
                                                      self.kwargs.get('inchikey'),
                                                      sql_filter_stmt)
        return super().get_table_data()

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(SpectralMatchingListView, self).get_context_data(**kwargs)

        return context


def get_spectral_matching_table(dataset_id, grpid, sid, inchikey, sql_filter_stmt):
    dataset = models_datasets.Dataset.objects.get(id=dataset_id)
    print(dataset.sqlite.path)
    conn = sqlite3.connect(dataset.sqlite.path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    if grpid != 'None':
        sql_stmt = """SELECT ROW_NUMBER() OVER() AS id, {} AS dataset_id, mid, 
                 CAST(lpid AS INT) AS lpid,
                 CAST(qpid AS INT) AS qpid, 
                 ROUND(dpc,3) AS dpc,
                 ROUND(rdpc,3) AS rdpc,
                 ROUND(cdpc,3) AS cdpc,
                 mcount,
                 allcount,
                 ROUND(mpercent,3) AS mpercent,
                 ROUND(library_rt,3) AS library_rt,
                 ROUND(query_rt,3) AS query_rt,
                 ROUND(rtdiff,3) AS rtdiff,
                 ROUND(library_precursor_mz,6) AS library_precursor_mz,
                 ROUND(query_precursor_mz,6) AS query_precursor_mz,
                 library_accession,
                 library_precursor_type,
                 library_entry_name,
                 ca.inchikey,
                 library_source_name,
                 library_compound_name
                   FROM sm_matches AS sm 
                   LEFT JOIN combined_annotations AS ca  ON ca.sm_mid=sm.mid
                LEFT JOIN
                  c_peak_groups AS cpg ON cpg.grpid == ca.grpid
                WHERE ca.inchikey == "{}" AND ca.grpid == {} {}
                                       """.format(dataset_id, inchikey, grpid, sql_filter_stmt)
        print(sql_stmt)

    elif sid != 'None':
        sql_stmt = """SELECT spXsp.sid2
        FROM s_peaks AS sp 
          LEFT JOIN
            s_peaks_X_s_peaks AS spXsp ON spXsp.sid2 = sp.sid       
        WHERE spXsp.sid1={};
                        """.format(sid)
        print(sql_stmt)
        r0 = c.execute(sql_stmt)
        sid2s = [str(row['sid2']) for row in r0]
        print(sid2s)


        sql_stmt = """SELECT ROW_NUMBER() OVER() AS id, {} AS dataset_id, mid, 
                 CAST(lpid AS INT) AS lpid,
                 CAST(qpid AS INT) AS qpid, 
                 ROUND(dpc,3) AS dpc,
                 ROUND(rdpc,3) AS rdpc,
                 ROUND(cdpc,3) AS cdpc,
                 mcount,
                 allcount,
                 ROUND(mpercent,3) AS mpercent,
                 ROUND(library_rt,3) AS library_rt,
                 ROUND(query_rt,3) AS query_rt,
                 ROUND(rtdiff,3) AS rtdiff,
                 ROUND(library_precursor_mz,6) AS library_precursor_mz,
                 ROUND(query_precursor_mz,6) AS query_precursor_mz,
                 library_accession,
                 library_precursor_type,
                 library_entry_name,
                 inchikey,
                 library_source_name,
                 library_compound_name
                   FROM sm_matches AS m
                    LEFT JOIN
                        s_peak_meta AS spm ON spm.pid = m.qpid
                    LEFT JOIN
                        s_peak_meta_X_s_peaks AS sxs ON sxs.pid = spm.pid
                    LEFT JOIN
                        s_peaks AS sp ON sp.sid = sxs.sid
                    LEFT JOIN
                        s_peaks_X_s_peaks AS spXsp ON spXsp.sid2 = sp.sid
                    WHERE m.inchikey='{}' AND sp.sid IN ('{}') {}
                                       """.format(dataset_id, inchikey, "','".join(sid2s), sql_filter_stmt)
        print(sql_stmt)
    else:
        return []

    r = c.execute(sql_stmt)

    return [row for row in r]


class SMPlotView(LoginRequiredMixin, SuccessMessageMixin, TemplateView):
    '''
    '''

    template_name = 'mogi/smplot.html'

    def get(self, *args, **kwargs):
        if self.kwargs.get('pid') == 'None' or self.kwargs.get('did') == 'None':
            messages.info(self.request, 'Spectral matching plot not available for chosen feature')
            return HttpResponseRedirect(self.request.META.get('HTTP_REFERER', '/'))
        else:
            return super(SMPlotView, self).get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(SMPlotView, self).get_context_data(**kwargs)

        if self.kwargs.get('lpid') == 'None' or self.kwargs.get('did') == 'None' or self.kwargs.get('qpid') == 'None':
            return context

        context = sm_plot(self.kwargs.get('did'),
                          self.kwargs.get('qpid'),
                          self.kwargs.get('lpid'),
                          context)

        return context


def sm_plot(did, qpid, lpid, context):

    dataset = models_datasets.Dataset.objects.get(id=did)

    #############################
    # QUERY
    #############################
    print(dataset.sqlite.path)
    conn = sqlite3.connect(dataset.sqlite.path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    sql_stmt = """SELECT sp.pid, mz,
       i / (
               SELECT max(i) 
                 FROM s_peaks AS sp
                WHERE sp.pid = {pid}
           ) *  100 AS ra
        FROM s_peaks AS sp
        WHERE sp.pid = {pid}""".format(pid=qpid)
    print(sql_stmt)
    query_spectra = c.execute(sql_stmt)

    np.random.seed(sum(map(ord, "palettes")))

    data = []
    current_palette = sns.color_palette('colorblind', 2)
    colour = current_palette.as_hex()
    showLegend = True
    for row in query_spectra:
        print('QUERY', row)
        trace = go.Scatter(x=[row['mz'], row['mz']],
                               y=[0, row['ra']],
                               mode='lines+markers',
                               name='QUERY',
                               legendgroup='QUERY',
                               showlegend=showLegend,
                               line=dict(color=(str(colour[0]))))

        data.append(trace)
        if showLegend:
            showLegend = False


    #############################
    # LIBRARY
    #############################
    sql_stmt = """SELECT sp.library_spectra_meta_id AS pid, spm.accession, spm.name, mz, spo.name AS source,
       i / (
               SELECT max(i) 
                 FROM l_s_peaks AS sp
                WHERE sp.library_spectra_meta_id = {pid}
           ) *  100 AS ra
        FROM l_s_peaks AS sp LEFT JOIN l_s_peak_meta AS spm ON sp.library_spectra_meta_id=spm.id
        LEFT JOIN l_source AS spo ON spm.library_spectra_source_id=spo.id
        WHERE sp.library_spectra_meta_id = {pid}""".format(pid=lpid)
    print(sql_stmt)
    r = c.execute(sql_stmt)
    library_spectra = [row for row in r]

    if len(library_spectra)==0:
        # i.e. missing from the inidividual sqlite then we check the default library
        conn_lib = sqlite3.connect(settings.EXTERNAL_LIBRARY_SPECTRA_PTH)
        print(settings.EXTERNAL_LIBRARY_SPECTRA_PTH)
        conn_lib.row_factory = sqlite3.Row
        c_l = conn_lib.cursor()

        sql_stmt = """SELECT sp.library_spectra_meta_id AS pid, spm.accession, spm.name, mz, spo.name AS source,
           i / (
                   SELECT max(i) 
                     FROM library_spectra AS sp
                    WHERE sp.library_spectra_meta_id = {pid}
               ) *  100 AS ra
            FROM library_spectra AS sp LEFT JOIN library_spectra_meta AS spm ON sp.library_spectra_meta_id=spm.id
            LEFT JOIN library_spectra_source AS spo ON spm.library_spectra_source_id=spo.id
            WHERE sp.library_spectra_meta_id = {pid}""".format(pid=lpid)
        print(sql_stmt)
        library_spectra = c_l.execute(sql_stmt)

    # library

    showLegend=True
    for row in library_spectra:
        print(row)
        trace = go.Scatter(x=[row['mz'], row['mz']],
                               y=[0, -row['ra']],
                               mode='lines+markers',
                               name='LIBRARY | {} | {} | {}'.format(row['accession'], row['name'], row['source']),
                               legendgroup='LIBRARY',
                               showlegend=showLegend,
                               line=dict(color=(str(colour[1]))))

        data.append(trace)
        if showLegend:
            showLegend = False

    layout = dict(title='Spectral match',
                  xaxis=dict(title='m/z'),
                  yaxis=dict(title='Relative abundance'),
                  legend=dict(
                      orientation="v",
                      yanchor="bottom",
                      y=-1.1,
                      xanchor="left",
                      x=0)
                  )

    # layout = go.Layout(title="Meine Daten", xaxis={'title': 'x1'}, yaxis={'title': 'x2'})
    figure = go.Figure(data=data, layout=layout)
    div = opy.plot(figure, auto_open=False, output_type='div')

    context['graph'] = div

    context['data'] = ''


    return context


class MetFragListView(ExportMixin, LoginRequiredMixin, SingleTableMixin, FilterView):
    model = models_annotations.MetFrag
    table_class = tables_annotations.MetFragTable
    filterset_class = filter_annotations.MetFragFilter
    template_name = 'mogi/metfrag_list.html'
    task_string = 'view MetFrag results'
    success_message = 'view MetFrag results'
    redirect_string = 'data_and_results_summary'
    export_formats = ['csv']
    export_name = 'metfrag'

    def handle_no_permission(self):
        messages.error(self.request, 'User has insufficient privileges to {}'.format(self.task_string))
        return redirect(self.redirect_string)

    # def get_queryset(self):
        # smr = models_annotations.CombinedAnnotation.objects.filter(id=self.kwargs.get('spid'))
        # smr = get_combined_annotation_table(self.kwargs.get('did'))
        # return smr

    def get_table_data(self):
        sql_filter_stmt = filterset_to_sql_stmt(self.filterset)
        self.table_data = get_metfrag_table(self.kwargs.get('did'),
                                                      self.kwargs.get('grpid'),
                                                      self.kwargs.get('sid'),
                                                      self.kwargs.get('inchikey'),
                                                      sql_filter_stmt)
        return super().get_table_data()

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(MetFragListView, self).get_context_data(**kwargs)

        return context

def get_metfrag_table(did, grpid, sid, inchikey, sql_filter_stmt):
    dataset = models_datasets.Dataset.objects.get(id=did)
    conn = sqlite3.connect(dataset.sqlite.path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    colnames = """ROW_NUMBER() OVER() AS id, {} AS dataset_id,
                             m.sample_name, 
                             m.MZ AS mz,
                             m.grpid,
                             m.RT AS rt,
                             m.adduct,
                             m.CompoundName AS compound_name,
                             m.ExplPeaks AS expl_peaks,
                             m.FormulasOfExplPeaks AS formulas_of_expl_peaks,
                             m.FragmenterScore AS fragmenter_score,
                             m.FragmenterScore_Values AS fragmenter_score_values,
                             m.Identifier AS identifier,
                             m.InChI AS inchi,
                             m.InChIKey AS inchikey,
                             m.InChIKey1 AS inchikey1,
                             m.InChIKey2 AS inchikey2,
                             m.InChIKey3 AS inchikey3,
                             m.MaximumTreeDepth AS maximum_tree_depth,
                             m.MolecularFormula AS molecular_formula,
                             m.MonoisotopicMass AS monoisotopic_mass,
                             m.NoExplPeaks AS no_expl_peaks,
                             m.NumberPeaksUsed AS number_peaks_used,
                             m.file,
                             m.OfflineMetFusionScore AS offline_met_fusion_score,
                             m.SMILES AS smiles,
                             m.Score AS score,
                             m.SuspectListScore AS suspect_list_score,                          
                             m.XlogP3 AS xlogp3""".format(did)

    if grpid != 'None':
        sql_stmt = "SELECT {} FROM metfrag_results AS m WHERE m.inchikey='{}' AND grpid=={} {}"\
                   .format(colnames, inchikey, grpid, sql_filter_stmt)
    elif sid != 'None':
        colnames = colnames + ",m.pid,m.well"
        sql_stmt = """SELECT spXsp.sid2
              FROM s_peaks AS sp 
                LEFT JOIN
                  s_peaks_X_s_peaks AS spXsp ON spXsp.sid2 = sp.sid       
              WHERE spXsp.sid1={};
                              """.format(sid)
        print(sql_stmt)
        r0 = c.execute(sql_stmt)
        sid2s = [str(row['sid2']) for row in r0]
        print(sid2s)

        sql_stmt = """SELECT {}
                         FROM metfrag_results AS m
                          LEFT JOIN
                            s_peak_meta AS spm ON spm.pid = m.pid
                          LEFT JOIN
                            s_peak_meta_X_s_peaks AS sxs ON sxs.pid = spm.pid
                          LEFT JOIN
                            s_peaks AS sp ON sp.sid = sxs.sid
                          LEFT JOIN
                            s_peaks_X_s_peaks AS spXsp ON spXsp.sid2 = sp.sid
                          WHERE m.inchikey='{}' AND sp.sid IN ({}) {}
                           """.format(colnames, inchikey, "','".join(sid2s), sql_filter_stmt)
        print(sql_stmt)

    else:
        sql_stmt = ""
    mf = c.execute(sql_stmt)
    summary_mf = [row for row in mf]
    return summary_mf



class SiriusCSIFingerIDListView(ExportMixin, LoginRequiredMixin, SingleTableMixin, FilterView):
    model = models_annotations.SiriusCSIFingerID
    table_class = tables_annotations.SiriusCSIFingerIDTable
    filterset_class = filter_annotations.SiriusCSIFingerIDFilter
    template_name = 'mogi/sirius_list.html'
    task_string = 'view SIRIUS CSI:FingerID results'
    success_message = 'view SIRIUS CSI:FingerID results'
    redirect_string = 'data_and_results_summary'
    export_formats = ['csv']
    export_name = 'sirius_csifingerid'

    def handle_no_permission(self):
        messages.error(self.request, 'User has insufficient privileges to {}'.format(self.task_string))
        return redirect(self.redirect_string)

    # def get_queryset(self):
        # smr = models_annotations.CombinedAnnotation.objects.filter(id=self.kwargs.get('spid'))
        # smr = get_combined_annotation_table(self.kwargs.get('did'))
        # return smr

    def get_table_data(self):
        sql_filter_stmt = filterset_to_sql_stmt(self.filterset)
        self.table_data = get_sirius_csifingerid_table(self.kwargs.get('did'),
                                                      self.kwargs.get('grpid'),
                                                      self.kwargs.get('sid'),
                                                      self.kwargs.get('inchikey'),
                                                      sql_filter_stmt)
        return super().get_table_data()

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(SiriusCSIFingerIDListView, self).get_context_data(**kwargs)

        return context

def get_sirius_csifingerid_table(did, grpid, sid, inchikey, sql_filter_stmt):
    dataset = models_datasets.Dataset.objects.get(id=did)
    conn = sqlite3.connect(dataset.sqlite.path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    inchikey1 = inchikey.split('-')[0]

    colnames = """ROW_NUMBER() OVER() AS id, {} AS dataset_id, 
                  c.MZ AS mz,
                  c.RT AS rt,
                  c.grpid, 
                  c.file,
                  c.adduct,
                  c.rank,
                  c.formulaRank AS formula_rank,
                  c.Score AS score,
                  c.molecularFormula AS molecular_formula,
                  c.InChIkey2D AS inchikey2,
                  c.InChI AS inchi,
                  c.name,
                  c.smiles,
                  c.xlogp,
                  c.pubchemids,
                  c.links,
                  c.dbflags,
                  c.bounded_score""".format(did)

    if grpid != 'None':
        sql_stmt = "SELECT {} FROM sirius_csifingerid_results AS c WHERE  c.inchikey2D='{}' AND c.grpid=={} AND c.rank<=5 {}"\
            .format(colnames, inchikey1, grpid, sql_filter_stmt)
    elif sid != 'None':
        colnames = colnames + ",c.pid"

        sql_stmt = """SELECT spXsp.sid2
              FROM s_peaks AS sp 
                LEFT JOIN
                  s_peaks_X_s_peaks AS spXsp ON spXsp.sid2 = sp.sid       
              WHERE spXsp.sid1={};
                              """.format(sid)
        print(sql_stmt)
        r0 = c.execute(sql_stmt)
        sid2s = [str(row['sid2']) for row in r0]
        print(sid2s)

        sql_stmt = """SELECT {} 
                          FROM sirius_csifingerid_results AS c 
                        LEFT JOIN s_peak_meta AS spm ON spm.pid=c.pid
                        LEFT JOIN s_peak_meta_X_s_peaks AS sxs ON sxs.pid=spm.pid  
                        LEFT JOIN s_peaks AS sp ON sp.sid=sxs.sid
                        LEFT JOIN s_peaks_X_s_peaks AS spXsp ON spXsp.sid2=sp.sid
                        WHERE c.inchikey2D='{}' AND sp.sid IN ({})  AND c.rank<=5 {}
                           """.format(colnames, inchikey1, "','".join(sid2s), sql_filter_stmt)
        print(sql_stmt)

    else:
        sql_stmt = ""
    mf = c.execute(sql_stmt)
    summary_mf = [row for row in mf]
    return summary_mf
