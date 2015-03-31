from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf.urls.static import static

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic.base import RedirectView

urlpatterns = patterns('',
                       url(r'^$', RedirectView.as_view(url='/dashboard/home', permanent=False), name='home'),
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^dashboard/', include('dashboard.urls')),
                       url(r'^accounts/', include('accounts.urls')),
                       url(r'^importer/', include('importer.urls')),
                       )

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
