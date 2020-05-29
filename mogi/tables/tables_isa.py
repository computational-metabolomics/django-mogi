# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
from django.utils.safestring import mark_safe

import django_tables2 as tables
from django_tables2.utils import A
from django_tables2_column_shifter.tables import ColumnShiftTable

from gfiles.tables import GFileTable
from gfiles.models import GenericFile
from gfiles.utils.icons import EYE

from mogi.models import models_isa
from .tables_general import TABLE_CLASS



class InvestigationTableUpload(ColumnShiftTable):
    details = tables.LinkColumn('idetail_tables', text=EYE, args=[A('id')])

    check = tables.CheckBoxColumn(accessor="id",
                                               attrs={
                                                   "th__input": {"onclick": "toggle(this)"},
                                                   "td__input": {"onclick": "addfile(this)"}},
                                               )

    class Meta:
        model = models_isa.Investigation

        attrs = {"class": TABLE_CLASS}
        fields = ('id','name','description', 'details', 'public')


class AssayFileTable(ColumnShiftTable):

    study = tables.Column(accessor='run.assaydetail.assay.study.name',
                                  verbose_name='Study')

    assay = tables.Column(accessor='run.assaydetail.assay.name',
                          verbose_name='Assay')

    sample_name = tables.LinkColumn(accessor='run.assaydetail.studysample.sample_name',
                                verbose_name='Sample name', viewname='ssam_list')

    technical_replicate = tables.Column(accessor='run.technical_replicate',
                                        verbose_name='tech replicate')

    samplecollection = tables.LinkColumn(
        accessor='run.assaydetail.samplecollectionprocess.samplecollectionprotocol.code_field',
                                verbose_name='Sample collection', viewname='scp_list')

    lpe = tables.LinkColumn(
        accessor='run.assaydetail.extractionprocess.extractionprotocol.code_field',
         verbose_name='Liquid Phase Extraction (LPE)', viewname='ep_list')

    spetype = tables.LinkColumn(accessor='run.assaydetail.speprocess.speprotocol.code_field',
                            verbose_name='Solid Phase Extraction (SPE)',
                            viewname='spep_list')

    spefrac = tables.Column(accessor='run.assaydetail.speprocess.spefrac',
                            verbose_name='SPE frac')

    chromatography = tables.LinkColumn(
        accessor='run.assaydetail.chromatographyprocess.chromatographyprotocol.code_field',
        verbose_name='Chromatography',
        viewname='cp_list')

    chromatographyfrac = tables.Column(accessor='run.assaydetail.chromatographyprocess.chromatographyfrac',
                                       verbose_name='Chromatography frac')

    measurement = tables.LinkColumn(
        accessor='run.assaydetail.measurementprocess.measurementprotocol.code_field',
        verbose_name='Measurement',
        viewname='mp_list')
    
    polarity = tables.Column(accessor='run.assaydetail.measurementprocess.polaritytype.type',
                             verbose_name='Polarity')

    code_field = tables.Column(accessor='run.assaydetail.code_field',
                             verbose_name='Code field')


    class Meta:
        model = models_isa.MFile
        attrs = {"class": TABLE_CLASS}

        fields = ('id', 'original_filename', 'data_file')


class AssayDetailTable(ColumnShiftTable):


    study = tables.Column(accessor='assay.study.name',
                                  verbose_name='Study')

    assay = tables.Column(accessor='assay.name',
                          verbose_name='Assay')

    sample_name = tables.LinkColumn(accessor='studysample.sample_name',
                                    verbose_name='Sample name',
                                    viewname='ssam_list')


    samplecollection = tables.LinkColumn(
        accessor='samplecollectionprocess.samplecollectionprotocol.code_field',
        viewname='scp_list', verbose_name='Sample collection')

    lpe = tables.LinkColumn(accessor='extractionprocess.extractionprotocol.code_field',
                             viewname='ep_list',   verbose_name='Liquid Phase Extraction (LPE)')


    spetype = tables.LinkColumn(accessor='speprocess.speprotocol.code_field',
                            viewname='spep_list', verbose_name='Solid Phase Extraction (SPE)')

    spefrac = tables.Column(accessor='speprocess.spefrac',
                            verbose_name='SPE frac')

    chromatography = tables.LinkColumn(
        accessor='chromatographyprocess.chromatographyprotocol.code_field',
        verbose_name='Chromatography', viewname='cp_list')

    chromatographyfrac = tables.Column(accessor='chromatographyprocess.chromatographyfrac',
                                       verbose_name='Chromatography frac')

    measurement = tables.LinkColumn(
        accessor='measurementprocess.measurementprotocol.code_field',
        verbose_name='Measurement', viewname='mp_list')

    polarity = tables.Column(accessor='measurementprocess.polaritytype.type',
                             verbose_name='Polarity')

    code_field = tables.Column(accessor='code_field',
                             verbose_name='Code field')


    class Meta:
        model = models_isa.AssayDetail
        attrs = {"class": TABLE_CLASS}

        fields = ('id',)




class ISAFileSelectTable(ColumnShiftTable):

    user = tables.Column(accessor='user',
                         verbose_name='user')

    file = tables.Column(accessor='data_file',
                         verbose_name='Full path')

    non_mfile_investigation = tables.Column(accessor='misafile.investigation',
                         verbose_name='Investigation (non-mfile)')

    original_filename = tables.Column(accessor='original_filename',
                                      verbose_name='File name')

    filesuffix = tables.Column(accessor='mfile.mfilesuffix.suffix',
                               verbose_name='File suffix')

    investigation = tables.Column(accessor='mfile.run.assaydetail.assay.study.investigation.name',
                                  verbose_name='Investigation')

    study = tables.Column(accessor='mfile.run.assaydetail.assay.study.name',
                                  verbose_name='Study')

    assay = tables.Column(accessor='mfile.run.assaydetail.assay.name',
                          verbose_name='Assay')

    sample_name = tables.Column(accessor='mfile.run.assaydetail.studysample.sample_name',
                                verbose_name='Sample name')

    technical_replicate = tables.Column(accessor='mfile.run.technical_replicate',
                                        verbose_name='tech replicate')

    samplecollection = tables.LinkColumn(accessor='mfile.run.assaydetail.samplecollectionprocess.samplecollectionprotocol.code_field',
                                verbose_name='Sample collection', viewname='scp_list')

    lpe = tables.Column(accessor='mfile.run.assaydetail.extractionprocess.extractionprotocol.code_field',
                                verbose_name='Liquid Phase Extraction (LPE)')


    spetype = tables.Column(accessor='mfile.run.assaydetail.speprocess.speprotocol.code_field',
                            verbose_name='Solid Phase Extraction (SPE)')

    spefrac = tables.Column(accessor='mfile.run.assaydetail.speprocess.spefrac',
                            verbose_name='SPE frac')

    chromatography = tables.Column(
        accessor='mfile.run.assaydetail.chromatographyprocess.chromatographyprotocol.code_field',
        verbose_name='Chromatography')

    chromatographyfrac = tables.Column(accessor='mfile.run.assaydetail.chromatographyprocess.chromatographyfrac',
                                       verbose_name='Chromatography frac')

    measurement = tables.Column(
        accessor='mfile.run.assaydetail.measurementprocess.measurementprotocol.code_field',
        verbose_name='Measurement')

    polarity = tables.Column(accessor='mfile.run.assaydetail.measurementprocess.polaritytype.type',
                             verbose_name='Polarity')

    code_field = tables.Column(accessor='mfile.run.assaydetail.code_field',
                             verbose_name='Code field')


    def get_column_default_show(self):
        self.column_default_show = ['id', 'user', 'original_filename', 'sample_name', 'technical_replicate', 'study', 'assay']
        return super(ISAFileSelectTable, self).get_column_default_show()

    class Meta:
        model = GenericFile

        attrs = {"class": TABLE_CLASS}
        fields = ('id',)



class ISAFileSelectTableWithCheckBox(ISAFileSelectTable):

    check = tables.CheckBoxColumn(accessor="pk",
                                  attrs={
                                      "th__input": {"onclick": "toggle(this)"},
                                      "td__input": {"onclick": "addfile(this)"}},
                                  orderable=False)

    class Meta:
        model = GenericFile

        attrs = {"class": TABLE_CLASS}
        fields = ('id',)

    def get_column_default_show(self):
        self.column_default_show = ['id', 'user', 'original_filename', 'sample_name', 'technical_replicate',
                                    'investigation', 'study', 'assay', 'check']
        return super(ISAFileSelectTableWithCheckBox, self).get_column_default_show()




class InvestigationTable(ColumnShiftTable):
    details = tables.LinkColumn('idetail_tables', text='details', args=[A('id')])
    export = tables.LinkColumn('export_isa_json', text='export', verbose_name='Export ISA-JSON', args=[A('id')])
    update = tables.LinkColumn('iupdate', text='Update', verbose_name='Update', args=[A('id')])

    delete = tables.LinkColumn('idelete', text='delete', verbose_name='Delete', args=[A('id')])

    class Meta:
        model = models_isa.Investigation

        attrs = {"class": TABLE_CLASS}
        fields = ('id','name','description', 'details', 'update', 'public', 'owner', 'export')


class AssayTable(tables.Table):
    upload = tables.LinkColumn('upload_assay_data_files',  text='upload', verbose_name='Upload Assay Data Files', args=[A('id')])
    details = tables.LinkColumn('assaydetail_summary', text='details',verbose_name='Assay details', args=[A('id')])
    files = tables.LinkColumn('assayfile_summary',  text='files', verbose_name='Assay files', args=[A('id')])
    delete = tables.LinkColumn('adelete', text='delete', verbose_name='Delete', args=[A('id')])



    class Meta:
        model = models_isa.Assay
        attrs = {"class": TABLE_CLASS}
        fields = ('id', 'name', 'public', 'owner')
        sequence = ('id', 'name', 'details', 'files', 'upload', 'public', 'owner', 'delete')


class OntologyTermTable(ColumnShiftTable):
    add = tables.LinkColumn('add_ontologyterm', text='add', verbose_name='Add Ontology Term',
                               args=[A('c')])

    c = tables.Column(verbose_name='Match count')

    class Meta:
        model = models_isa.OntologyTerm
        attrs = {"class": TABLE_CLASS}



class OntologyTermTableLocal(ColumnShiftTable):
    update = tables.LinkColumn('update_ontologyterm', text='update', verbose_name='Update', args=[A('id')])
    delete = tables.LinkColumn('delete_ontologyterm', text='delete', verbose_name='Delete', args=[A('id')])

    class Meta:
        model = models_isa.OntologyTerm
        attrs = {"class": TABLE_CLASS}
        template = 'django_tables2/bootstrap.html'


class ExtractionProtocolTable(tables.Table):
    ontology_terms = tables.Column(accessor='all_ontologyterms', verbose_name='Ontology terms')
    extractiontype = tables.LinkColumn('et_list', verbose_name='Type')
    update = tables.LinkColumn('ep_update', text='update', verbose_name='Update', args=[A('id')])
    delete = tables.LinkColumn('ep_delete', text='delete', verbose_name='Delete', args=[A('id')])
    class Meta:
        model = models_isa.ExtractionProtocol
        attrs = {"class": TABLE_CLASS}



class ExtractionTypeTable(tables.Table):

    update = tables.LinkColumn('et_update', text='update', verbose_name='Update', args=[A('id')])
    delete = tables.LinkColumn('et_delete', text='delete', verbose_name='Delete', args=[A('id')])
    class Meta:
        model = models_isa.ExtractionType
        attrs = {"class": TABLE_CLASS}
        fields = ('id', 'type', 'description', 'all_ontologyterms')


class SpeProtocolTable(tables.Table):
    ontology_terms = tables.Column(accessor='all_ontologyterms', verbose_name='Ontology terms')
    spetype = tables.LinkColumn('spet_list', verbose_name='Type')
    update = tables.LinkColumn('spep_update', text='update', verbose_name='Update', args=[A('id')])
    delete = tables.LinkColumn('spep_delete', text='delete', verbose_name='Delete', args=[A('id')])
    class Meta:
        model = models_isa.SpeProtocol
        attrs = {"class": TABLE_CLASS}



class SpeTypeTable(tables.Table):

    update = tables.LinkColumn('spet_update', text='update', verbose_name='Update', args=[A('id')])
    delete = tables.LinkColumn('spet_delete', text='delete', verbose_name='Delete', args=[A('id')])
    class Meta:
        model = models_isa.SpeType
        attrs = {"class": TABLE_CLASS}
        fields = ('id', 'type', 'description', 'all_ontologyterms')


class ChromatographyProtocolTable(tables.Table):
    ontology_terms = tables.Column(accessor='all_ontologyterms', verbose_name='Ontology terms')
    chromatographytype = tables.LinkColumn('ct_list', verbose_name='Type')
    update = tables.LinkColumn('cp_update', text='update', verbose_name='Update', args=[A('id')])
    delete = tables.LinkColumn('cp_delete', text='delete', verbose_name='Delete', args=[A('id')])
    class Meta:
        model = models_isa.ChromatographyProtocol
        attrs = {"class": TABLE_CLASS}
        template = 'django_tables2/bootstrap.html'


class ChromatographyTypeTable(tables.Table):

    update = tables.LinkColumn('ct_update', text='update', verbose_name='Update', args=[A('id')])
    delete = tables.LinkColumn('ct_delete', text='delete', verbose_name='Delete', args=[A('id')])
    class Meta:
        model = models_isa.ChromatographyType
        attrs = {"class": TABLE_CLASS}
        fields = ('id', 'type', 'description', 'all_ontologyterms', 'owner', 'public')


class MeasurementProtocolTable(tables.Table):
    ontology_terms = tables.Column(accessor='all_ontologyterms', verbose_name='Ontology terms')
    measurementtechnique = tables.LinkColumn('mt_list', verbose_name='Technique')
    update = tables.LinkColumn('mp_update', text='update', verbose_name='Update', args=[A('id')])
    delete = tables.LinkColumn('mp_delete', text='delete', verbose_name='Delete', args=[A('id')])
    class Meta:
        model = models_isa.MeasurementProtocol
        attrs = {"class": TABLE_CLASS}


class MeasurementTechniqueTable(tables.Table):

    update = tables.LinkColumn('mt_update', text='update', verbose_name='Update', args=[A('id')])
    delete = tables.LinkColumn('mt_delete', text='delete', verbose_name='Delete', args=[A('id')])
    class Meta:
        model = models_isa.MeasurementTechnique
        attrs = {"class": TABLE_CLASS}
        fields = ('id', 'type', 'description', 'all_ontologyterms')


class SampleCollectionProtocolTable(tables.Table):

    update = tables.LinkColumn('scp_update', text='update', verbose_name='Update', args=[A('id')])
    delete = tables.LinkColumn('scp_delete', text='delete', verbose_name='Delete', args=[A('id')])
    class Meta:
        model = models_isa.SampleCollectionProtocol
        attrs = {"class": TABLE_CLASS}


class DataTransformationProtocolTable(tables.Table):

    update = tables.LinkColumn('dtp_update', text='update', verbose_name='Update', args=[A('id')])
    delete = tables.LinkColumn('dtp_delete', text='delete', verbose_name='Delete', args=[A('id')])
    class Meta:
        model = models_isa.DataTransformationProtocol
        attrs = {"class": TABLE_CLASS}


class MarkSafeLinkColumn(tables.LinkColumn):
    def render(self, record, value):
        return self.text_value(record, value=mark_safe(value))




class StudySampleTable(tables.Table):

    investigation = tables.Column(accessor='study.investigation.name', verbose_name='Investigation')
    study = tables.Column(accessor='study.name', verbose_name='Study')
    all_studyfactors = MarkSafeLinkColumn('sflist', verbose_name='Study Factors')
    organism = tables.LinkColumn('org_list')
    organism_part = tables.LinkColumn('orgpart_list')

    update = tables.LinkColumn('ssam_update', text='update', verbose_name='Update', args=[A('id')])
    delete = tables.LinkColumn('ssam_delete', text='delete', verbose_name='Delete', args=[A('id')])


    class Meta:
        model = models_isa.StudySample
        attrs = {"class": TABLE_CLASS}

        fields = ('id', 'investigation', 'study', 'sample_name', 'all_studyfactors', 'organism', 'organism_part',
                  'update', 'delete', 'public')


class StudyFactorTable(tables.Table):

    update = tables.LinkColumn('sfupdate', text='update', verbose_name='Update', args=[A('id')])
    delete = tables.LinkColumn('sfdelete', text='delete', verbose_name='Delete', args=[A('id')])
    class Meta:
        model = models_isa.StudyFactor
        attrs = {"class": TABLE_CLASS}




class OrganismTable(tables.Table):

    update = tables.LinkColumn('org_update', text='update', verbose_name='Update', args=[A('id')])
    delete = tables.LinkColumn('org_delete', text='delete', verbose_name='Delete', args=[A('id')])
    class Meta:
        model = models_isa.Organism
        attrs = {"class": TABLE_CLASS}


class OrganismPartTable(tables.Table):

    update = tables.LinkColumn('orgpart_update', text='update', verbose_name='Update', args=[A('id')])
    delete = tables.LinkColumn('orgpart_delete', text='delete', verbose_name='Delete', args=[A('id')])
    class Meta:
        model = models_isa.OrganismPart
        attrs = {"class": TABLE_CLASS}


