# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
from io import TextIOWrapper
import csv
import re
import six
from mogi.models.models_isa import StudySample, StudyFactor, SampleType, OrganismPart, Organism, Study, Investigation
from mogi.utils.ontology_utils import check_and_create_ontology

def check_and_create_model(name, model_to_check, db_alias=''):
    # check if we have the organism
    # if we do return the pk

    qs = model_to_check.objects.filter(ontologyterm__name=name)

    if qs:
        return qs[0]

    # if we do not have the organism name, check ontology
    # if we do have an ontology create the organism with the ontology and return the pk
    ont_ids = check_and_create_ontology(name, db_alias=db_alias)

    ob = model_to_check(ontologyterm_id=ont_ids[0])
    ob.name = ob.ontologyterm.name
    ob.public = True
    if db_alias:
        ob.save(using=db_alias)
    else:
        ob.save()

    return ob



def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def check_and_create_study_factor(study_factor_type, study_factor_value, study_factor_unit=''):
    # Check if we have the study factor type already. If not, check ontology and add.
    study_factor_type_ont_id = check_and_create_ontology(study_factor_type)[0]

    # Check if we have the study factor unit, if not check ontology and add
    if study_factor_unit:
        study_factor_unit_id = check_and_create_ontology(study_factor_unit)[0]
    else:
        study_factor_unit_id = None

    # Check if we have the study factor value, if not check ontology and add
    if is_number(study_factor_value):
        value = study_factor_value
        study_factor_value_ont_id = None
    else:
        value = None
        study_factor_value_ont_id = check_and_create_ontology(study_factor_value)[0]

    sf_qs = StudyFactor.objects.filter(ontologyterm_type_id=study_factor_type_ont_id,
                                       value=value,
                                       ontologyterm_unit_id=study_factor_unit_id,
                                       ontologyterm_value_id=study_factor_value_ont_id)
    if sf_qs:
        return sf_qs[0]
    else:
        # if not create a new study factor
        studyfactor = StudyFactor(ontologyterm_type_id=study_factor_type_ont_id,
                                           value=value,
                                           ontologyterm_unit_id=study_factor_unit_id,
                                           ontologyterm_value_id=study_factor_value_ont_id)

        studyfactor.save()
        return studyfactor



def sample_batch_create(sample_list, study_default='', replace_duplicates=False, delimiter='\t'):
    reader = csv.reader(TextIOWrapper(sample_list, encoding='ascii', errors='replace'), delimiter=delimiter)

    # Get indexes of column. Can use either ISA style study file or simplified version
    cols = next(reader)
    idxs = {'study_factors': {}}
    fc = 0
    for i, col in enumerate(cols):
        if col.lower() == 'investigation':
            idxs['investigation'] = i
        elif col.lower() == 'study':
            idxs['study'] = i
        if col == 'Characteristics[Organism]' or col == 'organism':
            idxs['organism'] = i
        elif col == 'Characteristics[Organism part]' or col == 'organism_part':
            idxs['organism_part'] = i
        elif col == 'Source Name' or col == 'source_name':
            idxs['source_name'] = i
        elif col == 'Sample Name' or col == 'sample_name':
            idxs['sample_name'] = i
        elif col == 'sample_type':
            idxs['sample_type'] = i
        else:
            match_type = re.match('^(?:Factor Value|factor_)\[(.*)\]$', col)
            if match_type:
                fc += 1
                fc_type = match_type.group(1)

                idxs['study_factors'][fc] = {
                    'value': i,
                    'unit': '',
                    'type': fc_type
                }

            if fc:
                match_unit = re.match('(?:Unit|factor_\[.*\]_unit)$', col)
                if match_unit:
                    idxs['study_factors'][fc]['unit'] = i


    for row in reader:

        # get organism and check if we have relevant ontology (if not add best match)
        organism = check_and_create_model(row[idxs['organism']], Organism)
        # same for organism type
        organism_part = check_and_create_model(row[idxs['organism_part']], OrganismPart)

        # get sample type (if not defined will either be blank or animal depending on sample name)
        if 'sample_type' in idxs.keys():
            st_qs = SampleType.objects.filter(type=row[idxs['sample_type']])
            if st_qs:
                sampletype = st_qs[0]
        else:
            if re.match('.*blank.*', row[idxs['sample_name']], re.IGNORECASE):
                sampletype = SampleType.objects.get(type='BLANK')  # defaults to animal if no sampletype giv
            else:
                sampletype = SampleType.objects.get(type='ANIMAL')  # defaults to animal if no sampletype giv

        # get study factors
        studyfactors = []
        for k, v in six.iteritems(idxs['study_factors']):

            sf = check_and_create_study_factor(v['type'],
                                                              row[v['value']],
                                                              row[v['unit']] if v['unit'] else '')
            studyfactors.append(sf)

        if not study_default and 'study' in idxs and 'investigation' in idxs:
            investigation = Investigation.objects.filter(name=row[idxs['investigation']]).first()
            study = Study.objects.filter(name=row[idxs['study']], investigation=investigation).first()

        else:
            study = study_default

        if not study:
            print('missing study')
            continue

        # # Create (or replace) Study samples with details
        study_samples_present = StudySample.objects.filter(study=study, sample_name=row[idxs['sample_name']])

        if not study_samples_present:
            create_ss(study, organism, organism_part, row[idxs['sample_name']], row[idxs['source_name']],
                      sampletype, studyfactors)
        elif study_samples_present and replace_duplicates:
            study_samples_present[0].delete()
            create_ss(study, organism, organism_part, row[idxs['sample_name']], row[idxs['source_name']],
                      sampletype, studyfactors)



def create_ss(study, organism, organism_part, sample_name, source_name, sampletype, studyfactors):
    studysample = StudySample(study=study,
                              sample_name=sample_name,
                              source_name=source_name,
                              organism=organism,
                              organism_part=organism_part,
                              sampletype=sampletype)

    studysample.save()
    studysample.studyfactor.add(*studyfactors)






