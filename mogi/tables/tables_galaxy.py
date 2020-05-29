import django_tables2 as tables
from django_tables2.utils import A
from django_tables2_column_shifter.tables import ColumnShiftTable

from gfiles.utils.icons import EYE, DOWN, PLAY, SAVE
from galaxy.models import Workflow, History
from galaxy.tables import HistoryTable, HistoryDataTable

from mogi.models import models_galaxy
from .tables_general import TABLE_CLASS


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


class IncomingGalaxyDataTable(ColumnShiftTable):
    mogi_create = tables.LinkColumn('save_lcms_from_from_rest', verbose_name='Save metabolomics data',
                                            text=SAVE, args=[A('galaxy_name'),
                                                             A('galaxy_data_id'),
                                                             A('galaxy_history_id'),
                                                             A('investigation_name')]
                                     )

    class Meta:
        attrs = {"class": TABLE_CLASS}
        model = models_galaxy.IncomingGalaxyData

#