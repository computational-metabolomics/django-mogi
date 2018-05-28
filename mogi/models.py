# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models

from galaxy.models import GalaxyInstanceTracking, FilesToGalaxyDataLibraryParam, HistoryData
from misa.models import Investigation, Assay

from metab.models import CAnnotation, Compound, CPeakGroupMeta


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


class CPeakGroupMetaMOGI(CPeakGroupMeta):
    historydatamogi = models.ForeignKey(HistoryDataMOGI, on_delete=models.CASCADE)
    assay = models.ManyToManyField(Assay)


class CAnnotationMOGI(CAnnotation):
    galaxy_history = models.ForeignKey(GalaxyInstanceTracking, on_delete=models.CASCADE)
    assay = models.ManyToManyField(Assay)


class AnnotationSummary(models.Model):
    compound = models.ForeignKey(Compound, on_delete=models.CASCADE)
    lcms_ann_level = models.TextField(max_length=100, null=True, blank=True)
    best_score = models.FloatField(null=True, blank=True)
    assays = models.TextField(max_length=100, null=True, blank=True)
    mzmin = models.FloatField(null=True, blank=True)
    mzmax = models.FloatField(max_length=100, null=True, blank=True)

    rtmin = models.FloatField(max_length=100, null=True, blank=True)
    rtmax = models.FloatField(null=True, blank=True)

    def __str__(self):              # __unicode__ on Python 2
        return '{} {}'.format(self.compound, self.lcms_ann_level)
