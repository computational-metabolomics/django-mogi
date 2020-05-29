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
    investigation = models.ManyToManyField('Investigation',
                                           help_text='Choose investigation to search against')
    study = models.ManyToManyField('Study', help_text='Choose study to search against')
    assay = models.ManyToManyField('Assay', help_text='Choose assay to search against')


    def __str__(self):              # __unicode__ on Python 2
        return self.searchmzparam


class SearchResult(models.Model):
    result_file = models.FileField(upload_to=data_file_store, blank=True, null=True)
    matches = models.BooleanField()
    searchparam = models.ForeignKey(SearchParam, on_delete=models.CASCADE)

    def __str__(self):              # __unicode__ on Python 2
        return self.searchmzparam


class SearchFragParam(SearchParam):

    mz_precursor = models.FloatField()
    products = models.TextField(help_text=
                                'list product ions m/z and intensity pairs on each row')
    ppm_precursor_tolerance = models.FloatField(default=5)
    ppm_product_tolerance = models.FloatField(default=10)
    dot_product_score_threshold = MinMaxFloat(default=0.5, max_value=1, min_value=0)
    precursor_ion_purity = MinMaxFloat(default=0, max_value=1, min_value=0)
    ra_threshold = MinMaxFloat(default=0.05, max_value=1, min_value=0,
                               help_text='Remove any peaks below %x of the most intense peak ')
    ra_diff_threshold = models.FloatField(default=10)

    filter_on_precursor = models.BooleanField(blank=True)
    polarity = models.ManyToManyField('PolarityType',
                                      help_text='Choose polarites to search against')



    def __str__(self):              # __unicode__ on Python 2
        return self.description


class MsLevel(models.Model):
    ms_level = models.IntegerField(blank=False, null=False)

    def __str__(self):              # __unicode__ on Python 2
        return str(self.ms_level)


class SearchNmParam(SearchParam):
    masses = models.TextField(blank=True, null=True,
                              help_text='list of exact masses to search against database')
    ppm_target_tolerance = models.FloatField(blank=True, null=True, default=10)
    ppm_library_tolerance = models.FloatField(blank=True, null=True, default=10)
    polarity = models.ManyToManyField('PolarityType',
                                      help_text='Choose polarites to search against')

    # mass_type = models.ForeignKey('MassType', on_delete=models.CASCADE,
    #                               help_text='Choose if "mass in neutral form" or "mass in ion form". '
    #                                         'Ion form here being the m/z value directly from the mass spectrometer',
    #                               null=False, blank=False)


class SearchMzParam(SearchParam):

    masses = models.TextField(blank=True, null=True, help_text='list of exact masses to search against database')
    ppm_target_tolerance = models.FloatField(blank=True, null=True, default=10)
    ppm_library_tolerance = models.FloatField(blank=True, null=True, default=10)
    polarity = models.ManyToManyField('PolarityType',
                                      help_text='Choose polarites to search against')


    # mass_type = models.ForeignKey('MassType', on_delete=models.CASCADE,
    #                               help_text='Choose if "mass in neutral form" or "mass in ion form". '
    #                                         'Ion form here being the m/z value directly from the mass spectrometer',
    #                               null=False, blank=False)


    ms_level = models.ManyToManyField(MsLevel,
                                  help_text='Choose the ms levels to search against')

