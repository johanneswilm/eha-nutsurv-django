from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf.urls.static import static


urlpatterns = patterns('',
                       url(r'^$', 'dashboard.views.dashboard', name='home'),
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^dashboard/', include('dashboard.urls')),
                       url(r'^accounts/', include('accounts.urls')),
                       url(r'^importer/', include('importer.urls')),
                       )

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)




