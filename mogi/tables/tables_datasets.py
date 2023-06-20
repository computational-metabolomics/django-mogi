import django_tables2 as tables
from django_tables2.utils import A
from django_tables2_column_shifter.tables import ColumnShiftTable
from gfiles.utils.icons import EYE
from mogi.models import models_datasets
from .tables_general import TABLE_CLASS


class ResultsDataTable(ColumnShiftTable):
    galaxy_history_url = tables.URLColumn()
    canns = tables.LinkColumn('canns', verbose_name='Combined annotations', text=EYE, args=[A('id')])

    class Meta:

        model = models_datasets.Dataset
        # add class="paleblue" to <table> tag

        attrs = {"class": TABLE_CLASS}
