from django.conf.urls import patterns, url

urlpatterns = patterns('',
                       url(r'^$', 'importer.views.importer', name='importer'),
                       url(r'^import_csvfile$', 'importer.views.import_csvfile', name='import_csvfile'),
                       )
