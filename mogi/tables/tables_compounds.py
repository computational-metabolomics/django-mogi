import django_tables2 as tables
from django_tables2.utils import A
from django_tables2_column_shifter.tables import ColumnShiftTable
from mogi.models import models_compounds
from .tables_general import TABLE_CLASS

PUBCHEM_STRUCTURE_IMAGE = '<a href="https://pubchem.ncbi.nlm.nih.gov/compound/{{record.pubchem_cids}}"><img ' \
                          'src="https://pubchem.ncbi.nlm.nih.gov/image/imgsrv.fcgi?cid={{record.pubchem_cids}}&t=s">' \
                          '</a>'

class CompoundTable(ColumnShiftTable):

    top_score = tables.Column(accessor='compoundannotationsummary.top_score', verbose_name='Top score')
    top_rank = tables.Column(accessor='compoundannotationsummary.top_rank', verbose_name='Top rank')
    assays = tables.Column(accessor='compoundannotationsummary.assays', verbose_name='Assays')

    structure = tables.TemplateColumn(PUBCHEM_STRUCTURE_IMAGE)


    class Meta:

        model = models_compounds.Compound

        # add class="paleblue" to <table> tag

        attrs = {"class": TABLE_CLASS}
