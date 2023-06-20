# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
from django.views.generic import CreateView, ListView, View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, AccessMixin
from django.shortcuts import render, redirect
from django_tables2.views import SingleTableMixin, MultiTableMixin
from django.contrib.messages.views import SuccessMessageMixin
from django_tables2.export.views import ExportMixin
from django.contrib import messages
from django_filters.views import FilterView

from mogi.models import models_annotations, models_search, models_isa
from mogi.forms import forms_search
from mogi.tables import tables_search, tables_annotations
from mogi.filter import filter_search
from mogi.tasks import search_mz_task, search_mono_task, search_frag_task

import numpy as np
import collections
import seaborn as sns
import plotly.offline as opy
import plotly.graph_objs as go
import sqlite3

class SearchMzParamCreateView(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = models_search.SearchMzParam
    form_class = forms_search.SearchMzParamForm
    success_url = '/mogi/success'

    task_string = 'search mz'
    success_message = 'searching mz'
    redirect_string = 'data_and_results_summary'

    def handle_no_permission(self):
        messages.error(self.request, 'User has insufficient privileges to {}'.format(self.task_string))
        return redirect(self.redirect_string)

    def form_valid(self, form):
        form.instance.user = self.request.user
        smp = form.save()
        result = search_mz_task.delay(smp.id, self.request.user.id)
        self.request.session['result'] = result.id
        return render(self.request, 'gfiles/status.html', {'s': 0, 'progress': 0})



class SearchMonoParamCreateView(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = models_search.SearchMonoParam
    form_class = forms_search.SearchMonoParamForm
    success_url = '/mogi/success'

    task_string = 'search monoisotopic exact mass'
    success_message = 'searching monoisotopic exact mass'
    redirect_string = 'data_and_results_summary'

    def handle_no_permission(self):
        messages.error(self.request, 'User has insufficient privileges to {}'.format(self.task_string))
        return redirect(self.redirect_string)

    def form_valid(self, form):
        form.instance.user = self.request.user
        smp = form.save()
        result = search_mono_task.delay(smp.id, self.request.user.id)
        self.request.session['result'] = result.id
        return render(self.request, 'gfiles/status.html', {'s': 0, 'progress': 0})
    
    def get_initial(self):
        initial = super(SearchMonoParamCreateView, self).get_initial()
        initial['masses'] = """165.0789
132.05349
244.06953
"""
        initial['description'] = 'test'
        return initial

class SearchFragParamCreateView(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = models_search.SearchFragParam
    form_class = forms_search.SearchFragParamForm
    success_url = '/mogi/success'

    task_string = 'search fragmentation spectra'
    success_message = 'searching fragmentation spectra'
    redirect_string = 'data_and_results_summary'

    def handle_no_permission(self):
        messages.error(self.request, 'User has insufficient privileges to {}'.format(self.task_string))
        return redirect(self.redirect_string)

    def get_initial(self):
        initial = super(SearchFragParamCreateView, self).get_initial()
        initial['products'] = """67.0544,733.3
80.0494, 13947.8
81.0698, 1535.9
96.0441, 5689.4
106.028, 7309.0
123.0550, 90000.7
123.0804, 870.4
123.0913, 907.3
124.0391, 2227.9
"""
        initial['mz_precursor'] = 123.0553
        initial['description'] = 'test'
        initial['metabolite_reference_standard'] = False

        fst_q = models_search.FragSpectraType.objects.filter(type='LC-MS/MS averaged (inter)')
        if fst_q:
            initial['fragspectratype'] = fst_q[0]

        pol_q = models_isa.PolarityType.objects.filter(type='POSITIVE')
        if pol_q:
            initial['polarity'] = pol_q[0]


        return initial

    def form_valid(self, form):
        form.instance.user = self.request.user
        sp = form.save()
        # result = search_frag(sp.id)
        result = search_frag_task.delay(sp.id, self.request.user.id)
        self.request.session['result'] = result.id
        # self.request.session['result'] = result.id
        return render(self.request, 'gfiles/status.html', {'s': 0, 'progress': 0})



class SearchMonoParamListView(LoginRequiredMixin, SingleTableMixin, ListView):
    model = models_search.SearchMonoParam
    table_class = tables_search.SearchMonoParamTable
    template_name = 'mogi/searchmonoparam_list.html'
    task_string = 'view search results'
    success_message = 'view search results'
    redirect_string = 'data_and_results_summary'

    def handle_no_permission(self):
        messages.error(self.request, 'User has insufficient privileges to {}'.format(self.task_string))
        return redirect(self.redirect_string)

    def get_queryset(self):
        if self.request.user.is_superuser:
            return self.model.objects.all()
        elif self.request.user.is_authenticated:
            return self.model.objects.filter(user = self.request.user)
        
   


class SearchFragParamListView(LoginRequiredMixin, SingleTableMixin, ListView):
    model = models_search.SearchFragParam
    table_class = tables_search.SearchFragParamTable
    template_name = 'mogi/searchfragparam_list.html'
    task_string = 'view search results'
    success_message = 'view search results'
    redirect_string = 'data_and_results_summary'

    def handle_no_permission(self):
        messages.error(self.request, 'User has insufficient privileges to {}'.format(self.task_string))
        return redirect(self.redirect_string)

    def get_queryset(self):
        if self.request.user.is_superuser:
            return self.model.objects.all()
        elif self.request.user.is_authenticated:
            return self.model.objects.filter(user = self.request.user)


class SearchMonoResultListView(ExportMixin, LoginRequiredMixin, SingleTableMixin, ListView):
    model = models_search.SearchMonoResult
    table_class = tables_search.SearchMonoResultTable
    template_name = 'mogi/searchmonoresult_list.html'
    task_string = 'view search monoisotopic exact mass results'
    success_message = 'view search monoisotopic exact mass results'
    redirect_string = 'data_and_results_summary'
    export_formats = ['csv']
    export_name = 'search_monoisotopic_exact_mass_result'


    def handle_no_permission(self):
        messages.error(self.request, 'User has insufficient privileges to {}'.format(self.task_string))
        return redirect(self.redirect_string)

    def get_queryset(self):
        smr = models_search.SearchMonoResult.objects.filter(searchparam_id=self.kwargs.get('spid'))
        if self.request.user.is_superuser:
            return smr
        elif self.request.user.is_authenticated:
            return smr.filter(searchparam__user=self.request.user)




class SearchFragResultListView(ExportMixin, LoginRequiredMixin, SingleTableMixin, FilterView):
    model = models_search.SearchFragResult
    table_class = tables_search.SearchFragResultTable
    filterset_class = filter_search.SearchFragResultFilter
    template_name = 'mogi/searchfragresult_list.html'
    task_string = 'view search fragmentation results'
    success_message = 'view search fragmentation  results'
    redirect_string = 'data_and_results_summary'
    export_formats = ['csv']
    export_name = 'search_fragmentation_result'


    def handle_no_permission(self):
        messages.error(self.request, 'User has insufficient privileges to {}'.format(self.task_string))
        return redirect(self.redirect_string)

    def get_queryset(self):
        smr = models_search.SearchFragResult.objects.filter(searchparam_id=self.kwargs.get('spid'))
        if self.request.user.is_superuser:
            return smr
        elif self.request.user.is_authenticated:
            return smr.filter(searchparam__user=self.request.user)


class SearchFragResultAnnotationListView(LoginRequiredMixin, MultiTableMixin, TemplateView):
    model = models_annotations.CombinedAnnotation

    template_name = 'mogi/searchfragresultannotation_list.html'
    task_string = 'view search fragmentation annotations'
    success_message = 'view search fragmentation annotations'
    redirect_string = 'data_and_results_summary'
    #export_formats = ['csv']
    #export_name = 'search_fragmentation_annotation'

    def get_tables(self):


        data1 = get_combined_annotation_table(self.kwargs.get('sfid'))
        data2 = get_spectral_matching_table(self.kwargs.get('sfid'))
        data3 = get_sirius_table(self.kwargs.get('sfid'))
        data4 = get_metfrag_table(self.kwargs.get('sfid'))

        self.tables = [
            tables_annotations.CombinedAnnotationTable(data1),
            tables_annotations.SpectralMatchingTable(data2),
            tables_annotations.SiriusCSIFingerIDTable(data3),
            tables_annotations.MetFragTable(data4)
        ]
        return super().get_tables()

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(SearchFragResultAnnotationListView, self).get_context_data(**kwargs)
        context = sm_plot_search(self.kwargs.get('sfid'), context)

        return context


    def handle_no_permission(self):
        messages.error(self.request, 'User has insufficient privileges to {}'.format(self.task_string))
        return redirect(self.redirect_string)

    # def get_queryset(self):
    #     smr = models_search.SearchFragResultAnnotation.objects.filter(searchfragresult_id=self.kwargs.get('sfid'))
    #     if self.request.user.is_superuser:
    #         return smr
    #     elif self.request.user.is_authenticated:
    #         return smr.filter(searchparam__user=self.request.user)


def get_combined_annotation_table(searchfragresult_id):
    sfr = models_search.SearchFragResult.objects.get(id=searchfragresult_id)
    print(sfr.dataset.sqlite.path)
    conn = sqlite3.connect(sfr.dataset.sqlite.path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()


    if sfr.spectrum_type in ['inter', 'intra']:
        sql_stmt = """ 
                                       SELECT ROW_NUMBER() OVER() AS id, 
                                          {} AS dataset_id,
                                          ca.grpid, ca.sid, ROUND(cpg.mz,5) AS mz, ROUND(cpg.rt,3) AS rt, cpg.grp_name, 
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
                                       WHERE ca.grpid=={} AND ca.rank<=5 
                                       """.format(sfr.dataset.id, sfr.dataset_grpid)
    if sfr.spectrum_type == 'scan':
        sql_stmt = """
                      SELECT ROW_NUMBER() OVER() AS id,
                         {} AS dataset_id, ca.grpid, ca.sid, ROUND(cpg.mz,5) AS mz, ROUND(cpg.rt,3) AS rt, cpg.grp_name, 
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
                   LEFT JOIN c_peak_X_c_peak_group AS cpXcpg ON cpXcpg.grpid = cpg.grpid
                   LEFT JOIN c_peaks AS cp ON cp.cid = cpXcpg.cid
                   LEFT JOIN c_peak_X_s_peak_meta AS cpXspm ON cp.cid = cpXspm.cid
                   LEFT JOIN s_peak_meta AS spm ON spm.pid = cpXspm.pid

                   WHERE spm.pid={}  AND ca.rank<=5 
                   GROUP BY ca.inchikey
                   ORDER by ca.rank
                      """.format(sfr.dataset.id, sfr.dataset_pid)
        print(sql_stmt)

    if sfr.spectrum_type == 'msnpy':
        sql_stmt = """SELECT ROW_NUMBER() OVER() AS id,
                         {} AS dataset_id, ca.grpid, ca.sid, ROUND(spm1.precursor_mz,5) AS mz, spm.well, spm.well_rt AS rt,
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
                               FROM s_peak_meta AS spm1 
                               LEFT JOIN s_peak_meta_X_s_peaks AS sxs ON spm1.pid=sxs.pid
                               LEFT JOIN
                                   s_peaks_X_s_peaks AS spXsp ON spXsp.sid2 = sxs.sid
                               LEFT JOIN s_peaks AS sp ON sp.sid=spXsp.sid1
                               LEFT JOIN s_peak_meta AS spm ON spm.pid=sp.pid
                               LEFT JOIN combined_annotations AS ca ON spXsp.sid1=ca.sid
                               LEFT JOIN metab_compound as mc ON mc.inchikey=ca.inchikey 
                               WHERE spm1.pid=={}  AND ca.rank<=5
                               ORDER by ca.rank
                              """.format(sfr.dataset.id, sfr.dataset_pid)

    print(sql_stmt)
    r = c.execute(sql_stmt)
    return [row for row in r]




def get_spectral_matching_table(searchfragresult_id):
    sfr = models_search.SearchFragResult.objects.get(id=searchfragresult_id)
    print(sfr.dataset.sqlite.path)
    conn = sqlite3.connect(sfr.dataset.sqlite.path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

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
                 library_compound_name,
                 msnpy_convert_id
                    FROM sm_matches AS sm
                        WHERE qpid={}
                        ORDER BY -dpc
                        LIMIT 20
                               """.format(sfr.dataset.id, sfr.dataset_pid)
    sm = c.execute(sql_stmt)
    summary_spectral_match = [row for row in sm]
    return summary_spectral_match


def get_sirius_table(searchfragresult_id):
    sfr = models_search.SearchFragResult.objects.get(id=searchfragresult_id)
    print(sfr.dataset.sqlite.path)
    conn = sqlite3.connect(sfr.dataset.sqlite.path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    cn = """ROW_NUMBER() OVER() AS id, {} AS dataset_id, MZ AS mz,
                RT AS rt,
                grpid, 
                            file,
                            adduct,
                            rank,
                            formulaRank AS formula_rank,
                            Score AS score,
                            molecularFormula AS molecular_formula,
                            InChIkey2D AS inchikey2,
                            InChI AS inchi,
                            name,
                            smiles,
                            xlogp,
                            pubchemids,
                            links,
                            dbflags,
                            bounded_score,
                            msnpy_convert_id,
                            pid""".format(sfr.dataset.id)
    # Get best sirius annotation
    if sfr.spectrum_type in ['scan', 'msnpy']:
        # Don't have the anem recorded for DIMSn analysis
        sql_stmt = "SELECT {} FROM sirius_csifingerid_results WHERE pid=={} AND rank<=5".format(cn, sfr.dataset_pid)

    elif sfr.spectrum_type in ['inter', 'intra']:
        sql_stmt = "SELECT {} FROM sirius_csifingerid_results WHERE grpid=={}  AND rank<=5".format(cn, sfr.dataset_grpid)
    else:
        sql_stmt = ""
    sm = c.execute(sql_stmt)
    summary_spectral_match = [row for row in sm]
    return summary_spectral_match


def get_metfrag_table(searchfragresult_id):
    sfr = models_search.SearchFragResult.objects.get(id=searchfragresult_id)
    print(sfr.dataset.sqlite.path)
    conn = sqlite3.connect(sfr.dataset.sqlite.path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    colnames = """ROW_NUMBER() OVER() AS id, {} AS dataset_id, sample_name, 
                             MZ AS mz,
                             grpid,
                             RT AS rt,
                             adduct,
                             CompoundName AS compound_name,
                             ExplPeaks AS expl_peaks,
                             FormulasOfExplPeaks AS formulas_of_expl_peaks,
                             FragmenterScore AS fragmenter_score,
                             FragmenterScore_Values AS fragmenter_score_values,
                             Identifier AS identifier,
                             InChI AS inchi,
                             InChIKey AS inchikey,
                             InChIKey1 AS inchikey1,
                             InChIKey2 AS inchikey2,
                             InChIKey3 AS inchikey3,
                             MaximumTreeDepth AS maximum_tree_depth,
                             MolecularFormula AS molecular_formula,
                             MonoisotopicMass AS monoisotopic_mass,
                             NoExplPeaks AS no_expl_peaks,
                             NumberPeaksUsed AS number_peaks_used,
                             file,
                             OfflineMetFusionScore AS offline_met_fusion_score,
                             SMILES AS smiles,
                             Score AS score,
                             SuspectListScore AS suspect_list_score,                          
                             XlogP3 AS xlogp3,msnpy_convert_id,pid,well""".format(sfr.dataset.id)

    if sfr.spectrum_type in ['scan', 'msnpy']:
        sql_stmt = "SELECT {} FROM metfrag_results WHERE pid=={}".format(colnames, sfr.dataset_pid)
    elif sfr.spectrum_type in ['inter', 'intra']:
        sql_stmt = "SELECT {} FROM metfrag_results WHERE grpid=={}".format(colnames, sfr.dataset_grpid)
    else:
        sql_stmt = ""
    sm = c.execute(sql_stmt)
    summary_spectral_match = [row for row in sm]
    return summary_spectral_match


def sm_plot_search(searchfragresult_id, context):
    sfr = models_search.SearchFragResult.objects.get(id=searchfragresult_id)

    values = models_search.SearchFragSpectra.objects.filter(
        searchparam=sfr.searchparam
    ).values(
        'searchparam_id',
        'mz',
        'ra',
    )

    values4plot = collections.defaultdict(list)

    for d in values:
        spmid = d['searchparam_id']

        if not values4plot[spmid]:
            values4plot[spmid] = collections.defaultdict(list)

        values4plot[spmid]['mz'].append(d['mz'])
        values4plot[spmid]['ra'].append(d['ra'])
        values4plot[spmid]['searchparam_id'].append(d['searchparam_id'])
        values4plot[spmid]['spectrum_type'].append('query')

    np.random.seed(sum(map(ord, "palettes")))
    c = 0
    current_palette = sns.color_palette('colorblind', 2)
    colour = current_palette.as_hex()

    data = []

    # Query
    for k, v in values4plot.items():

        mzs = v['mz']
        intens = v['ra']
        spmids = v['spmid']
        stype = v['spectrum_type']


        for i in range(0, len(mzs)):
            if i == 0:
                showLegend = True
            else:
                showLegend = False

            name = 'QUERY'

            trace = go.Scatter(x=[mzs[i], mzs[i]],
                               y=[0, intens[i]],
                               mode='lines+markers',
                               name=name,
                               legendgroup=name,
                               showlegend=showLegend,
                               line=dict(color=(str(colour[0]))))

            data.append(trace)


    # library
    print(sfr.dataset.sqlite.path)
    conn = sqlite3.connect(sfr.dataset.sqlite.path)
    c = conn.cursor()
    sql_stmt = """SELECT mz,
       i / (
               SELECT max(i) 
                 FROM s_peaks AS sp
                WHERE sp.pid = {pid}
           ) *  100
        FROM s_peaks AS sp
        WHERE sp.pid = {pid}""".format(pid=sfr.dataset_pid)
    print(sql_stmt)
    r = c.execute(sql_stmt)

    showLegend=True
    for row in r:
        print(row)
        trace = go.Scatter(x=[row[0], row[0]],
                               y=[0, -row[1]],
                               mode='lines+markers',
                               name='LIBRARY',
                               legendgroup='LIBRARY',
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