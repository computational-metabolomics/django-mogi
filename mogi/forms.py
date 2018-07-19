# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# general python
from bioblend.galaxy import GalaxyInstance
from bioblend.galaxy.workflows import WorkflowClient
from bioblend.galaxy.client import ConnectionError

# standard django
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django import forms
from django.contrib.auth.models import User


from galaxy.forms import FilesToGalaxyDataLibraryParamForm, HistoryDataForm, WorkflowRunForm
from galaxy.models import FilesToGalaxyDataLibraryParam
from mogi.models import HistoryDataMOGI

# django external apps
# none

# django custom user external apps
# none


class ISAtoGalaxyParamForm(FilesToGalaxyDataLibraryParamForm):

    class Meta:
        model = FilesToGalaxyDataLibraryParam
        fields = ('galaxyinstancetracking', 'remove', 'link2files', 'ftp')



class ISAWorkflowRunForm(WorkflowRunForm):
    auto_samplelist = forms.BooleanField(required=False)




class HistoryMogiDataForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(HistoryMogiDataForm, self).__init__(*args, **kwargs)
        self.fields['history'].disabled = True
        self.fields['name'].disabled = True

    class Meta:
        model = HistoryDataMOGI
        fields = ('history', 'name', 'investigation')

