import django_filters
from mogi.models import models_datasets


class DatasetFilter(django_filters.FilterSet):
    BOOLEAN_FILTER_CHOICES = (
        ('unknown', 'Unknown'),
        ('true', 'True'),
        ('false', 'False'),
    )

    metabolite_standard = django_filters.ChoiceFilter(
        method='filter_metabolite_standard',
        choices=BOOLEAN_FILTER_CHOICES
    )
    fractionation = django_filters.ChoiceFilter(
        method='filter_fractionation',
        choices=BOOLEAN_FILTER_CHOICES
    )

    @staticmethod
    def _apply_boolean_filter(queryset, field_name, value):
        value_normalized = str(value).strip().lower()
        if value_normalized == 'true':
            return queryset.filter(**{field_name: True})
        if value_normalized == 'false':
            return queryset.filter(**{field_name: False})
        return queryset

    @staticmethod
    def filter_metabolite_standard(queryset, name, value):
        return DatasetFilter._apply_boolean_filter(queryset, 'metabolite_standard', value)

    @staticmethod
    def filter_fractionation(queryset, name, value):
        return DatasetFilter._apply_boolean_filter(queryset, 'fractionation', value)

    class Meta:
        model = models_datasets.Dataset
        fields = {
            'assay__name': ['contains'],
            'polarity__type': ['contains'],
            'metabolite_standard': ['exact'],
            'fractionation': ['exact']

        }
