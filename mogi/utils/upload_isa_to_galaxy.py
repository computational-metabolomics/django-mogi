from __future__ import print_function
import itertools
import os
import tempfile
import shutil
import csv
import sys
from operator import itemgetter
from django.core.files import File
from bioblend.galaxy.libraries import LibraryClient
from bioblend.galaxy.folders import FoldersClient
from bioblend.galaxy.client import ConnectionError
from io import TextIOWrapper

from django.conf import settings

from galaxy.utils.galaxy_utils import create_library, get_gi_gu
from galaxy.utils.upload_to_galaxy import add_filelist_datalib, link_files_in_galaxy
from misa.models import Investigation, MISAFile
from mbrowse.models import MFile
from ftplib import FTP, error_perm

from mogi.models import ISAGalaxyTrack


def galaxy_isa_upload_datalib(pks, galaxy_isa_upload_param, galaxy_pass, user_id, celery_obj=''):

    # ... Should this just be for admin? or shall all user have ability ? .... not sure

    # update celery
    if celery_obj:
        celery_obj.update_state(state='RUNNING',
                          meta={'current': 0.1, 'total': 100, 'status': 'Initialising galaxy'})

    # get the galaxy clients required for updating the galaxy instance
    git = galaxy_isa_upload_param.galaxyinstancetracking
    gi, gu = get_gi_gu(galaxy_isa_upload_param.added_by, git)
    lc = LibraryClient(gi)

    # Retrieve or create the base library used for all ISA folders
    lib = create_library(lc, 'mogi')

    # get all associated files for the selected ISA projects
    mfiles = get_mfile_qs(pks)
    #
    # # Add the files to Galaxy data library

    try:
        create_isa_datalib(mfiles, lib, gi, gu, galaxy_pass, galaxy_isa_upload_param, user_id, celery_obj)
    except error_perm as e:
        print('ERROR CATCH', e)
        if celery_obj:
            celery_obj.update_state(state='FAILURE',
                                    meta={'current': 0.0, 'total': 100, 'status': 'Failed {}'.format(e)})
        return 0
    except bioblend.ConnectionError as e:
        print('ERROR CATCH', e)
        if celery_obj:
            celery_obj.update_state(state='FAILURE',
                                    meta={'current': 0.0, 'total': 100, 'status': 'Failed {}'.format(e)})
        return 0



    return 1

def create_samplelist(user_id, igrp):
    dirpth = tempfile.mkdtemp()
    # dirpth = '/tmp/'
    nm = get_namemap()
    fnm = 'samplelist_{}.tabular'.format(igrp[0][nm['investigation']].replace(" ", "_"))
    tmp_pth = os.path.join(dirpth, fnm)

    with open(tmp_pth, 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter='\t')
        writer.writerow(
                ['prefix', 'sample_class', 'code_field', 'blank', 'sample_type', 'full_path', 'original_filename', 'investigation',
                 'investigation_id', 'study', 'assay', 'fileid'])
        for m in igrp:
            if m[nm['sampletype']].lower() == 'blank':
                blank = 'yes'
            else:
                blank = 'no'

            code_field = m[nm['code_field']]
            code_field_r_compat = code_field.replace('_', '.')
            code_field_r_compat = code_field_r_compat.replace('-', '.')
            row = [
                m[nm['prefix']],
                code_field_r_compat,
                code_field,
                blank,
                m[nm['sampletype']],
                m['data_file'],
                m['original_filename'],
                m[nm['investigation']],
                m[nm['investigation_id']],
                m[nm['study']],
                m[nm['assay']],
                m['id']
            ]

            writer.writerow(row)
            investigation_id = m[nm['investigation_id']]


    misafile = MISAFile(investigation_id=investigation_id, user_id=user_id)
    misafile.original_filename = fnm
    misafile.data_file.save(fnm, File(open(tmp_pth)))
    misafile.save()

    fullpth = os.path.join(settings.MEDIA_ROOT, misafile.data_file.path)
    print(fullpth)
    return fullpth, misafile.id


def get_namemap():
    return  {'assay': 'run__assayrun__assaydetail__assay__name',
             'study': 'run__assayrun__assaydetail__assay__study__name',
             'investigation': 'run__assayrun__assaydetail__assay__study__investigation__name',
             'investigation_id': 'run__assayrun__assaydetail__assay__study__investigation__id',
             'sampletype': 'run__assayrun__assaydetail__studysample__sampletype__type',
             'code_field': 'run__assayrun__assaydetail__code_field',
             'prefix': 'run__prefix',
             }


def get_mfile_qs(pks):
    # get files associated with this isa project
    name_map = get_namemap()

    mfiles = MFile.objects.filter(
        run__assayrun__assaydetail__assay__study__investigation__id__in=pks
    ).values(
        name_map['assay'],
        name_map['study'],
        name_map['investigation'],
        name_map['investigation_id'],
        name_map['code_field'],
        name_map['sampletype'],
        name_map['prefix'],
        'data_file',
        'original_filename',
        'id'
    ).order_by(
        name_map['investigation'],
        name_map['study'],
        name_map['assay']
    )

    return mfiles



def create_isa_datalib(mfiles, lib, gi, gu, galaxy_pass, galaxy_isa_upload_param, user_id, celery_obj=''):
    name_map = get_namemap()
    igrps = group_by_keys(mfiles, (name_map['investigation'],))

    file_count = 0

    lc = LibraryClient(gi)
    fc = FoldersClient(gi)


    for igrp in igrps:
        print(igrp)
        # get the investigation name of the group, and create folder
        ifolder, sgrps = create_investigation_folder(igrp, lc, fc, lib, galaxy_isa_upload_param, name_map)
        samplelist_pth, misafile = create_samplelist(user_id, igrp)

        save_to_galaxy([samplelist_pth], galaxy_isa_upload_param, lc, gu, gi, galaxy_pass,
                                        lib['id'], ifolder['id'], 'samplelist', [{'id':misafile}])

        for sgrp in sgrps:
            print(sgrp)
            # get the study name of the group and create folder
            sfolder, agrps = create_study_folder(sgrp, lc, lib, name_map, ifolder)

            for agrp in agrps:
                print(agrp)

                study_n = agrp[0][name_map['study']]
                investigation_n = agrp[0][name_map['investigation']]
                assay_n = agrp[0][name_map['assay']]

                full_assay_name = '{}_{}_{}'.format(study_n, investigation_n, assay_n)

                if celery_obj:
                    if file_count==0:
                        count = 0.1
                    else:
                        count = file_count
                    celery_obj.update_state(state='RUNNING',
                                            meta={'current': count, 'total': len(mfiles)+1,
                                                  'status': 'Assay: {}'.format(assay_n)})

                afolder = create_assay_folder(agrp, lc, lib, name_map, sfolder)
                filelist = [os.path.join(settings.MEDIA_ROOT, f['data_file']) for f in agrp]

                data_lib_files = save_to_galaxy(filelist, galaxy_isa_upload_param, lc, gu, gi, galaxy_pass,
                                                 lib['id'], afolder['id'], full_assay_name, agrp)
                #
                file_count += len(data_lib_files)



def save_to_galaxy(filelist, galaxy_isa_upload_param, lc, gu, gi, galaxy_pass, lib_id, folder_id, full_name, filedetails):
    data_lib_files = add_filelist_datalib(filelist,
                                          galaxy_isa_upload_param,
                                          lc,
                                          gu,
                                          gi,
                                          galaxy_pass,
                                          lib_id,
                                          folder_id,
                                          full_name)

    link_files_in_galaxy(data_lib_files, filedetails, galaxy_isa_upload_param.galaxyinstancetracking, library=True)

    return data_lib_files


def create_investigation_folder(igrp, lc, fc, lib, galaxy_isa_upload_param, name_map):
    investigation_n = igrp[0][name_map['investigation']]
    print('========> Investigation:', investigation_n)

    if galaxy_isa_upload_param.remove:
        igt_for_removal = ISAGalaxyTrack.objects.filter(investigation__name=investigation_n)
        if igt_for_removal:
            for i in igt_for_removal:
                # remove folder
                fc.delete_folder(i.galaxy_id)
                # remove django entry
                i.delete()



    ifolder = lc.create_folder(library_id=lib['id'], description='isa_investigation', folder_name=investigation_n)[
        0]

    igt = ISAGalaxyTrack(galaxyinstancetracking=galaxy_isa_upload_param.galaxyinstancetracking,
                         isatogalaxyparam=galaxy_isa_upload_param,
                         investigation=Investigation.objects.get(name=investigation_n),
                         galaxy_id=ifolder['id']
                         )
    igt.save()
    sgrps = group_by_keys(igrp, (name_map['study'],))

    return ifolder, sgrps

def create_study_folder(sgrp, lc, lib, name_map, ifolder):
    study_n = sgrp[0][name_map['study']]
    print('====> Study:', study_n)
    sfolder = lc.create_folder(library_id=lib['id'],
                               folder_name=study_n,
                               description='isa_study',
                               base_folder_id=ifolder['id'])[0]

    agrps = group_by_keys(sgrp, (name_map['assay'],))
    return sfolder, agrps

def create_assay_folder(agrp, lc, lib, name_map, sfolder):
    # get the study name of the group and create folder
    assay_n = agrp[0][name_map['assay']]
    print('========> Assay:', assay_n)

    afolder = lc.create_folder(library_id=lib['id'],
                               folder_name=assay_n,
                               description='isa_assay',
                               base_folder_id=sfolder['id'])[0]

    return afolder









def group_by_keys(iterable, keys):
    # https://stackoverflow.com/questions/31955389/how-to-group-an-array-by-multiple-keys
    key_func = itemgetter(*keys)

    # For groupby() to do what we want, the iterable needs to be sorted
    # by the same key function that we're grouping by.
    sorted_iterable = sorted(iterable, key=key_func)

    return [list(group) for key, group in itertools.groupby(sorted_iterable, key_func)]