# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
from django.test import TestCase
from mogi.models.models_isa import OntologyTerm, Organism


# models test
class OntologyTermTest(TestCase):
    def test_ontologyterm_creation(self):
        ot = OntologyTerm.objects.create(name='test', ontology_id=1)
        self.assertTrue(isinstance(ot, OntologyTerm))
        self.assertEqual(str(ot), ot.name)


class OrganismTest(TestCase):
    def test_Organism_creation(self):
        ot = OntologyTerm.objects.create(name='test', ontology_id=2)
        ot.save()
        o = Organism.objects.create(ontologyterm=ot)
        self.assertTrue(isinstance(o, Organism))
        self.assertEqual(o.name, ot.name)
