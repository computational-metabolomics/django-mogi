import django_filters
from mogi.models import models_compounds


class CompoundFilter(django_filters.FilterSet):

    class Meta:
        model = models_compounds.Compound
        fields = {
            'monoisotopic_exact_mass': ['gt', 'lt'],
            'inchikey': ['contains'],
            'inchi': ['contains'],
            'smiles': ['contains'],
            'molecular_formula': ['contains'],
            'compound_name': ['contains'],
            'natural_product_inchikey1': ['exact'],
            'pubchem_cids': ['contains'],
            'hmdb_ids': ['contains'],
            'kegg_ids': ['contains'],
            'chebi_ids': ['contains'],
            'kingdom': ['contains'],
            'superclass': ['contains'],
            '_class': ['contains'],
            'subclass': ['contains'],
            'direct_parent': ['contains'],
            'molecular_framework': ['contains'],
            'predicted_lipidmaps_terms': ['contains'],
            'assay': ['contains'],
            'extraction': ['contains'],
            'spe_frac': ['contains'],
            'chromatography': ['contains'],
            'measurement': ['contains'],
            'polarity': ['contains'],
            'lcmsdimsbool': ['exact'],
            'nmrbool': ['exact'],
            'gcmsbool': ['exact'],
            'smbool': ['exact'],
            'metfragbool': ['exact'],
            'siriusbool': ['exact'],
            'mzcloudsmbool': ['exact'],
            'galaxysmbool': ['exact'],
            'gnpssmbool': ['exact'],
            'msi_level': ['contains'],

        }
