from misa.tables import InvestigationTable
import django_tables2 as tables
from django_tables2.utils import A
from misa.models import Investigation
from galaxy.models import Workflow, History
from galaxy.tables import HistoryTable, HistoryDataTable
from mbrowse.tables import CAnnotationTable, CPeakGroupMetaTable, NumberColumn2, NumberColumn4
from mogi.models import CPeakGroupMetaMOGI, CAnnotationMOGI, IncomingGalaxyData
from gfiles.utils.icons import EYE, DOWN, PLAY, SAVE
from mbrowse.models import CAnnotation
from django_tables2_column_shifter.tables import ColumnShiftTable
from django.utils.text import slugify

TABLE_CLASS = "mogi table-bordered table-striped table-condensed table-hover"


class InvestigationTableUpload(ColumnShiftTable):
    details = tables.LinkColumn('idetail', text=EYE, args=[A('id')])

    check = tables.CheckBoxColumn(accessor="id",
                                               attrs={
                                                   "th__input": {"onclick": "toggle(this)"},
                                                   "td__input": {"onclick": "addfile(this)"}},
                                               )

    class Meta:
        model = Investigation

        attrs = {"class": TABLE_CLASS}
        fields = ('id','name','description', 'details')




class WorkflowTableISA(ColumnShiftTable):
    run = tables.LinkColumn('isa_workflow_run', text=PLAY, args=[A('id')])

    def get_column_default_show(self):
        self.column_default_show = ['id', 'name', 'galaxyinstancetracking', 'accessible', 'run']
        return super(WorkflowTableISA, self).get_column_default_show()

    class Meta:

        model = Workflow
        attrs = {"class": TABLE_CLASS}



class HistoryMogiTable(HistoryTable):
    history_mogi_data = tables.LinkColumn('history_mogi_data', text=EYE, args=[A('id')])

    def get_column_default_show(self):
        self.column_default_show = ['galaxyinstancetracking', 'name', 'update_time', 'running', 'estimated_progress', 'history_mogi_data', 'check']
        return super(HistoryTable, self).get_column_default_show()

    class Meta:
        model = History
        sequence = ( 'id', 'galaxyinstancetracking', 'name', 'update_time', 'empty', 'failed_metadata', 'new', 'ok', 'paused', 'error',
                     'queued', 'setting_metadata', 'upload', 'running', 'estimated_progress', 'galaxy_id', 'history_data_bioblend_list',
                     'history_mogi_data', 'check')
        attrs = {"class": TABLE_CLASS}
        # running_tasks_details = tables.Column()
        order_by = ('-update_time',)






class HistoryMogiDataTable(HistoryDataTable):
    mogi_create = tables.LinkColumn('history_mogi_data_save', verbose_name='Save metabolomics data',
                                            text=SAVE, args=[A('history_internal_id'), A('id')])



    def get_column_default_show(self):
        self.column_default_show = ['galaxy_instance', 'name', 'data_type', 'create_time', 'download_url', 'mogi_create']
        return super(HistoryDataTable, self).get_column_default_show()

    class Meta:
        attrs = {"class": TABLE_CLASS}

#
class CPeakGroupMetaMogiTable(ColumnShiftTable):



    filename = tables.Column(accessor='filename', verbose_name='Input Filename', orderable=True, attrs={'test':'test'})
    investigation = tables.Column(accessor='historydatamogi.investigation.name', verbose_name='Investigation')
    study = tables.Column(accessor='study_names', verbose_name='Study')
    assay = tables.Column(accessor='assay_names')
    c_peak_group_table = tables.LinkColumn('cpeakgroup_summary', verbose_name='View grouped peaklist', text=EYE, args=[A('id')])

    class Meta:
        model = CPeakGroupMetaMOGI
        attrs = {"class": TABLE_CLASS}
        fields = ('id', 'date', 'metabinputdata', 'filename', 'investigation', 'study', 'assay', 'polarity', 'c_peak_group_table')

        template = 'django_tables2/bootstrap.html'


# class CPeakGroupMetaMogiTable(ColumnShiftTable):
#     # galaxy_history = tables.Column(accessor='historydatamogi', verbose_name='Galaxy history details')
#
#     # galaxy_history = tables.Column(empty_values=())
#
#     # investigation = tables.Column(accessor='historydatamogi.investigation',
#     #                                verbose_name='Investigation')
#
#
#     class Meta:
#         model = ISAGalaxyTrack
#         attrs = {'class': 'paleblue'}
#         template = 'django_tables2/bootstrap.html'







class CAnnotationMogiTable(ColumnShiftTable):
    # galaxy_history = tables.Column(accessor='cpeakgroup.cpeakgroupmeta.metabinputdata.historymogi.name', verbose_name='Galaxy history details')
    #
    inputdata = tables.Column(accessor='cannotation.cpeakgroup.cpeakgroupmeta.metabinputdata.id',
                              verbose_name='Input Dataset (id)')

    inputdata_name = tables.Column(accessor='cannotation.cpeakgroup.cpeakgroupmeta.metabinputdata.name',
                              verbose_name='Input Dataset (name)')

    investigation = tables.Column(accessor='investigation_names', verbose_name='Investigation')
    study = tables.Column(accessor='study_names',
                                   verbose_name='Study')

    assay = tables.Column(accessor='assay_names',
                                   verbose_name='Assay')

    polarity = tables.Column(accessor='cannotation.cpeakgroup.cpeakgroupmeta.polarity', verbose_name='Polarity')

    galaxy_history_name = tables.Column(accessor='galaxy_history_name', verbose_name='Galaxy history)')
    galaxy_history_data_name = tables.Column(accessor='galaxy_history_data_name', verbose_name='Galaxy history (data)')

    inchikey = tables.Column(accessor='cannotation.compound.inchikey_id', verbose_name='InChIKey')
    compound_name = tables.Column(accessor='cannotation.compound.name', verbose_name='Compound name')
    pubchem_ids = tables.Column(accessor='cannotation.compound.pubchem_id', verbose_name='PubChem cid(s)')
    kegg_ids = tables.Column(accessor='cannotation.compound.kegg_id', verbose_name='KEGG cid(s)')

    # library_spectra = tables.Column(accessor='cannotation.compound.library_spectra_meta.name',
    #                                 verbose_name='Library spectra')
    # library_spectra_accession = tables.Column(accessor='cannotation.compound.library_spectra_meta.name',
    #                                 verbose_name='Library spectra accession')


    compound_id =  tables.Column(accessor='cannotation.cpeakgroup.id', verbose_name='C Peak Group ID')
    mzmed = NumberColumn4(accessor='cannotation.cpeakgroup.mzmed',verbose_name='MZ Med')
    rtmed = NumberColumn2(accessor='cannotation.cpeakgroup.rtmed', verbose_name='RT Med')

    spectral_matching_average_score = NumberColumn2(accessor='cannotation.spectral_matching_average_score')
    metfrag_average_score = NumberColumn2(accessor='cannotation.metfrag_average_score')
    mzcloud_average_score = NumberColumn2(accessor='cannotation.mzcloud_average_score')
    sirius_csifingerid_average_score = NumberColumn2(accessor='cannotation.sirius_csifingerid_average_score')
    ms1_average_score = NumberColumn2(accessor='cannotation.ms1_average_score')
    weighted_score = NumberColumn2(accessor='cannotation.weighted_score')
    rank = tables.Column(accessor='cannotation.rank')



    # how to get assay? Details are stored in the filenames... Perhaps better to create a new model to store this information

    # def get_column_default_show(self):
    #     self.column_default_show = ['galaxy_instance', 'name', 'data_type', 'create_time', 'download_url', 'mogi_create']
    #     return super(HistoryDataTable, self).get_column_default_show()
    #
    class Meta:
        attrs = {"class": TABLE_CLASS}

        model = CAnnotationMOGI


class IncomingGalaxyDataTable(ColumnShiftTable):
    mogi_create = tables.LinkColumn('save_lcms_from_from_rest', verbose_name='Save metabolomics data',
                                            text=SAVE, args=[A('galaxy_name'),
                                                             A('galaxy_data_id'),
                                                             A('galaxy_history_id'),
                                                             A('investigation_name')]
                                     )

    class Meta:
        attrs = {"class": TABLE_CLASS}
        model = IncomingGalaxyData

#