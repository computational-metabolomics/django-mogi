from django_tables2_column_shifter.tables import ColumnShiftTable

from mogi.models import models_search
from .tables_general import TABLE_CLASS, NumberColumn2, NumberColumn4


class SearchResultTable(ColumnShiftTable):


    class Meta:

        model = models_search.SearchResult

        # add class="paleblue" to <table> tag

        attrs = {"class": TABLE_CLASS}
