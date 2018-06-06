from mogi.models import CAnnotationMOGI

import django_filters

class CAnotationMOGIFilter(django_filters.FilterSet):

    class Meta:
        model = CAnnotationMOGI
        fields = {
            'cannotation__mzmed': ['gt', 'lt'],
            'cannotation__rtmed': ['gt', 'lt'],
            'cannotation__name': ['contains'],
            'assay_names': ['contains'],
            'study_names': ['contains'],
            'investigation_names': ['contains']
            # 'msms_count': ['range'],
            # 'accessible': ['isnull']
        }
