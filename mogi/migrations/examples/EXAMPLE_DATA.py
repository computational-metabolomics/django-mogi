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


    Organism = apps.get_model("mogi", "Organism")
    OrganismPart = apps.get_model("mogi", "OrganismPart")
    SampleType = apps.get_model("mogi", "SampleType")
    MeasurementTechnique = apps.get_model("mogi", "MeasurementTechnique")

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


    #######################################################################################################
    # Setup ISA backbone
    #######################################################################################################
    # print('###ISA backbone')
    investigation1 = Investigation(name='Example Investigation 1', description='Example investigation for MOGI tutorial. '
                                                            'Data derived from the MetaboLights study '
                                                            'MTBLS144. https://www.ebi.ac.uk/metabolights/MTBLS144',
                                   slug='TEST1', public=True)
    investigation1.save(using=db_alias)

    study1 = Study(investigation=investigation1, name='MTBLS144-TEST-CASE',
                  description='Phytoplankton are significant producers of '
                      'dissolved organic matter (DOM) in marine ecosystems but '
                      'the identity and dynamics of this DOM remain poorly constrained. '
                      'Knowledge on the identity and dynamics of DOM are crucial for understanding '
                      'the molecular-level reactions at the base of the global carbon cycle. '
                      'Here we apply emerging analytical and computational tools from metabolomics '
                      'to investigate the composition of DOM produced by the centric diatom '
                      'Thalassiosira pseudonana. We assessed both intracellular metabolites within T. pseudonana '
                      '(the endo-metabolome) and extracellular metabolites released by T. pseudonana '
                      '(the exo-metabolome). The intracellular metabolites had a more variable composition than '
                      'the extracellular metabolites. We putatively identified novel compounds not previously '
                      'associated with T. pseudonana as well as compounds that have previously been identified '
                      'within T. pseudonana’s metabolic capacity (e.g. dimethylsulfoniopropionate and degradation '
                      'products of chitin). The resulting information will provide the basis for '
                      'future experiments to assess the impact of T. pseudonana on the composition of '
                      'dissolved organic matter in marine environments.', public=True)
    study1.save()

    assay1_pos = Assay(name='Positive metabolic profiling (FT-ICR)', study=study1, public=True)
    assay1_pos.save(using=db_alias)

    investigation2 = Investigation(name='Example Investigation 2',
                                   description='Example investigation for MOGI tutorial. Data derived from'
                                               'analysis performed at the University of Birmingham',
                                   slug='TEST2', public=True)
    investigation2.save(using=db_alias)

    study2 = Study(investigation=investigation2, name='IN-HOUSE-MOGI-TEST-CASE',
                  description='Example LC-MS/MS dataset to test MOGI', public=True)
    study2.save()

    assay2_pos = Assay(name='Positive metabolic profiling (Q-Exactive)', study=study2, public=True)
    assay2_pos.save(using=db_alias)



    #######################################
    # Add study samples
    #######################################
    ss1 = StudySample(sampletype=SampleType.objects.filter(type='ANIMAL')[0],
                      sample_name='BOVINE_SERUM',
                      study_id=study2.id,
                      organism=Organism.objects.filter(name='Bos taurus')[0],
                      organism_part=OrganismPart.objects.filter(name='serum')[0],
                      public=True)
    ss2 = StudySample(sampletype=SampleType.objects.filter(type='BLANK')[0], sample_name='BLANK', study_id=study2.id,
                      public=True)

    ss1.save(using=db_alias)
    ss2.save(using=db_alias)

    #######################################################################################################
    # Protocols
    #######################################################################################################
    #============================================
    # Sample collection
    #============================================
    # print('###Sample collection protocol')
    sc_protocol1 = SampleCollectionProtocol(name="Diatom culturing",
                             description="The diatom Thalassiosira pseudonana (CCMP 1335) was cultured "
                                         "axenically in a modified version of L1 media with Turks Island Salts. "
                                         "The cultures were incubated under a 12 h:12 h light:dark cycle. Cells were "
                                         "collected 6 h into the light cycle on days 0, 1, 3, 7, 8, and 10.",
                             version=1,
                             code_field="DIATOM", public=True)
    sc_protocol1.save(using=db_alias)

    sc_protocol2 = SampleCollectionProtocol(name="Bovine serum collection",
                             description="Bovine serum sample was supplied from Sigma",
                             version=1,
                             code_field="B-SERUM", public=True)
    sc_protocol2.save(using=db_alias)


    # Liquid Phase Extraction protocol
    lpe_protocol1 = ExtractionProtocol(name="DOM-acetonitrile",
                                      description="""The intracellular metabolites were extracted using a previously described method [1]. Briefly, 1.5 ml samples were centrifuged at 16,000 x g at 4 ºC for 30 minutes and the supernatant discarded. The resulting cell pellet was extracted three times with ice-cold extraction solvent (acetonitrile:methanol:water with 0.1 M formic acid, 40:40:20). The combined extracts were neutralized with 0.1 M ammonium hydroxide, dried in a vacufuge, and then re-dissolved in 1 ml of 90:10 (v/v) water:acetonitrile for analysis on the mass spectrometer. 
                                                     Prior to sampling the extracellular metabolites, the cells were removed by gentle vacuum filtration through 0.2 µm Omnipore filters (hydrophilic PTFE membranes, Millipore). [2] have observed filtration may release intracellular metabolites into the exometabolome, and this potential bias must be considered in the discussion of our results. 
                                                    Ref:
                                                    [1] Rabinowitz JD, Kimball E. Acidic acetonitrile for cellular metabolome extraction from Escherichia coli. Anal Chem. 2007 Aug 15;79(16):6167-73. PMID: 17630720.
                                                    [2] Barofsky A, Vidoudez C, Pohnert G. Metabolic profiling reveals growth stage variability in diatom exudates. Limnology and Oceanography: Methods. June 2009, 7(6), 382–390.
                                                  """,
                                      version=1,
                                      code_field="DOM",
                                      extractiontype=lpe_type2,
                                      postextraction="90:10 (v/v) water:acetonitrile",
                                      public=True
                                      )
    lpe_protocol1.save(using=db_alias)


    lpe_protocol2 = ExtractionProtocol(name="Bovine serum dilution",
                                      description="""
                                      re-suspend in 100% of A-Phase solution - 0.1% v/v formic acid in 95:5% v/v 
                                      water/methanol - vortexed for 60 seconds and centrifuged at 15000 rpm for 10 minutes
                                      """,
                                      version=1,
                                      code_field="B-SERUM",
                                      extractiontype=lpe_type3,
                                      postextraction="90:10 (v/v) water:acetonitrile",
                                      public=True
                                      )
    lpe_protocol2.save(using=db_alias)

    spe_protocol1 = SpeProtocol(name="SPE-DOM (PPL)",
                                      description="The acidified filtrate was extracted using solid phase extraction with PPL cartridges (Varian Bond Elut PPL cartridges) as previously described [3]. After eluting with methanol, the extracts were dried in a vacufuge, and then re-dissolved in 1 ml 90:10 water:acetonitrile prior to analysis. [1] Dittmar T, Koch B, Hertkorn N, Kattner G. A simple and efficient method for the solid-phase extraction of dissolved organic matter (SPE-DOM) from seawater. Limnology and Oceanography: Methods. June 2008, 6(6), 230–235",
                                      version=1,
                                      code_field="DOM",
                                      spetype=spe_type4,
                                public=True
                                      )
    spe_protocol1.save(using=db_alias)
    # spe_protocol2 = SpeProtocol(name="NA",
    #                             description="Not applicable",
    #                             code_field="NA"
    #                             )
    # spe_protocol2.save(using=db_alias)

    lc_protocol1 = ChromatographyProtocol(name="Synergi Fusion RP",
                                      description="LC separation was performed on a Synergi Fusion reversed-phase column using a binary gradient with solvent A being water with 0.1% formic acid and solvent B being acetonitrile with 0.1% formic acid. Samples were eluted at 250 µl/min with the following gradient: hold at 5% B for 0-2 min, ramp from 5 to 65% B between 2 and 20 min, ramp from 65 to 100% B between 20 and 25 min, hold at 100% B from 25-32 min, and then ramp back to 5% B between 32 and 32.5 min for re-equilibration (32.5-40 min).",
                                      version=1,
                                      code_field="SFRP",
                                      chromatographytype=lc_type1,
                                      public=True
                                      )
    lc_protocol1.save(using=db_alias)

    lc_protocol2 = ChromatographyProtocol(name="Syncronis aQ",
                                      description="""
                                                  Liquid chromatography was performed with A-phase consisting of 0.1% 
                                                  v/v formic acid in 95:5% v/v water/methanol. B-phase consisted of 
                                                  0.1% v/v formic acid in 95:5% v/v methanol/water. The column was a 
                                                  Syncronis aQ (1.7 um, 2.1 x 100 mm), with a flow rate: 0.4 mL/min, 
                                                  column temperature: 40 °C., and injection volume: 10 uL""",
                                      version=1,
                                      code_field="SQ",
                                      chromatographytype=lc_type1,
                                      public=True
                                      )
    lc_protocol2.save(using=db_alias)


    m_protocol1 = MeasurementProtocol(name="FT-ICR",
                                     description="All metabolomics analyses were conducted using liquid chromatography (LC) coupled by electrospray ionization to a hybrid linear ion trap - Fourier-transform ion cyclotron resonance (FT-ICR) mass spectrometer (7T LTQ FT Ultra, Thermo Scientific) Both full MS and MS/MS data were collected. The MS scan was performed in the FT-ICR cell from m/z 100-1000 at 100,000 resolving power (defined at 400 m/z). In parallel to the FT acquisition, MS/MS scans were collected at nominal mass resolution in the ion trap from the two features with the highest peak intensities in each scan. Separate autosampler injections were made for analysis in positive and negative ion modes.",
                                     version=1,
                                     code_field="FT-ICR",
                                     measurementtechnique=m_type2,
                                     public=True
                                     )
    m_protocol1.save(using=db_alias)
    m_protocol1.ontologyterm.add(OntologyTerm.objects.filter(
        name='linear quadrupole ion trap Fourier transform ion cyclotron resonance mass spectrometer')[0])
    m_protocol1.ontologyterm.add(OntologyTerm.objects.filter(short_form='CHMO_0000575')[0])

    m_protocol2 = MeasurementProtocol(name="Q-Exactive LC-MS",
                                     description="Liquid chromatography mass spectrometry measurements "
                                                 "with Q Exactive for Bovine serum sample",
                                     version=1,
                                     code_field="QE-LC-MS",
                                     measurementtechnique=MeasurementTechnique.objects.filter(type='LC-MS')[0],
                                     public=True
                                     )
    m_protocol2.save(using=db_alias)
    m_protocol2.ontologyterm.add(OntologyTerm.objects.filter(short_form='MS_1001911')[0])

    m_protocol3 = MeasurementProtocol(name="Q-Exactive LC-MSMS with Q Exactive for DMA D. magna",
                                     version=1,
                                     code_field="QE-LC-MSMS",
                                     measurementtechnique=MeasurementTechnique.objects.filter(type='LC-MSMS')[0],
                                     public=True
                                     )
    m_protocol3.save(using=db_alias)
    m_protocol3.ontologyterm.add(OntologyTerm.objects.filter(short_form='MS_1001911')[0])
    m_protocol3.ontologyterm.add(OntologyTerm.objects.filter(short_form='CHMO_0000575')[0])


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

