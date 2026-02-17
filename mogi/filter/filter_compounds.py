import django_filters
from mogi.models import models_compounds


class CompoundFilter(django_filters.FilterSet):
    BOOLEAN_FILTER_CHOICES = (
        ('unknown', 'Unknown'),
        ('true', 'True'),
        ('false', 'False'),
    )

    monoisotopic_exact_mass__gt = django_filters.NumberFilter(
        field_name='monoisotopic_exact_mass',
        lookup_expr='gt'
    )
    monoisotopic_exact_mass__lt = django_filters.NumberFilter(
        field_name='monoisotopic_exact_mass',
        lookup_expr='lt'
    )

    natural_product_inchikey1 = django_filters.ChoiceFilter(
        method='filter_natural_product_inchikey1',
        choices=BOOLEAN_FILTER_CHOICES
    )
    lcmsdimsbool = django_filters.ChoiceFilter(method='filter_lcmsdimsbool', choices=BOOLEAN_FILTER_CHOICES)
    nmrbool = django_filters.ChoiceFilter(method='filter_nmrbool', choices=BOOLEAN_FILTER_CHOICES)
    gcmsbool = django_filters.ChoiceFilter(method='filter_gcmsbool', choices=BOOLEAN_FILTER_CHOICES)
    smbool = django_filters.ChoiceFilter(method='filter_smbool', choices=BOOLEAN_FILTER_CHOICES)
    metfragbool = django_filters.ChoiceFilter(method='filter_metfragbool', choices=BOOLEAN_FILTER_CHOICES)
    siriusbool = django_filters.ChoiceFilter(method='filter_siriusbool', choices=BOOLEAN_FILTER_CHOICES)
    mzcloudsmbool = django_filters.ChoiceFilter(method='filter_mzcloudsmbool', choices=BOOLEAN_FILTER_CHOICES)
    galaxysmbool = django_filters.ChoiceFilter(method='filter_galaxysmbool', choices=BOOLEAN_FILTER_CHOICES)
    gnpssmbool = django_filters.ChoiceFilter(method='filter_gnpssmbool', choices=BOOLEAN_FILTER_CHOICES)

    @staticmethod
    def _apply_boolean_filter(queryset, field_name, value):
        value_normalized = str(value).strip().lower()
        if value_normalized == 'true':
            return queryset.filter(**{field_name: True})
        if value_normalized == 'false':
            return queryset.filter(**{field_name: False})
        return queryset

    @staticmethod
    def filter_natural_product_inchikey1(queryset, name, value):
        return CompoundFilter._apply_boolean_filter(queryset, 'natural_product_inchikey1', value)

    @staticmethod
    def filter_lcmsdimsbool(queryset, name, value):
        return CompoundFilter._apply_boolean_filter(queryset, 'lcmsdimsbool', value)

    @staticmethod
    def filter_nmrbool(queryset, name, value):
        return CompoundFilter._apply_boolean_filter(queryset, 'nmrbool', value)

    @staticmethod
    def filter_gcmsbool(queryset, name, value):
        return CompoundFilter._apply_boolean_filter(queryset, 'gcmsbool', value)

    @staticmethod
    def filter_smbool(queryset, name, value):
        return CompoundFilter._apply_boolean_filter(queryset, 'smbool', value)

    @staticmethod
    def filter_metfragbool(queryset, name, value):
        return CompoundFilter._apply_boolean_filter(queryset, 'metfragbool', value)

    @staticmethod
    def filter_siriusbool(queryset, name, value):
        return CompoundFilter._apply_boolean_filter(queryset, 'siriusbool', value)

    @staticmethod
    def filter_mzcloudsmbool(queryset, name, value):
        return CompoundFilter._apply_boolean_filter(queryset, 'mzcloudsmbool', value)

    @staticmethod
    def filter_galaxysmbool(queryset, name, value):
        return CompoundFilter._apply_boolean_filter(queryset, 'galaxysmbool', value)

    @staticmethod
    def filter_gnpssmbool(queryset, name, value):
        return CompoundFilter._apply_boolean_filter(queryset, 'gnpssmbool', value)

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
