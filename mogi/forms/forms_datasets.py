from __future__ import unicode_literals, print_function
from django import forms
from dal import autocomplete

from mogi.models import models_datasets

class UploadDatasetsForm(forms.ModelForm):

    class Meta:

        model = models_datasets.UploadDatasets
        fields = ('data_file',)
