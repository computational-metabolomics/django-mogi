import django_filters
from mogi.models import models_peaks, models_isa


class CombinedPeakFilter(django_filters.FilterSet):
    investigation = django_filters.CharFilter('metabinputdata__investigation_names',
                                              lookup_expr='contains', label="Investigation contains")

    study = django_filters.CharFilter('metabinputdata__study_names',
                                      lookup_expr='contains', label="Study contains")

    assay = django_filters.CharFilter('metabinputdata__assay_names',
                                      lookup_expr='contains', label="Assay contains")


    bestscore_gt = django_filters.NumberFilter('combinedannotationconcat__best_score',
                                               label='Best score is greater than')

    bestscore_lt = django_filters.NumberFilter('combinedannotationconcat__best_score',
                               lookup_expr='lt', label='Best score is less than')


    class Meta:
        model = models_peaks.CombinedPeak
        fields = {
            'mz': ['gt', 'lt'],
            'rt': ['gt', 'lt'],
            'rtmin': ['gt', 'lt'],
            'rtmax': ['gt', 'lt'],
            'intensity': ['gt', 'lt'],

            # 'ms_type': ['contains'],
            'camera_adducts': ['contains'],
            'camera_isotopes': ['contains'],

            # 'fraction_match': ['isnull'],
        }


class CPeakGroupFilter(django_filters.FilterSet):

    class Meta:
        model = models_peaks.CPeakGroup
        fields = {
            'mzmed': ['gt', 'lt'],
            'rtmed': ['gt', 'lt'],
            'isotopes': ['contains'],
            'adducts': ['contains']
            # 'msms_count': ['range'],
            # 'accessible': ['isnull']
        }