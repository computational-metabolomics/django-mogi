from __future__ import unicode_literals, print_function
import os
import csv
from django.core.files import File
from django.contrib.auth import get_user_model
from mogi.models.models_datasets import Dataset
from mogi.models.models_isa import Assay, PolarityType
from django.conf import settings
from gfiles.utils.save_as_symlink import save_as_symlink
from .upload_compounds import rw_itm

def upload_datasets(datsets_list_pth):

    with open(datsets_list_pth, newline='') as csvfile:
        r = csv.DictReader(csvfile, delimiter=',')
        for row in r:

            # Create dataset object
            dataset = Dataset.objects.create(fractionation=rw_itm(row, 'fractionation'),
                                             metabolite_standard=rw_itm(row, 'metabolite_standard'),
                                             galaxy_history_url=rw_itm(row, 'galaxy_history_url'))

            # check if we have relevant assay in the database and add to dataset object
            aq = Assay.objects.filter(name=rw_itm(row, 'assay'))
            if aq:
                dataset.assay = aq[0]

            pq = PolarityType.objects.filter(type__iexact=rw_itm(row, 'polarity'))

            print(pq)
            if pq:
                dataset.polarity = pq[0]

            dataset.save()

            # Add symlinks to any data
            sqlite_pth = rw_itm(row, 'sqlite')
            tsv_pth = rw_itm(row, 'tsv')

            if os.path.exists(sqlite_pth):
                save_as_symlink(sqlite_pth, os.path.basename(sqlite_pth), dataset, 'sqlite')

            if os.path.exists(tsv_pth):
                save_as_symlink(tsv_pth, os.path.basename(tsv_pth), dataset, 'tsv')








