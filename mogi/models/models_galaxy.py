# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from galaxy.models import GalaxyInstanceTracking, FilesToGalaxyDataLibraryParam, HistoryData

from .models_isa import Investigation

#################################################################################################
# ISA - Galaxy interfacing
#################################################################################################
class ISAGalaxyTrack(models.Model):
    galaxyinstancetracking = models.ForeignKey(GalaxyInstanceTracking, on_delete=models.CASCADE, null=False,
                                               blank=False)
    isatogalaxyparam = models.ForeignKey(FilesToGalaxyDataLibraryParam, on_delete=models.CASCADE)
    investigation = models.ForeignKey(Investigation, on_delete=models.CASCADE)
    galaxy_id = models.CharField(max_length=250)

    def __str__(self):              # __unicode__ on Python 2
        return self.galaxy_id



class IncomingGalaxyData(models.Model):
    galaxy_url = models.TextField(max_length=100, null=True, blank=True)
    galaxy_name = models.TextField(max_length=100)
    galaxy_data_id = models.TextField(max_length=100)
    galaxy_history_id = models.TextField(max_length=100)
    galaxy_history_name = models.TextField(max_length=100, null=True, blank=True)
    other_details = models.TextField(max_length=100, null=True, blank=True)
    investigation_name = models.TextField(max_length=100)

    def __str__(self):              # __unicode__ on Python 2
        return self.galaxy_data_id
