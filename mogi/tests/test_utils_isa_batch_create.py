# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import csv
import os
from django.conf import settings
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser, Permission, Group
from mogi.utils.isa_create import isa_batch_create
from mogi.models import models_isa

# models test
class IsaBatchCreateUtil(TestCase):

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
        sample_list = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tests', 'data',
                     'mapping_P_WAX1_PHE.csv')

        isa_batch_create(open(sample_list, 'rb'),
                         self.user.id,
                         celery_obj=None,
                         root_dir=settings.EXTERNAL_DATA_ROOTS['TEST']['path'])

        # check all investigation, study, files and assay are available
        i = models_isa.Investigation.objects.get(name='DMA of D. magna')
        self.assertEqual(i.name, 'DMA of D. magna')

        s = models_isa.Study.objects.get(name='DMA of D. magna (2020)', investigation=i)
        self.assertEqual(s.name, 'DMA of D. magna (2020)')

        a = models_isa.Assay.objects.all()[0]
        self.assertEqual(a.name, 'POL_WAX_1_AMD_POS')

        # Check 18 mzml files added
        mzmls = models_isa.MFile.objects.filter(mfilesuffix__suffix='.mzml')
        self.assertEqual(len(mzmls), 18)

        # check 34 raw files added
        raws = models_isa.MFile.objects.filter(mfilesuffix__suffix='.raw')
        self.assertEqual(len(raws), 34)

        # check 6 assay details added
        ads = models_isa.AssayDetail.objects.all()
        self.assertEqual(len(ads), 6)



