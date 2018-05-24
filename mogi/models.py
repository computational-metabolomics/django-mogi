# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models

from galaxy.models import GalaxyInstanceTracking, FilesToGalaxyDataLibraryParam, HistoryData
from misa.models import Investigation


################################################################################################################
# ISA - Galaxy interfacing
################################################################################################################
class ISAGalaxyTrack(models.Model):
    galaxyinstancetracking = models.ForeignKey(GalaxyInstanceTracking, on_delete=models.CASCADE, null=False,
                                               blank=False)
    isatogalaxyparam = models.ForeignKey(FilesToGalaxyDataLibraryParam, on_delete=models.CASCADE)
    investigation = models.ForeignKey(Investigation, on_delete=models.CASCADE)
    galaxy_id = models.CharField(max_length=250, unique=True)

    def __str__(self):              # __unicode__ on Python 2
        return self.galaxy_id

class HistoryDataMOGI(HistoryData):
    investigation = models.ForeignKey(Investigation, on_delete=models.CASCADE, null=True, blank=True)


