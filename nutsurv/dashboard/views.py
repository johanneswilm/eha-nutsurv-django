import json
import math
import logging

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
from rest_framework.decorators import list_route
from rest_framework.response import Response

from importer import anthrocomputation
from django.utils.decorators import method_decorator
from django_dont_vary_on.decorators import dont_vary_on
from collections import Counter


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
    pagination_class = pagination.PageNumberPagination
    queryset = HouseholdMember.objects.all()
    serializer_class = HouseholdMemberSerializer

    @list_route(methods=['get'])
    def age_distribution(self, request, format):

        c = HouseholdMember.children
        h = HouseholdMember.objects

        if request.GET.get('team_lead'):
            team_lead = TeamMember.objects.get(pk=int(request.GET['team_lead']))
            c = c.by_teamlead(team_lead)
            h = h.by_teamlead(team_lead)

        if request.GET.get('stratum'):
            stratum = request.GET['stratum']
            c = c.by_first_admin_level(stratum)
            h = h.by_first_admin_level(stratum)

        months_list = [v.get('age_months', 0) for v in HouseholdMember.children.all().values_list('extra_questions', flat=True)]
        children_age_distrobutions = list({'count': v, 'age_in_months': k} for k, v in Counter(months_list).items())
        return Response({
            'age_distribution': {
                'children': children_age_distrobutions,
                'household_member': h.age_distribution_in_years(),
            }
        })


class HouseholdSurveyJSONViewset(viewsets.ModelViewSet):
    queryset = HouseholdSurveyJSON.objects.prefetch_related('members').all()
    serializer_class = HouseholdSurveyJSONSerializer

    def list(request, *args, **kwargs):
        return Response([])

    def retrieve(request, *args, **kwargs):
        return Response([])

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

    h = HouseholdMember.objects

    if request.GET.get('team_lead'):
        team_lead = TeamMember.objects.get(pk=int(request.GET['team_lead']))
        h = h.by_teamlead(team_lead)

    if request.GET.get('stratum'):
        stratum = request.GET['stratum']
        h = h.by_first_admin_level(stratum)

    return render(request, 'dashboard/missing_data.html', {
        'existing_data': HouseholdMember.missing_data(h),
    })


@login_required
def child_anthropometry(request):
    response = {}
    return render(request, 'dashboard/child_anthropometry.html', response)


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


class AggregateSurveyDataJSONView(LoginRequiredView):

    @method_decorator(dont_vary_on('Cookie'))
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
                        'surveyType': 'woman',
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
        docs = HouseholdSurveyJSON.objects.all()
        survey_data = []
        for doc in docs:
            survey_data.append(self._clean_json(doc))
        return JsonResponse({'survey_data': survey_data})

    @classmethod
    def _clean_json(cls, doc):
        """Clean JSON document given containing data from a
        single survey to decrease the amount of data sent to the
        client.
        """

        output = {}

        # map the top-level attributes

        if hasattr(doc, 'location') and doc.location:
            output['location'] = list(doc.location)
        else:
            output['location'] = None

        output['cluster'] = doc.cluster
        output['startTime'] = str(doc.start_time)
        output['endTime'] = str(doc.end_time)
        output['team'] = doc.team_lead.id

        output['members'] = []
        # map household members

        for i_member in doc.members.all().with_age():

            o_member = {}
            o_member['gender'] = i_member.gender

            o_member['birthdate'] = i_member.birthdate

            o_member['survey'] = {
                'muac': i_member.muac,
                'height': i_member.height,
                'weight': i_member.weight,
                'recumbent': i_member.height_type == 'recumbent',
                'zscores': {},
            }

            if i_member.age_in_months:

                zscores = anthrocomputation.keys_who_to_unicef(anthrocomputation.getAnthroResult(
                    ageInDays=i_member.age_in_months * anthrocomputation.DAYSINMONTH,
                    sex=i_member.gender,
                    weight=i_member.weight,
                    height=i_member.height,
                    isRecumbent=i_member.height_type == 'recumbent',
                    hasOedema=i_member.edema,
                    hc=None,  # TODO use actual data ?
                    muac=i_member.muac,
                    tsf=None,  # TODO use actual data ?
                    ssf=None,  # TODO use actual data ?
                ))

                for zscore_name in ('HAZ', 'WAZ', 'WHZ',):
                    if not math.isnan(zscores[zscore_name]):
                        o_member["survey"]["zscores"][zscore_name] = zscores[zscore_name]
                    else:
                        logging.warn("'%s' calculation returned NaN, not calculating this", zscore_name)

            if HouseholdMember.women.all().filter(id__in=[i_member.id]).count():
                o_member['surveyType'] = 'woman'
            elif HouseholdMember.children.all().filter(id__in=[i_member.id]).count():
                o_member['surveyType'] = 'child'

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
