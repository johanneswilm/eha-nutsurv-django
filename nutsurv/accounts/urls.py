from django.conf.urls import patterns, url

urlpatterns = patterns('',
                       url(r'^login/$', 'accounts.views.user_login', name='login'),
                       url(r'^logout/$', 'accounts.views.user_logout', name='logout'),
                       )
