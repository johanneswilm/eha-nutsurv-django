import json

import datetime
import dateutil.parser
import dateutil.relativedelta

from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.generic import View
from django.conf import settings

from .serializers import (AlertSerializer, HouseholdSurveyJSONSerializer,
                          TeamMemberSerializer, HouseholdMemberSerializer)

from .models import Alert
from .models import HouseholdSurveyJSON
from .models import Clusters
from .models import QuestionnaireSpecification
from .models import ClustersPerFirstAdminLevel
from .models import FirstAdminLevels
from .models import FirstAdminLevelsReserveClusters
from .models import TeamMember
from .models import HouseholdMember

from rest_framework import viewsets, pagination


class HardLimitPagination(pagination.PageNumberPagination):
    page_size = 1000
    max_page_size = 1000


class TeamMemberViewset(viewsets.ModelViewSet):
    queryset = TeamMember.objects.all()
    permission_classes = ()
    serializer_class = TeamMemberSerializer
    template_name = 'dashboard/teammember.html'
    lookup_field = 'pk'


class HouseholdMemberViewset(viewsets.ModelViewSet):
    queryset = HouseholdMember.objects.all()
    serializer_class = HouseholdMemberSerializer


class HouseholdSurveyJSONViewset(viewsets.ModelViewSet):
    queryset = HouseholdSurveyJSON.objects.prefetch_related('members').all()
    serializer_class = HouseholdSurveyJSONSerializer
    permission_classes = ()  # Allow any


@login_required
def home(request):
    response = {}
    return render(request, 'dashboard/home.html', response)


@login_required
def fieldwork(request):
    response = {}
    return render(request, 'dashboard/fieldwork.html', response)


@login_required
def age_distribution(request):
    response = {}
    return render(request, 'dashboard/age_distribution.html', response)


@login_required
def survey_completed_teams(request):
    response = {}
    return render(request, 'dashboard/survey_completed_teams.html', response)


@login_required
def survey_completed_strata(request):
    response = {}
    return render(request, 'dashboard/survey_completed_strata.html', response)


@login_required
def missing_data(request):
    return render(request, 'dashboard/missing_data.html', {
        'existing_data': HouseholdMember.missing_data(),
    })


@login_required
def data_quality(request):
    response = {}
    return render(request, 'dashboard/data_quality.html', response)


@login_required
def personnel(request):
    response = {}
    return render(request, 'dashboard/personnel.html', response)


@login_required
def time_of_data_collection(request):
    response = {}
    return render(request, 'dashboard/time_of_data_collection.html', response)


class LoginRequiredView(View):

    @classmethod
    def as_view(cls, **kwargs):
        view = super(LoginRequiredView, cls).as_view(**kwargs)
        return login_required(view)


class TeamsJSONView(LoginRequiredView):

    def get(self, request, *args, **kwargs):
        """Generates an HTTP response with a JSON document containing
        information about all teams in the format requested by Johannes and
        shown below:
        {
            "teams": {
                "1": "John, Daisy & Flint",
                "2": "Patrick, Abigail & Stephanie",
                "3": "Rose, Hannah & Chris"
            }
        }
        """
        teams = {'teams': self._find_all_teams()}
        return HttpResponse(json.dumps(teams), content_type='application/json')

    @staticmethod
    def _find_all_teams():
        """Computes and returns a dictionary containing team data in the format
        requested by Johannes and shown in the following example:
        {
            '1': 'John, Daisy & Flint',
            '2': 'Patrick, Abigail & Stephanie',
            '3': 'Rose, Hannah & Chris'
        }
        """
        docs = HouseholdSurveyJSON.objects.all()
        teams_dict = {}
        for doc in docs:
            team = doc.json['team']
            team_id = team['teamID']
            if team_id in teams_dict:
                continue
            members = team['members']
            member_names = [
                u'%s %s' % (m['firstName'], m['lastName']) for m in members
            ]
            teams_dict[team_id] = u'%s, %s & %s' % tuple(member_names)
        return teams_dict


class AggregateSurveyDataJSONView(LoginRequiredView):

    def get(self, request, *args, **kwargs):
        """Generates an HTTP response with a JSON document containing
        information from all surveys:
        {
            "survey_data": dictionary_containing_survey_data
        }
        The data format being described through the following example:
        {
            '1': {
                'location': [6.9249100685,
                             8.6650104523
                ],
                'cluster': 657,
                'startTime': '2014-10-18T19:56:23',
                'endTime': '2014-10-18T20:43:23',
                'team': 1,
                'members': [
                    {
                        'gender': 'M',
                        'age': 40
                    },
                    {
                        'gender': 'M',
                        'age': 4,
                        'surveyType': 'child',
                        'survey': {
                            'weight': 45.0,
                            'heightType': 'Child Standing (height)',
                            'edema': 'N',
                            'birthDate': '2011-01-18',
                            'height': 35.2,
                            'diarrhoea': 'N',
                            'zscores': {
                                'WAZ': 3.1,
                                'HAZ': -1.7,
                                'WHZ': -1.3
                            }
                        }

                    },
                    {
                        'gender': 'F',
                        'age': 25,
                        'surveyType': 'women',
                        'survey': {
                            'breastfeeding': 'Y',
                            'muac': 25.3,
                            'height': 165.9,
                            'weight': 56.0,
                            'pregnant': 'N',
                            'ante-natal_care': 'Y',
                            'ever_pregnant': 'Y'
                        }
                    },
                    ...
                ],
            },
        }

        """
        docs = HouseholdSurveyJSON.objects.all().only('json')
        survey_data = []
        for doc in docs:
            survey_data.append(self._clean_json(doc.json))
        return JsonResponse({'survey_data': survey_data})

    @classmethod
    def _clean_json(cls, i_json):
        """Clean JSON document given as i_json and containing data from a
        single survey to decrease the amount of data sent to the
        client.
        """
        output = {}

        # map the top-level attributes
        output['location'] = i_json['location']
        output['cluster'] = i_json['cluster']
        output['startTime'] = i_json['startTime']
        output['endTime'] = i_json['endTime']
        output['team'] = i_json['team']['teamID']

        output['members'] = []
        # map household members
        for i_member in i_json['members']:
            o_member = {}
            o_member['gender'] = i_member['gender']
            o_member['age'] = i_member['age']
            if 'surveyType' in i_member:
                o_member['surveyType'] = i_member['surveyType']
                o_member['survey'] = i_member['survey']
            output['members'].append(o_member)
        return output


class ActiveQuestionnaireSpecificationView(View):

    def get(self, request, *args, **kwargs):
        """Generates an HTTP response with a text document containing the
        current active questionnaire specification (or an empty text file if
        no active questionnaire specification has been found).
        """
        if request.encoding is not None:
            encoding = request.encoding
        else:
            encoding = settings.DEFAULT_CHARSET
        active_qs = self._get_active_questionnaire_specification()
        if isinstance(active_qs, QuestionnaireSpecification):
            text = active_qs.specification
            name = active_qs.name_or_id + '.txt'
            response = HttpResponse(
                text, content_type='text/plain; charset={}'.format(encoding)
            )
            response['Content-Disposition'] = \
                'attachment; filename="{}"'.format(name)
            return response
        else:
            return HttpResponse(content_type='text/plain')

    @staticmethod
    def _get_active_questionnaire_specification():
        return QuestionnaireSpecification.get_active()


class ClustersPerFirstAdminLevelJSONView(View):

    def get(self, request, *args, **kwargs):
        """Generates an HTTP response with a JSON document containing
        information about clusters per first admin level in the format requested by
        Johannes and shown below:
            {
                "first_admin_levels": {
                    "Kano": {
                        "standard": 5,
                        "reserve": 3
                        },
                    "Lagos": {
                        "standard": 7,
                        "reserve": 3
                        },
                    ...
            }
        """
        doc = ClustersPerFirstAdminLevel.get_active()
        if doc:
            data = doc.json
        else:
            data = {}
        return HttpResponse(json.dumps({'first_admin_levels': data}),
                            content_type='application/json')


class FirstAdminLevelJSONView(View):

    def get(self, request, *args, **kwargs):
        """Generates an HTTP response with a JSON document containing
        information about first admin levels in the format requested by Johannes
        and shown below:
            {
                "first_admin_levels": ["Kano", "Lagos", "Kaduna",
                    "Katsina", "Oyo", "Rivers",
                    "Bauchi", "Jigawa", "Benue",
                    "Anambra", "Borno", "Delta",
                    "Imo", "Niger", "Akwa Ibom",
                    "Ogun", "Sokoto", "Ondo",
                    "Osun", "Kogi", "Zamfara",
                    "Enugu", "Kebbi", "Edo",
                    "Plateau", "Adamawa",
                    "Cross River", "Abia",
                    "Ekiti", "Kwara", "Gombe",
                    "Yobe", "Taraba", "Ebonyi",
                    "Nasarawa", "Bayelsa",
                    "Abuja Federal Capital Territory"
                ]
            }

        """
        doc = FirstAdminLevels.get_active()
        if doc:
            data = doc.json
        else:
            data = []
        return HttpResponse(json.dumps({'first_admin_levels': data}),
                            content_type='application/json')


class FirstAdminLevelsReserveClustersJSONView(View):

    def get(self, request, *args, **kwargs):
        """Generates an HTTP response with a JSON document containing
        information about first admin levels with reserved clusters in the format requested
        by Johannes and shown below:
        {
            "first_admin_levels": [
                    "Kano",
                    "Gombe",
                    "Yobe",
                    "Abuja Federal Capital Territory"
            ]
        }
        """
        doc = FirstAdminLevelsReserveClusters.get_active()
        if doc:
            data = doc.json
        else:
            data = []
        return HttpResponse(json.dumps({'first_admin_levels': data}),
                            content_type='application/json')


class ClustersJSONView(View):

    def get(self, request, *args, **kwargs):
        """Generates an HTTP response with a JSON document containing
        information about clusters in the format requested by Johannes and
        shown below:
        {
            "clusters": {
                "723": {
                    "cluster_name": "Share",
                    "second_admin_level_name": "Ifelodun",
                    "first_admin_level_name": "Kwara"
                },
                "318": {
                    "cluster_name": "Emadadja",
                    "second_admin_level_name": "Udu",
                    "first_admin_level_name": "Delta"
                }
                ...

            }
        }
        """
        doc = Clusters.get_most_recently_modified()
        if doc:
            data = {'clusters': doc.json}
        else:
            data = {'clusters': {}}
        return HttpResponse(json.dumps(data), content_type='application/json')


class AlertViewSet(viewsets.ModelViewSet):

    """
    API endpoint that allows Alerts to be viewed.
    """

    template_name = 'dashboard/alert.html'

    queryset = Alert.objects.filter(
        archived=False,
        completed=False,
    ).order_by('-created')

    serializer_class = AlertSerializer
    pagination_class = HardLimitPagination
