from __future__ import unicode_literals, print_function
from django import forms
from dal import autocomplete

from mogi.models import models_inputdata

class MetabInputDataForm(forms.ModelForm):

    class Meta:

        model = models_inputdata.MetabInputData
        fields = ('data_file', 'assay', 'polaritytype', 'public')

        widgets = {
            'assay': autocomplete.ModelSelect2Multiple(url='assay-autocomplete'),
            'polaritytype': autocomplete.ModelSelect2(url='polaritytype-autocomplete'),
        }
