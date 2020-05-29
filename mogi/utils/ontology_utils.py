# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import json
import requests
import uuid
from difflib import SequenceMatcher
from mogi.models.models_isa import OntologyTerm

def get_resp_d(resp):
    if resp and resp.content:
        return json.loads(resp.content)
    else:
        return {}


def get_result_d(resp_d):
    if resp_d['response'] and resp_d['response']['docs']:
        result_d = resp_d['response']['docs']
        for c, row in enumerate(result_d):
            row['c'] = c
            row['name'] = row.pop('label')
            row['ontology_id'] = row.pop('id')
        return result_d
    else:
        return {}


def search_ontology_term(search_term):
    url = 'https://www.ebi.ac.uk/ols/api/search?q={}'.format(search_term)
    resp = requests.get(url)

    resp_d = get_resp_d(resp)

    if not resp_d:
        return {}

    return get_result_d(resp_d)


def search_ontology_term_shrt(shrt, ontology_prefix='', create=False, db_alias=''):
    url = 'https://www.ebi.ac.uk/ols/api/search?q={}&queryFields=short_form'.format(shrt)
    resp = requests.get(url)
    resp_d = get_resp_d(resp)
    if not resp_d:
        return {}

    result_d_l = get_result_d(resp_d)

    if not result_d_l:
        return {}

    if result_d_l and ontology_prefix:
        for row in result_d_l:
            if row['ontology_prefix'] == ontology_prefix:
                return row
    else:
        return result_d_l[0]


def create_ontology_from_search(result, db_alias=''):
    keys = ['name', 'description', 'ontology_id', 'iri', 'obo_id',
            'ontology_name', 'ontology_prefix', 'ontology_prefix', 'type', 'short_form']
    result_filtered = dict((k, result[k]) for k in keys if k in result)


    # potentially already have this ontology
    otm_qs = OntologyTerm.objects.filter(ontology_id=result_filtered['ontology_id'])
    if otm_qs:
        return otm_qs[0]

    ot = OntologyTerm(**result_filtered)
    ot.public = True

    if db_alias:
        ot.save(using=db_alias)
    else:
        ot.save()
    return ot

def create_custom_ontology(name, db_alias=''):
    shrt_uid = str(uuid.uuid4())[:8]
    ot = OntologyTerm(name=name,
                      description='',
                      ontology_id='custom_' + shrt_uid,
                      iri='custom',
                      obo_id='custom',
                      ontology_name='custom',
                      ontology_prefix='custom',
                      short_form='custom_' + shrt_uid,
                      type='custom',
                      public=True)

    if db_alias:
        ot.save(using=db_alias)
    else:
        ot.save()

    return ot


def check_and_create_ontology(value, db_alias='', check_similarity=True, similarity_thres=0.95):

    # check current ontology
    otm_qs = OntologyTerm.objects.filter(name=value)
    if otm_qs:
        return [i.pk for i in otm_qs]

    # search ontology
    sresult = search_ontology_term(value)

    if sresult and sresult[0]:
        sim_score = SequenceMatcher(None, sresult[0]['name'], value).ratio()
        # the matching ontology name has to be at least 99% the same as the original input string

        if check_similarity:
            if sim_score > similarity_thres:
                ot = create_ontology_from_search(sresult[0], db_alias)
                return [ot.pk]
            else:
                ot = create_custom_ontology(value, db_alias='')
                return [ot.pk]
        else:
            ot = create_ontology_from_search(sresult[0], db_alias)
            return [ot.pk]



    else:
        # add or create 'custom' version' as not available with lookup

        ot = create_custom_ontology(value, db_alias='')
        return [ot.pk]
