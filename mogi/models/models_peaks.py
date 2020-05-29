# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from .models_isa import Run, MFile
from .models_inputdata import MetabInputData

try:
    from itertools import zip_longest as zip_longest
except:
    from itertools import izip_longest as zip_longest


class CombinedPeak(models.Model):
    # This summarises all the peaks (including all CPeaks and all SPeak (DIMS)
    metabinputdata = models.ForeignKey('MetabInputData', on_delete=models.CASCADE)

    cpeakgroup = models.ForeignKey('CPeakGroup', on_delete=models.CASCADE, null=True, blank=True)
    speak = models.ForeignKey('SPeak', on_delete=models.CASCADE, null=True, blank=True)

    mz = models.FloatField(null=True, blank=True)
    intensity = models.FloatField(null=True, blank=True)
    rt = models.FloatField(null=True, blank=True)
    rtmin = models.FloatField(null=True, blank=True)
    rtmax = models.FloatField(null=True, blank=True)
    well = models.CharField(max_length=100, blank=True, null=True)

    ms_type = models.CharField(max_length=100, blank=True, null=True)

    fraction_match = models.BooleanField(default=False)
    frag_match = models.BooleanField(default=False)
    camera_adducts = models.CharField(max_length=1000, blank=True, null=True)
    camera_isotopes = models.CharField(max_length=1000, blank=True, null=True)





    def __str__(self):              # __unicode__ on Python 2
        return '{}'.format(self.id)



################################################################################################################
# Scan/spectral peak organisation (including averaged scan peaks, fragmentation data and DIMS)
################################################################################################################
class SPeakMeta(models.Model):
    run = models.ForeignKey(Run, on_delete=models.CASCADE, blank=True, null=True)
    idi = models.IntegerField()
    scan_idi = models.IntegerField(null=True, blank=True)
    precursor_mz = models.FloatField(null=True, blank=True)
    precursor_i = models.FloatField(null=True, blank=True)
    scan_num = models.IntegerField(null=True, blank=True)
    precursor_scan_num = models.IntegerField(null=True, blank=True)
    precursor_nearest = models.IntegerField(null=True, blank=True)
    precursor_rt = models.FloatField(null=True, blank=True)
    ms_level = models.IntegerField(null=True, blank=True)
    metabinputdata = models.ForeignKey(MetabInputData, on_delete=models.CASCADE, blank=True, null=True)

    spectrum_type = models.CharField(max_length=100, blank=True, null=True)
    spectrum_detail = models.CharField(max_length=1000, blank=True, null=True)

    well = models.CharField(max_length=100, blank=True, null=True)
    well_rtmin = models.FloatField(null=True, blank=True)
    well_rtmax = models.FloatField(null=True, blank=True)
    well_rt = models.FloatField(null=True, blank=True)

    cpeakgroup = models.ForeignKey('CPeakGroup', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return '{}'.format(self.id)


class PrecursorIonPurity(models.Model):
    speakmeta = models.ForeignKey(SPeakMeta, on_delete=models.CASCADE)
    a_mz = models.FloatField(null=True, blank=True)
    a_purity = models.FloatField(null=True, blank=True)
    a_pknm = models.FloatField(null=True, blank=True)
    i_mz = models.FloatField(null=True, blank=True)
    i_purity = models.FloatField(null=True, blank=True)
    i_pknm = models.FloatField(null=True, blank=True)
    in_purity = models.FloatField(null=True, blank=True)
    in_pknm = models.FloatField(null=True, blank=True)

    def __str__(self):
        return '{}'.format(self.pk)




class SPeak(models.Model):
    idi = models.IntegerField(blank=True, null=True)
    speakmeta = models.ForeignKey(SPeakMeta, on_delete=models.CASCADE)
    mz = models.FloatField(null=True)
    i = models.FloatField(null=True)
    isotopes = models.CharField(max_length=40, blank=True, null=True)
    adducts = models.CharField(max_length=1000, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Scan peaks"

    def __str__(self):              # __unicode__ on Python 2
        return '{}_{}'.format(round(self.mz, 3), round(self.i))


################################################################################################################
# Chromatography (LC-MS, GC-MS) peak organisation (cpeak)
################################################################################################################
class XCMSFileInfo(models.Model):
    idi = models.IntegerField()
    filename = models.CharField(max_length=100, blank=True, null=True)
    classname = models.CharField(max_length=100, blank=True, null=True)
    mfile = models.ForeignKey(MFile, on_delete=models.CASCADE)
    metabinputdata = models.ForeignKey(MetabInputData, on_delete=models.CASCADE)


class CPeak(models.Model):
    idi = models.IntegerField(blank=True, null=True)
    mz = models.FloatField()
    mzmin = models.FloatField()
    mzmax = models.FloatField()
    rt = models.FloatField()
    rtmin = models.FloatField()
    rtmax = models.FloatField()
    _into = models.FloatField()
    intb = models.FloatField(blank=True, null=True)
    maxo = models.FloatField()
    sn = models.FloatField(blank=True, null=True)
    rtminraw = models.FloatField(blank=True, null=True)
    rtmaxraw = models.FloatField(blank=True, null=True)

    xcmsfileinfo = models.ForeignKey('XCMSFileInfo', on_delete=models.CASCADE)
    speakmeta_frag = models.ManyToManyField(SPeakMeta, through='SPeakMetaCPeakFragLink')


    class Meta:
        verbose_name_plural = "Chromatography peaks"

    def __str__(self):              # __unicode__ on Python 2
        return '{}_{}_{}'.format(self.idi, round(self.mz, 2),round(self.rt, 2))



class CPeakGroup(models.Model):
    idi = models.IntegerField(blank=True, null=True)
    mzmed = models.FloatField()
    mzmin = models.FloatField()
    mzmax = models.FloatField()
    rtmed = models.FloatField()
    rtmin = models.FloatField()
    rtmax = models.FloatField()
    npeaks = models.IntegerField()
    isotopes = models.CharField(max_length=40, blank=True, null=True)
    adducts = models.CharField(max_length=1000, blank=True, null=True)
    pcgroup = models.IntegerField(blank=True, null=True)
    msms_count = models.IntegerField(blank=True, null=True)
    cpeakgroupmeta = models.ForeignKey('CPeakGroupMeta', on_delete=models.CASCADE)
    best_annotation = models.TextField(null=True, blank=True)
    best_score = models.FloatField(null=True, blank=True)

    cpeak = models.ManyToManyField(CPeak, through='CPeakGroupCPeakLink')
    speak = models.ManyToManyField(SPeak, through='CPeakGroupSPeakLink')


    class Meta:
        verbose_name_plural = "Grouped chromatography peaks"


    def __str__(self):              # __unicode__ on Python 2
        return '{} {}'.format(self.id, self.idi)


def grouper(n, iterable, fillvalue=None):
    args = [iter(iterable)] * n
    return zip_longest(fillvalue=fillvalue, *args)


def big_delete(qs, model_class, n=10):
    pks = list(qs.values_list('pk', flat=True))

    pk_blocks = list(grouper(n, pks))

    [model_class.objects.filter(pk__in=block).delete() for block in pk_blocks]



class CPeakGroupMeta(models.Model):
    date = models.DateField(auto_now_add=True)
    metabinputdata = models.ForeignKey(MetabInputData, on_delete=models.CASCADE)

    def __str__(self):  # __unicode__ on Python 2
        return '{}_{}'.format(self.pk, self.date)



class EicMeta(models.Model):
    metabinputdata = models.ForeignKey(MetabInputData, on_delete=models.CASCADE)

    def __str__(self):              # __unicode__ on Python 2
        return self.metabinputdata


class Eic(models.Model):
    idi =  models.IntegerField()
    scan = models.IntegerField()
    intensity = models.FloatField(blank=True, null=True)
    rt_raw = models.FloatField()
    rt_corrected = models.FloatField(blank=True, null=True)
    purity = models.FloatField(blank=True, null=True)
    cpeak = models.ForeignKey(CPeak, on_delete=models.CASCADE)
    cpeakgroup = models.ForeignKey(CPeakGroup, on_delete=models.CASCADE) # technically we could just have the cpeak reference (something to consider at another time)
    eicmeta = models.ForeignKey(EicMeta, on_delete=models.CASCADE)

    def __str__(self):              # __unicode__ on Python 2
        return '{}_{}'.format(self.scan, self.intensity)

class CPeakGroupCPeakLink(models.Model):
    cpeak = models.ForeignKey(CPeak, on_delete=models.CASCADE)
    cpeakgroup = models.ForeignKey(CPeakGroup, on_delete=models.CASCADE)
    best_feature = models.IntegerField(blank=True, null=True)


class SPeakMetaCPeakFragLink(models.Model):
    cpeak = models.ForeignKey(CPeak, on_delete=models.CASCADE)
    speakmeta = models.ForeignKey(SPeakMeta, on_delete=models.CASCADE)


class CPeakGroupSPeakLink(models.Model):
    speak = models.ForeignKey(SPeak, on_delete=models.CASCADE)
    cpeakgroup = models.ForeignKey(CPeakGroup, on_delete=models.CASCADE)
    mzdiff = models.FloatField(blank=True, null=True)


class SPeakMetaSPeakLink(models.Model):
    speak = models.ForeignKey(SPeak, on_delete=models.CASCADE)
    speakmeta = models.ForeignKey(SPeakMeta, on_delete=models.CASCADE)
    mzdiff = models.FloatField(blank=True, null=True)
    linktype = models.CharField(max_length=200, blank=True, null=True)

class SPeakSPeakLink(models.Model):
    speak1 = models.ForeignKey(SPeak, on_delete=models.CASCADE, related_name='speak1')
    speak2 = models.ForeignKey(SPeak, on_delete=models.CASCADE, related_name='speak2')
    mzdiff = models.FloatField(blank=True, null=True)
    linktype = models.CharField(max_length=200, blank=True, null=True)


