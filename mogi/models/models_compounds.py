# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models

class Compound(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    inchikey = models.CharField(max_length=254, primary_key=True)
    inchikey1 = models.CharField(max_length=254, blank=True, null=True)
    inchikey2 = models.CharField(max_length=254, blank=True, null=True)
    inchikey3 = models.CharField(max_length=254, blank=True, null=True)

    name = models.CharField(max_length=1024, blank=True, null=True)

    inchi = models.TextField(blank=True, null=True)
    smiles_canonical = models.TextField(blank=True, null=True)
    exact_mass = models.FloatField(blank=True, null=True)
    molecular_formula = models.TextField(blank=True, null=True)
    pubchem_cids = models.TextField(blank=True, null=True)

    kegg_drugs = models.CharField(max_length=1024, blank=True, null=True)
    kegg_brite = models.CharField(max_length=1024, blank=True, null=True)
    hmdb_ids = models.CharField(max_length=1024, blank=True, null=True)
    hmdb_bio_custom_flag = models.CharField(max_length=1024, blank=True, null=True)
    hmdb_drug_flag = models.CharField(max_length=1024, blank=True, null=True)
    biosim_max_score = models.FloatField(blank=True, null=True)
    biosim_max_count = models.IntegerField(blank=True, null=True)
    biosim_hmdb_ids = models.TextField(blank=True, null=True)


    def __str__(self):  # __unicode__ on Python 2
        return self.name



class PubChem(models.Model):
    inchikey = models.CharField(max_length=254, blank=False, null=False)
    cid = models.IntegerField(blank=False, null=False)

    def __str__(self):  # __unicode__ on Python 2
        return self.cid


class HMDB(models.Model):
    inchikey = models.CharField(max_length=254, blank=False, null=False)
    hmdbid = models.CharField(max_length=254, blank=False, null=False)

    def __str__(self):  # __unicode__ on Python 2
        return self.hmdbid

class KEGG(models.Model):
    inchikey = models.CharField(max_length=254, blank=False, null=False)
    cid = models.IntegerField(blank=False, null=False)

    def __str__(self):  # __unicode__ on Python 2
        return self.cid






