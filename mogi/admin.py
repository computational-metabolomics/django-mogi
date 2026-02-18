# -*- coding: utf-8 -*-
from django.contrib import admin
from django.apps import apps
from mogi.models.models_compounds import Compound


class CompoundAdmin(admin.ModelAdmin):
    list_per_page = 1000


mogi = apps.get_app_config('mogi')
admin.site.register(Compound, CompoundAdmin)

for model in mogi.get_models():
    if model is Compound:
        continue
    admin.site.register(model)