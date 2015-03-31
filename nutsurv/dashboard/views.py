import json

import datetime
import dateutil.parser
import dateutil.relativedelta

from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.generic import View
from django.conf import settings
from django.contrib.auth.models import User


from rest_framework import viewsets
from .serializers import (AlertSerializer, HouseholdSurveyJSONSerializer,
                          UserSerializer, TeamMemberSerializer)

from models import Alert
from models import HouseholdSurveyJSON
from models import Clusters
from models import LGA
from models import QuestionnaireSpecification
from models import ClustersPerState
from models import States
from models import StatesWithReserveClusters
from models import ClustersPerTeam
from models import TeamMember

from rest_framework import viewsets


class TeamMemberViewset(viewsets.ModelViewSet):
    queryset = TeamMember.objects.all()
    serializer_class = TeamMemberSerializer
    lookup_field = 'member_id'
    template_name = 'dashboard/teammember.html'


class HouseholdSurveyJSONViewset(viewsets.ModelViewSet):
    queryset = HouseholdSurveyJSON.objects.all()
    serializer_class = HouseholdSurveyJSONSerializer


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
def survey_completed_states(request):
    response = {}
    return render(request, 'dashboard/survey_completed_states.html', response)


@login_required
def missing_data(request):
    response = {}
    return render(request, 'dashboard/missing_data.html', response)


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


class PersonnelJSONView(LoginRequiredView):
    def get(self, request, *args, **kwargs):
        """Generates an HTTP response with a JSON document containing
        information about personnel in the format requested by Johannes and
        exemplified below:
        {
            "personnel": {
                "1": {
                    "name": "John Blacksmith",
                    "team": 1,
                    "birthDate": "1978-04-03",
                    "gender": "M",
                    "phone": "072993848",
                    "email": "john.blacksmith@unicef.org",
                    "position": "Team leader"
                },
                "2": {
                    "name": "Daisy Pato",
                    "team": 1,
                    "age": "32",
                    "gender": "F",
                    "phone": "079364573",
                    "email": "daisy.pato@unicef.org",
                    "position": "Anthropometrist"
                },
            },
        }
        """
        output = {'personnel': self._find_all_personnel_data()}
        return HttpResponse(json.dumps(output), content_type='application/json')

    @staticmethod
    def _compute_age(team_creation_date_string, person, dob_index):
        """This method computes the age of a person at the time when the team
        data was entered into the mobile application or returns None if there is
        not enough data to do that.
        """
        # Try to get the creation date of the team data object to use it later
        # for the member age computations.
        try:
            creation_date = dateutil.parser.parse(team_creation_date_string)
        except TypeError:
            # It is impossible to compute the age at the time without knowing
            # when it was.
            return None
        else:
            # if it worked, get rid of the TZ information and time
            creation_date = creation_date.date()

        try:
            dob = dateutil.parser.parse(person[dob_index])
        except TypeError:
            # It is impossible to compute the age at the time without knowing
            # the person's date of birth.
            return None
        else:
            # if it worked, get rid of the TZ info and time
            dob = dob.date()

        if isinstance(dob, datetime.date) and \
                isinstance(creation_date, datetime.date):
            delta = dateutil.relativedelta.relativedelta(
                creation_date, dob
            )
            # return the computed age in years
            return delta.years
        else:
            return None  # something must have gone wrong

    @classmethod
    def _find_all_personnel_data(cls):
        """Computes and returns a dictionary containing personnel data in the
        format requested by Johannes and shown in the following example:
        {
                "1": {
                    "name": "John Blacksmith",
                    "team": 1,
                    "birthDate": "1978-04-03",
                    "gender": "M",
                    "phone": "072993848",
                    "email": "john.blacksmith@unicef.org",
                    "position": "Team Leader"
                },
                "2": {
                    "name": "Daisy Pato",
                    "team": 1,
                    "birthDate": "1982-06-23",
                    "gender": "F",
                    "phone": "079364573",
                    "email": "daisy.pato@unicef.org",
                    "position": "Anthropometrist"
                },
        }

        If "age" not present in the original data but a valid "birthDate" and
        "created" (the former for a member, the latter for a team record) found,
        this function tries to compute "age" for such members and include it in
        the output.
        """
        docs = HouseholdSurveyJSON.objects.all()
        output = {}
        # Prepare the keys consumed by the dashboard JS code.
        dashboard_keys = (
            'name',
            'team',
            'age',
            'birthDate',
            'gender',
            'phone',
            'email',
            'position'
        )
        # Prepare the equivalent keys used by the mobile app in the structure
        # which stores the member data (keep the order).
        full_name_index = 0
        team_id_index = 1
        age_index = 2
        dob_index = 3
        mobile_keys = (
            'full_name',  # not present in the mobile app, computed
            'team_id',  # not present in the structure, stored one level higher
            'age',
            'birthDate',
            'gender',
            'mobile',
            'email',
            'designation'
        )
        distinct_individuals = set()  # used to check for duplicates
        teams_processed = set()
        i = 1  # used to number all personnel entries starting from one
        for doc in docs:
            team = doc.json['team']
            team_id = team['teamID']
            if team_id in teams_processed:
                continue
            members = team['members']
            for m in members:
                # Compute the full name and add it to the temporary member
                # structure using the correct (temporary) key defined earlier.
                m[mobile_keys[full_name_index]] = ' '.join(
                    (m['firstName'] or '[unknown forename]',
                     m['lastName']) or '[unknown surname]'
                )
                m[mobile_keys[team_id_index]] = int(team_id)
                person = map(m.get, mobile_keys)
                if tuple(person) in distinct_individuals:
                    # Ignore if this combination of member attributes has
                    # already been added.
                    continue
                else:
                    # A new distinct combination of member attributes has been
                    # detected.  Store it for further comparisons.
                    distinct_individuals.add(tuple(person))

                    # Try to compute the person's age (in years) if missing.
                    age = person[age_index]
                    dob = person[dob_index]
                    if not age and dob:
                        age = cls._compute_age(
                            team['created'],
                            person,
                            dob_index
                        )
                        if age is not None:
                            person[age_index] = age

                    # Generate a dictionary for this (apparently new) member and
                    # add it to the output dictionary using the current value
                    # of i as the key.
                    output[str(i)] = dict(zip(dashboard_keys, person))
                    # Increment the number of the distinct members found so far.
                    i += 1
            teams_processed.add(team_id)
        return output


class SurveyedClustersPerTeamJSONView(LoginRequiredView):
    def get(self, request, *args, **kwargs):
        """Generates an HTTP response with a JSON document containing
        information about clusters per team in the format requested by Johannes
        and shown in the example below:
        {
            "teams": {
                "1": 5,
                "2": 15,
                "3": 17
            }
        }
        WARNING: This is currently not needed to fulfil the client's
        requirements.
        """
        clusters_per_team = {'teams': self._compute_clusters_per_team()}
        return HttpResponse(json.dumps(clusters_per_team),
                            content_type='application/json')

    @staticmethod
    def _compute_clusters_per_team():
        """Computes and returns a dictionary containing information about
        distinct clusters per team in the format requested by Johannes and
        shown in the example below:
        {
            "teams": {
                "1": 5,
                "2": 15,
                "3": 17
            }
        }
        """
        # get all JSON documents
        docs = HouseholdSurveyJSON.objects.all()
        clusters_per_team_dict = {}
        # parse all documents and gather the data
        for doc in docs:
            team_id = doc.json['team']['teamID']
            cluster = doc.json['cluster']
            if team_id not in clusters_per_team_dict:
                clusters_per_team_dict[team_id] = set()
            clusters_per_team_dict[team_id].add(cluster)
        # count distinct clusters for each team
        for team_id in clusters_per_team_dict:
            clusters = len(clusters_per_team_dict[team_id])
            clusters_per_team_dict[team_id] = clusters
        return clusters_per_team_dict


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


class ClustersPerStateJSONView(View):
    def get(self, request, *args, **kwargs):
        """Generates an HTTP response with a JSON document containing
        information about clusters per state in the format requested by
        Johannes and shown below:
            {
                "states": {
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
        doc = ClustersPerState.get_active()
        if doc:
            data = doc.json
        else:
            data = {}
        return HttpResponse(json.dumps({'states': data}),
                            content_type='application/json')


class StatesJSONView(View):
    def get(self, request, *args, **kwargs):
        """Generates an HTTP response with a JSON document containing
        information about states in the format requested by Johannes
        and shown below:
            {
                "states": ["Kano", "Lagos", "Kaduna",
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
        doc = States.get_active()
        if doc:
            data = doc.json
        else:
            data = []
        return HttpResponse(json.dumps({'states': data}),
                            content_type='application/json')


class StatesWithReserveClustersJSONView(View):
    def get(self, request, *args, **kwargs):
        """Generates an HTTP response with a JSON document containing
        information about states with reserved clusters in the format requested
        by Johannes and shown below:
        {
            "states": [
                    "Kano",
                    "Gombe",
                    "Yobe",
                    "Abuja Federal Capital Territory"
            ]
        }
        """
        doc = StatesWithReserveClusters.get_active()
        if doc:
            data = doc.json
        else:
            data = []
        return HttpResponse(json.dumps({'states': data}),
                            content_type='application/json')


class ClustersPerTeamJSONView(View):
    def get(self, request, *args, **kwargs):
        """Generates an HTTP response with a JSON document containing
        information about the planned number of clusters per team in the format
        requested by Johannes and shown below:
        {
            "teams": {
                "1": 5,
                "2": 15,
                "3": 17
            }
        }
        """
        doc = ClustersPerTeam.get_active()
        if doc:
            data = doc.json
        else:
            data = {}
        return HttpResponse(json.dumps({'teams': data}),
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
                    "lga_name": "Ifelodun",
                    "state_name": "Kwara"
                },
                "318": {
                    "cluster_name": "Emadadja",
                    "lga_name": "Udu",
                    "state_name": "Delta"
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
