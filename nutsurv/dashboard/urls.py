from django.conf.urls import patterns, url

urlpatterns = patterns('',
    # Examples:
    #url(r'^$', 'nutsurv.views.home', name='home'),
    url(r'^$', 'dashboard.views.dashboard', name='index'),
    url(r'^home$', 'dashboard.views.home', name='home'),
    url(r'^mapping_checks$', 'dashboard.views.mapping_checks', name='mapping_checks'),
    url(r'^age_distribution$', 'dashboard.views.age_distribution', name='age_distribution'),   
)
