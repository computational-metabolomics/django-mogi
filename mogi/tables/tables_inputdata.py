import django_tables2 as tables
from django_tables2.utils import A
from django_tables2_column_shifter.tables import ColumnShiftTable
from gfiles.utils.icons import EYE
from mogi.models import models_inputdata
from .tables_general import TABLE_CLASS


class MetabInputDataTable(ColumnShiftTable):
    combined_peak_table = tables.LinkColumn('combinedpeak_summary', verbose_name='View',
                                            text=EYE, args=[A('id')])

    update = tables.LinkColumn('update_metabinputdata',
                               text='Update', verbose_name='Update', args=[A('id')])


    class Meta:

        model = models_inputdata.MetabInputData
        # add class="paleblue" to <table> tag

        attrs = {"class": TABLE_CLASS}




