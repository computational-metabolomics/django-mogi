from __future__ import unicode_literals, print_function
from django import forms
from mogi.models import models_annotations

class CombinedAnnotationDownloadForm(forms.ModelForm):

    class Meta:

        model = models_annotations.CombinedAnnotationDownload
        fields = ('rank',)

class UploadAdductsForm(forms.Form):
    adduct_rules = forms.FileField(label='Adduct rules (csv)',
                              help_text='The adduct rules used (for example from CAMERA)',
                                required=True, widget=forms.FileInput(attrs={'accept': ".csv"}))


    def check_adduct_rules(self, adduct_rules):

        if not adduct_rules.name.endswith('.csv'):
            raise forms.ValidationError('Invalid file type')

        with open(adduct_rules.file, 'r') as csvfile:
            try:
                csvreader = csv.reader(csvfile)
            except csv.Error:
                raise forms.ValidationError('Failed to parse the CSV file')

        return adduct_rules
