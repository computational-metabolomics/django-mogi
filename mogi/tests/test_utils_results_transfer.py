# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import csv
import os
from django.conf import settings
from gfiles.models import GenericFile

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser, Permission, Group
from mogi.utils.upload_results import UploadResults
from mogi.models import models_isa, models_general
from gfiles.utils.save_as_symlink import save_as_symlink

# models test
class ResultsTransfer(TestCase):

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='jacob', email='jacob@jacob.com', password='top_secret')
        self.group, created = Group.objects.get_or_create(name='new_group')
        self.group.save()
        permission = Permission.objects.get(codename='add_investigation')
        self.group.permissions.add(permission)
        self.group.save()
        self.user.groups.add(self.group)
        self.user.save()


    def test_example_list(self):
        # Upload the MetabInput data (the sqlite results file)
        pth = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tests', 'data',
                     'summary_results.sqlite')

        pth = '/home/tomnl/Dropbox/code/post-doc-brum/mogi/django-mogisite-dmadb/mogi/tests/data/summary_results.sqlite'

        mid = models_general.MetabInputData(original_filename='summary_results.sqlite')
        mid = save_as_symlink(pth, 'test.sqlite', mid)
        mid.save()

        print(mid)
        print('test!!')
        # Upload the result to the Django database
        results = UploadResults(mid.pk, None)
        results.upload()



