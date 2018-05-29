# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-05-29 06:56
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('metab', '0002_CUSTOM_IMPORT_DATA'),
        ('misa', '0002_IMPORT_DATA'),
        ('mogi', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CPeakGroupMetaMOGI',
            fields=[
                ('cpeakgroupmeta_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='metab.CPeakGroupMeta')),
                ('assay', models.ManyToManyField(to='misa.Assay')),
                ('historydatamogi', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mogi.HistoryDataMOGI')),
            ],
            bases=('metab.cpeakgroupmeta',),
        ),
    ]