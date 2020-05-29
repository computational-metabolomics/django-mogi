# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig


class MogiConfig(AppConfig):
    name = 'mogi'

    def ready(self):
        post_save.connect(add_to_default_group, sender=User)

