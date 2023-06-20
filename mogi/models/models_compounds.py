# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from .models_isa import Assay, Investigation, Study, PolarityType, MeasurementTechnique
from gfiles.models import GenericFile


class UploadCompounds(GenericFile):
    def __str__(self):  # __unicode__ on Python 2
        return '{} {}'.format(self.id, self.original_filename)


class Compound(GenericFile):
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    inchikey = models.CharField(max_length=254, blank=True, null=True, unique=True)
    inchikey1 = models.CharField(max_length=254, blank=True, null=True)

    inchi = models.TextField(blank=True, null=True)
    smiles = models.TextField(blank=True, null=True)
    molecular_formula = models.TextField(blank=True, null=True)
    monoisotopic_exact_mass = models.FloatField(blank=True, null=True)

    compound_name = models.TextField(blank=True, null=True)

    natural_product_inchikey1 = models.BooleanField(blank=True, null=True)

    pubchem_cids = models.TextField(blank=True, null=True)
    hmdb_ids = models.TextField(blank=True, null=True)
    kegg_ids = models.TextField(blank=True, null=True)
    chebi_ids = models.TextField(blank=True, null=True)

    kingdom = models.CharField(max_length=254, blank=True, null=True)
    superclass = models.CharField(max_length=254, blank=True, null=True)
    _class = models.CharField(max_length=254, blank=True, null=True)
    subclass = models.CharField(max_length=254, blank=True, null=True)
    direct_parent = models.CharField(max_length=254, blank=True, null=True)
    molecular_framework = models.TextField(max_length=254, blank=True, null=True)
    predicted_lipidmaps_terms = models.TextField(blank=True, null=True)

    assay = models.TextField(blank=True, null=True)
    extraction = models.TextField(blank=True, null=True)
    spe = models.TextField(blank=True, null=True)
    spe_frac = models.TextField(blank=True, null=True)
    chromatography = models.TextField(blank=True, null=True)
    measurement = models.TextField(blank=True, null=True)
    polarity = models.TextField(blank=True, null=True)
    organisms = models.TextField(blank=True, null=True)

    lcmsdimsbool = models.BooleanField(blank=True, null=True)
    nmrbool = models.BooleanField(blank=True, null=True)
    gcmsbool = models.BooleanField(blank=True, null=True)
    smbool = models.BooleanField(blank=True, null=True)
    metfragbool = models.BooleanField(blank=True, null=True)
    siriusbool = models.BooleanField(blank=True, null=True)
    mzcloudsmbool = models.BooleanField(blank=True, null=True)
    galaxysmbool = models.BooleanField(blank=True, null=True)
    gnpssmbool = models.BooleanField(blank=True, null=True)

    msi_level = models.CharField(max_length=254, blank=True, null=True)


    def __str__(self):  # __unicode__ on Python 2
        if self.compound_name:
            return self.compound_name
        else:
            return '{}'.format(self.id)

    def pubchem_id_single(self):
        if self.pubchem_cids:
            return self.pubchem_cids.split(',')[0]
        else:
            return ''

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






