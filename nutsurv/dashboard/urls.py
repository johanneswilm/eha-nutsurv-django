from django.conf.urls import include, patterns, url
from tastypie.api import Api

from api.resources import JSONDocumentResource

from dashboard.views import TeamsJSONView
from dashboard.views import AggregateSurveyDataJSONView
from dashboard.views import ClustersPerTeamJSONView
from dashboard.views import AlertsJSONView

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
                       url(r'^survey_completed$',
                           'dashboard.views.survey_completed',
                           name='survey_completed'),
                       url(r'^survey_completed_teams$',
                           'dashboard.views.survey_completed_teams',
                           name='survey_completed_teams'),
                       url(r'^survey_completed_states$',
                           'dashboard.views.survey_completed_states',
                           name='survey_completed_states'),
                       url(r'^missing_data$',
                           'dashboard.views.missing_data',
                           name='missing_data'),
                       url(r'^data_quality$',
                           'dashboard.views.data_quality',
                           name='data_quality'),
                       url(r'^personnel$',
                        'dashboard.views.personnel',
                        name='personnel'),
                       url(r'^teamsjsonview/$', TeamsJSONView.as_view(),
                           name='teams-json-view'),
                       url(r'^aggregatesurveydatajsonview/$',
                           AggregateSurveyDataJSONView.as_view(),
                           name='aggregate-survey-data-json-view'),
                       url(r'^clustersperteamjsonview/$',
                           ClustersPerTeamJSONView.as_view(),
                           name='clusters-per-team-json-view'),
                       url(r'^alertsjsonview/$',
                           AlertsJSONView.as_view(),
                           name='alerts-json-view'),
                       )
