import django_tables2 as tables
from django_tables2.utils import A
from django_tables2_column_shifter.tables import ColumnShiftTable
from mogi.models import models_compounds
from .tables_general import TABLE_CLASS

PUBCHEM_STRUCTURE_IMAGE = '<a href="https://pubchem.ncbi.nlm.nih.gov/compound/{{record.pubchem_id_single}}"><img ' \
                          'src="https://pubchem.ncbi.nlm.nih.gov/image/imgsrv.fcgi?cid={{record.pubchem_id_single}}&t=s">' \
                          '</a>'

class CompoundTable(ColumnShiftTable):

    structure = tables.TemplateColumn(PUBCHEM_STRUCTURE_IMAGE)

    class Meta:

        model = models_compounds.Compound
        row_attrs = {
            "ondblclick": lambda record: "document.location.href='/media/{0}';".format(record.data_file)
        }


        # add class="paleblue" to <table> tag

        attrs = {"class": TABLE_CLASS}
        fields = (

                  'id', 'structure', 'inchikey', 'inchikey1',
                  'smiles', 'molecular_formula', 'monoisotopic_exact_mass',
                  'compound_name', 'natural_product_inchikey1', 'pubchem_cids',
                  'hmdb_ids', 'kegg_ids', 'chebi_ids', 'kingdom',
                  'superclass', '_class', 'subclass', 'direct_parent',
                  'molecular_framework', 'predicted_lipidmaps_terms',
                  'assay', 'extraction', 'spe', 'spe_frac',
                  'chromatography', 'measurement', 'polarity',
                  'lcmsdimsbool', 'gcmsbool', 'smbool', 'metfragbool',
                  'siriusbool', 'mzcloudbool', 'galaxysmbool', 'gnpssmbool',
                  'msi_level')
