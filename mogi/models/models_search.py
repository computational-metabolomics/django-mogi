from __future__ import unicode_literals

from django.db import models
from datetime import datetime
import os
from django.conf import settings


class MinMaxFloat(models.FloatField):
    def __init__(self, min_value=None, max_value=None, *args, **kwargs):
        self.min_value, self.max_value = min_value, max_value
        super(MinMaxFloat, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {'min_value': self.min_value, 'max_value' : self.max_value}
        defaults.update(kwargs)
        return super(MinMaxFloat, self).formfield(**defaults)

def data_file_store(instance, filename):
    now = datetime.now()
    return os.path.join('data', 'search_results', now.strftime("%Y_%m_%d"), filename)

class SearchParam(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE, null=True, blank=True)
    description = models.CharField(max_length=100, blank=True, null=True,
                                   help_text='Any details to track for the analysis')

    class Meta:
        ordering = ('-id', )

    def __str__(self):              # __unicode__ on Python 2
        return str(self.id)


class FragSpectraType(models.Model):
    type = models.CharField(max_length=100, blank=True, null=True,)
    short_name = models.CharField(max_length=15, blank=True, null=True,)

    def __str__(self):
        return str(self.type)

class SearchFragParam(SearchParam):

    mz_precursor = models.FloatField()
    products = models.TextField(help_text=
                                'list product ions m/z and intensity pairs on each row')
    ppm_precursor_tolerance = MinMaxFloat(default=5, max_value=20, min_value=0)
    ppm_product_tolerance = MinMaxFloat(default=5, max_value=20, min_value=0)
    dot_product_score_threshold = MinMaxFloat(default=0.5, max_value=1, min_value=0)

    ra_threshold = MinMaxFloat(default=0.0, max_value=1, min_value=0,
                               help_text='Remove any peaks below %x of the most intense peak ')
    ra_diff_threshold = models.FloatField(default=10)

    metabolite_reference_standard = models.BooleanField(blank=False, null=False, default=False,
                                                        help_text='Include reference standard data in search '
                                                                  '(i.e. DMA assays where metabolite reference standards were measured)')

    fragspectratype = models.ManyToManyField('FragSpectraType',
                                             verbose_name='Fragmentation spectra type',
                                      help_text='Choose fragmentation spectra type')


    # filter_on_precursor = models.BooleanField(blank=True)
    polarity = models.ManyToManyField('PolarityType',
                                      help_text='Choose polarities to search against')


    def __str__(self):              # __unicode__ on Python 2
        return self.description


class MsLevel(models.Model):
    ms_level = models.IntegerField(blank=False, null=False)

    def __str__(self):              # __unicode__ on Python 2
        return str(self.ms_level)


class SearchMonoParam(SearchParam):
    masses = models.TextField(blank=True, null=True,
                              help_text='list of monoisotopic exact masses to search against database')
    ppm_tolerance = MinMaxFloat(default=5, max_value=100, min_value=0)
    matches = models.BooleanField(default=False)


class SearchMonoResult(models.Model):

    searchparam = models.ForeignKey(SearchParam, on_delete=models.CASCADE)
    compound = models.ForeignKey('Compound', on_delete=models.CASCADE)
    massquery = models.FloatField(blank=True, null=True, verbose_name='Query mass')
    ppmdiff = models.FloatField(blank=True, null=True)

    def __str__(self):              # __unicode__ on Python 2
        return str(self.id)

class SearchFragResult(models.Model):

    searchparam = models.ForeignKey(SearchParam, on_delete=models.CASCADE)
    dpc = models.FloatField(blank=True, null=True)
    l_prec_mz = models.FloatField(blank=True, null=True)
    q_prec_mz = models.FloatField(blank=True, null=True)
    rt = models.FloatField(blank=True, null=True)
    well = models.CharField(max_length=254, blank=True, null=True)
    ppm_diff_prec = models.FloatField(blank=True, null=True)
    dataset_pid = models.IntegerField(blank=True, null=True)
    dataset_grpid = models.IntegerField(blank=True, null=True)
    dataset_sid = models.IntegerField(blank=True, null=True)
    spectrum_type = models.CharField(max_length=254, blank=True, null=True)
    spectrum_details = models.CharField(max_length=254, blank=True, null=True)

    top_spectral_match = models.CharField(max_length=254, blank=True, null=True)
    top_metfrag = models.CharField(max_length=254, blank=True, null=True)
    top_sirius_csifingerid = models.CharField(max_length=254, blank=True, null=True)

    top_combined_annotation = models.CharField(max_length=254, blank=True, null=True)
    top_wscore = models.FloatField(blank=True, null=True)

    dataset = models.ForeignKey('Dataset', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):              # __unicode__ on Python 2
        return str(self.id)

    class Meta:
        ordering = ('-dpc', )





class SearchFragSpectra(models.Model):

    searchparam = models.ForeignKey(SearchParam, on_delete=models.CASCADE)
    mz = models.FloatField(blank=True, null=True)
    ra = models.FloatField(blank=True, null=True)
    query_library = models.CharField(max_length=254, blank=True, null=True)

    def __str__(self):              # __unicode__ on Python 2
        return str(self.id)


class SearchMzParam(SearchParam):

    masses = models.TextField(blank=True, null=True, help_text='list of exact masses to search against database')
    ppm_target_tolerance = models.FloatField(blank=True, null=True, default=5)
    ppm_library_tolerance = models.FloatField(blank=True, null=True, default=5)
    polarity = models.ManyToManyField('PolarityType',
                                      help_text='Choose polarities to search against')


    # mass_type = models.ForeignKey('MassType', on_delete=models.CASCADE,
    #                               help_text='Choose if "mass in neutral form" or "mass in ion form". '
    #                                         'Ion form here being the m/z value directly from the mass spectrometer',
    #                               null=False, blank=False)


    ms_level = models.ManyToManyField(MsLevel,
                                  help_text='Choose the ms levels to search against')

