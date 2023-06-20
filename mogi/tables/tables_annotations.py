import django_tables2 as tables
from django_tables2_column_shifter.tables import ColumnShiftTable
from django_tables2.utils import A
from gfiles.utils.icons import EYE

from mogi.models import models_annotations

class CombinedAnnotationTable(ColumnShiftTable):
    title = "Combined annotations"
    details = ""
    eics = tables.LinkColumn('eics', verbose_name='EICs', text=EYE, args=[A('dataset_id'), A('grpid')])
    frag = tables.LinkColumn('speaks', verbose_name='Frag', text=EYE, args=[A('dataset_id'), A('grpid'), A('sid')])
    sm = tables.LinkColumn('canns_sm', verbose_name='Spectral matching', text=EYE,
                           args=[A('dataset_id'), A('grpid'), A('sid'), A('inchikey')])
    metfrag = tables.LinkColumn('canns_metfrag', verbose_name='MetFrag', text=EYE,
                           args=[A('dataset_id'), A('grpid'), A('sid'), A('inchikey')])
    sirius = tables.LinkColumn('canns_sirius', verbose_name='Sirius CSI:FingerID', text=EYE,
                           args=[A('dataset_id'), A('grpid'), A('sid'), A('inchikey')])


    class Meta:
        name = 'test'
        model = models_annotations.CombinedAnnotation


class SpectralMatchingTable(ColumnShiftTable):
    title = "Spectral matching annotations"
    details = ""
    sm = tables.LinkColumn('smplot', verbose_name='Plot', text=EYE, args=[A('dataset_id'), A('qpid'), A('lpid')])

    class Meta:

        model = models_annotations.SpectralMatching


class SiriusCSIFingerIDTable(ColumnShiftTable):
    title = "SIRIUS CSI:FingerID annotations"
    details = ""
    class Meta:

        model = models_annotations.SiriusCSIFingerID

class MetFragTable(ColumnShiftTable):
    title = "MetFrag annotations"
    details = ""
    class Meta:

        model = models_annotations.MetFrag