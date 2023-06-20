from __future__ import unicode_literals, print_function
from django import forms
from dal import autocomplete

from mogi.models import models_compounds

class UploadCompoundsForm(forms.ModelForm):

    class Meta:

        model = models_compounds.UploadCompounds
        fields = ('data_file',)
