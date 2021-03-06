from __future__ import unicode_literals, print_function

from django.contrib.auth import get_user_model
from django.conf import settings
from mogi.models.models_isa import Investigation, Assay
from mogi.forms.forms_isa import UploadAssayDataFilesForm
from mogi.utils.isa_upload import upload_assay_data_files_dir



def map_assays_to_files(assay_mapping, user_id, study_id, celery_obj):
    User = get_user_model()
    
    count = len(assay_mapping)

    user = User.objects.get(id=user_id)
    c = 0


    for row in assay_mapping:
        if celery_obj:
            celery_obj.update_state(state='RUNNING',
                        meta={'current': c, 'total': count, 'status': 'Updating assays'})

        assay_match = Assay.objects.filter(study_id=study_id, name=row['assay'])

        if not assay_match:
            assay = Assay(study_id=study_id, name=row['assay'])
            assay.save()
        else:
            if row['replace'] == 'yes':
                assay_match.delete()
                assay = Assay(study_id=study_id, name=row['assay'])
                assay.save()
            else:
                assay = assay_match[0]

        assay_id = assay.id
        if row['save_as_link']=='yes':
            save_as_link=True
        else:
            save_as_link=False

        


    return 1


def map_assays_to_directories(assay_mapping, user_id, study_id, celery_obj):

    count = len(assay_mapping)

    user = User.objects.get(id=user_id)
    c = 0

    for row in assay_mapping:
        if celery_obj:
            celery_obj.update_state(state='RUNNING',
                        meta={'current': c, 'total': count, 'status': 'Updating assays'})

        # full_dir_pth = os.path.join(edrs[row['dir_tag']]['path'], username, row['dir'])

        assay_match = Assay.objects.filter(study_id=study_id, name=row['assay_name'])

        if not assay_match:
            assay = Assay(study_id=study_id, name=row['assay_name'])
            assay.save()
        else:
            if row['replace'] == 'yes':
                assay_match.delete()
                assay = Assay(study_id=study_id, name=row['assay_name'])
                assay.save()
            else:
                assay = assay_match[0]

        assay_id = assay.id
        if row['save_as_link']=='yes':
            save_as_link=True
        else:
            save_as_link=False

        data_in = {'recursive': True,
                   row['dir_tag']: row['dir'],
                   'create_assay_details': True,
                   'use_directories':True,
                   'save_as_link': save_as_link}

        form = UploadAssayDataFilesForm(user=User.objects.get(id=user_id),
                                        data=data_in,
                                        assayid=assay_id)

        if form.is_valid():
            
            create_assay_details = form.cleaned_data['create_assay_details']
            save_as_link = form.cleaned_data['save_as_link']

            upload_assay_data_files_dir(form.filelist,
                                        user.username,
                                        form.mapping_l,
                                        assay_id,
                                        create_assay_details,
                                        save_as_link,
                                        '')
        else:
            print(form.errors)
            if celery_obj:
                celery_obj.update_state(state='FAILURE-KNOWN',
                            meta={'current': 0, 'total': 1, 'status': form.errors.as_json()})
            return 0
        c += 1
    return 1

