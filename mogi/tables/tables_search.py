import django_tables2 as tables
from django_tables2_column_shifter.tables import ColumnShiftTable
from django_tables2.utils import A
from gfiles.utils.icons import EYE

from mogi.models import models_search
from .tables_general import TABLE_CLASS, NumberColumn2, NumberColumn4
PUBCHEM_STRUCTURE_IMAGE = '<a href="https://pubchem.ncbi.nlm.nih.gov/compound/{{record.compound.pubchem_id_single}}"><img ' \
                          'src="https://pubchem.ncbi.nlm.nih.gov/image/imgsrv.fcgi?cid={{record.compound.pubchem_id_single}}&t=s">' \
                          '</a>'

class SearchMonoParamTable(ColumnShiftTable):

    smatch = tables.LinkColumn('search_mono_results', verbose_name='View matches', text=EYE, args=[A('id')])

    class Meta:

        model = models_search.SearchMonoParam

        # add class="paleblue" to <table> tag

        attrs = {"class": TABLE_CLASS}
        fields = ('id',  'user', 'description', 'searchmonoparam.ppm_tolerance', 'matches',
                  'smatch')


class SearchFragParamTable(ColumnShiftTable):

    smatch = tables.LinkColumn('search_frag_results', verbose_name='View matches', text=EYE, args=[A('id')])


    class Meta:

        model = models_search.SearchFragParam


class SearchMonoResultTable(ColumnShiftTable):
    structure = tables.TemplateColumn(PUBCHEM_STRUCTURE_IMAGE)

    class Meta:

        model = models_search.SearchMonoResult

        row_attrs = {
            "ondblclick": lambda record: "document.location.href='/media/{0}';".format(record.compound.data_file)
        }

        attrs = {"class": TABLE_CLASS}
        fields = ('searchparam.searchmonoparam.ppm_tolerance', 'searchparam.user', 'ppmdiff', 'massquery',
                  'compound.monoisotopic_exact_mass',
                  'compound.id', 'structure', 'compound.inchikey', 'compound.inchikey1',
                  'compound.smiles', 'compound.molecular_formula',
                  'compound.compound_name', 'compound.natural_product_inchikey1', 'compound.pubchem_cids',
                  'compound.hmdb_ids', 'compound.kegg_ids', 'compound.chebi_ids', 'compound.kingdom',
                  'compound.superclass', 'compound._class', 'compound.subclass', 'compound.direct_parent',
                  'compound.molecular_framework', 'compound.predicted_lipidmaps_terms',
                  'compound.assay', 'compound.extraction', 'compound.spe', 'compound.spe_frac',
                  'compound.chromatography', 'compound.measurement', 'compound.polarity',
                  'compound.lcmsdimsbool', 'compound.gcmsbool', 'compound.smbool', 'compound.metfragbool',
                  'compound.siriusbool', 'compound.mzcloudbool', 'compound.galaxysmbool', 'compound.gnpssmbool',
                  'compound.msi_level')


class SearchFragResultTable(ColumnShiftTable):
    smatch = tables.LinkColumn('search_frag_annotations', verbose_name='View matches', text=EYE, args=[A('id')])

    class Meta:

        model = models_search.SearchFragResult
        fields = ('id', 'dpc', 'q_prec_mz', 'l_prec_mz', 'ppm_diff_prec', 'rt', 'well', 'dataset_pid',
                  'dataset_sid', 'spectrum_type', 'spectrum_details',
                  'dataset', 'dataset.assay.name', 'dataset.polarity', 'dataset.sqlite',
                  'top_spectral_match', 'top_metfrag', 'top_sirius_csifingerid', 'top_combined_annotation',
                  'top_wscore', 'smatch')