from django.views.generic.edit import CreateView
from django.contrib.auth.forms import UserCreationForm
from django.conf.urls import url
from django.urls import reverse
from django.contrib.auth import views as auth_views
import views

urlpatterns = [
    #############################################
    # General
    ##############################################
    url(r'^login/$', auth_views.login, {'template_name': 'mogi/login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/'}, name='logout'),
    url(r'^register/$', CreateView.as_view(
        template_name='mogi/register.html',
        form_class=UserCreationForm,
        success_url='/'
    ), name='register'),
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
    url(r'^canns_all_mogi/$', views.CPeakGroupMetaListMogiView.as_view(), name='canns_all_mogi'),

]