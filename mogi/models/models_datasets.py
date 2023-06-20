# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
from django.db import models

from gfiles.models import GenericFile, data_file_store

class UploadDatasets(GenericFile):
    def __str__(self):  # __unicode__ on Python 2
        return '{} {}'.format(self.id, self.original_filename)

class Dataset(models.Model):
    assay = models.ForeignKey('Assay', on_delete=models.CASCADE, blank=True, null=True)

    galaxy_history_url = models.TextField(blank=True, null=True)

    metabolite_standard = models.BooleanField(default=False, blank=False, null=False)
    fractionation = models.BooleanField(default=False, blank=False, null=False)

    sqlite = models.FileField(upload_to=data_file_store, blank=True, null=True, max_length=1000)
    tsv = models.FileField(upload_to=data_file_store, blank=True, null=True, max_length=1000)

    polarity = models.ForeignKey('PolarityType', on_delete=models.CASCADE, null=True, blank=True)


    def __str__(self):  # __unicode__ on Python 2
        return '{}'.format(self.id)

