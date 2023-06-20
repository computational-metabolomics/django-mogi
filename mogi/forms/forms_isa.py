# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import os
import csv
import six
import zipfile
from io import TextIOWrapper

from django.conf import settings
from django import forms
from dal import autocomplete

from mogi.models import models_isa
from mogi.utils.isa_create import check_mapping_details, file_upload_mapping_match
from mogi.utils.mfile_upload import get_all_suffixes, get_file_namelist, get_mfiles_from_dir, get_pths_from_field


class ExportISAForm(forms.ModelForm):
    class Meta:
        model = models_isa.ExportISA
        fields = '__all__'


class RunForm(forms.ModelForm):

    class Meta:
        model = models_isa.Run
        fields = '__all__'
        exclude = ['owner']

class UploadMFilesBatchForm(forms.Form):
    data_zipfile = forms.FileField(label='Zipped collection of data files',
                              help_text='The zip file should contain both the '
                                        'raw data and the open source equivalent '
                                        'e.g. mzML. Raw data files and open source '
                                        'data files should have matching '
                                        'names e.g. file1.mzML, file1.raw ',
                                required=False)

    use_directories = forms.BooleanField(initial=False, required=False)

    save_as_link = forms.BooleanField(initial=False, required=False, help_text='Save files as static link (can '
                                                                               'only be used with directories)')

    def __init__(self, user, *args, **kwargs):
        super(UploadMFilesBatchForm, self).__init__(*args, **kwargs)
        self.dir_fields = []
        self.filelist = []
        self.user = user

        if hasattr(settings, 'EXTERNAL_DATA_ROOTS'):
            edrs = settings.EXTERNAL_DATA_ROOTS

            for edr_name, edr in six.iteritems(edrs):

                if edr['filepathfield']:
                    if edr['user_dirs']:
                        path = os.path.join(edr['path'], user.username)
                    else:
                        path = edr['path']
                    self.fields[edr_name] = forms.FilePathField(path=path, recursive=True, allow_files=False, allow_folders=True,
                                      required=False, label= edr_name,
                                     help_text=edr['help_text'])
                else:
                    self.fields[edr_name] = forms.CharField(max_length=2000, help_text=edr['help_text'], required=False)

                self.dir_fields.append(edr_name)
            self.fields['recursive'] = forms.BooleanField(initial=False,
                                                          help_text='Search recursively through any sub directories '
                                                                    'of the chosen directory for metabolomics files',
                                                          required=False)


    def clean(self):
        cleaned_data = super(UploadMFilesBatchForm, self).clean()
        data_zipfile = cleaned_data.get('data_zipfile')
        use_directories = cleaned_data.get('use_directories')
        recursive = cleaned_data.get('recursive')

        dir_pths = get_pths_from_field(self.dir_fields, cleaned_data, self.user.username)


        if any(self.errors):
            return self.errors

        self.check_zip_or_directories(data_zipfile, use_directories, dir_pths, recursive)

        return cleaned_data


    def check_zip_or_directories(self, data_zipfile, use_directories, dir_pths, recursive):

        if use_directories:
            self.check_directories(dir_pths, recursive)
        else:
            if data_zipfile:
                self.check_zipfile(data_zipfile)
            else:
                msg = 'Choose either a directory or a zip file that contains metabolomics data files'
                raise forms.ValidationError(msg)


    def check_zipfile(self, data_zipfile):


        if not zipfile.is_zipfile(data_zipfile):
            msg = 'When using a zip file option the file needs to be a compressed zipfile'
            raise forms.ValidationError(msg)

        comp = zipfile.ZipFile(data_zipfile)

        namelist = get_file_namelist(comp)
        suffixes, suffix_str = get_all_suffixes()
        for n in namelist:
            bn = os.path.basename(n)
            prefix, suffix = os.path.splitext(bn)
            if not suffix.lower() in suffixes:
                msg = 'For file {}, the suffix (file ending) needs to be one of the following: {}'.format(bn, suffix_str)
                raise forms.ValidationError(msg)

        self.filelist = namelist

        return data_zipfile



    def check_directories(self, dir_pths, recursive):

        matches = []
        for pth in dir_pths:
            if not os.path.exists(pth):
                msg = 'Path does not exist {}'.format(pth)
                raise forms.ValidationError(msg)
            else:
                matches.extend(get_mfiles_from_dir(pth, recursive))


        if not matches:
            suffixes, suffix_str = get_all_suffixes()
            msg = 'No metabolomic files available within the chosen directories' \
                  '. The suffix (file ending) of the files needs to be one of the following: {}'.format(suffix_str)
            raise forms.ValidationError(msg)

        self.filelist = matches

        return matches




class MFileForm(forms.ModelForm):
    class Meta:

        model = models_isa.MFile
        fields = ['run', 'data_file']


    def clean_data_file(self):

        data_file = self.cleaned_data['data_file']

        prefix, suffix = os.path.splitext(os.path.basename(data_file.name))
        mfilesuffix_query = models_isa.MFileSuffix.objects.filter(suffix=suffix.lower())

        if not mfilesuffix_query:
            suffixes, suffixes_str = get_all_suffixes()
            msg = 'File suffix (file ending) needs to be one of the following: {}'.format(suffixes_str)
            raise forms.ValidationError(msg)

        run = self.cleaned_data['run']

        if not run.prefix == prefix:
            msg = 'File prefix (filename without the file ending) needs to match the Run name: {}'.format(run.prefix)
            raise forms.ValidationError(msg)

        return self.cleaned_data['data_file']


class ISABatchCreateForm(forms.Form):
    sample_list = forms.FileField()


class AssayDetailForm(forms.ModelForm):

    class Meta:
        model = models_isa.AssayDetail
        fields = '__all__'
        exclude = ['code_field']


class UploadAssayDataFilesForm(UploadMFilesBatchForm):

    data_mappingfile = forms.FileField(label='Mapping file upload', required=False,
                            help_text='csv file that maps the data files to the assay details. '\
                                      'When empty will search for a file called "mapping.csv" ' \
                                      'within the selected directories (not possible when using'\
                                       ' the zip option)')

    create_assay_details = forms.BooleanField(label='Create assay details',
                                              initial=True, required=False,
                                help_text='Assay details will be created on the fly')

    def __init__(self, user, *args, **kwargs):
        self.dir_pths = []
        self.mapping_l = []
        self.assayid = kwargs.pop('assayid')
        super(UploadAssayDataFilesForm, self).__init__(user, *args, **kwargs)


    def clean_datamappingfile(self):
        mappingfile = self.cleaned_data['data_mappingfile']

        # Check all required columns are present

        # Check if this type is available at all

        return self.cleaned_data['data_mappingfile']

    def clean(self):


        cleaned_data = super(UploadMFilesBatchForm, self).clean()
        data_zipfile = cleaned_data.get('data_zipfile')
        data_mappingfile = cleaned_data.get('data_mappingfile')
        use_directories = cleaned_data.get('use_directories')
        recursive = cleaned_data.get('recursive')
        create_assay_details = cleaned_data.get('create_assay_details')

        # check for any previous errors
        if any(self.errors):
            return self.errors


        # check directories
        dir_pths = get_pths_from_field(self.dir_fields, cleaned_data, self.user.username)
        self.check_zip_or_directories(data_zipfile, use_directories, dir_pths, recursive)


        #######################################################
        # Check matching files in zip and mapping file
        #######################################################
        filelist = self.filelist

        if not data_mappingfile and use_directories:
            found = False
            for dir_pth in dir_pths:
                for fn in os.listdir(dir_pth):
                    if fn == 'mapping.csv':
                        with open(os.path.join(dir_pth, fn)) as f:
                            mapping_l = list(csv.DictReader(f))
                        found = True
            if not found:
                msg = 'The mapping file was not found within the selected directories'
                raise forms.ValidationError(msg)

        elif not data_mappingfile:
            msg = 'The mapping file is required when using the zip option'
            raise forms.ValidationError(msg)
        else:

            mapping_l = list(csv.DictReader(TextIOWrapper(
                data_mappingfile, encoding='ascii', errors='replace')))

        missing_files = file_upload_mapping_match(filelist, mapping_l)
        missing_files = [os.path.basename(f) for f in missing_files]

        if missing_files:
            missing_files_str = ', '.join(missing_files)
            msg = 'The mapping file is missing the following files: {}'.format(missing_files_str)
            raise forms.ValidationError(msg)

        ###################################################
        # Check columns are present
        ###################################################
        expected_cols = ['filename', 'sample', 'sample_collection',
                         'extraction', 'spe', 'spe_frac', 'chromatography',
                         'chromatography_frac', 'measurement', 'polarity', 'fileformat']
        missing_cols = set(expected_cols).difference(list(mapping_l[0].keys()))

        if missing_cols:
            msg = 'The mapping file is missing the following columns: {}'.format(
                                                                    ', '.join(missing_cols))
            raise forms.ValidationError(msg)


        ###################################################
        # Check protocols and samples are available
        ###################################################
        missing_protocols = []
        for row in mapping_l:
            if not row['filename']:
                continue
            if not models_isa.SampleCollectionProtocol.objects.filter(code_field=row['sample_collection']):
                missing_protocols.append('sample collection: {}'.format(row['sample_collection']))

            if not models_isa.ExtractionProtocol.objects.filter(code_field=row['extraction']):
                missing_protocols.append('(liquid phase) extraction: {}'.format(row['extraction']))

            if not models_isa.SpeProtocol.objects.filter(code_field=row['spe']):
                missing_protocols.append('solid phase extraction: {}'.format(row['spe']))

            if not models_isa.MeasurementProtocol.objects.filter(code_field=row['measurement']):
                missing_protocols.append('Measurement: {}'.format(row['measurement']))

            if not models_isa.StudySample.objects.filter(sample_name=row['sample'],
                                              study=models_isa.Study.objects.get(assay__id=self.assayid)):
                missing_protocols.append('sample: {}'.format(row['sample']))

        if missing_protocols:
            missing_protocols = list(set(missing_protocols))
            msg = 'Protocols have not been created for: {}'.format(', '.join(missing_protocols))
            raise forms.ValidationError(msg)

        #######################################################
        # Check assay details are present
        #######################################################
        missing_inf = check_mapping_details(mapping_l, self.assayid)
        if missing_inf and not create_assay_details:
            missing_info_str = ', '.join(missing_inf)
            msg = 'The mapping file does not have corresponding assay details for the following files shown below ' \
                  '(Please add the assay details, or run again with "create assay details") {}' \
                  ''.format(missing_info_str)
            raise forms.ValidationError(msg)


        #######################################################
        # Check polarity present
        #######################################################
        missing_polaritytype = []
        for row in mapping_l:
            if not row['polarity']:
                continue
            if not models_isa.PolarityType.objects.filter(type=row['polarity']):
                missing_polaritytype.append('polarity type: {}'.format(row['sample']))

        if missing_polaritytype:
            missing_polaritytype = list(set(missing_polaritytype))
            msg = 'Polarity types not created for: {}'.format(', '.join(missing_polaritytype))
            raise forms.ValidationError(msg)


        # save some additional information to make processing the form easier
        self.mapping_l = mapping_l
        self.dir_pths = dir_pths

        return cleaned_data


class OntologyTermForm(forms.ModelForm):

    class Meta:
        model = models_isa.OntologyTerm
        exclude = ('owner', )

class SearchOntologyTermForm(forms.Form):

    search_term = forms.CharField()


class StudySampleBatchCreateForm(forms.Form):

    study = forms.ModelChoiceField(queryset=models_isa.Study.objects.all(), widget=autocomplete.ModelSelect2(url='study-autocomplete'))
    sample_list = forms.FileField()
    replace_duplicates = forms.BooleanField(required=False,
                                            help_text='If there is already a study sample with the same name for the '
                                                      'selected Study. Flag this option to remove the old sample '
                                                      'and replace with the one detailed in the new file. If this '
                                                      'option is not flagged the duplicate samples will be ignored')


class StudySampleForm(forms.ModelForm):

    class Meta:
        model = models_isa.StudySample
        fields = ('study', 'sample_name', 'studyfactor', 'organism', 'organism_part', 'sampletype','public')
        widgets = {
            'study': autocomplete.ModelSelect2(url='study-autocomplete'),
            'organism': autocomplete.ModelSelect2(url='organism-autocomplete'),
            'organism_part': autocomplete.ModelSelect2(url='organismpart-autocomplete'),
            'studyfactor': autocomplete.ModelSelect2Multiple(url='studyfactor-autocomplete'),
            'sampletype': autocomplete.ModelSelect2(url='sampletype-autocomplete'),
        }


class StudyFactorForm(forms.ModelForm):

    class Meta:
        model = models_isa.StudyFactor
        fields = ('__all__')
        widgets = {
            'study': autocomplete.ModelSelect2(url='study-autocomplete'),
            'ontologyterm_type': autocomplete.ModelSelect2(url='ontologyterm-autocomplete'),
            'ontologyterm_value': autocomplete.ModelSelect2(url='ontologyterm-autocomplete'),
            'ontologyterm_unit': autocomplete.ModelSelect2(url='ontologyterm-autocomplete')
        }


class StudyForm(forms.ModelForm):

    class Meta:
        model = models_isa.Study
        fields = ('investigation', 'description', 'name', 'title', 'grant_number', 'funding_agency', 'submission_date',
                 'public_release_date', 'study_design_descriptors', 'public')

        widgets = {
            'investigation': autocomplete.ModelSelect2(url='investigation-autocomplete'),
            'submission_date': forms.widgets.DateInput(attrs={'type': 'date'}),
            'public_release_date':  forms.widgets.DateInput(attrs={'type': 'date'}),

            'study_design_descriptors': autocomplete.ModelSelect2Multiple(url='ontologyterm-autocomplete'),

        }


class InvestigationForm(forms.ModelForm):

    class Meta:
        model = models_isa.Investigation
        fields = ('name', 'description', 'slug', 'public')


class AssayForm(forms.ModelForm):

    class Meta:
        model = models_isa.Assay
        fields = ('study', 'description', 'name', 'public')
        widgets = {
            'study': autocomplete.ModelSelect2(url='study-autocomplete'),
        }


class OrganismForm(forms.ModelForm):
    class Meta:
        model = models_isa.Organism
        fields = ('ontologyterm', 'public')
        widgets = {
            'ontologyterm': autocomplete.ModelSelect2(url='ontologyterm-autocomplete')
        }


class OrganismPartForm(forms.ModelForm):
    class Meta:
        model = models_isa.OrganismPart
        fields = ('ontologyterm',)
        widgets = {
            'ontologyterm': autocomplete.ModelSelect2(url='ontologyterm-autocomplete')
        }


class ChromatographyProtocolForm(forms.ModelForm):
    class Meta:
        model = models_isa.ChromatographyProtocol
        exclude = ('owner', )
        widgets = {
            'chromatographytype': autocomplete.ModelSelect2(url='chromatographytype-autocomplete'),
            'ontologyterm': autocomplete.ModelSelect2Multiple(url='ontologyterm-autocomplete')
            # 'instrument_name': autocomplete.ModelSelect2(url='ontologyterm-autocomplete')
        }

class ChromatographyTypeForm(forms.ModelForm):
    class Meta:
        model = models_isa.ChromatographyType
        exclude = ('owner', )
        widgets = {
            'ontologyterm': autocomplete.ModelSelect2Multiple(url='ontologyterm-autocomplete')
        }


class MeasurementTechniqueForm(forms.ModelForm):
    class Meta:
        model = models_isa.MeasurementTechnique
        exclude = ('owner',)
        widgets = {
            'ontologyterm': autocomplete.ModelSelect2Multiple(url='ontologyterm-autocomplete')
        }


class MeasurementProtocolForm(forms.ModelForm):
    class Meta:
        model = models_isa.MeasurementProtocol
        exclude = ('owner',)
        widgets = {
            'measurementtechnique': autocomplete.ModelSelect2(url='measurementtechnique-autocomplete'),
            'ontologyterm': autocomplete.ModelSelect2Multiple(url='ontologyterm-autocomplete')
        }


class ExtractionProtocolForm(forms.ModelForm):
    class Meta:
        model = models_isa.ExtractionProtocol
        exclude = ('owner',)
        widgets = {
            'extractiontype': autocomplete.ModelSelect2(url='extractiontype-autocomplete'),
            'ontologyterm': autocomplete.ModelSelect2Multiple(url='ontologyterm-autocomplete')
        }


class ExtractionTypeForm(forms.ModelForm):
    class Meta:
        model = models_isa.ExtractionType
        exclude = ('owner',)
        widgets = {
            'ontologyterm': autocomplete.ModelSelect2Multiple(url='ontologyterm-autocomplete'),

        }


class SpeProtocolForm(forms.ModelForm):
    class Meta:
        model = models_isa.SpeProtocol
        exclude = ('owner',)
        widgets = {
            'spetype': autocomplete.ModelSelect2(url='spetype-autocomplete'),
            'ontologyterm': autocomplete.ModelSelect2Multiple(url='ontologyterm-autocomplete')
        }


class SpeTypeForm(forms.ModelForm):
    class Meta:
        model = models_isa.SpeType
        exclude = ('owner',)
        widgets = {
            'ontologyterm': autocomplete.ModelSelect2Multiple(url='ontologyterm-autocomplete')
        }


class SampleCollectionProtocolForm(forms.ModelForm):
    class Meta:
        model = models_isa.SampleCollectionProtocol
        exclude = ('owner',)


class DataTransformationProtocolForm(forms.ModelForm):
    class Meta:
        model = models_isa.DataTransformationProtocol
        exclude = ('owner',)
