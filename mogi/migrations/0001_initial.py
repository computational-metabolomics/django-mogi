# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-06-05 04:49
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('galaxy', '0001_initial'),
        ('metab', '0002_CUSTOM_IMPORT_DATA'),
        ('misa', '0002_IMPORT_DATA'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnnotationSummary',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lcms_ann_level', models.TextField(blank=True, max_length=100, null=True)),
                ('best_score', models.FloatField(blank=True, null=True)),
                ('assays', models.TextField(blank=True, max_length=100, null=True)),
                ('mzmin', models.FloatField(blank=True, null=True)),
                ('mzmax', models.FloatField(blank=True, max_length=100, null=True)),
                ('rtmin', models.FloatField(blank=True, max_length=100, null=True)),
                ('rtmax', models.FloatField(blank=True, null=True)),
                ('compound', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='metab.Compound')),
            ],
        ),
        migrations.CreateModel(
            name='CAnnotationMOGI',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cannotation', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='metab.CAnnotation')),
            ],
        ),
        migrations.CreateModel(
            name='CPeakGroupMetaMOGI',
            fields=[
                ('cpeakgroupmeta_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='metab.CPeakGroupMeta')),
                ('assay', models.ManyToManyField(to='misa.Assay')),
            ],
            bases=('metab.cpeakgroupmeta',),
        ),
        migrations.CreateModel(
            name='HistoryDataMOGI',
            fields=[
                ('historydata_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='galaxy.HistoryData')),
                ('investigation', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='misa.Investigation')),
            ],
            bases=('galaxy.historydata',),
        ),
        migrations.CreateModel(
            name='IncomingGalaxyData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('galaxy_url', models.TextField(blank=True, max_length=100, null=True)),
                ('galaxy_name', models.TextField(max_length=100)),
                ('galaxy_data_id', models.TextField(max_length=100)),
                ('galaxy_history_id', models.TextField(max_length=100)),
                ('galaxy_history_name', models.TextField(blank=True, max_length=100, null=True)),
                ('other_details', models.TextField(blank=True, max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ISAGalaxyTrack',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('galaxy_id', models.CharField(max_length=250, unique=True)),
                ('galaxyinstancetracking', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='galaxy.GalaxyInstanceTracking')),
                ('investigation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='misa.Investigation')),
                ('isatogalaxyparam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='galaxy.FilesToGalaxyDataLibraryParam')),
            ],
        ),
        migrations.AddField(
            model_name='cpeakgroupmetamogi',
            name='historydatamogi',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mogi.HistoryDataMOGI'),
        ),
    ]
