from django.conf.urls import patterns, url

urlpatterns = patterns('',
    # Examples:
    #url(r'^$', 'nutsurv.views.home', name='home'),
    url(r'^$', 'dashboard.views.dashboard', name='index'),
    url(r'^home$', 'dashboard.views.home', name='home'),
)
