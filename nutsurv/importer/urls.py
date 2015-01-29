from django.conf.urls import patterns, url

urlpatterns = patterns('',
                       url(r'^$', 'importer.views.importer', name='importer'),
                       )
