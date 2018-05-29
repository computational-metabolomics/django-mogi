from misa.tables import InvestigationTable
import django_tables2 as tables
from django_tables2.utils import A
from misa.models import Investigation
from galaxy.models import Workflow, History
from galaxy.tables import HistoryTable, HistoryDataTable
from metab.tables import CAnnotationTable, CPeakGroupMetaTable
from mogi.models import CAnnotationMOGI, CPeakGroupMetaMOGI
from django_tables2_column_shifter.tables import ColumnShiftTable

# class InvestigationTableUpload(InvestigationTable):
#     details = tables.LinkColumn('idetail', text='details', args=[A('id')])
#     check = tables.CheckBoxColumn(accessor="name",
#                                            attrs={
#                                                "th__input": {"onclick": "toggle(this)"},
#                                                "td__input": {"onclick": "addfile(this)"}},
#                                            )

class InvestigationTableUpload(ColumnShiftTable):
    details = tables.LinkColumn('idetail', text='details', args=[A('id')])

    check = tables.CheckBoxColumn(accessor="id",
                                               attrs={
                                                   "th__input": {"onclick": "toggle(this)"},
                                                   "td__input": {"onclick": "addfile(this)"}},
                                               )

    class Meta:
        model = Investigation
        attrs = {'class': 'paleblue'}
        template = 'django_tables2/bootstrap.html'
        fields = ('id','name','description', 'details')




class WorkflowTableISA(ColumnShiftTable):
    run = tables.LinkColumn('isa_workflow_run', text='run', args=[A('id')])

    def get_column_default_show(self):
        self.column_default_show = ['id', 'name', 'galaxyinstancetracking', 'accessible', 'run']
        return super(WorkflowTableISA, self).get_column_default_show()

    class Meta:

        model = Workflow
        attrs = {'class': 'paleblue'}
        template = 'django_tables2/bootsrap.html'


class HistoryMogiTable(HistoryTable):
    history_mogi_data = tables.LinkColumn('history_mogi_data', text='View data', args=[A('id')])

    def get_column_default_show(self):
        self.column_default_show = ['galaxyinstancetracking', 'name', 'update_time', 'running', 'estimated_progress', 'history_mogi_data', 'check']
        return super(HistoryTable, self).get_column_default_show()

    class Meta:
        model = History
        sequence = ( 'id', 'galaxyinstancetracking', 'name', 'update_time', 'empty', 'failed_metadata', 'new', 'ok', 'paused', 'error',
                     'queued', 'setting_metadata', 'upload', 'running', 'estimated_progress', 'galaxy_id', 'history_data_bioblend_list',
                     'history_mogi_data', 'check')
        attrs = {
            ' class ': 'paleblue',
        }
        # running_tasks_details = tables.Column()
        order_by = ('-update_time',)

        template = 'django_tables2/bootstrap.html'




class HistoryMogiDataTable(HistoryDataTable):
    mogi_create = tables.LinkColumn('history_mogi_data_save', verbose_name='Save metabolomics data',
                                            text='Save item', args=[A('history_internal_id'), A('id')])

    def get_column_default_show(self):
        self.column_default_show = ['galaxy_instance', 'name', 'data_type', 'create_time', 'download_url', 'mogi_create']
        return super(HistoryDataTable, self).get_column_default_show()

    class Meta:
        attrs = {'class': 'paleblue'}
        template = 'django_tables2/bootstrap.html'


class CPeakMetaMogiTable(CPeakGroupMetaTable):
    galaxy_history = tables.Column(accessor='cpeakgroupmeta.metabinputdata.historymogi.name', verbose_name='Galaxy history details')

    investigation = tables.Column(accessor='metabinputdata.historymogi.investigation',
                                   verbose_name='Galaxy history details')

    class Meta:
        model = CPeakGroupMetaMOGI
        attrs = {'class': 'paleblue'}
        template = 'django_tables2/bootstrap.html'




class CAnnotationMogiTable(ColumnShiftTable):
    # galaxy_history = tables.Column(accessor='cpeakgroup.cpeakgroupmeta.metabinputdata.historymogi.name', verbose_name='Galaxy history details')
    #
    # investigation = tables.Column(accessor='cpeakgroup.cpeakgroupmeta.metabinputdata.historymogi.investigation',
    #                                verbose_name='Galaxy history details')

    # how to get assay? Detials are stored in the filenames... Perhaps better to create a new model to store this information

    # def get_column_default_show(self):
    #     self.column_default_show = ['galaxy_instance', 'name', 'data_type', 'create_time', 'download_url', 'mogi_create']
    #     return super(HistoryDataTable, self).get_column_default_show()
    #
    class Meta:
        attrs = {'class': 'paleblue'}
        template = 'django_tables2/bootstrap.html'
        model = CAnnotationMOGI


