from django.conf.urls import patterns, url

urlpatterns = patterns('',
                       url(r'^$', 'importer.views.import_csvfile', name='import_csvfile'),
                       )
