"""dma_site URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls import url, include



# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.

urlpatterns = [
    url(r'^', include('gfiles.urls')),
    url(r'^mogi/', include('mogi.urls')),
    url(r'^misa/', include('misa.urls')),
    url(r'^mbrowse/', include('mbrowse.urls')),
    url(r'^galaxy/', include('galaxy.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^django-sb-admin/', include('django_sb_admin.urls'))

]
