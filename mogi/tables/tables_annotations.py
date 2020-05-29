import django_tables2 as tables
from django_tables2.utils import A
from django_tables2_column_shifter.tables import ColumnShiftTable

from gfiles.utils.icons import EYE

from mogi.models import models_annotations
from .tables_general import TABLE_CLASS, NumberColumn2, NumberColumn4

PUBCHEM_STRUCTURE_IMAGE = '<a href="https://pubchem.ncbi.nlm.nih.gov/compound/{{record.compound.pubchem_cids}}"><img ' \
                          'src="https://pubchem.ncbi.nlm.nih.gov/image/imgsrv.fcgi?cid={{' \
                          'record.compound.pubchem_cids}}&t=s">' \
                          '</a>'


class SpectralMatchingTable(ColumnShiftTable):
    smatch = tables.LinkColumn('smatch', verbose_name='View Match',
                                            text=EYE, args=[A('id')])


    class Meta:

        model = models_annotations.MetaboliteAnnotation

        # add class="paleblue" to <table> tag

        attrs = {"class": TABLE_CLASS}


class CombinedAnnotationTable(ColumnShiftTable):
    mz = NumberColumn4(accessor='combinedpeak.mz', verbose_name='m/z')
    rt = NumberColumn2(accessor='combinedpeak.rt', verbose_name='rt')

    ms_type = tables.Column(accessor='combinedpeak.ms_type', verbose_name='MS type')

    assay_names = tables.Column(accessor='combinedpeak.metabinputdata.assay_names', verbose_name='Assay')
    study_names = tables.Column(accessor='combinedpeak.metabinputdata.study_names', verbose_name='Study')
    investigation_names = tables.Column(accessor='combinedpeak.metabinputdata.investigation_names',
                                        verbose_name='Investigation')

    total_wscore = NumberColumn2()
    spectral_matching_score = NumberColumn2()
    spectral_matching_wscore = NumberColumn2()
    metfrag_score = NumberColumn2()
    metfrag_wscore = NumberColumn2()
    sirius_csifingerid_score = NumberColumn2()
    sirius_csifingerid_wscore = NumberColumn2()
    biosim_max_score = NumberColumn2()
    biosim_wscore = NumberColumn2()


    compound_name = tables.Column(accessor='compound.name', verbose_name='Compound name')
    compound_inchikey = tables.Column(accessor='compound.inchikey', verbose_name='InChI Key')

    hmdb_sim = tables.Column(accessor='compound.biosim_hmdb_ids', verbose_name='HMDB similar compound')

    # smatch = tables.LinkColumn('smatch', verbose_name='Spectral Matches',
    #                                         text=EYE, args=[A('id')])
    #
    annotation_further = tables.LinkColumn('annotation_further', verbose_name='Further details', text=EYE,
                                           args=[A('combinedpeak__id'), A('compound__inchikey')])

    eics = tables.LinkColumn('eics', verbose_name='EICs',
                                            text=EYE, args=[A('combinedpeak__cpeakgroup__id')])

    frag4combinedpeak = tables.LinkColumn('frag4combinedpeak', verbose_name='Fragmentation',
                                            text=EYE, args=[A('combinedpeak__id')])



    structure = tables.TemplateColumn(PUBCHEM_STRUCTURE_IMAGE)

    class Meta:
        attrs = {"class": TABLE_CLASS}
        fields = ('id', 'compound_annotated_adduct', 'ms1_lookup_score', 'ms1_lookup_wscore', 'spectral_matching_score',
                  'spectral_matching_wscore', 'metfrag_score', 'metfrag_wscore', 'sirius_csifingerid_score',
                  'sirius_csifingerid_wscore', 'biosim_max_score', 'biosim_wscore', 'total_wscore', 'rank')
        model = models_annotations.CombinedAnnotation


        sequence = ('id','investigation_names', 'study_names', 'assay_names', 'mz', 'rt', 'ms_type',
                    'compound_annotated_adduct', 'ms1_lookup_score', 'ms1_lookup_wscore',
                    'spectral_matching_score', 'spectral_matching_wscore', 'metfrag_score', 'metfrag_wscore',
                    'sirius_csifingerid_score','sirius_csifingerid_wscore', 'biosim_max_score',
                    'biosim_wscore', 'total_wscore', 'rank', 'compound_name', 'compound_inchikey', 'hmdb_sim','structure',
                   'annotation_further', 'eics', 'frag4combinedpeak')


    def get_column_default_show(self):
        self.column_default_show = ['id', 'mz', 'rt', 'ms_type', 'compound_annotated_adduct',
                                    'total_wscore', 'rank', 'compound_name', 'inchikey', 'structure',
                                    'annotation_further',
                                    'eics', 'frag4combinedpeak']

        return super(CombinedAnnotationTable, self).get_column_default_show()



class MetaboliteAnnotationTable(ColumnShiftTable):
    approach = tables.Column(accessor='metaboliteannotationapproach.name', verbose_name='Approach')

    details = tables.LinkColumn('metabolite_annotation_details', verbose_name='View', text=EYE,
                                           args=[A('id')])

    class Meta:
        model = models_annotations.MetaboliteAnnotation
        # add class="paleblue" to <table> tag
        attrs = {"class": TABLE_CLASS}
        fields = ('id', 'metabinputdata', 'speak', 'cpeakgroup', 'inchikey', 'inchikey1', 'libraryspectrameta')


class MetaboliteAnnotationDetailTable(ColumnShiftTable):
    detailtype = tables.Column(accessor='detailtype.name', verbose_name='Detail type')
    detaildescription = tables.Column(accessor='detailtype.description', verbose_name='Description')

    class Meta:

        model = models_annotations.MetaboliteAnnotationDetail
        # add class="paleblue" to <table> tag
        attrs = {"class": TABLE_CLASS}
        fields = ('id', 'detailtype', 'detail_value', 'detaildescription')


class MetaboliteAnnotationScoreTable(ColumnShiftTable):
    scoretype = tables.Column(accessor='scoretype.name', verbose_name='Score type')
    scoredescription = tables.Column(accessor='scoretype.description', verbose_name='Description')
    score_value = NumberColumn4()
    class Meta:

        model = models_annotations.MetaboliteAnnotationScore
        # add class="paleblue" to <table> tag
        attrs = {"class": TABLE_CLASS}
        fields = ('id', 'scoretype', 'score_value', 'scoredescription')


class CombinedAnnotationDownloadResultTable(ColumnShiftTable):
    username = tables.Column(accessor='cannotationdownload.user.username', verbose_name='Username')

    class Meta:

        model = models_annotations.CombinedAnnotationDownloadResult
        fields = ('id', 'annotation_file', 'created', 'username')
        # add class="paleblue" to <table> tag
        attrs = {"class": TABLE_CLASS}