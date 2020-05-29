# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
try:
    # Python 3
    from itertools import zip_longest
except ImportError:
    # Python 2
    from itertools import izip_longest as zip_longest
import os

from django.db.models import Q
from django.shortcuts import render
from django.http.response import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin, AccessMixin
from django.views.generic import CreateView, DetailView, DeleteView, UpdateView, ListView, View

from django_tables2 import RequestConfig
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect


from django_tables2.views import SingleTableMixin
from django_filters.views import FilterView
from dal import autocomplete

from gfiles.views import GFileCreateView, GFileListView

from mogi.models import models_isa
from mogi.forms import forms_isa
from mogi.tables import tables_isa
from mogi.filter import filter_isa

from mogi.utils.isa_create import upload_assay_data_files_zip, isa_batch_create
from mogi.utils.isa_export import export_isa_files
from mogi.utils.ontology_utils import search_ontology_term
from mogi.utils.sample_batch_create import sample_batch_create
from mogi.utils.mfile_upload import upload_files_from_zip
from mogi.tasks import upload_assay_data_files_dir_task, upload_files_from_dir_task



TABLE_CLASS = "mogi table-bordered table-striped table-condensed table-hover"

def success(request):
    return render(request, 'mogi/success.html')

#################################################################################
# MFile stuff
#################################################################################
class ISAOperatorMixin(SuccessMessageMixin, LoginRequiredMixin, PermissionRequiredMixin, AccessMixin):
    # Provides mixins for messaging, login, permissions and permission handling (accessmixin)
    # Setup as default for InvestigationCreate.
    redirect_string = 'ilist'
    task_string = 'update'
    permission_required = 'mogi.add_investigation'
    success_message = 'Investigation created'
    permission_denied_message = 'Permission Denied'
    success_url = reverse_lazy('ilist')
    model = models_isa.Run

    def handle_no_permission(self):
        messages.error(self.request, 'User has insufficient privileges to {}'.format(self.task_string))
        return redirect(self.redirect_string)

    def form_valid(self, form):
        # The user is automatically added to the model based on whoever is logged in at the time
        i = form.save(commit=False)
        # Only update the owner if using "Create" - prevents from updates changing the owner
        if 'Create' in self.__class__.__name__:
            i.owner = self.request.user
        i.save()
        return super(ISAOperatorMixin, self).form_valid(form)



class RunCreateView(ISAOperatorMixin, CreateView):
    model = models_isa.Run
    form_class = forms_isa.RunForm

    redirect_string = 'ilist'
    task_string = 'update'
    permission_required = 'mogi.add_run'
    success_message = 'Run created'
    permission_denied_message = 'Permission Denied'
    success_url = reverse_lazy('ilist')




class MFileCreateView(GFileCreateView, PermissionRequiredMixin, AccessMixin):
    permission_required = 'mogi.add_mfile'
    model = models_isa.MFile
    success_msg = "Experimental metabolomics file uploaded"
    success_url = reverse_lazy('upload_mfile')
    form_class = forms_isa.MFileForm
    template_name = 'mogi/mfile_form.html'

    def update_form(self, form):
        form = super(MFileCreateView, self).update_form(form)
        prefix, suffix = os.path.splitext(os.path.basename(form.instance.original_filename))
        form.instance.mfilesuffix = models_isa.MFileSuffix.objects.get(suffix=suffix)
        form.instance.prefix = prefix
        return form

    def form_valid(self, form):
        form = self.update_form(form)

        return super(MFileCreateView, self).form_valid(form)


class UploadMFilesBatch(LoginRequiredMixin, View):

    success_msg = ""
    success_url = reverse_lazy('success')
    # initial = {'key': 'value'}
    template_name = 'mogi/upload_mfiles_batch.html'


    def get(self, request, *args, **kwargs):

        form = forms_isa.UploadMFilesBatchForm(user=request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = forms_isa.UploadMFilesBatchForm(request.user, request.POST, request.FILES)

        if form.is_valid():
            data_zipfile = form.cleaned_data['data_zipfile']

            user = request.user
            if data_zipfile:
                upload_files_from_zip(data_zipfile, user)
                return render(request, 'mogi/success.html')
            else:
                recursive = form.cleaned_data['recursive']
                save_as_link = form.cleaned_data['save_as_link']
                result = upload_files_from_dir_task.delay(form.filelist,
                                                          user.username, save_as_link)
                request.session['result'] = result.id
                return render(request, 'gfiles/status.html', {'s': 0, 'progress': 0})

        else:
            print(form.errors)

        return render(request, self.template_name, {'form': form})



class MFileListView(GFileListView):
    table_class = tables_isa.AssayFileTable
    model = models_isa.MFile
    filterset_class = filter_isa.ISAFileFilter
    template_name = 'mogi/mfile_summary.html'

    def get_queryset(self):
        if self.request.user.is_superuser:
            return self.model.objects.all()
        elif self.self.request.user.is_authenticated:
            return self.model.objects.filter(Q(run__assay__public=True) |
                                             Q(run__assay__owner=self.request.user))
        else:
            return self.model.objects.filter(run__assay__public=True)





class MFileAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return models_isa.MFile.objects.none()

        qs = models_isa.MFile.objects.all()

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs


class ISAListView(SingleTableMixin, FilterView):
    table_class = tables_isa.InvestigationTable
    model = models_isa.Investigation
    template_name = 'mogi/investigation_list.html'
    filterset_class = filter_isa.InvestigationFilter

    def get_queryset(self):
        if self.request.user.is_superuser:
            return self.model.objects.all()
        elif self.request.user.is_authenticated:
            return self.model.objects.filter(Q(public=True) | Q(owner=self.request.user))
        else:
            return self.model.objects.filter(public=True)


class AutoCompleteWithUserPermissions(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return self.model_class.objects.none()
        if self.request.user.is_superuser:
            qs = self.model_class.objects.all()
        else:
            qs = self.model_class.objects.filter(Q(public=True) | Q(owner=self.request.user))

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs


############################################################################################
# Export json
############################################################################################
class ISAJsonExport(ISAOperatorMixin, View):

    def handle_no_permission(self):
        return redirect('ilist')

    def get(self, request, *args, **kwargs):

        inv = models_isa.Investigation.objects.filter(pk=self.kwargs['pk'])

        if inv:
            isa_out, json_out = export_isa_files(inv[0].id)

        else:
            json_out = {}

        return HttpResponse(json_out, content_type="application/json")


#########################################
# Batch create ISA projects
#########################################
class ISABatchCreate(ISAOperatorMixin, View):
    redirect_string = 'ilist'
    task_string = 'batch create ISA projects'
    permission_required = 'mogi.add_investigation'
    success_message = 'batch of ISA projects created'
    success_url = reverse_lazy('ilist')
    # initial = {'key': 'value'}
    template_name = 'mogi/isa_batch_create.html'

    def get(self, request, *args, **kwargs):
        form = forms_isa.ISABatchCreateForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = forms_isa.ISABatchCreateForm(request.POST, request.FILES)

        if form.is_valid():
            sample_list = form.cleaned_data['sample_list']

            isa_batch_create(sample_list, request.user.id)

            return redirect('ilist')

        return render(request, self.template_name, {'form': form})


############################################################################################
# Adding ontology terms
############################################################################################
class OntologyTermCreateView(ISAOperatorMixin, CreateView):
    model = models_isa.OntologyTerm
    form_class = forms_isa.OntologyTermForm
    redirect_string = 'list_ontologyterm'
    success_url = reverse_lazy('list_ontologyterm')
    task_string = 'create ontology term'
    permission_required = 'mogi.add_ontologyterm'
    success_message = 'Ontology term created'


class OntologyTermUpdateView(ISAOperatorMixin, UpdateView):
    model = models_isa.OntologyTerm
    form_class = forms_isa.OntologyTermForm
    redirect_string = 'list_ontologyterm'
    success_url = reverse_lazy('list_ontologyterm')
    task_string = 'update ontology term'
    permission_required = 'mogi.change_ontologyterm'
    success_message = 'Ontology term updated'


class OntologyTermDeleteView(ISAOperatorMixin, DeleteView):
    model = models_isa.OntologyTerm
    redirect_string = 'list_ontologyterm'
    success_url = reverse_lazy('list_ontologyterm')
    template_name = 'mogi/confirm_delete.html'
    task_string = 'delete ontology term'
    permission_required = 'mogi.delete_ontologyterm'
    success_message = 'Ontology term deleted'


class OntologyTermListView(ISAListView):
    table_class = tables_isa.OntologyTermTableLocal
    model = models_isa.OntologyTerm
    filterset_class = filter_isa.OntologyTermFilter
    template_name = 'mogi/ontologyterm_list.html'


class OntologyTermSearchView(ISAOperatorMixin, View):
    redirect_string = 'list_ontologyterm'
    redirect_to = '/search_ontologyterm_result/'
    task_string = 'add ontology term'
    permission_required = 'mogi.add_ontologyterm'
    template_name = 'mogi/searchontologyterm_form.html'

    def get(self, request, *args, **kwargs):

        form = forms_isa.SearchOntologyTermForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = forms_isa.SearchOntologyTermForm(request.POST, request.FILES)

        if form.is_valid():
            search_term = form.cleaned_data['search_term']
            res = search_ontology_term(search_term)
            request.session['res'] = res  # set in session
            return redirect(self.redirect_to)

            # return render(request, 'mogi/ontology_search_results.html', {'table': ont_table})
        else:
            print(form.errors)

        return render(request, self.template_name, {'form': form})


class OntologyTermSearchResultView(ISAOperatorMixin, View):
    redirect_string = 'list_ontologyterm'
    redirect_to = '/search_ontologyterm_result/'
    task_string = 'add ontology term'
    permission_required = 'mogi.add_ontologyterm'
    template_name = 'mogi/ontology_search_results.html'

    def get(self, request, *args, **kwargs):
        res = request.session.get('res')
        ont_table = tables_isa.OntologyTermTable(res)
        RequestConfig(request).configure(ont_table)
        return render(request, self.template_name, {'table': ont_table})


class AddOntologyTermView(ISAOperatorMixin, CreateView):
    # NOTE: This is specific to if the data has been searched from the ontology lookup service
    model = models_isa.OntologyTerm
    redirect_string = 'list_ontologyterm'
    form_class = forms_isa.OntologyTermForm
    task_string = 'add ontology term'
    permission_required = 'mogi.add_ontologyterm'
    success_url = reverse_lazy('list_ontologyterm')
    success_message = 'Ontology term created'

    def get_initial(self):
        res = self.request.session.get('res')

        c = self.kwargs['c']
        for row in res:
            if row['c']==int(c):
                return row
        return {}


class OntologyTermAutocomplete(AutoCompleteWithUserPermissions):
    model_class = models_isa.OntologyTerm


############################################################################################
# Organism Views
############################################################################################
class OrganismCreateView(ISAOperatorMixin, CreateView):
    model = models_isa.Organism
    form_class = forms_isa.OrganismForm
    success_url = reverse_lazy('org_list')
    redirect_string = 'org_list'
    task_string = 'create organism details'
    permission_required = 'mogi.add_organism'
    success_message = 'Organism details created'


class OrganismUpdateView(ISAOperatorMixin, UpdateView):
    model = models_isa.Organism
    form_class = forms_isa.OrganismForm
    success_url = reverse_lazy('org_list')
    success_message = 'Organism updated'
    redirect_string = 'org_list'
    task_string = 'update organism details'
    permission_required = 'mogi.change_organism'



class OrganismDeleteView(ISAOperatorMixin, DeleteView):
    model = models_isa.Organism
    success_message = 'Organism Deleted'
    redirect_string = 'org_list'
    task_string = 'delete organism details'
    permission_required = 'mogi.delete_organism'
    template_name = 'mogi/confirm_delete.html'


class OrganismListView(ISAListView):
    model = models_isa.Organism
    table_class = tables_isa.OrganismTable
    filterset_class = filter_isa.OrganismFilter
    template_name = 'mogi/organism_list.html'


############################################################################################
# Organism Part Views
############################################################################################
class OrganismPartCreateView(ISAOperatorMixin, CreateView):
    model = models_isa.OrganismPart
    form_class = forms_isa.OrganismPartForm
    success_url = reverse_lazy('orgpart_list')
    success_message = 'Organism part created'
    redirect_string = 'orgpart_list'
    task_string = 'create organism part details'
    permission_required = 'mogi.add_organism'


class OrganismPartUpdateView(ISAOperatorMixin, UpdateView):
    model = models_isa.OrganismPart
    form_class = forms_isa.OrganismPartForm
    success_url = reverse_lazy('orgpart_list')
    success_message = 'Organism part updated'
    redirect_string = 'orgpart_list'
    task_string = 'update organism part details'
    permission_required = 'mogi.change_organism'


class OrganismPartDeleteView(ISAOperatorMixin, DeleteView):
    model = models_isa.OrganismPart
    success_url = reverse_lazy('orgpart_list')
    redirect_string = 'org_list'
    task_string = 'delete organism part details'
    permission_required = 'mogi.delete_organism_part'
    template_name = 'mogi/confirm_delete.html'


class OrganismPartListView(ISAListView):
    table_class = tables_isa.OrganismPartTable
    model = models_isa.OrganismPart
    filterset_class = filter_isa.OrganismPartFilter
    template_name = 'mogi/organism_part_list.html'


class OrganismAutocomplete(OntologyTermAutocomplete):
    model_class = models_isa.Organism


class OrganismPartAutocomplete(OntologyTermAutocomplete):
    model_class = models_isa.OrganismPart


############################################################################################
# Protocol views
###########################################################################################
#=======================================
# Sample Collection Protocol
#=======================================
class SampleCollectionProtocolCreateView(ISAOperatorMixin, CreateView):
    model = models_isa.SampleCollectionProtocol
    form_class = forms_isa.SampleCollectionProtocolForm
    success_url = reverse_lazy('scp_list')
    success_message = 'Sample collection protocol created'
    redirect_string = 'scp_list'
    task_string = 'create sample collection protocol'
    permission_required = 'mogi.add_samplecollectionprotocol'



class SampleCollectionProtocolUpdateView(ISAOperatorMixin, UpdateView):
    model = models_isa.SampleCollectionProtocol
    form_class = forms_isa.SampleCollectionProtocolForm
    success_url = reverse_lazy('scp_list')
    success_message = 'Sample collection protocol updated'
    redirect_string = 'scp_list'
    task_string = 'update sample collection protocol'
    permission_required = 'mogi.change_samplecollectionprotocol'


class SampleCollectionProtocolDeleteView(ISAOperatorMixin, DeleteView):
    model = models_isa.SampleCollectionProtocol
    success_url = reverse_lazy('scp_list')
    template_name = 'mogi/confirm_delete.html'
    redirect_string = 'scp_list'
    task_string = 'delete sample collection protocol'
    permission_required = 'mogi.delete_samplecollectionprotocol'


class SampleCollectionProtocolListView(ISAListView):
    table_class = tables_isa.SampleCollectionProtocolTable
    model = models_isa.SampleCollectionProtocol
    filterset_class = filter_isa.SampleCollectionProtocolFilter
    template_name = 'mogi/sample_collection_protocol_list.html'


#=======================================
# Data transformation Protocol
#=======================================
class DataTransformationProtocolCreateView(ISAOperatorMixin, CreateView):
    model = models_isa.DataTransformationProtocol
    form_class = forms_isa.DataTransformationProtocolForm
    success_url = reverse_lazy('dp_list')
    success_message = 'Data transformation protocol created'

    redirect_string = 'dp_list'
    task_string = 'create data transformation protocol'
    permission_required = 'mogi.add_datatransformationprotocol'


class DataTransformationProtocolUpdateView(ISAOperatorMixin, UpdateView):
    model = models_isa.DataTransformationProtocol
    form_class = forms_isa.DataTransformationProtocolForm
    success_url = reverse_lazy('dp_list')
    success_message = 'Data transformation protocol updated'

    redirect_string = 'dp_list'
    task_string = 'update data transformation protocol'
    permission_required = 'mogi.change_datatransformationprotocol'


class DataTransformationProtocolDeleteView(ISAOperatorMixin, DeleteView):
    model = models_isa.DataTransformationProtocol
    success_url = reverse_lazy('dp_list')
    template_name = 'mogi/confirm_delete.html'

    redirect_string = 'dp_list'
    task_string = 'delete data transformation protocol'
    permission_required = 'mogi.delete_datatransformationprotocol'


class DataTransformationProtocolListView(ISAListView):
    table_class = tables_isa.DataTransformationProtocolTable
    model = models_isa.DataTransformationProtocol
    filterset_class = filter_isa.DataTransformationProtocolFilter
    template_name = 'mogi/data_transformation_protocol_list.html'


#=======================================
# Extraction Protocol
#=======================================
class ExtractionProtocolCreateView(ISAOperatorMixin, CreateView):
    model = models_isa.ExtractionProtocol
    form_class = forms_isa.ExtractionProtocolForm
    success_url = reverse_lazy('ep_list')
    success_message = '(liquid-phase) Extraction protocol created'

    redirect_string = 'ep_list'
    task_string = 'create (liquid-phase) extraction protocol'
    permission_required = 'mogi.add_extractionprotocol'


class ExtractionProtocolUpdateView(ISAOperatorMixin, UpdateView):
    model = models_isa.ExtractionProtocol
    form_class = forms_isa.ExtractionProtocolForm
    success_url = reverse_lazy('ep_list')
    success_message = '(liquid-phase) Extraction protocol updated'

    redirect_string = 'ep_list'
    task_string = 'update (liquid-phase) extraction protocol'
    permission_required = 'mogi.change_extractionprotocol'


class ExtractionProtocolListView(ISAListView):
    table_class = tables_isa.ExtractionProtocolTable
    model = models_isa.ExtractionProtocol
    filterset_class = filter_isa.ExtractionProtocolFilter
    template_name = 'mogi/extraction_protocol_list.html'


class ExtractionProtocolDeleteView(DeleteView):
    model = models_isa.ExtractionProtocol
    success_url = reverse_lazy('ep_list')
    template_name = 'mogi/confirm_delete.html'

    redirect_string = 'ep_list'
    task_string = 'Delete (liquid-phase) extraction protocol'
    permission_required = 'mogi.delete_extractionprotocol'



#=======================================
# Extraction Type
#=======================================
class ExtractionTypeCreateView(ISAOperatorMixin, CreateView):
    model = models_isa.ExtractionType
    form_class = forms_isa.ExtractionTypeForm
    success_url = reverse_lazy('et_list')
    success_message = 'Extraction type created'

    redirect_string = 'et_list'
    task_string = 'create extraction type'
    permission_required = 'mogi.add_extractiontype'


class ExtractionTypeUpdateView(ISAOperatorMixin, UpdateView):
    model = models_isa.ExtractionType
    form_class = forms_isa.ExtractionTypeForm
    success_url = reverse_lazy('et_list')
    success_message = 'Extraction type updated'

    redirect_string = 'et_list'
    task_string = 'update extraction type'
    permission_required = 'mogi.change_extractiontype'


class ExtractionTypeDeleteView(ISAOperatorMixin, DeleteView):
    model = models_isa.ExtractionType
    success_url = reverse_lazy('et_list')
    template_name = 'mogi/confirm_delete.html'

    redirect_string = 'et_list'
    task_string = 'delete extraction type'
    permission_required = 'mogi.delete_extractiontype'



class ExtractionTypeListView(ISAListView):
    table_class = tables_isa.ExtractionTypeTable
    model = models_isa.ExtractionType
    filterset_class = filter_isa.ExtractionTypeFilter
    template_name = 'mogi/extraction_type_list.html'

class ExtractionTypeAutocomplete(OntologyTermAutocomplete):
    model_class = models_isa.ExtractionType


#=======================================
# Chromatography protocol
#=======================================
class ChromatographyProtocolCreateView(ISAOperatorMixin, CreateView):
    model = models_isa.ChromatographyProtocol
    form_class = forms_isa.ChromatographyProtocolForm
    success_url = reverse_lazy('cp_list')
    success_message = 'Chromatography protocol created'

    redirect_string = 'cp_list'
    task_string = 'create chromatography protocol'
    permission_required = 'mogi.add_chromatographyprotocol'


class ChromatographyProtocolUpdateView(ISAOperatorMixin, UpdateView):
    model = models_isa.ChromatographyProtocol
    form_class = forms_isa.ChromatographyProtocolForm
    success_url = reverse_lazy('cp_list')
    success_message = 'Chromatography protocol updated'

    redirect_string = 'cp_list'
    task_string = 'update chromatography protocol'
    permission_required = 'mogi.change_chromatographyprotocol'


class ChromatographyProtocolDeleteView(ISAOperatorMixin, DeleteView):
    model = models_isa.ChromatographyProtocol
    success_url = reverse_lazy('cp_list')
    template_name = 'mogi/confirm_delete.html'

    redirect_string = 'cp_list'
    task_string = 'delete chromatography protocol'
    permission_required = 'mogi.delete_chromatographyprotocol'


class ChromatographyProtocolListView(ISAListView):
    table_class = tables_isa.ChromatographyProtocolTable
    model = models_isa.ChromatographyProtocol
    filterset_class = filter_isa.ChromatographyProtocolFilter
    template_name = 'mogi/chromatography_protocol_list.html'


#=======================================
# Chromatography type
#=======================================
class ChromatographyTypeCreateView(ISAOperatorMixin, CreateView):
    model = models_isa.ChromatographyType
    form_class = forms_isa.ChromatographyTypeForm
    success_url = reverse_lazy('ct_list')
    success_message = 'Chromatography type created'

    redirect_string = 'ct_list'
    task_string = 'create chromatography type'
    permission_required = 'mogi.add_chromatographytype'



class ChromatographyTypeUpdateView(ISAOperatorMixin, UpdateView):
    model = models_isa.ChromatographyType
    form_class = forms_isa.ChromatographyTypeForm
    success_url = reverse_lazy('ct_list')
    success_message = 'Chromatography type updated'

    redirect_string = 'ct_list'
    task_string = 'update chromatography type'
    permission_required = 'mogi.change_chromatographytype'


class ChromatographyTypeDeleteView(ISAOperatorMixin, DeleteView):
    model = models_isa.ChromatographyType
    success_url = reverse_lazy('ct_list')
    template_name = 'mogi/confirm_delete.html'

    redirect_string = 'ct_list'
    task_string = 'delete chromatography type'
    permission_required = 'mogi.delete_chromatographytype'


class ChromatographyTypeListView(ISAListView):
    table_class = tables_isa.ChromatographyTypeTable
    model = models_isa.ChromatographyType
    filterset_class = filter_isa.ChromatographyTypeFilter
    template_name = 'mogi/chromatography_type_list.html'



class ChromatographyTypeAutocomplete(OntologyTermAutocomplete):
    model_class = models_isa.ChromatographyType


#=======================================
# SPE protocol
#=======================================
class SpeProtocolCreateView(ISAOperatorMixin, CreateView):
    model = models_isa.SpeProtocol
    form_class = forms_isa.SpeProtocolForm
    success_url = reverse_lazy('spep_list')
    success_message = 'Solid phase extraction protocol created'

    redirect_string = 'spep_list'
    task_string = 'create solid phase extraction protocol'
    permission_required = 'mogi.add_speprotocol'


class SpeProtocolUpdateView(ISAOperatorMixin, UpdateView):
    model = models_isa.SpeProtocol
    form_class = forms_isa.SpeProtocolForm
    success_url = reverse_lazy('spep_list')
    success_message = 'Solid phase extraction protocol updated'

    redirect_string = 'spep_list'
    task_string = 'update solid phase extraction protocol'
    permission_required = 'mogi.change_speprotocol'


class SpeProtocolDeleteView(ISAOperatorMixin, DeleteView):
    model = models_isa.SpeProtocol
    success_url = reverse_lazy('spep_list')
    template_name = 'mogi/confirm_delete.html'

    redirect_string = 'spep_list'
    task_string = 'delete solid phase extraction protocol'
    permission_required = 'mogi.delete_speprotocol'



class SpeProtocolListView(ISAListView):
    table_class = tables_isa.SpeProtocolTable
    model = models_isa.SpeProtocol
    filterset_class = filter_isa.SpeProtocolFilter
    template_name = 'mogi/spe_protocol_list.html'


#=======================================
# SPE type
#=======================================
class SpeTypeCreateView(ISAOperatorMixin, CreateView):
    model = models_isa.SpeType
    form_class = forms_isa.SpeTypeForm
    success_url = reverse_lazy('spet_list')
    success_message = 'Solid phase extraction type created'

    redirect_string = 'spet_list'
    task_string = 'create solid phase extraction type'
    permission_required = 'mogi.add_spetype'


class SpeTypeUpdateView(ISAOperatorMixin, UpdateView):
    model = models_isa.SpeType
    form_class = forms_isa.SpeTypeForm
    success_url = reverse_lazy('spet_list')
    success_message = 'Solid phase extraction type updated'

    redirect_string = 'spet_list'
    task_string = 'update solid phase extraction type'
    permission_required = 'mogi.change_spetype'


class SpeTypeDeleteView(ISAOperatorMixin, DeleteView):
    model = models_isa.SpeType
    success_url = reverse_lazy('spet_list')
    template_name = 'mogi/confirm_delete.html'

    redirect_string = 'spet_list'
    task_string = 'delete solid phase extraction type'
    permission_required = 'mogi.delete_spetype'


class SpeTypeListView(ISAListView):
    table_class = tables_isa.SpeTypeTable
    model = models_isa.SpeType
    filterset_class = filter_isa.SpeTypeFilter
    template_name = 'mogi/spe_type_list.html'


class SpeTypeAutocomplete(OntologyTermAutocomplete):
    model_class = models_isa.SpeType



#=======================================
# Measurement protocol
#=======================================
class MeasurementProtocolCreateView(ISAOperatorMixin, CreateView):
    model = models_isa.MeasurementProtocol
    form_class = forms_isa.MeasurementProtocolForm
    success_url = reverse_lazy('mp_list')
    success_message = 'Measurement protocol created'

    redirect_string = 'mp_list'
    task_string = 'create measurement protocol'
    permission_required = 'mogi.add_measurementprotocol'


class MeasurementProtocolUpdateView(ISAOperatorMixin, UpdateView):
    model = models_isa.MeasurementProtocol
    form_class = forms_isa.MeasurementProtocolForm
    success_url = reverse_lazy('mp_list')
    success_message = 'Measurement protocol updated'

    redirect_string = 'mp_list'
    task_string = 'edit measurement protocol'
    permission_required = 'mogi.change_measurementprotocol'


class MeasurementProtocolDeleteView(ISAOperatorMixin, DeleteView):
    model = models_isa.MeasurementProtocol
    success_url = reverse_lazy('mp_list')
    template_name = 'mogi/confirm_delete.html'

    redirect_string = 'mp_list'
    task_string = 'delete measurement protocol'
    permission_required = 'mogi.delete_measurementprotocol'


class MeasurementProtocolListView(ISAListView):
    table_class = tables_isa.MeasurementProtocolTable
    model = models_isa.MeasurementProtocol
    filterset_class = filter_isa.MeasurementProtocolFilter
    template_name = 'mogi/measurement_protocol_list.html'


#=======================================
# Measurement technique
#=======================================
class MeasurementTechniqueCreateView(ISAOperatorMixin, CreateView):
    model = models_isa.MeasurementTechnique
    form_class = forms_isa.MeasurementTechniqueForm
    success_url = reverse_lazy('mt_list')
    success_message = 'Measurement technique created'

    redirect_string = 'mt_list'
    task_string = 'create measurement technique'
    permission_required = 'mogi.add_measurementtechnique'


class MeasurementTechniqueUpdateView(ISAOperatorMixin, UpdateView):
    model = models_isa.MeasurementTechnique
    form_class = forms_isa.MeasurementTechniqueForm
    success_url = reverse_lazy('mt_list')
    success_message = 'Measurement technique updated'

    redirect_string = 'mt_list'
    task_string = 'update measurement technique'
    permission_required = 'mogi.change_measurementtechnique'


class MeasurementTechniqueDeleteView(ISAOperatorMixin, DeleteView):
    model = models_isa.MeasurementTechnique
    success_url = reverse_lazy('mt_list')
    template_name = 'mogi/confirm_delete.html'

    redirect_string = 'mt_list'
    task_string = 'delete measurement technique'
    permission_required = 'mogi.delete_measurementtechnique'



class MeasurementTechniqueListView(ISAListView):
    table_class = tables_isa.MeasurementTechniqueTable
    model = models_isa.MeasurementTechnique
    filterset_class = filter_isa.MeasurementTechniqueFilter
    template_name = 'mogi/measurement_technique_list.html'

class MeasurementTechniqueAutocomplete(OntologyTermAutocomplete):
    model_class = models_isa.MeasurementTechnique




from django.contrib import messages

#
# class SuccessMessageExtraMixin(SuccessMessageMixin):
#     """
#     Adds a success message on successful form submission.
#     """
#     extra_tags = ''
#
#     def form_valid(self, form):
#         response = super(SuccessMessageMixin, self).form_valid(form)
#         success_message = self.get_success_message(form.cleaned_data)
#         if success_message:
#             messages.success(self.request, success_message, self.extra_tags)
#         return response


############################################################################################
# Investigation views
############################################################################################
class InvestigationCreateView(ISAOperatorMixin, CreateView):
    model = models_isa.Investigation
    form_class = forms_isa.InvestigationForm

    redirect_string = 'ilist'
    task_string = 'create investigation'
    permission_required = 'mogi.add_investigation'

    success_message = 'Investigation created'

    success_url = reverse_lazy('ilist')





class InvestigationUpdateView(ISAOperatorMixin, UpdateView):
    permission_required = 'mogi.change_investigation'
    model = models_isa.Investigation
    form_class = forms_isa.InvestigationForm
    task_string = "update investigation"
    success_message = 'Investigation updated'
    success_url = reverse_lazy('ilist')



class InvestigationDeleteView(ISAOperatorMixin, DeleteView):
    model = models_isa.Investigation
    success_url = reverse_lazy('ilist')
    template_name = 'mogi/confirm_delete.html'
    success_message = 'Investigation Deleted'
    redirect_string = 'ilist'
    task_string = 'delete investigation'
    permission_required = 'mogi.delete_investigation'


# Not required (use InvestigationDetailTablesView instead)
#class InvestigationDetailView(LoginRequiredMixin, DetailView):
#    model = models_isa.Investigation
#    fields = '__all__'


class InvestigationAutocomplete(OntologyTermAutocomplete):
    model_class = models_isa.Investigation


class InvestigationDetailTablesView(View):
    '''
    Run a registered workflow
    '''

    template_name = 'mogi/investigation_detail_tables.html'

    def get_queryset(self):
        if self.request.user.is_superuser:
            return models_isa.Investigation.objects.get(pk=self.kwargs['pk'])
        else:
            return models_isa.Investigation.objects.get(pk=self.kwargs['pk'], public=True)


    def get(self, request, *args, **kwargs):

        l1, l2, investigation = self.page_setup(request)

        return render(request, self.template_name, {'list1': l1, 'list2': l2, 'investigation': investigation})

    def page_setup(self, request):
        # Need to setup a config for the tables (only 1 required per template page)
        rc = RequestConfig(request, paginate={'per_page': 20})

        investigation = self.get_queryset()

        atables = []
        afilters = []

        stables = []
        sfilters = []

        studies = []
        c = 0
        # loop through all the data_inputs from the associated workflow
        for s in investigation.study_set.all():
            assay_track = 'assay{}'.format(c)
            sample_track = 'sample{}'.format(c)

            assays = s.assay_set.all()

            # Create an invidivual filter for each table (assays)
            af = filter_isa.AssayFilter(request.GET, queryset=assays, prefix=c)

            atable = tables_isa.AssayTable(af.qs, prefix=c, attrs={'name': assay_track, 'id': assay_track,
                                                        'class': TABLE_CLASS})
            # load the table into the requestconfig
            rc.configure(atable)

            # Create an invidivual filter for each table (samples)
            sf = filter_isa.StudySampleFilter(request.GET, queryset=s.studysample_set.all(), prefix=c+1)
            stable = tables_isa.StudySampleTable(sf.qs, prefix=c, attrs={'name': sample_track, 'id': sample_track,
                                                              'class': TABLE_CLASS})
            # load the table into the requestconfig
            rc.configure(stable)

            # add the tables and filters to the list used in the template
            atables.append(atable)
            afilters.append(af)
            stables.append(stable)
            sfilters.append(sf)
            studies.append(s)

            c+=2

        # create a list of all the information. Using a simple list format as it is just easy to use in the template
        l1 = zip(studies, atables, afilters, stables, sfilters)
        l2 = zip(studies, atables, afilters, stables, sfilters)
        return l1, l2, investigation


class InvestigationListViewOLD(ISAListView):
    model = models_isa.Investigation
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super(InvestigationListViewOLD, self).get_context_data(**kwargs)
        context['now'] = 1
        # Investigation.objects.filter(self.kwargs['company']).order_by('-pk')
        return context

class InvestigationListView(ISAListView):
    # table_class = ISAFileSelectTable
    # model = GenericFile
    # template_name = 'mogi/isa_file_select.html'
    # filterset_class =  ISAFileFilter
    permission_required = 'mogi.view_investigation'

    table_class = tables_isa.InvestigationTable
    model = models_isa.Investigation
    template_name = 'mogi/investigation_list.html'
    filterset_class = filter_isa.InvestigationFilter

    def get_queryset(self):
        if self.request.user.is_superuser:
            return self.model.objects.all()
        elif self.request.user.is_authenticated:
            return self.model.objects.filter(Q(public=True) | Q(owner=self.request.user))
        else:
            return self.model.objects.filter(public=True)

    # def post(self, request, *args, **kwargs):
        # workflow_sync(request.user)
        # redirects to show the current available workflows
        # return redirect('workflow_summary')


############################################################################################
# Study views
############################################################################################
class StudyCreateView(ISAOperatorMixin, CreateView):
    model = models_isa.Study
    success_url = reverse_lazy('ilist')
    form_class = forms_isa.StudyForm
    success_message = 'Study created'

    redirect_string = 'ilist'
    task_string = 'create study'
    permission_required = 'mogi.add_study'



class StudyUpdateView(ISAOperatorMixin, UpdateView):
    model = models_isa.Study
    success_url = reverse_lazy('ilist')
    form_class = forms_isa.StudyForm
    success_message = 'Study updated'

    redirect_string = 'ilist'
    task_string = 'update study'
    permission_required = 'mogi.change_study'


# Not required
# class StudyListView(ISAListView):
#     table_class = tables_isa.StudyTable
#     model = models_isa.Study
#     fields = '__all__'


class StudyDeleteView(ISAOperatorMixin, DeleteView):
    model = models_isa.Study
    success_url = reverse_lazy('ilist')
    template_name = 'mogi/confirm_delete.html'

    redirect_string = 'ilist'
    task_string = 'delete study'
    permission_required = 'mogi.delete_study'


class StudyAutocomplete(OntologyTermAutocomplete):
    model_class = models_isa.Study


############################################################################################
# Assay views
############################################################################################
class AssayCreateView(ISAOperatorMixin, CreateView):
    model = models_isa.Assay
    success_url = reverse_lazy('ilist')
    form_class = forms_isa.AssayForm
    success_message = 'Assay created'

    redirect_string = 'ilist'
    task_string = 'create assay'
    permission_required = 'mogi.add_assay'



class AssayUpdateView(ISAOperatorMixin, UpdateView):
    model = models_isa.Assay
    success_url = reverse_lazy('ilist')
    fields = '__all__'
    success_message = 'Assay updated'

    redirect_string = 'ilist'
    task_string = 'update assay'
    permission_required = 'mogi.change_assay'

# Not required
# class AssayListView(ISAListView):
#    model = models_isa.Assay
#    fields = '__all__'


class AssayAutocomplete(OntologyTermAutocomplete):
    model_class = models_isa.Assay


class UploadAssayDataFilesView(ISAOperatorMixin, View):

    # initial = {'key': 'value'}
    template_name = 'mogi/upload_assay_data_files.html'

    def get(self, request, *args, **kwargs):
        form = forms_isa.UploadAssayDataFilesForm(user=self.request.user, assayid=self.kwargs['assayid'])

        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = forms_isa.UploadAssayDataFilesForm(request.user, request.POST, request.FILES, assayid=self.kwargs[
            'assayid'])

        if form.is_valid():

            data_zipfile = form.cleaned_data['data_zipfile']
            data_mappingfile = form.cleaned_data['data_mappingfile']
            assayid = kwargs['assayid']
            create_assay_details = form.cleaned_data['create_assay_details']


            if data_zipfile:
                upload_assay_data_files_zip(assayid, data_zipfile,  form.mapping_l, request.user, create_assay_details)
                return redirect('ilist')
            else:
                save_as_link = form.cleaned_data['save_as_link']
                # recursive = form.cleaned_data['recursive']
                # dir_pths = get_pths_from_field(form.dir_fields, form.cleaned_data, request.user.username)

                # rstring = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
                # unique_folder = os.path.join(settings.MEDIA_ROOT, 'mapping', rstring)
                # os.makedirs(unique_folder)
                # data_mappingfile_pth = os.path.join(unique_folder, data_mappingfile.name)
                # with default_storage.open(data_mappingfile_pth, 'wb+') as destination:
                #     for chunk in data_mappingfile.chunks():
                #         print chunk
                #         destination.write(chunk)

                # mapping_l = list(csv.DictReader(data_mappingfile))

                result = upload_assay_data_files_dir_task.delay(form.filelist, request.user.id,
                                                                form.mapping_l, assayid, save_as_link,
                                                                create_assay_details)
                request.session['result'] = result.id
                return render(request, 'gfiles/status.html', {'s': 0, 'progress': 0})


        return render(request, self.template_name, {'form': form})


class AssayDeleteView(ISAOperatorMixin, DeleteView):
    model = models_isa.Assay
    success_url = reverse_lazy('ilist')
    template_name = 'mogi/confirm_delete.html'

    redirect_string = 'ilist'
    task_string = 'delete assay'
    permission_required = 'mogi.delete_assay'


############################################################################################
# Study sample views
############################################################################################
class StudySampleCreateView(ISAOperatorMixin, CreateView):
    form_class = forms_isa.StudySampleForm
    model = models_isa.StudySample
    success_url = reverse_lazy('ssam_list')
    success_message = 'Study sample created'

    redirect_string = 'ssam_list'
    task_string = 'create study sample'
    permission_required = 'mogi.add_studysample'


class StudySampleUpdateView(ISAOperatorMixin, UpdateView):
    form_class = forms_isa.StudySampleForm
    model = models_isa.StudySample
    success_url = reverse_lazy('ssam_list')
    success_message = 'Study sample updated'

    redirect_string = 'ssam_list'
    task_string = 'update study sample'
    permission_required = 'mogi.change_studysample'


class StudySampleDeleteView(ISAOperatorMixin, DeleteView):
    model = models_isa.StudySample
    success_url = reverse_lazy('ssam_list')
    template_name = 'mogi/confirm_delete.html'

    redirect_string = 'ssam_list'
    task_string = 'delete study sample'
    permission_required = 'mogi.delete_studysample'


class StudySampleListView(ISAListView):
    table_class = tables_isa.StudySampleTable
    model = models_isa.StudySample
    filterset_class = filter_isa.StudySampleFilter
    template_name = 'mogi/study_sample_list.html'


class StudySampleBatchCreate(ISAOperatorMixin, View):

    success_msg = "batch of samples created"
    # initial = {'key': 'value'}
    template_name = 'mogi/study_sample_batch_create.html'

    redirect_string = 'ssam_list'
    task_string = 'batch create study samples'
    permission_required = ('mogi.add_studyfactor', 'mogi.add_studysample')

    def get(self, request, *args, **kwargs):
        form = forms_isa.StudySampleBatchCreateForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = forms_isa.StudySampleBatchCreateForm(request.POST, request.FILES)

        if form.is_valid():

            study = form.cleaned_data['study']
            sample_list = form.cleaned_data['sample_list']
            replace_duplicates = form.cleaned_data['replace_duplicates']
            sample_batch_create(sample_list, study, replace_duplicates)

            return redirect('ssam_list')

        return render(request, self.template_name, {'form': form})


############################################################################################
# Study factor views
############################################################################################
class StudyFactorCreateView(ISAOperatorMixin, CreateView):
    model = models_isa.StudyFactor
    form_class = forms_isa.StudyFactorForm
    success_url = reverse_lazy('sflist')
    success_message = 'Study factor created'

    redirect_string = 'sflist'
    task_string = 'create study factor'
    permission_required = 'mogi.add_studyfactor'



class StudyFactorUpdateView(ISAOperatorMixin, UpdateView):
    model = models_isa.StudyFactor
    form_class =  forms_isa.StudyFactorForm
    success_url = reverse_lazy('sflist')
    success_message = 'Study factor updated'

    redirect_string = 'sflist'
    task_string = 'update study factor'
    permission_required = 'mogi.change_studyfactor'


class StudyFactorDeleteView(ISAOperatorMixin, DeleteView):
    model = models_isa.StudyFactor
    success_url = reverse_lazy('sflist')
    template_name = 'mogi/confirm_delete.html'

    redirect_string = 'sflist'
    task_string = 'delete study factor'
    permission_required = 'mogi.delete_studyfactor'


class StudyFactorListView(ISAListView):
    table_class = tables_isa.StudyFactorTable
    model = models_isa.StudyFactor
    filterset_class = filter_isa.StudyFactorFilter
    template_name = 'mogi/study_factor_list.html'


class StudyFactorAutocomplete(OntologyTermAutocomplete):
    model_class = models_isa.StudyFactor

class SampleTypeAutocomplete(OntologyTermAutocomplete):
    model_class = models_isa.SampleType



############################################################################################
# Assay file views
###########################################################################################
class ISAFileSummaryView(LoginRequiredMixin, SingleTableMixin, FilterView):
    '''
    View and initiate a run for all registered workflows.

    Workflows can also be synced here as well
    '''
    table_class = tables_isa.ISAFileSelectTable
    model = models_isa.GenericFile
    template_name = 'mogi/isa_file_select.html'
    filterset_class =  filter_isa.ISAFileFilter

    # def post(self, request, *args, **kwargs):
    #     workflow_sync(request.user)
    #     # redirects to show the current available workflows
    #     return redirect('workflow_summary')


def check_assay_detail_perm(assayid, user, detail=True):
    if user.is_superuser or models_isa.Assay.objects.get(id=assayid).public or models_isa.Assay.objects.get(id=assayid).owner == user:
        if detail:
            return models_isa.AssayDetail.objects.filter(assay_id=assayid)
        else:
            return models_isa.MFile.objects.filter(run__assaydetail__assay_id=assayid)
    else:
        if detail:
            return models_isa.AssayDetail.objects.none()
        else:
            return models_isa.MFile.objects.none()


class AssayFileSummaryView(View):

    # initial = {'key': 'value'}
    template_name = 'mogi/assay_files.html'

    def get(self, request, *args, **kwargs):
        mfiles = check_assay_detail_perm(kwargs['assayid'], request.user, detail=False)
        print(mfiles)
        table = tables_isa.AssayFileTable(mfiles)
        RequestConfig(request).configure(table)

        i = models_isa.Investigation.objects.get(study__assay__id=kwargs['assayid'])

        return render(request, self.template_name,  {'table': table, 'investigation_id':i.id})

    # def post(self, request, *args, **kwargs):
    #     form = UploadAssayDataFilesForm(request.POST, request.FILES, assayid=self.kwargs['assayid'])
    #
    #     if form.is_valid():
    #
    #         data_zipfile = form.cleaned_data['data_zipfile']
    #         data_mappingfile = form.cleaned_data['data_mappingfile']
    #         assayid = kwargs['assayid']
    #         upload_assay_data_files(assayid, data_zipfile, data_mappingfile)
    #
    #         # result = update_workflows_task.delay(self.kwargs['dmaid'])
    #         # request.session['result'] = result.id
    #         return render(request, 'dma/submitted.html')
    #
    #     return render(request, self.template_name, {'form': form})


class AssayDetailSummaryView(View):

    # initial = {'key': 'value'}
    template_name = 'mogi/assay_details.html'

    def get(self, request, *args, **kwargs):
        mfiles = check_assay_detail_perm(kwargs['assayid'], request.user)
        table = tables_isa.AssayDetailTable(mfiles)
        RequestConfig(request).configure(table)
        i = models_isa.Investigation.objects.get(study__assay__id=kwargs['assayid'])
        assay_desc= models_isa.Assay.objects.get(id=kwargs['assayid']).description

        return render(request, self.template_name,  {'table': table,
                                                     'investigation_id': i.id,
                                                     'assay_description': assay_desc,
                                                     'assayid':kwargs['assayid']
                                                       })


class PolarityTypeAutocomplete(OntologyTermAutocomplete):
    model_class = models_isa.PolarityType
