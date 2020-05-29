from django import forms
from mogi.models import models_search
from dal import autocomplete

class SearchFragParamForm(forms.ModelForm):
    class Meta:
        model = models_search.SearchFragParam
        fields = ['description', 'mz_precursor', 'products', 'ppm_precursor_tolerance', 'ppm_product_tolerance',
                  'dot_product_score_threshold', 'precursor_ion_purity', 'filter_on_precursor', 'ra_diff_threshold',
                  'ra_threshold', 'polarity']


class SearchMzParamForm(forms.ModelForm):
    class Meta:
        model = models_search.SearchMzParam
        fields = ['description', 'masses', 'ppm_target_tolerance',
                  'ppm_library_tolerance', 'ms_level', 'polarity', 'investigation', 'study', 'assay']
        widgets = {
            'investigation': autocomplete.ModelSelect2(url='investigation-autocomplete'),
            'study': autocomplete.ModelSelect2(url='study-autocomplete'),
            'assay': autocomplete.ModelSelect2(url='assay-autocomplete'),

        }


class SearchNmParamForm(forms.ModelForm):
    class Meta:
        model = models_search.SearchNmParam
        fields = ['description', 'masses', 'ppm_target_tolerance',
                  'ppm_library_tolerance', 'polarity']