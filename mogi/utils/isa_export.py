# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import zipfile
import os
import json
from django.contrib.auth.models import User
from django import forms

from mogi.models.models_isa import Investigation
from isatools import model as itm
from isatools.isajson import ISAJSONEncoder
import six

def add_lcms_untargeted_meta(itm_i, itm_s, msms_performed=True):
    obi = itm.OntologySource(name='CHMO', description="Chemical Methods Ontology")
    itm_i.ontology_source_references.append(obi)
    uplcms = itm.OntologyAnnotation(term_source=obi)
    uplcms.term = "ultra-performance liquid chromatography-mass spectrometry"
    uplcms.term_accession = "http://purl.obolibrary.org/obo/CHMO_0000715"
    itm_s.design_descriptors.append(uplcms)

    if msms_performed:
        msms = itm.OntologyAnnotation(term_source=obi)
        msms.term = "tandem mass spectrometry"
        msms.term_accession = "http://purl.obolibrary.org/obo/CHMO_0000575"
        itm_s.design_descriptors.append(msms)

    untargeted_met = itm.OntologyAnnotation()
    untargeted_met.term = "untargeted metabolites"
    itm_s.design_descriptors.append(untargeted_met)

    return itm_i, itm_s


def add_organism_details(itm_i, itm_s, dj_organism):
    ncbitaxon = itm.OntologySource(name='NCBITaxon', description="NCBI Taxonomy")
    itm_i.ontology_source_references.append(ncbitaxon)
    organism = itm.OntologyAnnotation(term_source=ncbitaxon)
    organism.term = dj_organism.ontology_term
    organism.term_accession = dj_organism.ontology_accession
    itm_s.design_descriptors.append(organism)

    return organism


def add_organism_sample(dj_ss):
    if dj_ss.organism:
        dj_org_ont = dj_ss.organism.ontologyterm
        src =  itm.OntologySource(name=dj_org_ont.ontology_prefix,
                                  description=dj_org_ont.ontology_name)
        val = itm.OntologyAnnotation(term=dj_org_ont.name,
                                     term_source=src,
                                     term_accession=dj_org_ont.iri)
    else:

        val = itm.OntologyAnnotation(term='',  term_source='', term_accession='')

    return itm.Characteristic(category=itm.OntologyAnnotation(term="Organism",
                                                              term_source="NCIT",
                                                              term_accession="http://purl.obolibrary.org/obo/NCIT_C14250"),
                                                              value=val)


def add_organism_part_sample(dj_ss):
    if dj_ss.organism_part:
        dj_org_ont = dj_ss.organism_part.ontologyterm
        src =  itm.OntologySource(name=dj_org_ont.ontology_prefix,
                                  description=dj_org_ont.ontology_name)
        val = itm.OntologyAnnotation(term=dj_org_ont.name,
                                     term_source=src,
                                     term_accession=dj_org_ont.iri)
    else:
        val = itm.OntologyAnnotation(term='',  term_source='', term_accession='')

    return itm.Characteristic(category=itm.OntologyAnnotation(term="Organism part",
                                                              term_source="NCIT",
                                                              term_accession="http://purl.obolibrary.org/obo/NCIT_C103199"),
                                                              value=val)




def check_ontology_source(itm_i, query_source_name):
    ont_source = ''
    for ionts in itm_i.ontology_source_references:
        if ionts.name==query_source_name:
            ont_source=ionts
    return ont_source


def export_isa_files(investigation_id):

    # Create investigation
    dj_i = Investigation.objects.get(pk=investigation_id)
    itm_i = itm.Investigation(filename="i_investigation.txt")
    itm_i.identifier = "i1"
    itm_i.title = dj_i.name
    itm_i.description = dj_i.description


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

        itm_i, itm_s = add_lcms_untargeted_meta(itm_i, itm_s, msms_performed=True)

        # Add study samples
        # loop through the study samples

        ################################################################################################################
        # STUDY SAMPLES
        ################################################################################################################
        for j, dj_ss in enumerate(dj_s.studysample_set.all()):
            # We are saying that each sample is derived from a different source material, this might not be true for
            # for all cases but should be fine for the resulting ISA-Tab structure for MetaboLights
            source = itm.Source(name='{} source'.format(dj_ss.sample_name))
            itm_s.sources.append(source)

            # Sample material from the source
            itm_sample = itm.Sample(name=dj_ss.sample_name, derives_from=source)

            #=====================
            # Add organism for sample
            #=====================
            if dj_ss.organism:
                dj_org_ont = dj_ss.organism.ontologyterm
                source = check_ontology_source(itm_i, dj_org_ont.ontology_name)
                if not source:
                    source = itm.OntologySource(name=dj_org_ont.ontology_prefix,
                                         description=dj_org_ont.ontology_name)
                    itm_i.ontology_source_references.append(source)

                val = itm.OntologyAnnotation(term=dj_org_ont.name,
                                             term_source=source,
                                             term_accession=dj_org_ont.iri)
            else:

                val = itm.OntologyAnnotation(term='', term_source='', term_accession='')

            char =  itm.Characteristic(category=itm.OntologyAnnotation(term="Organism",
                                                                      term_source="NCIT",
                                                                      term_accession="http://purl.obolibrary.org/obo/NCIT_C14250"),
                                      value=val)
            itm_sample.characteristics.append(char)

            # =====================
            # Add organism part
            # =====================
            if dj_ss.organism_part:
                dj_org_ont = dj_ss.organism_part.ontologyterm

                source = check_ontology_source(itm_i, dj_org_ont.ontology_name)
                if not source:
                    source = itm.OntologySource(name=dj_org_ont.ontology_prefix,
                                         description=dj_org_ont.ontology_name)
                    itm_i.ontology_source_references.append(source)

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
                                                      protocol_type=itm.OntologyAnnotation(term="sample collection"))
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

        # sequencing_protocol = itm.Protocol(name='sequencing', protocol_type=itm.OntologyAnnotation(term="material sequencing"))
        # itm_s.protocols.append(sequencing_protocol)



        for k, dj_ex in six.iteritems(dj_p['ex']):

            if dj_ex.name:
                nm = dj_ex.name
            else:
                nm = dj_ex.extractiontype.type


            #===========================================
            # Get extraction protocols
            #===========================================
            source = check_ontology_source(itm_i, 'CHMO')
            extraction_protocol = itm.Protocol(name='Extraction {}'.format(nm),
                                               protocol_type=itm.OntologyAnnotation(term="Extraction"),
                                               )

            param = itm.ProtocolParameter(parameter_name=itm.OntologyAnnotation(term="Derivatization", term_source=source,
                                                                 term_accession='http://purl.obolibrary.org/obo/CHMO_0001485'))
            extraction_protocol.parameters.append(param)

            itm_s.protocols.append(extraction_protocol)

            itm_p['ex'][k] = extraction_protocol

        for k, dj_spe in six.iteritems(dj_p['spe']):
            if dj_spe.name:
                nm = dj_spe.name
            else:
                nm = dj_spe.spetype.type

            #===========================================
            # Get chromatography protocols
            #===========================================
            spe_protocol = itm.Protocol(name='Solid Phase Extraction {}'.format(nm),
                                        protocol_type=itm.OntologyAnnotation(term="Solid Phase Extraction"),
                                        components=itm.OntologyAnnotation(term=nm),
                                        description=dj_spe.description
                                        )
            itm_s.protocols.append(spe_protocol)
            itm_p['spe'][k] = spe_protocol



        for k, dj_chr in six.iteritems(dj_p['chr']):

            #===========================================
            # Get chromatography protocols
            #===========================================
            chromatography_protocol = itm.Protocol(name='Chromatography {}'.format(dj_chr.name),
                                                   protocol_type=itm.OntologyAnnotation(term="Chromatography"))

            itm_s.protocols.append(chromatography_protocol)

            itm_p['chr'][k] = chromatography_protocol



        for k, dj_meas in six.iteritems(dj_p['meas']):
            #===========================================
            # Get measurment protocols (just mass spec for now)
            #===========================================
            if dj_meas.name:
                nm = dj_meas.name
            else:
                nm = dj_meas.measurementtechnique.type
            mass_spec_protocol = itm.Protocol(name='Mass spectrometry {}'.format(nm),
                                              protocol_type=itm.OntologyAnnotation(term="Mass spectrometry"))
            itm_s.protocols.append(mass_spec_protocol)
            itm_p['meas'][k] = mass_spec_protocol




        for dj_a in dj_s.assay_set.all():
            itm_a = itm.Assay(filename="a_assay_{}.txt".format(dj_a.name))

            # go through each details (which is linked to all the relevant process)
            for dj_ad in dj_a.assaydetail_set.all():

                ####################################
                # Get extraction
                ####################################
                itm_ex_prot = itm_p['ex'][dj_ad.extractionprocess.extractionprotocol.id]

                extraction_process = itm.Process(executes_protocol=itm_ex_prot)
                extraction_process.name = "extract-process-{}".format(dj_ad.code_field)
                material = itm.Material(name="extract-{}".format(dj_ad.code_field))
                material.type = "Extract Name"
                extraction_process.outputs.append(material)

                ############################################################
                ##### IMPORTANT: WE add the sample input here! #############
                itm_samplei = itm_sample_d[dj_ad.studysample_id]
                extraction_process.inputs.append(itm_samplei)

                ####################################
                # Get SPE
                ####################################
                if dj_ad.speprocess:

                    itm_spe_prot = itm_p['spe'][dj_ad.speprocess.speprotocol.id]
                    spe_process = itm.Process(executes_protocol=itm_spe_prot)
                    spe_process.name = "spe-process-{}".format(dj_ad.code_field)
                    spe_process.inputs.append(extraction_process.outputs[0])

                    material = itm.Material(name="SPE-Eluent-{}".format(dj_ad.code_field))
                    material.type = "Extract Name"
                    spe_process.outputs.append(material)


                ####################################
                # Get chromatography
                ####################################
                itm_chr_prot = itm_p['chr'][dj_ad.chromatographyprocess.chromatographyprotocol.id]
                chr_process = itm.Process(executes_protocol=itm_chr_prot)
                chr_process.name = "chr-process-{}".format(dj_ad.code_field)

                if dj_ad.speprocess:
                    chr_process.inputs.append(spe_process.outputs[0])
                else:
                    chr_process.inputs.append(extraction_process.outputs[0])

                material = itm.Material(name="Chromatography-Eluent-{}".format(dj_ad.code_field))
                material.type = "Extract Name"

                chr_process.outputs.append(material)


                ####################################
                # Get measurements (mass spec only)
                ####################################
                itm_meas_prot = itm_p['meas'][dj_ad.measurementprocess.measurementprotocol.id]
                meas_process = itm.Process(executes_protocol=itm_meas_prot)
                meas_process.name = "meas-process-{}".format(dj_ad.code_field)
                meas_process.inputs.append(chr_process.outputs[0])


                # get output file
                for file_details in dj_ad.assayrun_set.all().values('run__mfile', 'run__mfile__original_filename'):
                    datafile = itm.DataFile(filename=file_details['run__mfile__original_filename'], label="Raw Data File")
                    meas_process.outputs.append(datafile)
                    itm_a.data_files.append(datafile)

                if dj_ad.speprocess:
                    itm.plink(extraction_process, spe_process)
                    itm.plink(spe_process, chr_process)
                else:
                    itm.plink(extraction_process, chr_process)

                itm.plink(chr_process, meas_process)


                itm_a.samples.append(itm_samplei)
                itm_a.other_material.append(material)
                itm_a.process_sequence.append(extraction_process)

                if dj_ad.speprocess:
                    itm_a.process_sequence.append(spe_process)

                itm_a.process_sequence.append(chr_process)
                itm_a.process_sequence.append(meas_process)
                itm_a.measurement_type = itm.OntologyAnnotation(term="gene sequencing")
                itm_a.technology_type = itm.OntologyAnnotation(term="nucleotide sequencing")

            itm_s.assays.append(itm_a)


    # Note we haven't added factors yet

    return itm_i, json.dumps(itm_i, cls=ISAJSONEncoder, sort_keys=True, indent=4, separators=(',', ': '))
