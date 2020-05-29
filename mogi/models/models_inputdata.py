# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


from gfiles.models import GenericFile


class MetabInputData(GenericFile):
    polaritytype = models.ForeignKey('PolarityType', on_delete=models.CASCADE, null=True)

    historydatamogi = models.ForeignKey('HistoryDataMOGI', on_delete=models.CASCADE, null=True, blank=True)
    assay = models.ManyToManyField('Assay')

    public = models.BooleanField(default=False, help_text="If public, then anybody can see this dataset")

    # save as text. Makes it easier to filter at later stages (' difficult to filter on properties)
    assay_names = models.CharField(max_length=1000, blank=True, null=True)
    study_names = models.CharField(max_length=1000, blank=True, null=True)
    investigation_names = models.CharField(max_length=1000, blank=True, null=True)

    def __str__(self):  # __unicode__ on Python 2
        return '{}'.format(self.original_filename)


    def delete_dependents(self):

        print('delete annotation')
        #csi = CSIFingerIDAnnotation.objects.filter(s_peak_meta__cpeak__cpeakgroup__cpeakgroupmeta=self.pk)
        #big_delete(csi, CSIFingerIDAnnotation, 100)

        print('delete metfrag')
        #mfa = MetFragAnnotation.objects.filter(s_peak_meta__cpeak__cpeakgroup__cpeakgroupmeta=self.pk)
        #big_delete(mfa, MetFragAnnotation, 100)

        print('delete speakmeta')
        #spm = SPeakMeta.objects.filter(cpeak__cpeakgroup__cpeakgroupmeta=self.pk)
        #big_delete(spm, SPeakMeta)

        print('delete cpeaks')
        #cp = CPeak.objects.filter(cpeakgroup__cpeakgroupmeta=self.pk)
        #big_delete(cp, CPeak)

        # delete cpeakgroups
        print('delete cpeakgroup')
        #cpg = CPeakGroup.objects.filter(cpeakgroupmeta=self.pk)
        #big_delete(cpg, CPeakGroup)

    def delete(self, *args, **kwargs):
        self.delete_dependents()
        super(MetabInputData, self).delete(*args, **kwargs)
