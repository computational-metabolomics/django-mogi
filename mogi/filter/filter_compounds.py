import django_filters
from mogi.models import models_compounds


class CompoundFilter(django_filters.FilterSet):

    class Meta:
        model = models_compounds.Compound
        fields = {
            'exact_mass': ['gt', 'lt'],
        }

