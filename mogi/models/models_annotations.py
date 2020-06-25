# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import os
from datetime import datetime
from django.db import models
from django.utils import timezone
from django.conf import settings


class MetaboliteAnnotationApproach(models.Model):
    name = models.CharField(unique=True, null=True, blank=True, max_length=254)
    description = models.TextField(null=False, blank=False)


class ScoreType(models.Model):
    metaboliteannotationapproach = models.ForeignKey(MetaboliteAnnotationApproach, on_delete=models.CASCADE)
    name = models.CharField(null=True, blank=True, max_length=254)
    description = models.TextField()

    class Meta:
        unique_together = (("name", "metaboliteannotationapproach"),)


class DetailType(models.Model):
    metaboliteannotationapproach = models.ForeignKey(MetaboliteAnnotationApproach, on_delete=models.CASCADE)
    name = models.CharField(null=True, blank=True, max_length=254)
    description = models.TextField()

    class Meta:
        unique_together = (("name", "metaboliteannotationapproach"),)


class MetaboliteAnnotationDetail(models.Model):
    metaboliteannotation = models.ForeignKey('MetaboliteAnnotation', on_delete=models.CASCADE, null=True, blank=True)
    detailtype = models.ForeignKey('DetailType', on_delete=models.CASCADE)
    detail_value = models.CharField(null=True, blank=True, max_length=1000)


class MetaboliteAnnotationScore(models.Model):
    metaboliteannotation = models.ForeignKey('MetaboliteAnnotation', on_delete=models.CASCADE, null=True, blank=True)
    scoretype = models.ForeignKey('ScoreType', on_delete=models.CASCADE)
    score_value = models.FloatField()


class MetaboliteAnnotation(models.Model):
    metabinputdata = models.ForeignKey('MetabInputData', on_delete=models.CASCADE)

    idi = models.IntegerField()
    # Annotation of Spectral peak (i.e. ms1 lookup)
    speak = models.ForeignKey('SPeak', on_delete=models.CASCADE, null=True, blank=True)

    # Annotation of a set spectral peaks (i.e.  fragmentation spectra)
    speakmeta = models.ForeignKey('SPeakMeta', on_delete=models.CASCADE, null=True, blank=True)

    # Annotation of chromotographic peaks)
    cpeakgroup = models.ForeignKey('CPeakGroup', on_delete=models.CASCADE, null=True, blank=True)

    # Approach used
    metaboliteannotationapproach = models.ForeignKey('MetaboliteAnnotationApproach', on_delete=models.CASCADE)

    # Annotation of compound by full inchikey
    inchikey = models.CharField(max_length=254, blank=True, null=True)

    # annotation of compound by partial inchikey (we don't link this as a foreign key)
    inchikey1 = models.CharField(max_length=254, blank=True, null=True)

    # Annotation of compound by library spectra
    libraryspectrameta = models.ForeignKey('LibrarySpectraMeta', on_delete=models.CASCADE, null=True, blank=True,
                                           related_name='libraryspectrameta')

    def __str__(self):              # __unicode__ on Python 2
        return '{} {}'.format(self.id, self.idi)


class CombinedAnnotationConcat(models.Model):
    # This summarises the annotations in concatenated format (e.g. only 1 row per peak)
    combinedpeak = models.OneToOneField('CombinedPeak', on_delete=models.CASCADE, primary_key=True)
    top_score = models.FloatField(null=True, blank=True)
    concat_score = models.CharField(max_length=1000, blank=True, null=True)
    concat_inchikey = models.CharField(max_length=1000, blank=True, null=True)
    concat_name = models.CharField(max_length=1000, blank=True, null=True)
    concat_adduct = models.CharField(max_length=1000, blank=True, null=True)


class CompoundAnnotationSummary(models.Model):
    compound = models.OneToOneField('Compound', on_delete=models.CASCADE, primary_key=True)
    top_score = models.FloatField(null=True, blank=True)
    top_rank = models.IntegerField(null=True, blank=True)
    top_score_pos = models.FloatField(null=True, blank=True)
    top_score_neg = models.FloatField(null=True, blank=True)
    top_rank_pos = models.IntegerField(null=True, blank=True)
    top_rank_neg = models.IntegerField(null=True, blank=True)

    assays = models.CharField(max_length=1000)


class CombinedAnnotation(models.Model):
    # This summarises all the annotations and peaks (all the essential information from the DMA project can be found
    # from this table). As this table is very large it was required to hard code some elements and some aspects are
    # columns are "shortcuts" to prevent too many long joins and more complicated joins
    combinedpeak = models.ForeignKey('CombinedPeak', on_delete=models.CASCADE)

    compound = models.ForeignKey('Compound', on_delete=models.CASCADE, null=True)

    compound_annotated_adduct = models.CharField(max_length=1000, blank=True, null=True)

    ms1_lookup_score = models.FloatField(null=True, blank=True)
    ms1_lookup_wscore = models.FloatField(null=True, blank=True)

    spectral_matching_score = models.FloatField(null=True, blank=True)
    spectral_matching_wscore = models.FloatField(null=True, blank=True)

    metfrag_score = models.FloatField(null=True, blank=True)
    metfrag_wscore = models.FloatField(null=True, blank=True)

    sirius_csifingerid_score = models.FloatField(null=True, blank=True)
    sirius_csifingerid_wscore = models.FloatField(null=True, blank=True)

    biosim_max_score = models.FloatField(null=True, blank=True)
    biosim_wscore = models.FloatField(null=True, blank=True)

    total_wscore = models.FloatField(null=True, blank=True)
    rank = models.IntegerField(null=True, blank=True)


    def __str__(self):              # __unicode__ on Python 2
        return '{} {}'.format(self.id, self.compound)

    # @property
    # def investigation_names(self):
    #     m = self.combinedannotation.cpeakgroup.cpeakgroupmeta.metabinputdata
    #     hdm = HistoryDataMOGI.objects.get(metabinputdata=m)
    #     return hdm.investigation.name
    #
    # @property
    # def study_names(self):
    #     cpg = self.combinedannotation.cpeakgroup
    #
    #     return ', '.join(a.name for a in Study.objects.filter(assay__assaydetail__run__mfile__xcmsfileinfo__cpeak__cpeakgroup=cpg).distinct())
    #
    # @property
    # def assay_names(self):
    #     cpg = self.combinedannotation.cpeakgroup
    #     return ', '.join(a.name for a in Assay.objects.filter(assaydetail__run__mfile__xcmsfileinfo__cpeak__cpeakgroup=cpg).distinct())
    #
    # @property
    # def galaxy_history_data_name(self):
    #     # for mogi only
    #     m = self.combinedannotation.cpeakgroup.cpeakgroupmeta.metabinputdata
    #     hdm = HistoryDataMOGI.objects.get(metabinputdata=m)
    #     return hdm.name
    #
    # @property
    # def galaxy_history_name(self):
    #     # for mogi only
    #     m = self.combinedannotation.cpeakgroup.cpeakgroupmeta.metabinputdata
    #     hdm = HistoryDataMOGI.objects.get(metabinputdata=m)
    #     return hdm.history.name


class CombinedAnnotationWeightedScore(models.Model):
    combinedannotation = models.ForeignKey('CombinedAnnotation', on_delete=models.CASCADE)
    # Joins take too long with this foreign key - so we just save the score value again
    # metaboliteannotationscore = models.ForeignKey('MetaboliteAnnotationScore', on_delete=models.CASCADE)
    scoretype = models.ForeignKey('ScoreType', on_delete=models.CASCADE)
    score = models.FloatField(null=True, blank=True)
    wscore = models.FloatField(null=True, blank=True)


class CombinedAnnotationDownload(models.Model):
    rank = models.IntegerField(default=0, null=False, blank=False, help_text='What level of ranked peaks to include'
                                                                             ' (leave at 0 to include all)')

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, help_text='The user requesting '
                                                                                           'download', null=True,
                             blank=True)


def data_file_store(instance, filename):
    now = datetime.now()
    return os.path.join('data', 'cannoation_download_results', now.strftime("%Y_%m_%d"), filename)


class CombinedAnnotationDownloadResult(models.Model):
    annotation_file = models.FileField(upload_to=data_file_store, blank=True, null=True)
    created = models.DateTimeField(default=timezone.now)
    combinedannotationdownload = models.ForeignKey('CombinedAnnotationDownload', on_delete=models.CASCADE)



################################################################################################################
# Adduct and isotope annotations
################################################################################################################
class AdductRule(models.Model):
    adduct_type = models.CharField(max_length=255, blank=False, null=False, unique=True)
    nmol = models.IntegerField()
    charge = models.IntegerField()
    massdiff = models.FloatField()
    oidscore = models.FloatField()
    quasi = models.FloatField()
    ips = models.FloatField()
    frag_score = models.FloatField(null=True, blank=True)

    def __str__(self):              # __unicode__ on Python 2
        return self.adduct_type


class Adduct(models.Model):
    idi = models.IntegerField()
    adductrule = models.ForeignKey('AdductRule', on_delete=models.CASCADE)
    cpeakgroup = models.ForeignKey('CPeakGroup', on_delete=models.CASCADE)
    neutralmass = models.ForeignKey('NeutralMass', on_delete=models.CASCADE)


class Isotope(models.Model):
    idi = models.IntegerField()
    cpeakgroup1 = models.ForeignKey('CPeakGroup', on_delete=models.CASCADE, related_name='cpeakgroup1')
    cpeakgroup2 = models.ForeignKey('CPeakGroup', on_delete=models.CASCADE, related_name='cpeakgroup2')
    iso = models.IntegerField()
    charge = models.IntegerField()
    metabinputdata = models.ForeignKey('MetabInputData', on_delete=models.CASCADE)


class NeutralMass(models.Model):
    idi = models.IntegerField()
    nm = models.FloatField(blank=False, null=False)
    ips = models.IntegerField(blank=True, null=True)
    metabinputdata = models.ForeignKey('MetabInputData', on_delete=models.CASCADE)

