from django.conf.urls import include, patterns, url

from tastypie.api import Api
from api.resources import JSONDocumentResource

v1_api = Api(api_name='v1')
v1_api.register(JSONDocumentResource())

urlpatterns = patterns('',
                       (r'^api/', include(v1_api.urls)),
                       url(r'^$', 'dashboard.views.dashboard', name='index'),
                       url(r'^home$', 'dashboard.views.home', name='home'),
                       url(r'^mapping_checks$',
                           'dashboard.views.mapping_checks',
                           name='mapping_checks'),
                       url(r'^age_distribution$',
                           'dashboard.views.age_distribution',
                           name='age_distribution'),
                       )
