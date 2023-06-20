from django import forms
import re
from mogi.models import models_search
from dal import autocomplete

class SearchFragParamForm(forms.ModelForm):
    class Meta:
        model = models_search.SearchFragParam
        fields = ['description', 'mz_precursor', 'products', 'ppm_precursor_tolerance', 'ppm_product_tolerance',
                  'dot_product_score_threshold', 'ra_diff_threshold',
                  'ra_threshold', 'polarity', 'fragspectratype', 'metabolite_reference_standard']

    def clean(self):
        cleaned_data = super(SearchFragParamForm, self).clean()
        products_str = cleaned_data.get('products')

        for product in products_str.split('\n'):
            print(product)
            m = re.match(r'^\W*(\d+.\d+)\W*,\W*(\d+.\d+)\W*$', product)
            if not m:
                msg = 'Incorrect fromat (should be decimal separated by comma -' \
                      ' e.g. 100.123, 2000.41). See line {}'.format(product)
                raise forms.ValidationError(msg)

        return cleaned_data

class SearchMzParamForm(forms.ModelForm):
    class Meta:
        model = models_search.SearchMzParam
        fields = ['description', 'masses', 'ppm_target_tolerance',
                  'ppm_library_tolerance', 'ms_level', 'polarity']


class SearchMonoParamForm(forms.ModelForm):
    class Meta:
        model = models_search.SearchMonoParam
        fields = ['description', 'masses', 'ppm_tolerance']
