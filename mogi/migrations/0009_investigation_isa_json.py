# Generated by Django 3.2.18 on 2023-04-03 14:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mogi', '0008_auto_20221025_1515'),
    ]

    operations = [
        migrations.AddField(
            model_name='investigation',
            name='isa_json',
            field=models.JSONField(blank=True, null=True),
        ),
    ]