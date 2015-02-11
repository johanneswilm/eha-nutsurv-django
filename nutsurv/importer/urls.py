from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^$', 'importer.views.importer', name='importer'),
    url(r'^register_formhub_survey$', 'importer.views.register_formhub_survey', name='register_formhub_survey'),
    url(r'^reset_fake_teams$', 'importer.views.reset_fake_teams', name='reset_fake_teams'),
)
