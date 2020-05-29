import django_tables2 as tables
from django_tables2.utils import A
from django_tables2_column_shifter.tables import ColumnShiftTable
from gfiles.utils.icons import EYE
TABLE_CLASS = "mogi table-bordered table-striped table-condensed table-hover"

PUBCHEM_STRUCTURE_IMAGE = '<a href="https://pubchem.ncbi.nlm.nih.gov/compound/{{record.pubchem_cids}}"><img ' \
                          'src="https://pubchem.ncbi.nlm.nih.gov/image/imgsrv.fcgi?cid={{record.pubchem_cids}}&t=s">' \
                          '</a>'


class CheckBoxColumnWithName(tables.CheckBoxColumn):
    @property
    def header(self):
        return self.verbose_name


class NumberColumn4(tables.Column):
    def render(self, value):
        return '{:0.4f}'.format(value)


class NumberColumn2(tables.Column):
    def render(self, value):
        return '{:0.2f}'.format(value)






