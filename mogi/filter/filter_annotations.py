import django_filters
from mogi.models import models_annotations


class CombinedAnnotationFilter(django_filters.FilterSet):
    inchikey__contains = django_filters.CharFilter(field_name='inchikey', lookup_expr='contains')
    compound_name__contains = django_filters.CharFilter(field_name='compound_name', lookup_expr='contains')
    ms_type__contains = django_filters.CharFilter(field_name='ms_type', lookup_expr='contains')
    sid__gt = django_filters.NumberFilter(field_name='sid', lookup_expr='gt')
    sid__lt = django_filters.NumberFilter(field_name='sid', lookup_expr='lt')
    grpid__gt = django_filters.NumberFilter(field_name='grpid', lookup_expr='gt')
    grpid__lt = django_filters.NumberFilter(field_name='grpid', lookup_expr='lt')
    grp_name__contains = django_filters.CharFilter(field_name='grp_name', lookup_expr='contains')
    mz__gt = django_filters.NumberFilter(field_name='mz', lookup_expr='gt')
    mz__lt = django_filters.NumberFilter(field_name='mz', lookup_expr='lt')
    rt__gt = django_filters.NumberFilter(field_name='rt', lookup_expr='gt')
    rt__lt = django_filters.NumberFilter(field_name='rt', lookup_expr='lt')
    well__contains = django_filters.CharFilter(field_name='well', lookup_expr='contains')
    sm_score__gt = django_filters.NumberFilter(field_name='sm_score', lookup_expr='gt')
    sm_score__lt = django_filters.NumberFilter(field_name='sm_score', lookup_expr='lt')
    metfrag_score__gt = django_filters.NumberFilter(field_name='metfrag_score', lookup_expr='gt')
    metfrag_score__lt = django_filters.NumberFilter(field_name='metfrag_score', lookup_expr='lt')
    sirius_score__gt = django_filters.NumberFilter(field_name='sirius_score', lookup_expr='gt')
    sirius_score__lt = django_filters.NumberFilter(field_name='sirius_score', lookup_expr='lt')
    ms1_lookup_score__gt = django_filters.NumberFilter(field_name='ms1_lookup_score', lookup_expr='gt')
    ms1_lookup_score__lt = django_filters.NumberFilter(field_name='ms1_lookup_score', lookup_expr='lt')
    biosim_max_score__gt = django_filters.NumberFilter(field_name='biosim_max_score', lookup_expr='gt')
    biosim_max_score__lt = django_filters.NumberFilter(field_name='biosim_max_score', lookup_expr='lt')
    wscore__gt = django_filters.NumberFilter(field_name='wscore', lookup_expr='gt')
    wscore__lt = django_filters.NumberFilter(field_name='wscore', lookup_expr='lt')
    rank__gt = django_filters.NumberFilter(field_name='rank', lookup_expr='gt')
    rank__lt = django_filters.NumberFilter(field_name='rank', lookup_expr='lt')
    adduct_overall__contains = django_filters.CharFilter(field_name='adduct_overall', lookup_expr='contains')

    class Meta:
        model = models_annotations.CombinedAnnotation
        fields = {
            'inchikey': ['contains'],
            'compound_name': ['contains'],
            'ms_type': ['contains'],
            'sid': ['gt', 'lt'],
            'grpid': ['gt', 'lt'],
            'grp_name': ['contains'],
            'mz': ['gt', 'lt'],
            'rt': ['gt', 'lt'],
            'well': ['contains'],
            'sm_score': ['gt', 'lt'],
            'metfrag_score': ['gt', 'lt'],
            'sirius_score': ['gt', 'lt'],
            'ms1_lookup_score': ['gt', 'lt'],
            'biosim_max_score': ['gt', 'lt'],
            'wscore': ['gt', 'lt'],
            'rank': ['gt', 'lt'],
            'adduct_overall': ['contains']

        }


class SpectralMatchingFilter(django_filters.FilterSet):
    dpc__gt = django_filters.NumberFilter(field_name='dpc', lookup_expr='gt')
    dpc__lt = django_filters.NumberFilter(field_name='dpc', lookup_expr='lt')

    class Meta:
        model = models_annotations.SpectralMatching
        fields = {
            'dpc': ['gt', 'lt']
        }


class MetFragFilter(django_filters.FilterSet):
    score__gt = django_filters.NumberFilter(field_name='score', lookup_expr='gt')
    score__lt = django_filters.NumberFilter(field_name='score', lookup_expr='lt')

    class Meta:
        model = models_annotations.MetFrag
        fields = {
            'score': ['gt', 'lt']
        }


class SiriusCSIFingerIDFilter(django_filters.FilterSet):
    rank__gt = django_filters.NumberFilter(field_name='rank', lookup_expr='gt')
    rank__lt = django_filters.NumberFilter(field_name='rank', lookup_expr='lt')

    class Meta:
        model = models_annotations.SiriusCSIFingerID
        fields = {
            'rank': ['gt', 'lt']
        }