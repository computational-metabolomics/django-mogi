import django_filters
from mogi.models import models_search


class SearchFragResultFilter(django_filters.FilterSet):

    class Meta:
        model = models_search.SearchFragResult
        fields = {
            'dpc': ['gt', 'lt'],
            'l_prec_mz': ['gt', 'lt'],
            'q_prec_mz': ['gt', 'lt'],
            'ppm_diff_prec': ['gt', 'lt'],
            'rt': ['gt', 'lt'],
            'spectrum_type': ['contains'],
            'well': ['contains'],
            'dataset__id': ['gt', 'lt'],
        }
