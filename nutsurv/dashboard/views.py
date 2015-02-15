import json

import datetime
import dateutil.parser
import dateutil.relativedelta

from django.shortcuts import render, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.generic import View
from django.conf import settings

from models import Alert
from models import HouseholdSurveyJSON
from models import ClustersJSON
from models import LGA
from models import QuestionnaireSpecification
from models import ClustersPerState
from models import States
from models import StatesWithReserveClusters
from models import ClustersPerTeam


@login_required
def dashboard(request):
    response = {}
    return render(request, 'dashboard/index.html', response)


@login_required
def home(request):
    response = {}
    return render(request, 'dashboard/home.html', response)


@login_required
def mapping_checks(request):
    response = {}
    return render(request, 'dashboard/mapping_checks.html', response)


@login_required
def age_distribution(request):
    response = {}
    return render(request, 'dashboard/age_distribution.html', response)


@login_required
def survey_completed(request):
    response = {}
    return render(request, 'dashboard/survey_completed.html', response)


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
        information from all surveys in the format requested by Johannes:
        {
            "survey_data": dictionary_containing_survey_data
        }
        (the data format of the dictionary_containing_survey_data is described
         in _find_all_surveys()).
        """
        surveys = {'survey_data': self._find_all_surveys()}
        return HttpResponse(json.dumps(surveys),
                            content_type='application/json')

    @staticmethod
    def _correct_area(cluster_id, location):
        # get cluster data
        cluster = ClustersJSON.get_cluster_from_most_recently_modified(
            cluster_id)
        # if cluster data not found, assume location incorrect
        if cluster is None:
            return False
        # if cluster data found, get state and LGA
        lga_name = cluster.get('lga_name', None)
        state_name = cluster.get('state_name', None)
        # if LGA and state names not found, assume location incorrect
        if not (lga_name and state_name):
            return False
        # if state and LGA found, check the location
        lga = LGA.find_lga(name=lga_name, state_name=state_name)
        if lga is None:
            # if no LGA found, assume location incorrect
            return False
        else:
            return lga.contains_location(location)

    @classmethod
    def _musa_to_johannes(cls, musa_json):
        """Converts JSON document given as musa_json and containing data from a
        single survey from Musa's format into Johannes's format.  Returns a
        dictionary in the format specified by Johannes.
        The conversion may change either or both the name and type of an
        attribute.
        Only the information required by Johannes's code is converted.  Unused
        information is not included to decrease the amount of data sent to the
        client.
        """
        output = {}

        # map the top-level attributes
        output['location'] = musa_json['location']
        output['cluster'] = musa_json['cluster']
        output['startTime'] = musa_json['startTime']
        output['endTime'] = musa_json['endTime']
        output['team'] = musa_json['team']['teamID']

        # map household members
        output['members'] = []
        output['child_surveys'] = []
        output['women_surveys'] = []
        for member in musa_json['members']:
            gender = member['gender']
            age = member['age']
            output['members'].append({'gender': gender,
                                      'age': age})
            if 'surveyType' in member:
                if member['surveyType'] == 'child':
                    child = member['survey']
                    output['child_surveys'].append(child)
                elif member['surveyType'] == 'women':
                    woman = member['survey']
                    woman['age'] = age
                    output['women_surveys'].append(woman)

        # calculate correct_area
        output['correct_area'] = cls._correct_area(output['cluster'],
                                                   output['location'])

        # get rid of empty child_/women_surveys
        if not len(output['child_surveys']):
            del output['child_surveys']
        if not len(output['women_surveys']):
            del output['women_surveys']
        return output

    @classmethod
    def _find_all_surveys(cls):
        """Computes and returns a dictionary containing all available survey
        data in the format requested by Johannes and shown in the following
        example:
        {
            '1': {
                'location': [6.9249100685,
                             8.6650104523
                ],
                'correct_area': True,
                'cluster': 657,
                'startTime': '2014-10-18T19:56:23',
                'endTime': '2014-10-18T20:43:23',
                'team': 1,
                'members': [
                    {
                        'gender': 'M',
                        'age': 40
                    },
                    ...
                ],
                'women_surveys': [
                    {
                        'breastfeeding': 'Y',
                        'muac': 25.3,
                        'height': 165.9,
                        'weight': 56.0,
                        'age': 30,
                        'pregnant': 'N',
                        'ante-natal_care': 'Y',
                        'ever_pregnant': 'Y'
                    },
                    ...
                ],
                'child_surveys': [
                    {
                        'weight': 45.0,
                        'heightType': 'Child Standing (height)',
                        'edema': 'N',
                        'birthDate': '2009-10-18',
                        'height': 35.2,
                        'diarrhoea': 'N',
                        'zscores': {
                            'WAZ': 3.1,
                            'HAZ': -1.7,
                            'WHZ': -1.3
                        }
                    },
                    ...
                ]
            },
        }
        """
        # get all JSON documents
        docs = HouseholdSurveyJSON.objects.all()
        survey_data = {}
        # convert all documents
        i = 0
        for doc in docs:
            i += 1
            converted = cls._musa_to_johannes(doc.json)
            survey_data[str(i)] = converted

        return survey_data


class AlertsJSONView(LoginRequiredView):
    def get(self, request, *args, **kwargs):
        """Generates an HTTP response with a JSON document containing
        alerts in the format requested by Johannes and shown in the example
        below:
        {
            "alerts": [
                "GPS position issue with Ahmad in Nasarawa state",
                "Digit preference issue with Peter in Kogi state",
                "Age distribution issue with Mahamadou in Kano"
            ]
        }
        """
        alerts = {'alerts': self._find_all_alerts()}
        return HttpResponse(json.dumps(alerts),
                            content_type='application/json')

    @staticmethod
    def _find_all_alerts():
        """Computes and returns a list of strings each string representing one
        alert.  Archived alerts are not included.  Alerts are sorted by their
        creation date in the reverse chronological order (i.e. the list starts
        from the most recent).
        """
        alerts = Alert.objects.filter(archived=False).order_by('-created')
        return [
            {
                'timestamp': alert.created.isoformat(),
                'message': alert.text
            } for alert in alerts
        ]


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
        doc = ClustersJSON.get_most_recently_modified()
        if doc:
            data = doc.json
        else:
            data = {'clusters': {}}
        return HttpResponse(json.dumps(data), content_type='application/json')
