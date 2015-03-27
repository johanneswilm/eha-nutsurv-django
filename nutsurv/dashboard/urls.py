from django.conf.urls import include, patterns, url

from rest_framework import routers

from tastypie.api import Api

from api.resources import HouseholdSurveyJSONResource

from dashboard.views import TeamsJSONView
from dashboard.views import AggregateSurveyDataJSONView
from dashboard.views import SurveyedClustersPerTeamJSONView
from dashboard.views import PersonnelJSONView
from dashboard.views import ActiveQuestionnaireSpecificationView
from dashboard.views import ClustersPerStateJSONView
from dashboard.views import StatesJSONView
from dashboard.views import StatesWithReserveClustersJSONView
from dashboard.views import ClustersPerTeamJSONView
from dashboard.views import ClustersJSONView
from dashboard.views import AlertViewSet
from dashboard.views import HouseholdSurveyJSONViewset
from dashboard.views import TeamMemberViewset



v1_api = Api(api_name='v1')
v1_api.register(HouseholdSurveyJSONResource())

router = routers.DefaultRouter()
router.register(r'alerts', AlertViewSet)
router.register(r'surveys', HouseholdSurveyJSONViewset)
router.register(r'teammembers', TeamMemberViewset)

urlpatterns = patterns('',
                       url(r'^api/', include(v1_api.urls)),

                       url(r'^', include(router.urls)),
                       url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),

                       url(r'^home$', 'dashboard.views.home', name='home'),

                       url(r'^mapping_checks$',
                           'dashboard.views.mapping_checks',
                           name='mapping_checks'),
                       url(r'^age_distribution$',
                           'dashboard.views.age_distribution',
                           name='age_distribution'),
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
                       url(r'^time_of_data_collection$',
                        'dashboard.views.time_of_data_collection',
                        name='time_of_data_collection'),
                       url(r'^teamsjsonview/$', TeamsJSONView.as_view(),
                           name='teams-json-view'),
                       url(r'^personneljsonview/$', PersonnelJSONView.as_view(),
                           name='personnel-json-view'),
                       url(r'^aggregatesurveydatajsonview/$',
                           AggregateSurveyDataJSONView.as_view(),
                           name='aggregate-survey-data-json-view'),
                       url(r'^surveyedclustersperteamjsonview/$',
                           SurveyedClustersPerTeamJSONView.as_view(),
                           name='surveyed-clusters-per-team-json-view'),
                       url(r'^activequestionnairespecificationview/$',
                           ActiveQuestionnaireSpecificationView.as_view(),
                           name='active-questionnaire-specification-view'),
                       url(r'^clustersperstatejsonview/$',
                           ClustersPerStateJSONView.as_view(),
                           name='clusters-per-state-json-view'),
                       url(r'^statesjsonview/$',
                           StatesJSONView.as_view(),
                           name='states-json-view'),
                       url(r'^stateswithreserveclustersjsonview/$',
                           StatesWithReserveClustersJSONView.as_view(),
                           name='states-with-reserve-clusters-json-view'),
                       url(r'^clustersperteamjsonview/$',
                           ClustersPerTeamJSONView.as_view(),
                           name='clusters-per-team-json-view'),
                       url(r'^clustersjsonview/$',
                           ClustersJSONView.as_view(),
                           name='clusters-json-view'),
                       )
