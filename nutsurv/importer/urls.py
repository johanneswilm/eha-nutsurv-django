from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^$', 'importer.views.importer', name='importer'),
    url(r'^register_formhub_data$', 'importer.views.register_formhub_data', name='register_formhub_data'),
)
