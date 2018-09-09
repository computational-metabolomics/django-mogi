# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os

from django.db import models
from django.utils.functional import cached_property

from galaxy.models import GalaxyInstanceTracking, FilesToGalaxyDataLibraryParam, HistoryData
from misa.models import Investigation, Assay, Study

from mbrowse.models import CAnnotation, Compound, CPeakGroupMeta


################################################################################################################
# ISA - Galaxy interfacing
################################################################################################################
class ISAGalaxyTrack(models.Model):
    galaxyinstancetracking = models.ForeignKey(GalaxyInstanceTracking, on_delete=models.CASCADE, null=False,
                                               blank=False)
    isatogalaxyparam = models.ForeignKey(FilesToGalaxyDataLibraryParam, on_delete=models.CASCADE)
    investigation = models.ForeignKey(Investigation, on_delete=models.CASCADE)
    galaxy_id = models.CharField(max_length=250)

    def __str__(self):              # __unicode__ on Python 2
        return self.galaxy_id

class HistoryDataMOGI(HistoryData):
    investigation = models.ForeignKey(Investigation, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):              # __unicode__ on Python 2
        return self.investigation.name




class CPeakGroupMetaMOGI(CPeakGroupMeta):
    historydatamogi = models.ForeignKey(HistoryDataMOGI, on_delete=models.CASCADE)
    assay = models.ManyToManyField(Assay)

    @cached_property
    def assay_names(self):
        return ', '.join(l.name for l in self.assay.all())


    @cached_property
    def study_names(self):
        return ', '.join(l['study__name'] for l in self.assay.all().values('study__name'))

    @cached_property
    def filename(self):
        return os.path.basename(self.metabinputdata.gfile.data_file.name)

    @cached_property
    def filepath(self):
        return self.metabinputdata.gfile.data_file






class CAnnotationMOGI(models.Model):
    cannotation = models.OneToOneField(CAnnotation)
    # investigation_names = models.CharField(max_length=100, null=True, blank=True)

    # originally as properties but took too long calculate. Quicker (to save at the point of upload)
    @property
    def investigation_names(self):
        m = self.cannotation.cpeakgroup.cpeakgroupmeta.metabinputdata
        hdm = HistoryDataMOGI.objects.get(metabinputdata=m)
        return hdm.investigation.name

    @property
    def study_names(self):
        cpg = self.cannotation.cpeakgroup

        return ', '.join(a.name for a in Study.objects.filter(assay__assaydetail__assayrun__run__mfile__xcmsfileinfo__cpeak__cpeakgroup=cpg).distinct())

    @property
    def assay_names(self):
        cpg = self.cannotation.cpeakgroup
        return ', '.join(a.name for a in Assay.objects.filter(assaydetail__assayrun__run__mfile__xcmsfileinfo__cpeak__cpeakgroup=cpg).distinct())

    @property
    def galaxy_history_data_name(self):
        # for mogi only
        m = self.cannotation.cpeakgroup.cpeakgroupmeta.metabinputdata
        hdm = HistoryDataMOGI.objects.get(metabinputdata=m)
        return hdm.name

    @property
    def galaxy_history_name(self):
        # for mogi only
        m = self.cannotation.cpeakgroup.cpeakgroupmeta.metabinputdata
        hdm = HistoryDataMOGI.objects.get(metabinputdata=m)
        return hdm.history.name




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
