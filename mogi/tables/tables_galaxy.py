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
