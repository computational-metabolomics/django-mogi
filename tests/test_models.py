# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.test import TestCase
from misa.models import Investigation
from mogi.models import HistoryDataMOGI




class MisaGalaxyInteraction(TestCase):

    def test_investigation_link(self):

        # just check we can import misa models
        i = Investigation()
        i.save()

        self.assertEqual(len(Investigation.objects.all()), 1)

