import django_filters
from mogi.models import models_annotations


class CombinedAnnotationFilter(django_filters.FilterSet):

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

    class Meta:
        model = models_annotations.SpectralMatching
        fields = {
            'dpc': ['gt', 'lt']
        }


class MetFragFilter(django_filters.FilterSet):

    class Meta:
        model = models_annotations.MetFrag
        fields = {
            'score': ['gt', 'lt']
        }


class SiriusCSIFingerIDFilter(django_filters.FilterSet):

    class Meta:
        model = models_annotations.SiriusCSIFingerID
        fields = {
            'rank': ['gt', 'lt']
        }