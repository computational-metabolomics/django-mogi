from __future__ import unicode_literals, print_function
import os
import csv
from django.core.files import File
from django.contrib.auth import get_user_model
from mogi.models.models_compounds import Compound
from django.conf import settings
from gfiles.utils.save_as_symlink import save_as_symlink

################################
# Upload compounds
################################
def rw_itm(row, name):
    if name in row:
        item = row[name]
        if item.lower() == 'true':
            return True
        elif item.lower() == 'false':
            return False
        elif not row[name]:
            return None
        elif row[name].lower() == 'na':
            return None
        else:
            return item
    else:
        return None


def upload_compounds(compound_list_pth, compound_annotations_dir, replace=True, celery_obj=''):

    if celery_obj:
        celery_obj.update_state(state='RUNNING',
                                            meta={'current': 0, 'total':  100,
                                                  'status': 'Starting upload'})

    num_lines = sum(1 for line in open(compound_list_pth))

    with open(compound_list_pth, newline='') as csvfile:
        r = csv.DictReader(csvfile, delimiter=',')
        for c, row in enumerate(r):
            inchikey = rw_itm(row, 'inchikey')
            if not inchikey:
                continue

            if celery_obj and c % 100:
                celery_obj.update_state(state='RUNNING',
                                            meta={'current': c, 'total':  num_lines,
                                                  'status': 'Row {} of {}'.format(c, num_lines)})

            comp, created = Compound.objects.get_or_create(inchikey=inchikey)

            if created or replace:
                comp.inchikey1 = rw_itm(row, 'inchikey1')
                comp.smiles = rw_itm(row, 'smiles')
                comp.molecular_formula = rw_itm(row, 'molecular_formula')
                comp.monoisotopic_exact_mass = rw_itm(row, 'monoisotopic_exact_mass')
                comp.compound_name = rw_itm(row, 'compound_name')
                comp.natural_product_inchikey1 = rw_itm(row, 'natural_product_inchikey1')
                comp.pubchem_cids = rw_itm(row, 'pubchem_cids')
                comp.hmdb_ids = rw_itm(row, 'hmdb_ids')
                comp.kegg_ids = rw_itm(row, 'kegg_ids')
                comp.chebi_ids = rw_itm(row, 'chebi_ids')
                comp.kingdom = rw_itm(row, 'kingdom')
                comp.superclass = rw_itm(row, 'superclass')
                comp._class = rw_itm(row, 'class')
                comp.subclass = rw_itm(row, 'subclass')
                comp.direct_parent = rw_itm(row, 'direct_parent')
                comp.molecular_framework = rw_itm(row, 'molecular_framework')
                comp.predicted_lipidmaps_terms = rw_itm(row, 'predicted_lipidmaps_terms')
                comp.assay = rw_itm(row, 'assay')
                comp.extraction = rw_itm(row, 'extraction')
                comp.spe = rw_itm(row, 'spe')
                comp.spe_frac = rw_itm(row, 'spe_frac')
                comp.chromatography = rw_itm(row, 'chromatography')
                comp.measurement = rw_itm(row, 'measurement')
                comp.polarity = rw_itm(row, 'polarity')
                comp.lcmsdimsbool = rw_itm(row, 'lcmsdimsbool')
                comp.nmrbool = rw_itm(row, 'nmrbool')
                comp.gcmsbool = rw_itm(row, 'gcmsbool')
                comp.smbool = rw_itm(row, 'smbool')
                comp.metfragbool = rw_itm(row, 'mfbool')
                comp.siriusbool = rw_itm(row, 'siriusbool')
                comp.mzcloudsmbool = rw_itm(row, 'mzcloudsmbool')
                comp.galaxysmbool = rw_itm(row, 'galaxysmbool')
                comp.gnpssmbool = rw_itm(row, 'gnpssmbool')
                comp.msi_level = rw_itm(row, 'msi_level')
                comp.save()

                comp_html_nme = '{}.html'.format(inchikey)
                comp_html_pth = os.path.join(compound_annotations_dir, inchikey, comp_html_nme)
                if os.path.exists(comp_html_pth):
                    save_as_symlink(comp_html_pth, comp_html_nme, comp)

    if celery_obj:
        celery_obj.update_state(state='SUCCESS',
                                meta={'current': 100, 'total':  100,
                                      'status': 'Compounds uploaded'})








