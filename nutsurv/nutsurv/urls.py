from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    #url(r'^$', 'nutsurv.views.home', name='home'),
    url(r'^$', 'dashboard.views.dashboard', name='home'),
    url(r'^dashboard/', include('dashboard.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
