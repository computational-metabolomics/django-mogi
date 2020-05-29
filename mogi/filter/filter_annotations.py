import django_filters
from mogi.models import models_annotations

class CombinedAnnotationFilter(django_filters.FilterSet):

    mzm_gt = django_filters.NumberFilter(field_name='combinedpeak__mz', lookup_expr='gt', label='mz >')
    mzm_lt = django_filters.NumberFilter(field_name='combinedpeak__mz', lookup_expr='lt', label='mz <')
    #
    rt_gt = django_filters.NumberFilter(field_name='combinedpeak__rt', lookup_expr='gt', label='rt >')
    rt_lt = django_filters.NumberFilter(field_name='combinedpeak__rt', lookup_expr='lt', label='rt <')

    ms_type = django_filters.CharFilter(field_name='combinedpeak__ms_type', lookup_expr='contains',
                                        label='MS type')




    compound_name = django_filters.CharFilter(field_name='compound__name', lookup_expr='contains', label='Compound name')

    # def __init__(self, *args, **kwargs):
    #     super(CombinedAnnotationFilter, self).__init__(*args, **kwargs)
    #     # self.filters['cpeakgroup_mzmed'].label = 'mzmed'
    #     # self.filters['cpeakgroup_rtmed'].label = 'rtmed'

    class Meta:
        model = models_annotations.CombinedAnnotation
        # fields = ('mzmed_gt', 'mzmed_lt', 'rtmed_gt', 'rtmed_lt', 'compound_name')
        fields = {
            'rank': ['gt', 'lt'],
            'total_wscore': ['gt', 'lt'],
            'spectral_matching_score': ['gt', 'lt'],
        }


class CombinedAnnotationDownloadResultFilter(django_filters.FilterSet):
    # many to many assay
    class Meta:
        model = models_annotations.CombinedAnnotationDownloadResult
        fields = {
            'created': ['contains'],
        }


