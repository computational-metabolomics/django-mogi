from django.conf.urls import url
from django.urls import include
from mogi.views import (
    views_general,
    views_isa,
    views_galaxy,
    views_search,
    views_compounds,
    views_datasets,
    views_peaks,
    views_annotations,

)

from mogi.models.models_isa import OntologyTerm
from dal import autocomplete
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'incoming_galaxy_data', views_galaxy.IncomingGalaxyDataViewSet)

urlpatterns = [

    #############################################
    # General
    ##############################################
    url(r'^$', views_general.index, name='index'),
    url(r'^submitted/$', views_general.success, name='submitted'),
    url(r'^about/$', views_general.about, name='about'),
    url(r'^data_and_results_summary/$', views_general.DataAndResultsSummaryView.as_view(),
        name='data_and_results_summary'),

    #############################################
    # Datasets
    ##############################################
    url('^upload_datasets/$', views_datasets.UploadDatasetsView.as_view(), name='upload_datasets'),
    url('^dataset_summary/$', views_datasets.DatasetListView.as_view(), name='dataset_summary'),

    #############################################
    # Peaks
    ##############################################
    url('^eics/(?P<did>.+)/(?P<grpid>.+)/$', views_peaks.EicView.as_view(), name='eics'),
    url('^speaks/(?P<did>.+)/(?P<grpid>.+)/(?P<sid>.+)/$', views_peaks.SPeakView.as_view(), name='speaks'),

    #############################################
    # Compound
    ##############################################
    url('^compounds/$', views_compounds.CompoundListView.as_view(), name='compounds'),
    url('^upload_compounds/$', views_compounds.UploadCompounds.as_view(), name='upload_compounds'),

    #############################################
    # Annotations
    ##############################################
    url('^canns/(?P<did>\d+)/$', views_annotations.CombinedAnnotationListView.as_view(), name='canns'),
    url('^canns_sm/(?P<did>\d+)/(?P<grpid>.+)/(?P<sid>.+)/(?P<inchikey>.+)$', views_annotations.SpectralMatchingListView.as_view(), name='canns_sm'),
    url('^canns_metfrag/(?P<did>\d+)/(?P<grpid>.+)/(?P<sid>.+)/(?P<inchikey>.+)$', views_annotations.MetFragListView.as_view(), name='canns_metfrag'),
    url('^canns_sirius/(?P<did>\d+)/(?P<grpid>.+)/(?P<sid>.+)/(?P<inchikey>.+)$', views_annotations.SiriusCSIFingerIDListView.as_view(), name='canns_sirius'),
    url('^smplot/(?P<did>\d+)/(?P<qpid>\d+)/(?P<lpid>\d+)$', views_annotations.SMPlotView.as_view(), name='smplot'),

    #############################################
    # Search
    ##############################################
    url('^search_frag/$', views_search.SearchFragParamCreateView.as_view(), name='search_frag'),
    url('^search_frag_param/$', views_search.SearchFragParamListView.as_view(), name='search_frag_param'),
    url('^search_frag_results/(?P<spid>\d+)/$', views_search.SearchFragResultListView.as_view(), name='search_frag_results'),
    url('^search_frag_annotations/(?P<sfid>\d+)/$', views_search.SearchFragResultAnnotationListView.as_view(), name='search_frag_annotations'),
    url('^search_mz/$', views_search.SearchMzParamCreateView.as_view(), name='search_mz'),
    url('^search_mono/$', views_search.SearchMonoParamCreateView.as_view(), name='search_mono'),
    url('^search_mono_param/$', views_search.SearchMonoParamListView.as_view(), name='search_mono_param'),
    url('^search_mono_results/(?P<spid>\d+)/$', views_search.SearchMonoResultListView.as_view(), name='search_mono_results'),

    # Autocomplete urls (not currently used)
    # url('mfile_multi_summary/', views.MFileListMultiView.as_view(), name='mfile_multi_summary'),
    url(r'^mfile-autocomplete/$', views_isa.MFileAutocomplete.as_view(), name='mfile-autocomplete'),

    #############################################
    # ISA
    #############################################
    url('^add_run/$', views_isa.RunCreateView.as_view(), name='add_run'),
    url('^upload_mfile/$', views_isa.MFileCreateView.as_view(), name='upload_mfile'),
    url('^upload_mfiles_batch/$', views_isa.UploadMFilesBatch.as_view(), name='upload_mfiles_batch'),
    url('^mfile_summary/$', views_isa.MFileListView.as_view(), name='mfile_summary'),

    url(r'^isa_batch_create/$', views_isa.ISABatchCreate.as_view(), name='isa_batch_create'),

    url(r'^misa/$', views_isa.InvestigationListView.as_view(), name='ilist'),
    # Ontology
    url(r'^create_ontologyterm/$', views_isa.OntologyTermCreateView.as_view(), name='create_ontologyterm'),
    url(r'^update_ontologyterm/$', views_isa.OntologyTermUpdateView.as_view(), name='update_ontologyterm'),
    url(r'^delete_ontologyterm/$', views_isa.OntologyTermDeleteView.as_view(), name='delete_ontologyterm'),
    url(r'^list_ontologyterm/$', views_isa.OntologyTermListView.as_view(), name='list_ontologyterm'),

    # ontology term searching EBI ontology service
    url(r'^search_ontologyterm/$', views_isa.OntologyTermSearchView.as_view(), name='search_ontologyterm'),
    url(r'^search_ontologyterm_result/$', views_isa.OntologyTermSearchResultView.as_view(), name='search_ontologyterm_result'),
    url(r'^add_ontologyterm/(?P<c>\d+)/$', views_isa.AddOntologyTermView.as_view(), name='add_ontologyterm'),

    url(r'^update_ontologyterm/(?P<pk>\d+)/$', views_isa.OntologyTermUpdateView.as_view(), name='update_ontologyterm'),
    url(r'^delete_ontologyterm/(?P<pk>[\w]+)/$', views_isa.OntologyTermDeleteView.as_view(), name='delete_ontologyterm'),
    url(r'^list_ontologyterm/$', views_isa.OntologyTermListView.as_view(), name='list_ontologyterm'),

    url(r'^ontologyterm-autocomplete/$', views_isa.OntologyTermAutocomplete.as_view(), name='ontologyterm-autocomplete'),
    url(r'^ontologyterm-autocompleteTEST/$', autocomplete.Select2QuerySetView.as_view(model=OntologyTerm),name='select2_fk',),

    # Organism
    url(r'^org_create/$', views_isa.OrganismCreateView.as_view(), name='org_create'),
    url(r'^org_list/$', views_isa.OrganismListView.as_view(), name='org_list'),
    url(r'^org_update/(?P<pk>\d+)/$', views_isa.OrganismUpdateView.as_view(), name='org_update'),
    url(r'^org_delete/(?P<pk>[\w]+)/$', views_isa.OrganismDeleteView.as_view(), name='org_delete'),
    url(r'^organism-autocomplete/$', views_isa.OrganismAutocomplete.as_view(), name='organism-autocomplete'),

    # Organism part
    url(r'^orgpart_create/$', views_isa.OrganismPartCreateView.as_view(), name='orgpart_create'),
    url(r'^orgpart_list/$', views_isa.OrganismPartListView.as_view(), name='orgpart_list'),
    url(r'^orgpart_update/(?P<pk>\d+)/$', views_isa.OrganismPartUpdateView.as_view(), name='orgpart_update'),
    url(r'^orgpart_delete/(?P<pk>[\w]+)/$', views_isa.OrganismPartDeleteView.as_view(), name='orgpart_delete'),
    url(r'^organismpart-autocomplete/$', views_isa.OrganismPartAutocomplete.as_view(), name='organismpart-autocomplete'),

    # sample collection protocol
    url(r'^scp_create/$', views_isa.SampleCollectionProtocolCreateView.as_view(), name='scp_create'),
    url(r'^scp_list/$', views_isa.SampleCollectionProtocolListView.as_view(), name='scp_list'),
    url(r'^scp_update/(?P<pk>\d+)/$', views_isa.SampleCollectionProtocolUpdateView.as_view(), name='scp_update'),
    url(r'^scp_delete/(?P<pk>[\w]+)/$', views_isa.SampleCollectionProtocolDeleteView.as_view(), name='scp_delete'),

    # extraction protocol
    url(r'^ep_create/$', views_isa.ExtractionProtocolCreateView.as_view(), name='ep_create'),
    url(r'^ep_list/$', views_isa.ExtractionProtocolListView.as_view(), name='ep_list'),
    url(r'^ep_update/(?P<pk>\d+)/$', views_isa.ExtractionProtocolUpdateView.as_view(), name='ep_update'),
    url(r'^ep_delete/(?P<pk>[\w]+)/$', views_isa.ExtractionProtocolDeleteView.as_view(), name='ep_delete'),

    # extraction type
    url(r'^et_create/$', views_isa.ExtractionTypeCreateView.as_view(), name='et_create'),
    url(r'^et_list/$', views_isa.ExtractionTypeListView.as_view(), name='et_list'),
    url(r'^et_update/(?P<pk>\d+)/$', views_isa.ExtractionTypeUpdateView.as_view(), name='et_update'),
    url(r'^et_delete/(?P<pk>[\w]+)/$', views_isa.ExtractionTypeDeleteView.as_view(), name='et_delete'),
    url(r'^extractiontype-autocomplete/$', views_isa.ExtractionTypeAutocomplete.as_view(),
        name='extractiontype-autocomplete'),

    # chromatography protocol
    url(r'^cp_create/$', views_isa.ChromatographyProtocolCreateView.as_view(), name='cp_create'),
    url(r'^cp_list/$', views_isa.ChromatographyProtocolListView.as_view(), name='cp_list'),
    url(r'^cp_update/(?P<pk>\d+)/$', views_isa.ChromatographyProtocolUpdateView.as_view(), name='cp_update'),
    url(r'^cp_delete/(?P<pk>[\w]+)/$', views_isa.ChromatographyProtocolDeleteView.as_view(), name='cp_delete'),

    # chromatography type
    url(r'^ct_create/$', views_isa.ChromatographyTypeCreateView.as_view(), name='ct_create'),
    url(r'^ct_list/$', views_isa.ChromatographyTypeListView.as_view(), name='ct_list'),
    url(r'^ct_update/(?P<pk>\d+)/$', views_isa.ChromatographyTypeUpdateView.as_view(), name='ct_update'),
    url(r'^ct_delete/(?P<pk>[\w]+)/$', views_isa.ChromatographyTypeDeleteView.as_view(), name='ct_delete'),
    url(r'^chromatographytype-autocomplete/$', views_isa.ChromatographyTypeAutocomplete.as_view(), name='chromatographytype-autocomplete'),

    # spe protocol
    url(r'^spep_create/$', views_isa.SpeProtocolCreateView.as_view(), name='spep_create'),
    url(r'^spep_list/$', views_isa.SpeProtocolListView.as_view(), name='spep_list'),
    url(r'^spep_update/(?P<pk>\d+)/$', views_isa.SpeProtocolUpdateView.as_view(), name='spep_update'),
    url(r'^spep_delete/(?P<pk>[\w]+)/$', views_isa.SpeProtocolDeleteView.as_view(), name='spep_delete'),

    # spe type
    url(r'^spet_create/$', views_isa.SpeTypeCreateView.as_view(), name='spet_create'),
    url(r'^spet_list/$', views_isa.SpeTypeListView.as_view(), name='spet_list'),
    url(r'^spet_update/(?P<pk>\d+)/$', views_isa.SpeTypeUpdateView.as_view(), name='spet_update'),
    url(r'^spet_delete/(?P<pk>[\w]+)/$', views_isa.SpeTypeDeleteView.as_view(), name='spet_delete'),
    url(r'^spetype-autocomplete/$', views_isa.SpeTypeAutocomplete.as_view(), name='spetype-autocomplete'),

    # measurement protocol
    url(r'^mp_create/$', views_isa.MeasurementProtocolCreateView.as_view(), name='mp_create'),
    url(r'^mp_list/$', views_isa.MeasurementProtocolListView.as_view(), name='mp_list'),
    url(r'^mp_update/(?P<pk>\d+)/$', views_isa.MeasurementProtocolUpdateView.as_view(), name='mp_update'),
    url(r'^mp_delete/(?P<pk>[\w]+)/$', views_isa.MeasurementProtocolDeleteView.as_view(), name='mp_delete'),

    # measurement technique
    url(r'^mt_create/$', views_isa.MeasurementTechniqueCreateView.as_view(), name='mt_create'),
    url(r'^mt_list/$', views_isa.MeasurementTechniqueListView.as_view(), name='mt_list'),
    url(r'^mt_update/(?P<pk>\d+)/$', views_isa.MeasurementTechniqueUpdateView.as_view(), name='mt_update'),
    url(r'^mt_delete/(?P<pk>[\w]+)/$', views_isa.MeasurementTechniqueDeleteView.as_view(), name='mt_delete'),
    url(r'^measurementtechnique-autocomplete/$', views_isa.MeasurementTechniqueAutocomplete.as_view(),
        name='measurementtechnique-autocomplete'),

    # data transformation protocol
    url(r'^dp_create/$', views_isa.DataTransformationProtocolCreateView.as_view(), name='dp_create'),
    url(r'^dp_list/$', views_isa.DataTransformationProtocolListView.as_view(), name='dp_list'),
    url(r'^dp_update/(?P<pk>\d+)/$', views_isa.DataTransformationProtocolUpdateView.as_view(), name='dp_update'),
    url(r'^dp_delete/(?P<pk>[\w]+)/$', views_isa.DataTransformationProtocolDeleteView.as_view(), name='dp_delete'),

    # ISA export
    url(r'^export_isa/$', views_isa.ExportISACreateView.as_view(), name='export_isa'),

    # Investigation
    url(r'^icreate/$', views_isa.InvestigationCreateView.as_view(), name='icreate'),
    url(r'^iupdate/(?P<pk>\d+)/$', views_isa.InvestigationUpdateView.as_view(), name='iupdate'),
    #url(r'^idetail/(?P<pk>\d+)/$', views_isa.InvestigationDetailView.as_view(), name='idetail'), # not required
    url(r'^idetail_tables/(?P<pk>\d+)/$', views_isa.InvestigationDetailTablesView.as_view(), name='idetail_tables'),
    url(r'^investigation-autocomplete/$', views_isa.InvestigationAutocomplete.as_view(), name='investigation-autocomplete'),
    url(r'^idelete/(?P<pk>[\w]+)/$', views_isa.InvestigationDeleteView.as_view(), name='idelete'),

    # Study
    url(r'^screate/$', views_isa.StudyCreateView.as_view(), name='screate'),
    url(r'^supdate/(?P<pk>\d+)/$', views_isa.StudyUpdateView.as_view(), name='supdate'),
    url(r'^sdelete/(?P<pk>[\w]+)/$', views_isa.StudyDeleteView.as_view(), name='sdelete'),
    # url(r'^slist/$', views_isa.StudyListView.as_view(), name='slist'), #not required
    url(r'^study-autocomplete/$', views_isa.StudyAutocomplete.as_view(), name='study-autocomplete'),

    # Assay
    url(r'^acreate/$', views_isa.AssayCreateView.as_view(), name='acreate'),
    url(r'^aupdate/(?P<pk>\d+)/$', views_isa.AssayUpdateView.as_view(), name='aupdate'),
    # url(r'^alist/$', views_isa.AssayListView.as_view(), name='alist'),  #not required
    url(r'^assay-autocomplete/$', views_isa.AssayAutocomplete.as_view(), name='assay-autocomplete'),
    url(r'^adelete/(?P<pk>[\w]+)/$', views_isa.AssayDeleteView.as_view(), name='adelete'),

    # Study Sample
    url(r'^ssam_create/$', views_isa.StudySampleCreateView.as_view(), name='ssam_create'),
    url(r'^ssam_update/(?P<pk>\d+)/$', views_isa.StudySampleUpdateView.as_view(), name='ssam_update'),
    url(r'^ssam_list/$', views_isa.StudySampleListView.as_view(), name='ssam_list'),
    url(r'^ssam_delete/(?P<pk>[\w]+)/$', views_isa.StudySampleDeleteView.as_view(), name='ssam_delete'),
    url(r'^ssam_batch_create/$', views_isa.StudySampleBatchCreate.as_view(), name='ssam_batch_create'),
    url(r'^sampletype-autocomplete/$', views_isa.SampleTypeAutocomplete.as_view(), name='sampletype-autocomplete'),


    # Study Factor
    url(r'^sfcreate/$', views_isa.StudyFactorCreateView.as_view(), name='sfcreate'),
    url(r'^sfupdate/(?P<pk>\d+)/$', views_isa.StudyFactorUpdateView.as_view(), name='sfupdate'),
    url(r'^sfdelete/(?P<pk>\d+)/$', views_isa.StudyFactorDeleteView.as_view(), name='sfdelete'),
    url(r'^sflist/$', views_isa.StudyFactorListView.as_view(), name='sflist'),
    url(r'^studyfactor-autocomplete/$', views_isa.StudyFactorAutocomplete.as_view(), name='studyfactor-autocomplete'),


    url(r'^upload_assay_data_files/(?P<assayid>\d+)$', views_isa.UploadAssayDataFilesView.as_view(), name='upload_assay_data_files'),

    url(r'^view_isa_data_files/$', views_isa.ISAFileSummaryView.as_view(), name='view_isa_data_files'),


    url(r'^assayfile_summary/(?P<assayid>\d+)$', views_isa.AssayFileSummaryView.as_view(), name='assayfile_summary'),
    url(r'^assaydetail_summary/(?P<assayid>\d+)$', views_isa.AssayDetailSummaryView.as_view(), name='assaydetail_summary'),


    url(r'^misa_success/$', views_isa.success, name='misa_success'),

    url(r'^polaritytype-autocomplete/$', views_isa.PolarityTypeAutocomplete.as_view(),
        name='polaritytype-autocomplete'),

    #############################################
    # Galaxy ISA upload and workflows
    ##############################################
    url(r'^galaxy_isa_upload_datalib/$', views_galaxy.GalaxyISAupload.as_view(), name='galaxy_isa_upload_datalib'),
    url(r'^isa_workflow_run/(?P<wid>\d+)$', views_galaxy.ISAWorkflowRunView.as_view(), name='isa_workflow_run'),
    url(r'^isa_workflow_summary/', views_galaxy.ISAWorkflowListView.as_view(), name='isa_workflow_summary'),
    url(r'^galaxy_isa_fileselect_upload_datalib', views_galaxy.ISAFileSelectToGalaxyDataLib.as_view(),
        name='galaxy_isa_fileselect_upload_datalib'),
    url(r'^galaxy_isa_fileselect_upload_history', views_galaxy.ISAFileSelectToGalaxyHist.as_view(),
        name='galaxy_isa_fileselect_upload_history'),


    ##############################################
    # Galaxy and REST
    ##############################################
    url(r'^rest/', include(router.urls)),
]
