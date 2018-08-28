from django.conf.urls import url,include

from mogi import views

from rest_framework import routers
router = routers.DefaultRouter()
router.register(r'incoming_galaxy_data', views.IncomingGalaxyDataViewSet)

urlpatterns = [
    #############################################
    # General
    ##############################################

    url(r'^$', views.index, name='index'),
    url(r'^submitted/$', views.success, name='submitted'),
    url(r'^about/$', views.about, name='about'),

    #############################################
    # Galaxy ISA upload and workflows
    ##############################################
    url(r'^galaxy_isa_upload_datalib/$', views.GalaxyISAupload.as_view(), name='galaxy_isa_upload_datalib'),
    url(r'^isa_workflow_run/(?P<wid>\d+)$', views.ISAWorkflowRunView.as_view(), name='isa_workflow_run'),
    url(r'^isa_workflow_summary/', views.ISAWorkflowListView.as_view(), name='isa_workflow_summary'),
    url(r'^galaxy_isa_fileselect_upload_datalib', views.ISAFileSelectToGalaxyDataLib.as_view(), name='galaxy_isa_fileselect_upload_datalib'),
    url(r'^galaxy_isa_fileselect_upload_history', views.ISAFileSelectToGalaxyHist.as_view(), name='galaxy_isa_fileselect_upload_history'),

    #############################################
    # Galaxy ISA history data upload to django-metab
    ##############################################
    url(r'^history_mogi/$', views.HistoryMogiListView.as_view(), name='history_mogi'),
    url(r'^history_mogi_data/(?P<pk>\d+)/$', views.HistoryDataMogiListView.as_view(), name='history_mogi_data'),
    url(r'^history_mogi_data_save/(?P<history_internal_id>\d+)/(?P<galaxy_id>\w+)/$', views.HistoryDataMogiCreateView.as_view(), name='history_mogi_data_save'),

    #############################################
    # Peak and annotation summary
    ##############################################
    url(r'^cpeakgroupmeta_summary_mogi/$', views.CPeakGroupMetaListMogiView.as_view(), name='cpeakgroupmeta_summary_mogi'),
    url(r'^canns_all_mogi/$', views.CAnnotationListAllMogiView.as_view(), name='canns_all_mogi'),
    url(r'^canns_download_mogi/$', views.CAnnotationDownloadMogiView.as_view(), name='canns_download_mogi'),

    ##############################################
    # REST
    ##############################################
    url(r'^rest/', include(router.urls)),
    url(r'^incoming_galaxy_data_list/$', views.IncomingGalaxyDataListView.as_view(), name='incoming_galaxy_data_list'),
    url(r'^history_mogi_data_from_rest_save/(?P<galaxy_name>\w+)/(?P<galaxy_data_id>\w+)/(?P<galaxy_history_id>\w+)/$',
        views.HistoryDataMogiFromRestCreateView.as_view(), name='history_mogi_data_from_rest_save'),
    url(r'^save_lcms_from_from_rest/(?P<galaxy_name>[-\w]+)/(?P<galaxy_data_id>\w+)/(?P<galaxy_history_id>\w+)/(?P<investigation_name>[-\w]+)/$',
        views.SaveLcmsFromFromRest.as_view(), name='save_lcms_from_from_rest'),
]