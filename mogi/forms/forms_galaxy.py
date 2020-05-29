# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# general python

# standard django
from django import forms

# django external apps
from dal import autocomplete

# django custom user external apps
from galaxy.forms import FilesToGalaxyDataLibraryParamForm, WorkflowRunForm
from galaxy.models import FilesToGalaxyDataLibraryParam

# internal modules
from mogi.models import models_galaxy


class ISAtoGalaxyParamForm(FilesToGalaxyDataLibraryParamForm):

    class Meta:
        model = models_galaxy.FilesToGalaxyDataLibraryParam
        fields = ('galaxyinstancetracking', 'remove', 'link2files', 'ftp')
        widgets = {
            'galaxyinstancetracking': autocomplete.ModelSelect2(url='galaxyinstancetracking-autocomplete'),
        }


class ISAWorkflowRunForm(WorkflowRunForm):
    auto_samplelist = forms.BooleanField(required=False)


class HistoryMogiDataForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(HistoryMogiDataForm, self).__init__(*args, **kwargs)
        self.fields['history'].disabled = True
        self.fields['name'].disabled = True

    class Meta:
        model = models_galaxy.HistoryDataMOGI
        fields = ('history', 'name', 'investigation')

