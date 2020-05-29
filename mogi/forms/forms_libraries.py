import os
from django import forms
from mogi.models import models_libraries


class LibrarySpectraSourceForm(forms.ModelForm):

    msp = forms.FileField(label='library msp file',  required=True,
                          help_text='The library of spectra in msp format')
    class Meta:

        model = models_libraries.LibrarySpectraSource
        fields = ['name', 'description']
