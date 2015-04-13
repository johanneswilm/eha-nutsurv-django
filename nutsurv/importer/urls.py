from django.conf.urls import patterns, url

urlpatterns = patterns('',
                       url(r'^$', 'importer.views.importer', name='importer'),
                       url(r'^register_formhub_survey$', 'importer.views.register_formhub_survey', name='register_formhub_survey'),
                       url(r'^reset_data$', 'importer.views.reset_data', name='reset_data'),
                       url(r'^import_csvfile$', 'importer.views.import_csvfile', name='import_csvfile'),
                       )
