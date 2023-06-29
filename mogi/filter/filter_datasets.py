import django_filters
from mogi.models import models_datasets


class DatasetFilter(django_filters.FilterSet):

    class Meta:
        model = models_datasets.Dataset
        fields = {
            'assay__name': ['contains'],
            'polarity__type': ['contains'],
            'metabolite_standard': ['exact'],
            'fractionation': ['exact']

        }
