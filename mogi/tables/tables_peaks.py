import django_tables2 as tables
from django_tables2.utils import A
from django_tables2_column_shifter.tables import ColumnShiftTable

from gfiles.utils.icons import EYE

from mogi.models import models_peaks
from .tables_general import TABLE_CLASS, NumberColumn2, NumberColumn4


class SPeakMetaTable(ColumnShiftTable):
    plot = tables.LinkColumn('speak_plot', verbose_name='View plot', text=EYE, args=[A('id')])

    precursor_mz = NumberColumn4()
    precursor_rt = NumberColumn2()
    precursor_i = NumberColumn2()


    class Meta:

        model = models_peaks.SPeakMeta
        # add class="paleblue" to <table> tag

        attrs = {"class": TABLE_CLASS}
        fields = ('run', 'spectrum_type', 'spectrum_detail', 'idi', 'precursor_mz', 'precursor_i','precursor_rt',
                  'scan_num', 'precursor_scan_num', 'precursor_nearest', 'ms_level')



class CombinedPeakTable(ColumnShiftTable):

    inputdata_id = tables.Column(accessor='metabinputdata.id', verbose_name='Input Dataset (id)')
    name = tables.Column(accessor='metabinputdata.name', verbose_name='Input Dataset')
    polarity = tables.Column(accessor='metabinputdata.polarity', verbose_name='Polarity')
    assay_names = tables.Column(accessor='metabinputdata.assay_names', verbose_name='Assay')
    study_names = tables.Column(accessor='metabinputdata.study_names', verbose_name='Study')
    investigation_names = tables.Column(accessor='metabinputdata.investigation_names', verbose_name='Investigation')

    top_score = tables.Column(accessor='combinedannotationconcat.top_score', verbose_name='Top score')
    concat_score = tables.Column(accessor='combinedannotationconcat.concat_score', verbose_name='Scores')
    concat_inchikeys = tables.Column(accessor='combinedannotationconcat.concat_inchikey', verbose_name='Inchikeys')
    concat_adduct = tables.Column(accessor='combinedannotationconcat.concat_adduct', verbose_name='Adducts')
    concat_name = tables.Column(accessor='combinedannotationconcat.concat_name', verbose_name='Names')

    mz = NumberColumn4()
    rt = NumberColumn2()
    rtmin = NumberColumn2()
    rtmax = NumberColumn2()

    intensity = NumberColumn2()

    eics = tables.LinkColumn('eics', verbose_name='EICs', text=EYE, args=[A('cpeakgroup__id')])

    frag4combinedpeak = tables.LinkColumn('frag4combinedpeak', verbose_name='Fragmentation',
                                            text=EYE, args=[A('id')])

    canns = tables.LinkColumn('canns', verbose_name='Annotations',
                                            text=EYE, args=[A('id')])

    def get_column_default_show(self):
        self.column_default_show = ['id', 'idi', 'investigation', 'study', 'assay', 'ms_type',
                                    'mz', 'intensity', 'rt', 'rtmin', 'rtmax', 'top_score',
                                    'concat_name', 'eics', 'frag4combinedpeak', 'canns']
        return super(CombinedPeakTable, self).get_column_default_show()


    class Meta:
        model = models_peaks.CombinedPeak
        attrs = {"class": TABLE_CLASS}
        fields = ('id', 'cpeakgroup', 'speak', 'mz', 'intensity', 'rt', 'rtmin', 'rtmax', 'well',
                  'ms_type', 'fraction_match', 'frag_match', 'camera_adducts', 'camera_isotopes')

        sequence = ('id', 'inputdata_id', 'cpeakgroup', 'speak', 'polarity', 'investigation_names', 'study_names',
                    'assay_names', 'mz', 'intensity', 'rt', 'rtmin', 'rtmax', 'well', 'ms_type',
                    'fraction_match', 'frag_match', 'camera_adducts', 'camera_isotopes')



class EicTable(ColumnShiftTable):

    class Meta:

        model = models_peaks.Eic
        fields = ('scan', 'idi', 'intensity', 'cpeak_id')
        # add class="paleblue" to <table> tag

        attrs = {"class": TABLE_CLASS}


class SPeakTable(ColumnShiftTable):

    class Meta:

        model = models_peaks.SPeak

        # add class="paleblue" to <table> tag

        attrs = {"class": TABLE_CLASS}


# DEPRECATED
# class CPeakGroupTable(ColumnShiftTable):
#     # dma_c = tables.TemplateColumn("{{ value|safe }}")
#     # dma_name_c = tables.TemplateColumn("{{ value|safe }}")
#     # workflow_stage_code = tables.TemplateColumn("{{ value|safe }}")
#     # all_annotations = tables.TemplateColumn("{{ value|safe }}")
#     # # view_data = ButtonColumn()
#
#     inputdata_id = tables.Column(accessor='cpeakgroupmeta.metabinputdata.id', verbose_name='Input Dataset (id)')
#     inputdata = tables.Column(accessor='cpeakgroupmeta.metabinputdata.name', verbose_name='Input Dataset')
#     polarity = tables.Column(accessor='cpeakgroupmeta.polarity', verbose_name='Polarity')
#
#
#     mzmed = NumberColumn4()
#     mzmax = NumberColumn4()
#     mzmin = NumberColumn4()
#     rtmed = NumberColumn2()
#     rtmin = NumberColumn2()
#     rtmax = NumberColumn2()
#     best_score = NumberColumn2()
#
#     eics = tables.LinkColumn('eics', verbose_name='EICs',
#                                             text=EYE, args=[A('id')])
#
#     frag4feature = tables.LinkColumn('frag4feature', verbose_name='Fragmentation',
#                                             text=EYE, args=[A('id')])
#
#
#     filename = tables.Column(accessor='filename', verbose_name='Input Filename', orderable=True, attrs={'test':'test'})
#     investigation = tables.Column(accessor='historydatamogi.investigation.name', verbose_name='Investigation')
#     study = tables.Column(accessor='study_names', verbose_name='Study')
#     assay = tables.Column(accessor='assay_names')
#     c_peak_group_table = tables.LinkColumn('cpeakgroup_summary', verbose_name='View grouped peaklist', text=EYE, args=[A('id')])
#
#     def get_column_default_show(self):
#         self.column_default_show = ['id', 'idi', 'mzmed', 'rtmed', 'isotopes', 'adducts', 'best_annotation',
#                                     'best_score', 'eics', 'frag4feature', 'canns']
#         return super(CPeakGroupTable, self).get_column_default_show()
#
#     class Meta:
#         model = models_peaks.CPeakGroupMeta
#         attrs = {"class": TABLE_CLASS}
#         fields = ('id', 'date', 'metabinputdata', 'filename', 'investigation', 'study', 'assay', 'polarity', 'c_peak_group_table')
#
#         template = 'django_tables2/bootstrap.html'
#
#
#
#
# class CPeakGroupMetaTable(ColumnShiftTable):
#     c_peak_group_table = tables.LinkColumn('cpeakgroup_summary', verbose_name=EYE,
#                                             text=EYE, args=[A('id')])
#
#
#     class Meta:
#
#         model = models_peaks.CPeakGroupMeta
#         # add class="paleblue" to <table> tag
#
#         attrs = {"class": TABLE_CLASS}