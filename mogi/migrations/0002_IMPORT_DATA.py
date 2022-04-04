# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os

from django.db import migrations
from mogi.utils.ontology_utils import check_and_create_ontology
from mogi.utils.sample_batch_create import check_and_create_model


def save_model_list_migration(l,db_alias):
    [i.save(using=db_alias) for i in l]

def forwards_func(apps, schema_editor):
    # We get the model from the versioned app registry;
    # if we directly import it, it'll be the wrong version
    db_alias = schema_editor.connection.alias

    MFileSuffix = apps.get_model("mogi", "MFileSuffix")
    MsLevel = apps.get_model("mogi", "MsLevel")
    PolarityType = apps.get_model("mogi", "PolarityType")

    Organism = apps.get_model("mogi", "Organism")
    OrganismPart = apps.get_model("mogi", "OrganismPart")
    SampleType = apps.get_model("mogi", "SampleType")
    MeasurementTechnique = apps.get_model("mogi", "MeasurementTechnique")

    ExtractionType = apps.get_model("mogi", "ExtractionType")
    SpeType = apps.get_model("mogi", "SpeType")
    ChromatographyType = apps.get_model("mogi", "ChromatographyType")

    SampleCollectionProtocol = apps.get_model("mogi", "SampleCollectionProtocol")
    ExtractionProtocol = apps.get_model("mogi", "ExtractionProtocol")
    SpeProtocol = apps.get_model("mogi",  "SpeProtocol")
    ChromatographyProtocol = apps.get_model("mogi", "ChromatographyProtocol")
    MeasurementProtocol = apps.get_model("mogi", "MeasurementProtocol")

    OntologyTerm = apps.get_model("mogi", "OntologyTerm")

    StudySample = apps.get_model("mogi", "StudySample")

    Investigation = apps.get_model("mogi",  "Investigation")
    Study = apps.get_model("mogi",  "Study")
    Assay = apps.get_model("mogi", "Assay")

    MetaboliteAnnotationApproach = apps.get_model("mogi", "MetaboliteAnnotationApproach")
    ScoreType = apps.get_model("mogi", "ScoreType")
    DetailType = apps.get_model("mogi", "DetailType")


    mfs = MFileSuffix(suffix='.mzml')
    mfs.save(using=db_alias)
    mfr = MFileSuffix(suffix='.raw')
    mfr.save(using=db_alias)


    ml = MsLevel(ms_level=1)
    ml.save(using=db_alias)
    ml = MsLevel(ms_level=2)
    ml.save(using=db_alias)
    ml = MsLevel(ms_level=3)
    ml.save(using=db_alias)
    ml = MsLevel(ms_level=4)
    ml.save(using=db_alias)

    ps = PolarityType(type='NEGATIVE')
    ps.save(using=db_alias)
    ps = PolarityType(type='POSITIVE')
    ps.save(using=db_alias)
    ps = PolarityType(type='UNKNOWN')
    ps.save(using=db_alias)
    ps = PolarityType(type='COMBINATION')
    ps.save(using=db_alias)
    ps = PolarityType(type='NA')
    ps.save(using=db_alias)


    #############################################################################################
    # Setup ontologies
    #############################################################################################
    # print('###ontologies')
    terms = ['NCIT_C49019', 'NCIT_C61575', 'SIO_001046', 'SIO_001047', 'CHEMINF_000070',
             'CHMO_0002302', 'CHMO_0002262', 'CHMO_0002269', 'CO_356:3000142', 'CHMO_0002658',
             'CHMO_0002804', 'NCIT_C16631', 'NCIT_C43366', 'NCIT_C14182', 'NCIT_C62195',
             'NCIT_C25360', 'NCIT_C61299', 'NCIT_C25301', 'NCIT_C25207', 'NCBITaxon_35128',
             'NCIT_C13413', 'NCBITaxon_35525', 'NCBITaxon_6669', 'SIO_001047' 'OMIT_0025161',
             'CHMO_0000524', 'CHMO_0000701','OMIT_0025161', 'CHMO_0000575', 'FOODON:03414374',
             'MS_1001911', 'AFFN_0000004', 'NCIT_C69023', 'CHMO_0002767', 'MS_1001911',
             'CHMO_0002261', 'MS_1001910', 'OMIT_0025161', 'CHMO_0000524', 'CHMO_0000701',
             'NCIT_C15311',
             'MS_1001911']

    [check_and_create_ontology(term, db_alias, False) for term in terms]




    #============================================
    # Setup liquid Phase extraction types
    #============================================
    # print('###LPE')
    # Liquid Phase Extraction types
    lpe_type1 = ExtractionType(type="Apolar", description="Apolar (non-polar)", public=True)
    lpe_type1.save(using=db_alias)
    lpe_type1.ontologyterm.add(OntologyTerm.objects.filter(name='non-polar')[0])
    lpe_type1.ontologyterm.add(OntologyTerm.objects.filter(name='Extraction')[0])

    lpe_type2 = ExtractionType(type="Polar", description="Polar", public=True)
    lpe_type2.save(using=db_alias)
    lpe_type2.ontologyterm.add(OntologyTerm.objects.filter(name='polar')[0])
    lpe_type2.ontologyterm.add(OntologyTerm.objects.filter(name='Extraction')[0])

    lpe_type3 = ExtractionType(type="Just dilution",
                               description="Some sample types only require dilution",
                               public=True)
    lpe_type3.save(using=db_alias)

    etype = ExtractionType(type="NA", description="NA", public=True)
    etype.save(using=db_alias)


    #===========================================
    # Sold phase extraction types
    #============================================
    # print('###SPE')
    # SPE types
    spe_type1 = SpeType(type="Ion exchange SPE",
                        description="Electrostatic interactions between the analyte of interest "
                                                         "can be anion or cation",
                        public=True)
    spe_type1.save(using=db_alias)

    spe_type2 = SpeType(type="Normal-phase SPE",
                        description="Polar stationary phase", public=True)
    spe_type2.save(using=db_alias)

    spe_type3 = SpeType(type="Reverse-phase SPE",
                        description="Apolar stationary phase", public=True)
    spe_type3.save(using=db_alias)

    spe_type4 = SpeType(type="Mixed mode SPE",
                        description="Combination of retention mechanisms on a "
                                                           "single cartridge",
                        public=True)
    spe_type4.save(using=db_alias)


    #============================================
    # Chromatography types
    #============================================
    # print('###Chroma')
    # Chromatography types
    lc_type1 = ChromatographyType(type="Reversed phase chromatography",
                                  description="Reversed phase chromatography",
                                  public=True)
    lc_type1.save(using=db_alias)
    lc_type1.ontologyterm.add(OntologyTerm.objects.filter(
        name='reversed-phase chromatography')[0]
    )

    lc_type2 = ChromatographyType(type="HILIC",
                                  description="Hydrophilic interaction chromatography",
                                  public=True)
    lc_type2.save(using=db_alias)
    lc_type2.ontologyterm.add(OntologyTerm.objects.filter(
        name='hydrophilic interaction chromatography')[0]
    )


    #============================================
    # Measurements techniques (types)
    #============================================
    # print('###Meas')
    # Measurement types
    m_type1 = MeasurementTechnique(type="LC-MS",
                                   description="Liquid Chromatography mass spectrometry",
                                   public=True)
    m_type1.save(using=db_alias)
    m_type1.ontologyterm.add(OntologyTerm.objects.filter(short_form='CHMO_0000524')[0])

    m_type2 = MeasurementTechnique(type="LC-MSMS",
                                   description="Liquid Chromatography tandem mass spectrometry",
                                   public=True)
    m_type2.save(using=db_alias)
    m_type2.ontologyterm.add(OntologyTerm.objects.filter(short_form='CHMO_0000701')[0])

    m_type3 = MeasurementTechnique(type="DI-MS",
                                   description="Direct infusion mass spectrometry", public=True)
    m_type3.save(using=db_alias)

    m_type4 = MeasurementTechnique(type="DI-MSn",
                                   description="Direct infusion mass spectrometry with "
                                               "fragmentation",
                                   public=True)
    m_type4.save(using=db_alias)


    #############################################################################################
    # Organisms
    #############################################################################################
    # print('###Orgs')
    check_and_create_model('Thalassiosira pseudonana', Organism, db_alias)
    check_and_create_model('Daphnia magna', Organism, db_alias)
    check_and_create_model('Daphnia pulex', Organism, db_alias)
    check_and_create_model('Homo sapiens', Organism, db_alias)
    check_and_create_model('Mus musculus', Organism, db_alias)
    check_and_create_model('Bos taurus', Organism, db_alias)

    check_and_create_model('Whole Organism', OrganismPart, db_alias)
    check_and_create_model('exometabolome', OrganismPart, db_alias)
    check_and_create_model('endometabolome', OrganismPart, db_alias)
    check_and_create_model('serum', OrganismPart, db_alias)


    #############################################################################################
    # Sample types
    #############################################################################################
    # print('###Sample Types')
    st1 = SampleType(type='ANIMAL', public=True,
                     ontologyterm=OntologyTerm.objects.filter(name='Animal')[0])
    st2 = SampleType(type='COMPOUND', public=True,
                     ontologyterm=OntologyTerm.objects.filter(name='Compound')[0])
    st3 = SampleType(type='BLANK', public=True,
                     ontologyterm=OntologyTerm.objects.filter(name='blank value')[0])
    st4 = SampleType(type='MISC', public=True,
                     ontologyterm=OntologyTerm.objects.filter(name='Miscellaneous')[0])
    st5 = SampleType(type='EQUIL_BLANK', public=True,
                     ontologyterm=OntologyTerm.objects.filter(name='blank value')[0])
    st6 = SampleType(type='EQUIL', public=True,
                     ontologyterm=OntologyTerm.objects.filter(name='to equilibrate')[0])
    st7 = SampleType(type='QC', public=True,
                     ontologyterm=OntologyTerm.objects.filter(name='Quality Control')[0])

    st1.save(using=db_alias)
    st2.save(using=db_alias)
    st3.save(using=db_alias)
    st4.save(using=db_alias)
    st5.save(using=db_alias)
    st6.save(using=db_alias)
    st7.save(using=db_alias)


    #============================================================================================
    # DMA setup
    #============================================================================================
    #############################################################################################
    # Setup ISA backbone (DMA)
    #############################################################################################
    investigation = Investigation(name='DMA of D. magna',
                                  description="Deep metabolome annotation project of Daphnia "
                                              "magna",
                                  public=True)
    investigation.save(using=db_alias)

    # Create Study (has the same name of investigation by default)
    study = Study(investigation=investigation,
                  description='Deep metabolome annotation project of Daphnia magna (2020)',
                  name='DMA of D. magna (2020)', public=True)
    study.save(using=db_alias)

    #############################################################################################
    # Protocols
    #############################################################################################
    #============================================
    # Sample collection (DMA)
    #============================================
    # print('###Sample collection protocol')
    sc_protocol = SampleCollectionProtocol(name="DMA D. magna pooled culture",
                             description="9 geneticaly distinct strains of D.magna "
                                         "pooled together to form "
                                         "one representative sample",
                             version=1,
                             code_field="D-CULT",
                                           public=True)
    sc_protocol.save(using=db_alias)

    sc_protocol = SampleCollectionProtocol(name="NA",
                                           description="Sample collection not applicable",
                                           version=1,
                                           code_field="NA",
                                           public=True)
    sc_protocol.save(using=db_alias)


    #============================================
    # Liquid Phase extraction (DMA)
    #============================================
    lpe_protocol = ExtractionProtocol(name="NA",
                                      description="NA",
                                      version=0,
                                      code_field="NA",
                                      extractiontype=ExtractionType.objects.filter(type='NA')[0],
                                      public=True
                                       )
    lpe_protocol.save(using=db_alias)

    lpe_protocol = ExtractionProtocol(name="DMA D. magna apolar extraction",
                                      description="Deep Metabolome Annotation Apolar"
                                                   "extraction for Daphnia magna",
                                      version=1,
                                      code_field="D-APOL",
                                      extractiontype=ExtractionType.objects.filter(
                                          type='Apolar')[0],
                                      postextraction="90:10 (v/v) water:acetonitrile",
                                      public=True
                                      )
    lpe_protocol.save(using=db_alias)

    lpe_protocol = ExtractionProtocol(name="DMA D. magna polar extraction ",
                                      description="Deep Metabolome Annotation "
                                                  "polar extraction for Daphnia magna",
                                      version=1,
                                      code_field="D-POL",
                                      extractiontype=ExtractionType.objects.filter(
                                          type='Polar')[0],
                                      postextraction="90:10 (v/v) water:acetonitrile",
                                      public=True
                                      )
    lpe_protocol.save(using=db_alias)

    #============================================
    # Sold phase extraction (DMA)
    #============================================
    # print('###SPE')
    spe_protocol = SpeProtocol(name="NA",
                               description="",
                               version=1,
                               code_field="NA",
                               public=True)
    spe_protocol.save(using=db_alias)


    spe_protocol = SpeProtocol(name="DMA D. magna Weak anion-exchange",
                               description="",
                               version=1,
                               code_field="D-WAX",
                               spetype=SpeType.objects.filter(type='Ion exchange SPE')[0],
                               public=True)
    spe_protocol.save(using=db_alias)


    spe_protocol = SpeProtocol(name="DMA D. magna Weak cation-exchange",
                               description="",
                               version=1,
                               code_field="D-WCX",
                               spetype=SpeType.objects.filter(type='Ion exchange SPE')[0],
                               public=True)
    spe_protocol.save(using=db_alias)


    spe_protocol = SpeProtocol(name="DMA D. magna Aminopropyl",
                               description="",
                               version=1,
                               code_field="D-AMP", # type to update
                               spetype=SpeType.objects.filter(type='Ion exchange SPE')[0],
                               public=True)
    spe_protocol.save(using=db_alias)

    spe_protocol = SpeProtocol(name="DMA D. magna C18",
                               description="",
                               version=1,
                               code_field="D-C18", # type to update
                               spetype=SpeType.objects.filter(type='Ion exchange SPE')[0],
                               public=True)
    spe_protocol.save(using=db_alias)


    #============================================
    # Chromatography (DMA)
    #============================================
    lc_protocol = ChromatographyProtocol(name="NA",
                                         description="",
                                         version=1,
                                         code_field="NA",
                                         public=True
                                         )
    lc_protocol.save(using=db_alias)

    lc_protocol = ChromatographyProtocol(name="DMA D. magna Syncronis phenyl ",
                                         description="",
                                         version=1,
                                         code_field="D-PHE",
                                         chromatographytype=ChromatographyType.objects.filter(
                                             type='Reversed phase chromatography')[0],
                                         public=True
                                         )
    lc_protocol.save(using=db_alias)

    lc_protocol = ChromatographyProtocol(name="DMA D. magna Syncronis C18",
                                         description="",
                                         version=1,
                                         code_field="D-C18",
                                         chromatographytype=ChromatographyType.objects.filter(
                                             type='Reversed phase chromatography')[0],
                                         public=True
                                         )
    lc_protocol.save(using=db_alias)


    lc_protocol = ChromatographyProtocol(name="DMA D. magna Accucore C30",
                                         description="",
                                         version=1,
                                         code_field="D-C30",
                                         chromatographytype=ChromatographyType.objects.filter(
                                             type='Reversed phase chromatography')[0],
                                         public=True
                                         )
    lc_protocol.save(using=db_alias)

    lc_protocol = ChromatographyProtocol(name="DMA D. magna Accucore Amide",
                                         description="",
                                         version=1,
                                         code_field="D-AMD",
                                         chromatographytype=ChromatographyType.objects.filter(
                                             type='HILIC')[0],
                                         public=True
                                         )
    lc_protocol.save(using=db_alias)

    
    #============================================
    # Measurements (DMA)
    #============================================
    # print('###Meas')
    # Measurement types
    m_protocol = MeasurementProtocol(name="NA",
                                     description="",
                                     version=0,
                                     code_field="NA",
                                     public=True

                                     )
    m_protocol.save(using=db_alias)

    m_protocol = MeasurementProtocol(name="DMA D. magna QE LC-MS",
                                     description="Liquid chromatography mass spectrometry"
                                                 "measurements "
                                                 "with Q Exactive for DMA D. magna",
                                     version=1,
                                     code_field="D-LCMS",
                                     measurementtechnique=MeasurementTechnique.objects.filter(
                                         type='LC-MS')[0],
                                     public=True
                                     )
    m_protocol.save(using=db_alias)
    print(OntologyTerm.objects.filter(short_form='CHMO_0000575'))
    print(OntologyTerm.objects.filter(short_form='MS_1001911'))
    m_protocol.ontologyterm.add(OntologyTerm.objects.filter(short_form='MS_1001911')[0])


    m_protocol = MeasurementProtocol(name="DMA D. magna QE LC-MSMS",
                                     description="Liquid chromatography tandem mass spectrometry"
                                                 "measurements "
                                                 "with Q Exactive for DMA D. magna",
                                     version=1,
                                     code_field="D-LCMSMS",
                                     measurementtechnique=MeasurementTechnique.objects.filter(
                                         type='LC-MSMS')[0],
                                     public=True
                                     )
    m_protocol.save(using=db_alias)
    m_protocol.ontologyterm.add(OntologyTerm.objects.filter(short_form='MS_1001911')[0])
    m_protocol.ontologyterm.add(OntologyTerm.objects.filter(short_form='CHMO_0000575')[0])

    m_protocol = MeasurementProtocol(name="DMA D. magna Elite DI-MS",
                                     description="Direct infusion mass spectrometry using "
                                                 "Obitrap Elite for "
                                                 "DMA D. magna",
                                     version=1,
                                     code_field="D-DIMS",
                                     measurementtechnique=MeasurementTechnique.objects.filter(
                                         type='DI-MS')[0],
                                     public=True
                                     )
    m_protocol.save(using=db_alias)
    m_protocol.ontologyterm.add(OntologyTerm.objects.filter(short_form='MS_1001910')[0])


    m_protocol = MeasurementProtocol(name="DMA D. magna Elite DI-MSn",
                                     description="Direct infusion mass spectrometry with "
                                                 "fragmentation using Obitrap Elite for DMA "
                                                 "D. magna",
                                     version=1,
                                     code_field="D-DIMSn",
                                     measurementtechnique=MeasurementTechnique.objects.filter(
                                         type='DI-MSn')[0],
                                     public=True
                                     )
    m_protocol.save(using=db_alias)
    m_protocol.ontologyterm.add(OntologyTerm.objects.filter(short_form='MS_1001910')[0])
    m_protocol.ontologyterm.add(OntologyTerm.objects.filter(short_form='CHMO_0000575')[0])


    #######################################
    # Add Study sample (DMA)
    #######################################
    ss1 = StudySample(sampletype=SampleType.objects.filter(type='ANIMAL')[0],
                      sample_name='DAPH',
                      study_id=study.id,
                      organism=Organism.objects.filter(name='Daphnia magna')[0],
                      organism_part=OrganismPart.objects.filter(name='Whole Organism')[0],
                      public=True)
    ss2 = StudySample(sampletype=SampleType.objects.filter(type='COMPOUND')[0],
                      sample_name='COMPOUND',
                      study_id=study.id, public=True)
    ss3 = StudySample(sampletype=SampleType.objects.filter(type='BLANK')[0],
                      sample_name='BLANK', study_id=study.id,
                      public=True)

    ss4 = StudySample(sampletype=SampleType.objects.filter(type='EQUIL_BLANK')[0],
                      sample_name='EQUIL_BLANK',
                      study_id=study.id,
                      public=True)

    ss5 = StudySample(sampletype=SampleType.objects.filter(type='EQUIL')[0], sample_name='EQUIL',
                      study_id=study.id,
                      organism=Organism.objects.filter(name='Daphnia magna')[0],
                      organism_part=OrganismPart.objects.filter(name='Whole Organism')[0],
                      public=True)

    ss6 = StudySample(sampletype=SampleType.objects.filter(type='MISC')[0], sample_name='MISC',
                      study_id=study.id,
                      public=True)

    ss1.save(using=db_alias)
    ss2.save(using=db_alias)
    ss3.save(using=db_alias)
    ss4.save(using=db_alias)
    ss5.save(using=db_alias)
    ss6.save(using=db_alias)

    #############################################################################################
    # Spectral matching annotation details
    #############################################################################################
    maa = MetaboliteAnnotationApproach(name='Spectral matching')
    maa.save(using=db_alias)

    st = ScoreType(name='dpc', description='Dot product cosine',
                   metaboliteannotationapproach=maa)
    st.save(using=db_alias)

    st = ScoreType(name='rdpc', description='Reverse dot product cosine',
                   metaboliteannotationapproach=maa)
    st.save(using=db_alias)

    st = ScoreType(name='cdpc', description='Composite dot product cosine',
                   metaboliteannotationapproach=maa)
    st.save(using=db_alias)

    st = ScoreType(name='mcount', description='Count of matching peaks',
                   metaboliteannotationapproach=maa)
    st.save(using=db_alias)

    st = ScoreType(name='allcount', description='Count of all peaks',
                   metaboliteannotationapproach=maa)
    st.save(using=db_alias)

    st = ScoreType(name='mpercent', description='Percentage of all peaks',
                   metaboliteannotationapproach=maa)
    st.save(using=db_alias)

    st = ScoreType(name='rtdiff', description='retention time difference',
                   metaboliteannotationapproach=maa)
    st.save(using=db_alias)


    #############################################################################################
    # Metfrag annotation details
    #############################################################################################
    maa = MetaboliteAnnotationApproach(name='Metfrag')
    maa.save(using=db_alias)

    st = ScoreType(name='OfflineMetFusionScore', description='Offline MetFusion Score',
                   metaboliteannotationapproach=maa)
    st.save(using=db_alias)

    st = ScoreType(name='SuspectListScore', description='Suspect List Score',
                   metaboliteannotationapproach=maa)
    st.save(using=db_alias)

    st = ScoreType(name='FragmenterScore', description='Fragmeter Score',
                   metaboliteannotationapproach=maa)
    st.save(using=db_alias)

    st = ScoreType(name='Score',
                   description='Final score from Metfrag (weighted internally within Metfrag)',
                   metaboliteannotationapproach=maa)
    st.save(using=db_alias)

    st = ScoreType(name='NoExplPeaks', description='NoExplPeaks',
                   metaboliteannotationapproach=maa)
    st.save(using=db_alias)

    st = ScoreType(name='NumberPeaksUsed', description='NumberPeaksUsed',
                   metaboliteannotationapproach=maa)
    st.save(using=db_alias)

    st = ScoreType(name='MaximumTreeDepth', description='MaximumTreeDepth',
                   metaboliteannotationapproach=maa)
    st.save(using=db_alias)

    dt = DetailType(name='adduct', description='adduct', metaboliteannotationapproach=maa)
    dt.save(using=db_alias)

    dt = DetailType(name='ExplPeaks', description='ExplPeaks', metaboliteannotationapproach=maa)
    dt.save(using=db_alias)

    dt = DetailType(name='FormulasOfExplPeaks', description='FormulasOfExplPeaks',
                    metaboliteannotationapproach=maa)
    dt.save(using=db_alias)

    dt = DetailType(name='FragmenterScore_Values', description='FragmenterScore_Values',
                    metaboliteannotationapproach=maa)
    dt.save(using=db_alias)

    dt = DetailType(name='MaximumTreeDepth', description='MaximumTreeDepth',
                    metaboliteannotationapproach=maa)
    dt.save(using=db_alias)

    dt = DetailType(name='MolecularFormula', description='MolecularFormula',
                    metaboliteannotationapproach=maa)
    dt.save(using=db_alias)

    dt = DetailType(name='MonoisotopicMass', description='MonoisotopicMass',
                    metaboliteannotationapproach=maa)
    dt.save(using=db_alias)

    #############################################################################################
    # Sirius Annotation details
    #############################################################################################
    maa = MetaboliteAnnotationApproach(name='SIRIUS CSI:FingerID')
    maa.save(using=db_alias)

    st = ScoreType(name='rank', description='rank',
                   metaboliteannotationapproach=maa)
    st.save(using=db_alias)

    st = ScoreType(name='score', description='score',
                   metaboliteannotationapproach=maa)
    st.save(using=db_alias)

    st = ScoreType(name='bounded_score', description='bounded score',
                   metaboliteannotationapproach=maa)
    st.save(using=db_alias)


    dt = DetailType(name='links',
                    description='Relevant links for compound annotation (generated from SIRIUS '
                                              'CSI:FingerID',
                    metaboliteannotationapproach=maa)
    dt.save(using=db_alias)

    dt = DetailType(name='adduct', description='Adduct used for lookup',
                    metaboliteannotationapproach=maa)
    dt.save(using=db_alias)


    #############################################################################################
    # MS1 Lookup details
    #############################################################################################
    maa = MetaboliteAnnotationApproach(name='MS1 Lookup')
    maa.save(using=db_alias)

    st = ScoreType(name='score', description='score - default is set to 1',
                   metaboliteannotationapproach=maa)
    st.save(using=db_alias)

    dt = DetailType(name='adduct', description='Adduct used for lookup',
                    metaboliteannotationapproach=maa)

    dt.save(using=db_alias)



    #===================================================================================================================
    # Other examples
    #===================================================================================================================
    #######################################################################################################
    # Setup ISA backbone
    #######################################################################################################
    # print('###ISA backbone')
    # investigation1 = Investigation(name='Example Investigation 1', description='Example investigation for MOGI tutorial. '
    #                                                         'Data derived from the MetaboLights study '
    #                                                         'MTBLS144. https://www.ebi.ac.uk/metabolights/MTBLS144',
    #                                slug='TEST1', public=True)
    # investigation1.save(using=db_alias)
    #
    # study1 = Study(investigation=investigation1, name='MTBLS144-TEST-CASE',
    #               description='Phytoplankton are significant producers of '
    #                   'dissolved organic matter (DOM) in marine ecosystems but '
    #                   'the identity and dynamics of this DOM remain poorly constrained. '
    #                   'Knowledge on the identity and dynamics of DOM are crucial for understanding '
    #                   'the molecular-level reactions at the base of the global carbon cycle. '
    #                   'Here we apply emerging analytical and computational tools from metabolomics '
    #                   'to investigate the composition of DOM produced by the centric diatom '
    #                   'Thalassiosira pseudonana. We assessed both intracellular metabolites within T. pseudonana '
    #                   '(the endo-metabolome) and extracellular metabolites released by T. pseudonana '
    #                   '(the exo-metabolome). The intracellular metabolites had a more variable composition than '
    #                   'the extracellular metabolites. We putatively identified novel compounds not previously '
    #                   'associated with T. pseudonana as well as compounds that have previously been identified '
    #                   'within T. pseudonana’s metabolic capacity (e.g. dimethylsulfoniopropionate and degradation '
    #                   'products of chitin). The resulting information will provide the basis for '
    #                   'future experiments to assess the impact of T. pseudonana on the composition of '
    #                   'dissolved organic matter in marine environments.', public=True)
    # study1.save()
    #
    # assay1_pos = Assay(name='Positive metabolic profiling (FT-ICR)', study=study1, public=True)
    # assay1_pos.save(using=db_alias)
    #
    # investigation2 = Investigation(name='Example Investigation 2',
    #                                description='Example investigation for MOGI tutorial. Data derived from'
    #                                            'analysis performed at the University of Birmingham',
    #                                slug='TEST2', public=True)
    # investigation2.save(using=db_alias)
    #
    # study2 = Study(investigation=investigation2, name='IN-HOUSE-MOGI-TEST-CASE',
    #               description='Example LC-MS/MS dataset to test MOGI', public=True)
    # study2.save()
    #
    # assay2_pos = Assay(name='Positive metabolic profiling (Q-Exactive)', study=study2, public=True)
    # assay2_pos.save(using=db_alias)
    #
    #
    #
    # #######################################
    # # Add study samples
    # #######################################
    # ss1 = StudySample(sampletype=SampleType.objects.filter(type='ANIMAL')[0],
    #                   sample_name='BOVINE_SERUM',
    #                   study_id=study2.id,
    #                   organism=Organism.objects.filter(name='Bos taurus')[0],
    #                   organism_part=OrganismPart.objects.filter(name='serum')[0],
    #                   public=True)
    # ss2 = StudySample(sampletype=SampleType.objects.filter(type='BLANK')[0], sample_name='BLANK', study_id=study2.id,
    #                   public=True)
    #
    # ss1.save(using=db_alias)
    # ss2.save(using=db_alias)
    #
    # # #######################################################################################################
    # # Protocols
    # #######################################################################################################
    # #============================================
    # # Sample collection
    # #============================================
    # # print('###Sample collection protocol')
    # sc_protocol1 = SampleCollectionProtocol(name="Diatom culturing",
    #                          description="The diatom Thalassiosira pseudonana (CCMP 1335) was cultured "
    #                                      "axenically in a modified version of L1 media with Turks Island Salts. "
    #                                      "The cultures were incubated under a 12 h:12 h light:dark cycle. Cells were "
    #                                      "collected 6 h into the light cycle on days 0, 1, 3, 7, 8, and 10.",
    #                          version=1,
    #                          code_field="DIATOM", public=True)
    # sc_protocol1.save(using=db_alias)
    #
    # sc_protocol2 = SampleCollectionProtocol(name="Bovine serum collection",
    #                          description="Bovine serum sample was supplied from Sigma",
    #                          version=1,
    #                          code_field="B-SERUM", public=True)
    # sc_protocol2.save(using=db_alias)
    #
    #
    # # Liquid Phase Extraction protocol
    # lpe_protocol1 = ExtractionProtocol(name="DOM-acetonitrile",
    #                                   description="""The intracellular metabolites were extracted using a previously described method [1]. Briefly, 1.5 ml samples were centrifuged at 16,000 x g at 4 ºC for 30 minutes and the supernatant discarded. The resulting cell pellet was extracted three times with ice-cold extraction solvent (acetonitrile:methanol:water with 0.1 M formic acid, 40:40:20). The combined extracts were neutralized with 0.1 M ammonium hydroxide, dried in a vacufuge, and then re-dissolved in 1 ml of 90:10 (v/v) water:acetonitrile for analysis on the mass spectrometer.
    #                                                  Prior to sampling the extracellular metabolites, the cells were removed by gentle vacuum filtration through 0.2 µm Omnipore filters (hydrophilic PTFE membranes, Millipore). [2] have observed filtration may release intracellular metabolites into the exometabolome, and this potential bias must be considered in the discussion of our results.
    #                                                 Ref:
    #                                                 [1] Rabinowitz JD, Kimball E. Acidic acetonitrile for cellular metabolome extraction from Escherichia coli. Anal Chem. 2007 Aug 15;79(16):6167-73. PMID: 17630720.
    #                                                 [2] Barofsky A, Vidoudez C, Pohnert G. Metabolic profiling reveals growth stage variability in diatom exudates. Limnology and Oceanography: Methods. June 2009, 7(6), 382–390.
    #                                               """,
    #                                   version=1,
    #                                   code_field="DOM",
    #                                   extractiontype=lpe_type2,
    #                                   postextraction="90:10 (v/v) water:acetonitrile",
    #                                   public=True
    #                                   )
    # lpe_protocol1.save(using=db_alias)
    #
    #
    # lpe_protocol2 = ExtractionProtocol(name="Bovine serum dilution",
    #                                   description="""
    #                                   re-suspend in 100% of A-Phase solution - 0.1% v/v formic acid in 95:5% v/v
    #                                   water/methanol - vortexed for 60 seconds and centrifuged at 15000 rpm for 10 minutes
    #                                   """,
    #                                   version=1,
    #                                   code_field="B-SERUM",
    #                                   extractiontype=lpe_type3,
    #                                   postextraction="90:10 (v/v) water:acetonitrile",
    #                                   public=True
    #                                   )
    # lpe_protocol2.save(using=db_alias)
    #
    # spe_protocol1 = SpeProtocol(name="SPE-DOM (PPL)",
    #                                   description="The acidified filtrate was extracted using solid phase extraction with PPL cartridges (Varian Bond Elut PPL cartridges) as previously described [3]. After eluting with methanol, the extracts were dried in a vacufuge, and then re-dissolved in 1 ml 90:10 water:acetonitrile prior to analysis. [1] Dittmar T, Koch B, Hertkorn N, Kattner G. A simple and efficient method for the solid-phase extraction of dissolved organic matter (SPE-DOM) from seawater. Limnology and Oceanography: Methods. June 2008, 6(6), 230–235",
    #                                   version=1,
    #                                   code_field="DOM",
    #                                   spetype=spe_type4,
    #                             public=True
    #                                   )
    # spe_protocol1.save(using=db_alias)
    # # spe_protocol2 = SpeProtocol(name="NA",
    # #                             description="Not applicable",
    # #                             code_field="NA"
    # #                             )
    # # spe_protocol2.save(using=db_alias)
    #
    # lc_protocol1 = ChromatographyProtocol(name="Synergi Fusion RP",
    #                                   description="LC separation was performed on a Synergi Fusion reversed-phase column using a binary gradient with solvent A being water with 0.1% formic acid and solvent B being acetonitrile with 0.1% formic acid. Samples were eluted at 250 µl/min with the following gradient: hold at 5% B for 0-2 min, ramp from 5 to 65% B between 2 and 20 min, ramp from 65 to 100% B between 20 and 25 min, hold at 100% B from 25-32 min, and then ramp back to 5% B between 32 and 32.5 min for re-equilibration (32.5-40 min).",
    #                                   version=1,
    #                                   code_field="SFRP",
    #                                   chromatographytype=lc_type1,
    #                                   public=True
    #                                   )
    # lc_protocol1.save(using=db_alias)
    #
    # lc_protocol2 = ChromatographyProtocol(name="Syncronis aQ",
    #                                   description="""
    #                                               Liquid chromatography was performed with A-phase consisting of 0.1%
    #                                               v/v formic acid in 95:5% v/v water/methanol. B-phase consisted of
    #                                               0.1% v/v formic acid in 95:5% v/v methanol/water. The column was a
    #                                               Syncronis aQ (1.7 um, 2.1 x 100 mm), with a flow rate: 0.4 mL/min,
    #                                               column temperature: 40 °C., and injection volume: 10 uL""",
    #                                   version=1,
    #                                   code_field="SQ",
    #                                   chromatographytype=lc_type1,
    #                                   public=True
    #                                   )
    # lc_protocol2.save(using=db_alias)
    #
    #
    # m_protocol1 = MeasurementProtocol(name="FT-ICR",
    #                                  description="All metabolomics analyses were conducted using liquid chromatography (LC) coupled by electrospray ionization to a hybrid linear ion trap - Fourier-transform ion cyclotron resonance (FT-ICR) mass spectrometer (7T LTQ FT Ultra, Thermo Scientific) Both full MS and MS/MS data were collected. The MS scan was performed in the FT-ICR cell from m/z 100-1000 at 100,000 resolving power (defined at 400 m/z). In parallel to the FT acquisition, MS/MS scans were collected at nominal mass resolution in the ion trap from the two features with the highest peak intensities in each scan. Separate autosampler injections were made for analysis in positive and negative ion modes.",
    #                                  version=1,
    #                                  code_field="FT-ICR",
    #                                  measurementtechnique=m_type2,
    #                                  public=True
    #                                  )
    # m_protocol1.save(using=db_alias)
    # m_protocol1.ontologyterm.add(OntologyTerm.objects.filter(
    #     name='linear quadrupole ion trap Fourier transform ion cyclotron resonance mass spectrometer')[0])
    # m_protocol1.ontologyterm.add(OntologyTerm.objects.filter(short_form='CHMO_0000575')[0])
    #
    # m_protocol2 = MeasurementProtocol(name="Q-Exactive LC-MS",
    #                                  description="Liquid chromatography mass spectrometry measurements "
    #                                              "with Q Exactive for Bovine serum sample",
    #                                  version=1,
    #                                  code_field="QE-LC-MS",
    #                                  measurementtechnique=MeasurementTechnique.objects.filter(type='LC-MS')[0],
    #                                  public=True
    #                                  )
    # m_protocol2.save(using=db_alias)
    # m_protocol2.ontologyterm.add(OntologyTerm.objects.filter(short_form='MS_1001911')[0])
    #
    # m_protocol3 = MeasurementProtocol(name="Q-Exactive LC-MSMS with Q Exactive for DMA D. magna",
    #                                  version=1,
    #                                  code_field="QE-LC-MSMS",
    #                                  measurementtechnique=MeasurementTechnique.objects.filter(type='LC-MSMS')[0],
    #                                  public=True
    #                                  )
    # m_protocol3.save(using=db_alias)
    # m_protocol3.ontologyterm.add(OntologyTerm.objects.filter(short_form='MS_1001911')[0])
    # m_protocol3.ontologyterm.add(OntologyTerm.objects.filter(short_form='CHMO_0000575')[0])


def reverse_func(apps, schema_editor):
    ##########################
    # Reverse func not currently implemented
    ############################
    print("Reverse func not currently implemented")

class Migration(migrations.Migration):
    dependencies = [
        ('mogi', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_func),
    ]

