# Generated by Django 3.2.18 on 2023-04-12 09:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mogi', '0011_investigation_isa_tab_zip'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExportISA',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mzml_parse', models.BooleanField(default=False, help_text='Parse mzML files to extract metadata information')),
                ('metabolights_compat', models.BooleanField(default=False, help_text='Export the ISA data in a format that is more easy to incoporate into aMetaboLights submission', verbose_name='MetaboLights compatible ISA export')),
                ('json', models.BooleanField(default=True, help_text='Create and save an ISA JSON')),
                ('isatab', models.BooleanField(default=True, help_text='Create and save ISA-tab files (in a zip file)', verbose_name='ISA-tab zip')),
                ('investigation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mogi.investigation')),
            ],
        ),
    ]