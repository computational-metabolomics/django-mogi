# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.apps import apps

mogi = apps.get_app_config('mogi')
admin.site.register(mogi.get_models())
