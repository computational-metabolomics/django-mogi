from __future__ import unicode_literals

from django.db import models
from .models_peaks import SPeakMeta

class LibrarySpectraSource(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)
    description = models.CharField(max_length=100, blank=True, null=True)
    # msp_file = models.FileField(upload_to=data_msp_file_store, blank=False, null=False)

    def __str__(self):  # __unicode__ on Python 2
        return self.name

    class Meta:
        db_table = 'library_spectra_source'
        verbose_name_plural = "library spectra references"


class LibrarySpectraMeta(SPeakMeta):
    name = models.TextField(blank=True, null=True)
    accession = models.TextField(blank=False, null=False)
    collision_energy = models.TextField(blank=True, null=True)
    resolution = models.CharField(max_length=400, blank=True, null=True)
    polarity = models.CharField(max_length=400, blank=True, null=True)
    fragmentation_type = models.CharField(max_length=400, blank=True, null=True)
    precursor_type = models.TextField(blank=True, null=True)
    instrument_type = models.CharField(max_length=400, blank=True, null=True)
    instrument = models.CharField(max_length=400, blank=True, null=True)
    copyright = models.TextField(blank=True, null=True)
    column = models.TextField(blank=True, null=True)
    mass_accuracy = models.FloatField(blank=True, null=True)
    mass_error = models.FloatField(blank=True, null=True)
    origin = models.TextField(blank=True, null=True)

    libraryspectrasource = models.ForeignKey('LibrarySpectraSource', on_delete=models.CASCADE, blank=True, null=True)
    inchikey = models.CharField(max_length=254)
    splash = models.TextField(blank=True, null=True)
    retention_index = models.FloatField(blank=True, null=True)
    retention_time = models.FloatField(blank=True, null=True)


    def __str__(self):  # __unicode__ on Python 2
        return '{}  [accession:{}]'.format(self.name, self.accession)


