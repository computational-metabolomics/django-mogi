from mogi.models import CAnnotationMOGI

import django_filters

class CAnnotationMOGIFilter(django_filters.FilterSet):

    mzmed_gt = django_filters.NumberFilter(name='cannotation__cpeakgroup__mzmed', lookup_expr='gt', label='mzmed >')
    mzmed_lt = django_filters.NumberFilter(name='cannotation__cpeakgroup__mzmed', lookup_expr='lt', label='mzmed <')

    rtmed_gt = django_filters.NumberFilter(name='cannotation__cpeakgroup__rtmed', lookup_expr='gt', label='rtmed >')
    rtmed_lt = django_filters.NumberFilter(name='cannotation__cpeakgroup__rtmed', lookup_expr='lt',  label='rtmed <')

    compound_name = django_filters.CharFilter(name='cannotation__compound__name', lookup_expr='contains', label='compound name')

    class Meta:
        model = CAnnotationMOGI
        fields = ('mzmed_gt', 'mzmed_lt', 'rtmed_gt', 'rtmed_lt', 'compound_name')