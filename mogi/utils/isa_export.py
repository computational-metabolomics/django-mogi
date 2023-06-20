# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import zipfile
import os
import json
from django.contrib.auth.models import User
from django.db.models import F
from django import forms
from collections import defaultdict
from mzml2isa import mzml
import tempfile
import shutil
from mogi.models.models_compounds import Compound
from mogi.models.models_isa import Investigation, MFile
from isatools import model as itm
from isatools import isatab
from isatools.isajson import ISAJSONEncoder
from django.core.files.base import ContentFile, File
import six
import pandas as pd

def init_ontology_sources(itm_i):
    ontology_sources = [
                        itm.OntologySource(name='CHMO', file='http://purl.obolibrary.org/obo/chmo.owl', description="Chemical Methods Ontology"),
                        itm.OntologySource(name='MS', file=' http://purl.obolibrary.org/obo/ms.owl', description="Mass spectrometry ontology"),                       
                        itm.OntologySource(name='SIO', file=' http://semanticscience.org/ontology/sio.owl', description="Semanticscience Integrated Ontology"),                       
                        itm.OntologySource(name='OBI', file='http://purl.obolibrary.org/obo/obi.owl', description="Ontology for Biomedical Investigations"),
                        itm.OntologySource(name='CHEBI', file='http://purl.obolibrary.org/obo/chebi.owl', description="Chemical Entities of Biological Interest"),
                        itm.OntologySource(name='NCIT', file='http://purl.obolibrary.org/obo/ncit.owl', description="NCI Thesaurus OBO Edition"),
                        itm.OntologySource(name='NCBITAXON', file='http://purl.obolibrary.org/obo/ncit.owl', description="NCI Thesaurus OBO Edition"),
                        itm.OntologySource(name='CHEMINF', file='http://semanticchemistry.github.io/semanticchemistry/ontology/cheminf.owl', description="chemical information ontology (cheminf) - information entities about chemical entities"),
                        itm.OntologySource(name='AFO', file='http://purl.obolibrary.org/obo/afo.owl', description="Allotrope Merged Ontology Suite"),
                        itm.OntologySource(name='OMIT', file=' http://purl.obolibrary.org/obo/omit.owl', description="Ontology for MIRNA Target"), 
                        ]
    itm_i.ontology_source_references.extend(ontology_sources)

    return itm_i


def extract_parameter_value_mzml(mzmlf, name, itm_pparams, itm_i, section='meas', value=False):
    if not value:
        return(itm.ParameterValue(itm_pparams[section][name], 
                              itm.OntologyAnnotation(term=mzmlf.metadata[name]['name'],
                                                     term_source=check_ontology_source(itm_i, mzmlf.metadata[name]['ref']),
                                                     term_accession=mzmlf.metadata[name]['accession']
                                             )))
    else:
        return(itm.ParameterValue(itm_pparams[section][name], mzmlf.metadata[name]['value']))


def check_ontology_source(itm_i, query_source_name):
    ont_source = ''
    for ionts in itm_i.ontology_source_references:
        if ionts.name==query_source_name:
            ont_source=ionts
            break

    if not ont_source:
        ont_source = itm.OntologySource(name=query_source_name)
        itm_i.ontology_source_references.append(ont_source)

    return ont_source


def export_isa_files(investigation_id, metabolights_compat=True, extract_mzml_info=True, export_json=True, export_isatab=True, celery_obj=''):

    if celery_obj:
        celery_obj.update_state(state='RUNNING',
                                            meta={'current': 0, 'total':  100,
                                                  'status': 'Setup of investigation and study files'})
        
    
    
    # Save ISA-Tab zip
    if export_isatab:
        tmpdir = tempfile.mkdtemp()
        isa_temp_dir = os.path.join(tmpdir, 'isa')
        os.makedirs(isa_temp_dir, exist_ok=True)
   

    # Create investigation
    dj_i = Investigation.objects.get(pk=investigation_id)
    itm_i = itm.Investigation(filename="i_investigation.txt")
    itm_i.identifier = "i1"
    itm_i.title = dj_i.name
    itm_i.description = dj_i.description

    itm_i = init_ontology_sources(itm_i)


    ################################################################################################################
    # STUDIES
    ################################################################################################################
    itm_sample_d  = {}  # to traceback from django samples
    for i, dj_s in enumerate(dj_i.study_set.all()):

        itm_s = itm.Study(filename="s_study.txt")
        itm_s.identifier = "s"+str(i)
        itm_s.title = dj_s.name
        itm_s.description = dj_s.description
        itm_s.grant_number = dj_s.grant_number
        itm_s.public_release_date = dj_s.public_release_date.strftime("%Y-%m-%d") if dj_s.public_release_date else ''
        itm_s.submission_date = dj_s.submission_date.strftime("%Y-%m-%d") if dj_s.submission_date else ''


        itm_i.studies.append(itm_s)

        chmo = check_ontology_source(itm_i, 'CHMO')        
        itm_s.design_descriptors.extend([
                            itm.OntologyAnnotation(term_source=chmo,term = "ultra-performance liquid chromatography-mass spectrometry",
                                                   term_accession = "http://purl.obolibrary.org/obo/CHMO_0000715"),
                            itm.OntologyAnnotation(term_source=chmo, term="tandem mass spectrometry",
                                      term_accession="http://purl.obolibrary.org/obo/CHMO_0000575"),
                            itm.OntologyAnnotation(term = "untargeted metabolites"),            
        ])

        ################################################################################################################
        # STUDY SAMPLES
        ################################################################################################################
        #if metabolights_compat:
        material_source = itm.Source(name='DMA source')
        itm_s.sources.append(material_source)

        for j, dj_ss in enumerate(dj_s.studysample_set.all()):
            #if not metabolights_compat:
            #    source = itm.Source(name='{} source'.format(dj_ss.sample_name))
            #    itm_s.sources.append(source)

            # Sample material from the source
            itm_sample = itm.Sample(name=dj_ss.sample_name, derives_from=[material_source])

            #=====================
            # Add organism for sample
            #=====================
            if dj_ss.organism:
                dj_org_ont = dj_ss.organism.ontologyterm
                ont_source = check_ontology_source(itm_i, dj_org_ont.ontology_prefix)

                val = itm.OntologyAnnotation(term=dj_org_ont.name,
                                             term_source=ont_source,
                                             term_accession=dj_org_ont.iri)
            else:

                val = itm.OntologyAnnotation(term='', term_source='', term_accession='')

            char =  itm.Characteristic(category=itm.OntologyAnnotation(term="Organism",
                                                                      term_source= check_ontology_source(itm_i, 'NCIT'),
                                                                      term_accession="http://purl.obolibrary.org/obo/NCIT_C14250"),
                                       value=val)
            itm_sample.characteristics.append(char)

            # =====================
            # Add organism part
            # =====================
            if dj_ss.organism_part:
                dj_org_ont = dj_ss.organism_part.ontologyterm

                source = check_ontology_source(itm_i, dj_org_ont.ontology_prefix)

                val = itm.OntologyAnnotation(term=dj_org_ont.name,
                                             term_source=source,
                                             term_accession=dj_org_ont.iri)


            else:
                val = itm.OntologyAnnotation(term='', term_source='', term_accession='')

            char =  itm.Characteristic(category=itm.OntologyAnnotation(term="Organism part",
                                                                      term_source="NCIT",
                                                                      term_accession="http://purl.obolibrary.org/obo/NCIT_C103199"),
                                      value=val)

            # Add organism part for sample (e.g. foot, eye, leg, whole organism...)
            itm_sample.characteristics.append(char)


            # Potential to add technical replicates (repeat extractions of the same material but
            # to confusing to use for DMA because we have extractions at different points (Liquid Extraction, SPE and
            # Fractionation
            itm_s.samples.append(itm_sample)
            itm_sample_d[dj_ss.id] = itm_sample

        # Create sample collection protocol (we just use 1 for all samples for the time being) but should technically
        # be divided into groups (if resulting ISA-Tab for MetaboLights is the same then we can just leave as is)
        sample_collection_protocol = itm.Protocol(name="sample collection",
                                                    protocol_type=itm.OntologyAnnotation(term="sample collection",))
        itm_s.protocols.append(sample_collection_protocol)
        sample_collection_process = itm.Process(executes_protocol=sample_collection_protocol)

        # Next, we link our materials to the Process. In this particular case, we are describing a sample collection
        # process that takes one source material, and produces three different samples.
        #
        # (daphnia magna source) -> (sample collection) -> [(daphnia_material0-0), (daphnia_material0-1), (daphnia_material0-2)]
        # (solvent blank source) -> (sample collection) -> [(blank_material1-0), (blank_material1-1), (sample_material1-2)]

        for src in itm_s.sources:
            sample_collection_process.inputs.append(src)
        for sam in itm_s.samples:
            sample_collection_process.outputs.append(sam)

        # Finally, attach the finished Process object to the study process_sequence. This can be done many times to
        # describe multiple sample collection events.
        itm_s.process_sequence.append(sample_collection_process)

        ################################################################################################################
        #  ASSAYS
        ################################################################################################################

        # get dictionary of Django protocols
        dj_p = {
            'ex':{},
            'spe':{},
            'chr':{},
            'meas':{}
        }



        for dj_a in dj_s.assay_set.all():
            for dj_ad in dj_a.assaydetail_set.all():
                ex = dj_ad.extractionprocess.extractionprotocol
                dj_p['ex'][ex.id] = ex

                spe = dj_ad.speprocess.speprotocol
                dj_p['spe'][spe.id] = spe

                chrom = dj_ad.chromatographyprocess.chromatographyprotocol
                dj_p['chr'][chrom.id] = chrom

                meas = dj_ad.measurementprocess.measurementprotocol
                dj_p['meas'][meas.id] = meas

        # Create isa tab protocols
        itm_p = {
            'ex': {},
            'spe': {},
            'chr': {},
            'meas': {}
        }

        itm_pparams = {
            'ex':{},
            'spe':{},
            'chr':{},
            'meas':{}
        }

        #===========================================
        # Get Extraction protocols
        #===========================================
        itm_pparams['ex']['Derivatization'] = itm.ProtocolParameter(parameter_name=itm.OntologyAnnotation(term="Derivatization", term_source=check_ontology_source(itm_i, 'CHMO'),
                                                                    term_accession='http://purl.obolibrary.org/obo/CHMO_0001485'))
        itm_pparams['ex']['Post Extraction'] = itm.ProtocolParameter(parameter_name=itm.OntologyAnnotation(term="Post Extraction"))    
        if not metabolights_compat:
            # Only one extraction protocol for Metabolights
            extraction_protocol = itm.Protocol(name='Extraction',
                                                protocol_type=itm.OntologyAnnotation(term="Extraction"),
                                                )  

            extraction_protocol.parameters.extend(itm_pparams['ex'].values())

            itm_s.protocols.append(extraction_protocol)
            for k, dj_ex in six.iteritems(dj_p['ex']):
                itm_p['ex'][k] = extraction_protocol
        
        else:
            for k, dj_ex in six.iteritems(dj_p['ex']):

                extraction_protocol = itm.Protocol(name='Extraction ({})'.format(dj_ex.code_field),
                                                protocol_type=itm.OntologyAnnotation(term="Extraction"),
                                                description=dj_ex.name
                                                )  

                extraction_protocol.parameters.extend(itm_pparams['ex'].values())

                itm_s.protocols.append(extraction_protocol)

                itm_p['ex'][k] = extraction_protocol



        #===========================================
        # Get SPE protocols
        #===========================================
        if not metabolights_compat:
            # MetaboLights doesn't record SPE details
            for k, dj_spe in six.iteritems(dj_p['spe']):
                spe_protocol = itm.Protocol(name='Solid Phase Extraction ({})'.format(dj_spe.code_field),
                                            protocol_type=itm.OntologyAnnotation(term="Solid Phase Extraction"),
                                            #components=[itm.OntologyAnnotation(term='')],  # this does not work with isa dump to isa tab
                                            description=dj_spe.name
                                            )
                itm_s.protocols.append(spe_protocol)
                itm_p['spe'][k] = spe_protocol


        #===========================================
        # Get chromatography protocols
        #===========================================
        itm_pparams['chr']['Chromatography instrument']= itm.ProtocolParameter(parameter_name=itm.OntologyAnnotation(term="Chromatography instrument", term_source=check_ontology_source(itm_i, 'OBI'),
                                            term_accession='http://purl.obolibrary.org/obo/OBI_0000485'))
            
        itm_pparams['chr']['Autosampler model'] = itm.ProtocolParameter(parameter_name=itm.OntologyAnnotation(term="Autosampler model"))
        itm_pparams['chr']['Column model'] = itm.ProtocolParameter(parameter_name=itm.OntologyAnnotation(term="Column model"))
        itm_pparams['chr']['Column type'] = itm.ProtocolParameter(parameter_name=itm.OntologyAnnotation(term="Column type"))
        itm_pparams['chr']['Guard column'] = itm.ProtocolParameter(parameter_name=itm.OntologyAnnotation(term="Guard column"))

        if not metabolights_compat:
            for k, dj_chr in six.iteritems(dj_p['chr']):


                chromatography_protocol = itm.Protocol(name='Chromatography ({})'.format(dj_chr.code_field), 
                                                    protocol_type=itm.OntologyAnnotation(term="Chromatography"),
                                                    description=dj_chr.name)

                chromatography_protocol.parameters.extend(itm_pparams['chr'].values())

                itm_s.protocols.append(chromatography_protocol)

                itm_p['chr'][k] = chromatography_protocol
        else:
            chromatography_protocol = itm.Protocol(name='Chromatography',
                                                    protocol_type=itm.OntologyAnnotation(term="Chromatography"),
                                                    description='')

            chromatography_protocol.parameters.extend(itm_pparams['chr'].values())
            itm_s.protocols.append(chromatography_protocol)
            for k, dj_ex in six.iteritems(dj_p['spe']):
                itm_p['chr'][k] = chromatography_protocol

        #===========================================
        # Get measurment protocols
        #===========================================
        for term in ['Scan polarity', 'Scan m/z range', 'Ion source', 'Mass analyzer', 'Detector', 'Inlet type',
                     'Instrument', 'Instrument manufacturer', 'Instrument serial number', 'Instrument software',
                     'Instrument software version']:
            itm_pparams['meas'][term] = itm.ProtocolParameter(parameter_name=itm.OntologyAnnotation(term=term))
       
        if not metabolights_compat:
            # MetaboLights should only have one protocol per for Mass Spectrometry - where as for DMAdb
            # we separate into different protocols
            for k, dj_meas in six.iteritems(dj_p['meas']):
                
                mass_spec_protocol = itm.Protocol(name='Mass spectrometry ({})'.format(dj_meas.code_field),
                                                protocol_type=itm.OntologyAnnotation(term="Mass spectrometry"))
                mass_spec_protocol.parameters.extend(itm_pparams['meas'].values())
                itm_s.protocols.append(mass_spec_protocol)
                
                itm_p['meas'][k] = mass_spec_protocol
        else:
            # i.e. MetaboLights do not distinguish Mass spectrometry protocols and ISA tab export can only handle
            # one type of measurment protocol per assay file - so we can't separate here
            mass_spec_protocol = itm.Protocol(name='Mass spectrometry',
                                              protocol_type=itm.OntologyAnnotation(term="Mass spectrometry"))
            mass_spec_protocol.parameters.extend(itm_pparams['meas'].values())
            itm_s.protocols.append(mass_spec_protocol)
            for k, dj_meas in six.iteritems(dj_p['meas']):
                itm_p['meas'][k] = mass_spec_protocol

        

        #===========================================
        # Get data transformation protocols
        #===========================================
        dt_protocol = itm.Protocol(name='Data transformation',
                                   protocol_type=itm.OntologyAnnotation(term="Data transformation"))
        itm_s.protocols.append(dt_protocol)
        
        itm_p['dt'] = dt_protocol

        #===========================================
        # Metabolite annnotation protocol
        #===========================================
        ma_protocol = itm.Protocol(name='Metabolite annotation',
                                   protocol_type=itm.OntologyAnnotation(term="Metabolite annotation"))
        itm_s.protocols.append(ma_protocol)
        
        itm_p['ma'] = ma_protocol

        # To simplify the structure for MetaboLights we also break the assays for LC-MS derived annotations
        # as  POLAR-POS, POLAR-NEG, APOLAR-POS, APOLAR-NEG. This fits with the more common structure in MetaboLights
        # of separating out the reverse phase (Lipid - apolar) and HILIC assays (metabolites - polar) assays and 
        # makes the MetaboLights ISA page more intepretable 
        dj_assay_lists = defaultdict(list)
        if metabolights_compat:
            for dj_a in dj_s.assay_set.all():
                # assay name should be in this form [EXTRACTION]_[SPE]_[SPE_NUMBER]_[CHROM]_[MSM optional]_[POLARITY]
                dj_a_name_l = dj_a.name.split('_')
                extraction_type = dj_a_name_l[0]
                polarity_type = dj_a_name_l[len(dj_a_name_l)-1]
                if extraction_type.lower() == 'apol' and polarity_type.lower() == 'pos':
                    dj_assay_lists['apolar_positive'].append(dj_a)
                elif extraction_type.lower() == 'apol' and polarity_type.lower() == 'neg':
                    dj_assay_lists['apolar_negative'].append(dj_a)
                elif extraction_type.lower() == 'pol' and polarity_type.lower() == 'pos':
                    dj_assay_lists['polar_positive'].append(dj_a)
                elif extraction_type.lower() == 'pol' and polarity_type.lower() == 'neg':
                    dj_assay_lists['polar_negative'].append(dj_a)
                
        else:
            for dj_a in dj_s.assay_set.all():
                dj_assay_lists[dj_a.name].append(dj_a)

        c = 0
        
        for assay_name, dj_assays in dj_assay_lists.items():
            c += 1
            itm_a = itm.Assay(filename="a_assay_{}.txt".format(assay_name))  

            # go through each file (logically this should be the assay detail but this does not
            # fit with the structure of ISA tab used for MetaboLights where each row is a file )
            for idx, dj_mfile in enumerate(MFile.objects.filter(run__assaydetail__assay__in=dj_assays, mfilesuffix__suffix='.mzml')):

                print(dj_mfile.prefix)
                if celery_obj:
                     celery_obj.update_state(state='RUNNING',
                                            meta={'current': c, 'total':  len(dj_assay_lists)+10,
                                                  'status': 'Assay ({} of {}) - current file {}'.format(c, len(dj_assay_lists), dj_mfile.prefix)})

                datafile = itm.DataFile(filename=dj_mfile.prefix+'.raw', label="Raw Spectral Data File")
                itm_a.data_files.append(datafile)
                
                dj_ad = dj_mfile.run.assaydetail
                ####################################
                # Get extraction
                ####################################
                itm_ex_prot = itm_p['ex'][dj_ad.extractionprocess.extractionprotocol.id]

                extraction_process = itm.Process(executes_protocol=itm_ex_prot)
                extraction_process.name = "extract-process-{}".format(dj_ad.code_field)
                
                if dj_ad.speprocess and metabolights_compat:
                    extraction_process.parameter_values.extend([
                        itm.ParameterValue(itm_pparams['ex']['Post Extraction'], 
                                        '{} ({}), SPE ({})'.format(
                                                                    dj_ad.extractionprocess.extractionprotocol.extractiontype.type,
                                                                    dj_ad.extractionprocess.extractionprotocol.postextraction,
                                                                    dj_ad.speprocess.speprotocol.name.replace('DMA D. magna ', '')))
                    ])
                else:
                    extraction_process.parameter_values.extend([
                        itm.ParameterValue(itm_pparams['ex']['Post Extraction'], dj_ad.extractionprocess.extractionprotocol.postextraction),
                    ])

                extract_material = itm.Material(name=' ')
                extract_material.type = "Extract Name"
                extraction_process.outputs.append(extract_material)
                itm_a.other_material.append(extract_material)

                ############################################################
                ##### IMPORTANT: WE add the sample input here! #############
                itm_samplei = itm_sample_d[dj_ad.studysample_id]
                extraction_process.inputs.append(itm_samplei)

                ####################################
                # Get SPE
                ####################################
                if dj_ad.speprocess and not metabolights_compat:

                    itm_spe_prot = itm_p['spe'][dj_ad.speprocess.speprotocol.id]
                    spe_process = itm.Process(executes_protocol=itm_spe_prot)
                    spe_process.name = "spe-process-{}".format(dj_ad.code_field)
                    spe_process.inputs.append(extraction_process.outputs[0])

                    spe_material = itm.Material(name=idx+1)
                    spe_material.type = "Extract Name"
                    spe_process.outputs.append(spe_material)
                    itm_a.other_material.append(spe_material)
                


                ####################################
                # Get chromatography
                ####################################
                itm_chr_prot = itm_p['chr'][dj_ad.chromatographyprocess.chromatographyprotocol.id]
                chr_process = itm.Process(executes_protocol=itm_chr_prot)
                chr_process.name = "chr-process-{}".format(dj_ad.code_field)
                chrom_type = dj_ad.chromatographyprocess.chromatographyprotocol.chromatographytype.ontologyterm.all()[0]
                chrom_instrument = dj_ad.chromatographyprocess.chromatographyprotocol.instrument_name
                column_model = dj_ad.chromatographyprocess.chromatographyprotocol.description
                chr_process.parameter_values.extend([
                    itm.ParameterValue(itm_pparams['chr']['Chromatography instrument'], chrom_instrument if chrom_instrument else ' '),
                    itm.ParameterValue(itm_pparams['chr']['Autosampler model'], ' '), # too detailed to add here
                    itm.ParameterValue(itm_pparams['chr']['Column model'], column_model if column_model else ' '),
                    itm.ParameterValue(itm_pparams['chr']['Column type'], itm.OntologyAnnotation(term=chrom_type.name,
                                                                                                term_source= check_ontology_source(itm_i,  chrom_type.ontology_prefix),
                                                                                                term_accession=chrom_type.iri)),
                    itm.ParameterValue(itm_pparams['chr']['Guard column'], ' '),  # we don't record the guard column information
                ])



                if dj_ad.speprocess and not metabolights_compat:
                    chr_process.inputs.append(spe_process.outputs[0])
                else:
                    chr_process.inputs.append(extraction_process.outputs[0])

                chr_material = itm.Material(name=' ')   # leave blank - causes problems having multiple materials in isa-tab output
                chr_material.type = "Labeled Extract Name"  # Namining used by metabolights
                chr_material.label = " "

                chr_process.outputs.append(chr_material)
                itm_a.other_material.append(chr_material)


                ####################################
                # Get measurements (mass spec only)
                ####################################
                itm_meas_prot = itm_p['meas'][dj_ad.measurementprocess.measurementprotocol.id]               
                meas_process = itm.Process(executes_protocol=itm_meas_prot)
                meas_process.name = "meas-process-{}".format(dj_ad.code_field)
                meas_process.inputs.append(chr_process.outputs[0])
                meas_process.outputs.append(datafile)

                #read in mzml file
                if  extract_mzml_info and dj_mfile.mfilesuffix.suffix == '.mzml':
                    mzmlf = mzml.MzMLFile(os.path.dirname(dj_mfile.data_file.path), os.path.basename(dj_mfile.data_file.path))
                    
                    meas_process.parameter_values.extend([
                        extract_parameter_value_mzml(mzmlf, 'Scan polarity', itm_pparams, itm_i, section='meas', value=False),
                        extract_parameter_value_mzml(mzmlf, 'Scan m/z range', itm_pparams, itm_i,section='meas', value=True),
                        extract_parameter_value_mzml(mzmlf, 'Ion source', itm_pparams,itm_i, section='meas', value=False),
                        extract_parameter_value_mzml(mzmlf, 'Mass analyzer', itm_pparams,itm_i, section='meas', value=False),
                        extract_parameter_value_mzml(mzmlf, 'Detector', itm_pparams, itm_i,section='meas', value=False),
                        extract_parameter_value_mzml(mzmlf, 'Inlet type', itm_pparams,itm_i, section='meas', value=False),
                        extract_parameter_value_mzml(mzmlf, 'Instrument', itm_pparams,itm_i, section='meas', value=False),
                        extract_parameter_value_mzml(mzmlf, 'Instrument serial number', itm_pparams,itm_i, section='meas', value=True),
                        extract_parameter_value_mzml(mzmlf, 'Instrument software', itm_pparams, itm_i,section='meas', value=False),
                        extract_parameter_value_mzml(mzmlf, 'Instrument software version', itm_pparams,itm_i, section='meas', value=True),
                    ])

                
                ####################################
                # Data transformations
                ####################################
                dt_process = itm.Process(executes_protocol=itm_p['dt'])
                dt_process.inputs.append(meas_process.outputs[0])
                datafile = itm.DataFile(filename=dj_mfile.original_filename, label="Derived Spectral Data File")
                dt_process.outputs.append(datafile)
                dt_process.name = " "

                ####################################
                # Metabolite annotation
                ####################################
                ma_process = itm.Process(executes_protocol=itm_p['ma'])
                ma_process.inputs.append(dt_process.outputs[0])
                ma_process.name = " "

                if metabolights_compat and export_isatab:
                    # Create MetaboLight compatible Metabolight Assignment Files - some field missing but
                    # enough for the submission
                    met_id_file_name = 'm_{}.tsv'.format(assay_name)
                    datafile = itm.DataFile(filename=met_id_file_name, label="Metabolite Assignment File" )
                    ma_process.outputs.append(datafile)
                    extraction, polarity = assay_name.split('_')

                    compounds = Compound.objects.filter(
                                                        polarity__icontains=polarity,
                                                        extraction__icontains=extraction
                                                        ).values().annotate(
                                                                  species=F('organisms'), 
                                                                  database_identifier=F('chebi_ids'), 
                                                                  chemical_formula=F('molecular_formula'), 
                                                                  metabolite_identification=F('compound_name'),
                                                        )
                     
                    
                    df = pd.DataFrame(list(compounds))
                    df = df.replace({'NA': None})
                    df = df.reindex(columns=['database_identifier', 'chemical_formula', 
                                        'smiles', 'inchi', 'metabolite_identification',
                                         'hmdb_ids', 'kegg_ids', 'pubchem_cids', 'mass_to_charge', 'fragmentation',	'modifications'
                                        'charge', 'retention_time', 'taxid', 'species', 'database',
                                        'database_version', 'reliability', 'uri',
                                        'search_engine', 'search_engine_score', 'smallmolecule_abundance_sub',
                                         'smallmolecule_abundance_stdev_sub', 'smallmolecule_abundance_std_error_sub'], fill_value=None)
                    df = df.sort_values(by=['database_identifier', 'hmdb_ids', 'kegg_ids', 'metabolite_identification'])
                    df.to_csv(os.path.join(isa_temp_dir, met_id_file_name), sep="\t", index=False)

                    

                

                if dj_ad.speprocess and not metabolights_compat:
                    itm.plink(extraction_process, spe_process)
                    itm.plink(spe_process, chr_process)
                else:
                    itm.plink(extraction_process, chr_process)

                itm.plink(chr_process, meas_process)
                itm.plink(meas_process, dt_process)               
                itm.plink(dt_process, ma_process)               


                itm_a.samples.append(itm_samplei)
                
                itm_a.process_sequence.append(extraction_process)

                if dj_ad.speprocess and not metabolights_compat:
                    itm_a.process_sequence.append(spe_process)

                itm_a.process_sequence.append(chr_process)
                itm_a.process_sequence.append(meas_process)
                itm_a.process_sequence.append(dt_process)
                itm_a.process_sequence.append(ma_process)
                
                itm_a.measurement_type = itm.OntologyAnnotation(term='metabolite profiling')
                itm_a.technology_type = itm.OntologyAnnotation(term='mass spectrometry')


            itm_s.assays.append(itm_a)


    # Save ISA-Tab zip
    if export_isatab:
        if celery_obj:
            celery_obj.update_state(state='RUNNING',
                                            meta={'current': c+5, 'total':  len(dj_assays)+10,
                                                  'status': 'Exporting ISA tab zip'})

        isatab.dump(itm_i, isa_temp_dir)
        shutil.make_archive(isa_temp_dir, 'zip', isa_temp_dir)
        isa_temp_zip = os.path.join(tmpdir, 'isa.zip')        
        print(isa_temp_zip)
        
        dj_i.isa_tab_zip.save(os.path.basename(isa_temp_zip), content=File(open(isa_temp_zip, 'rb')))
        shutil.rmtree(tmpdir)
   
    
    # create json
    if export_json: 
        if celery_obj:
            celery_obj.update_state(state='RUNNING',
                                            meta={'current': c+9, 'total':  len(dj_assay_lists)+10,
                                                  'status': 'Exporting IS-JSON'})
        json_out = json.dumps(itm_i, cls=ISAJSONEncoder, sort_keys=True, indent=4, separators=(',', ': '))
        dj_i.json_file.save('isa.json', ContentFile(json_out), save=True)
    
    if celery_obj:
        celery_obj.update_state(state='SUCCESS',
                                meta={'current': 100, 'total':  100,
                                      'status': 'ISA data exported'})
    return itm_i
    