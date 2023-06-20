# Generated by Django 3.2.16 on 2022-10-25 14:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mogi', '0003_auto_20221025_1303'),
    ]

    operations = [
        migrations.CreateModel(
            name='FragSpectraType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='searchfragparam',
            name='metabolite_reference_standards',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='searchfragparam',
            name='fragspectratype',
            field=models.ManyToManyField(help_text='Choose fragmentation spectra type', to='mogi.FragSpectraType'),
        ),
    ]
