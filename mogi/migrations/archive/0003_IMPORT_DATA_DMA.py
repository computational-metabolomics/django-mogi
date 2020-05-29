# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from mogi.utils.ontology_utils import check_and_create_ontology

def forwards_func(apps, schema_editor):

    # We get the model from the versioned app registry;
    # if we directly import it, it'll be the wrong version
    db_alias = schema_editor.connection.alias

    Investigation = apps.get_model("mogi", "Investigation")
    Study = apps.get_model("mogi", "Study")
    Organism = apps.get_model("mogi", "Organism")
    OrganismPart = apps.get_model("mogi", "OrganismPart")
    SampleType = apps.get_model("mogi", "SampleType")
    MeasurementTechnique = apps.get_model("mogi", "MeasurementTechnique")
    PolarityType = apps.get_model("mogi", "PolarityType")
    ExtractionType = apps.get_model("mogi", "ExtractionType")
    SpeType = apps.get_model("mogi", "SpeType")
    ChromatographyType = apps.get_model("mogi", "ChromatographyType")

    SampleCollectionProtocol = apps.get_model("mogi", "SampleCollectionProtocol")
    ExtractionProtocol = apps.get_model("mogi", "ExtractionProtocol")
    SpeProtocol = apps.get_model("mogi", "SpeProtocol")
    ChromatographyProtocol = apps.get_model("mogi", "ChromatographyProtocol")
    MeasurementProtocol = apps.get_model("mogi", "MeasurementProtocol")
    StudySample = apps.get_model('mogi', "StudySample")

    OntologyTerm = apps.get_model("mogi", "OntologyTerm")



def reverse_func(apps, schema_editor):
    ##########################
    # Reverse func not currently implemented
    ############################
    print('Reverse func not currently implemented')



class Migration(migrations.Migration):
    dependencies = [
        ('mogi', '0001_initial'),
        ('mogi', '0002_IMPORT_DATA')
    ]
    operations = [
        migrations.RunPython(forwards_func, reverse_func),
    ]

