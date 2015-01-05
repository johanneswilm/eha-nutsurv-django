import json

from django.shortcuts import render, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.generic import View

from models import Alert
from models import JSONDocument
from models import ClustersJSON
from models import LGA


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
        docs = JSONDocument.objects.all()
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


class ClustersPerTeamJSONView(LoginRequiredView):
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
        docs = JSONDocument.objects.all()
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
    def _yn_to_yes_no(value, attribute_name=''):
        """Converts 'Y' to 'Yes' and 'N' and an empty string to 'No'.  Raises an
        exception if any other value received.
        """
        if not attribute_name:
            attribute_name = 'unknown'
        if value == 'Y':
            return 'Yes'
        elif value == 'N' or value == '':
            return 'No'
        else:
            raise ValueError('Invalid value: "%s".  Attribute "%s" must be '
                             'either Y or N (or an empty string for No).' %
                             (value, attribute_name))

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
        output['location'] = []
        for c in musa_json['location']:
            output['location'].append(float(c))
        output['cluster'] = int(musa_json['cluster'])
        output['startTime'] = musa_json['startTime']
        output['endTime'] = musa_json['endTime']
        output['team'] = int(musa_json['team']['teamID'])

        # map household members
        output['members'] = []
        output['child_surveys'] = []
        output['women_surveys'] = []
        for member in musa_json['members']:
            gender = member['gender']
            age = int(member['age'])
            output['members'].append({'gender': gender,
                                      'age': age})
            if member['surveyType'] == 'child':
                survey = member['survey']
                child = {}
                child['weight'] = float(survey['weight'])
                child['height_type'] = survey['heightType']
                if child['height_type'] == 'Child Standing (height)':
                    child['height_type'] = 'Child Standing (Height)'
                child['edema'] = cls._yn_to_yes_no(
                    survey['edema'], 'edema')
                child['birthDate'] = survey['birthDate']
                child['height'] = float(survey['height'])
                child['diarrhoea'] = cls._yn_to_yes_no(
                    survey['diarrhoea'], 'diarrhoea')
                child['zscores'] = {
                    'WAZ': float(survey['zscores']['WAZ']),
                    'HAZ': float(survey['zscores']['HAZ']),
                    'WHZ': float(survey['zscores']['WHZ'])
                }
                output['child_surveys'].append(child)
            elif member['surveyType'] == 'women':
                survey = member['survey']
                woman = {}
                woman['breastfeeding'] = cls._yn_to_yes_no(
                    survey['breastfeeding'], 'breastfeeding')
                woman['muac'] = float(survey['muac'])
                woman['height'] = float(survey['height'])
                woman['weight'] = float(survey['weight'])
                woman['age'] = age
                woman['pregnant'] = cls._yn_to_yes_no(survey['pregnant'],
                                                      'pregnant')
                woman['ante-natal_care'] = cls._yn_to_yes_no(
                    survey['anteNatalCare'], 'ante-natal_care')
                woman['ever_pregnant'] = cls._yn_to_yes_no(
                    survey['everPregnant'], 'ever_pregnant')
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
                'start_time': '2014-10-18T19:56:23',
                'end_time': '2014-10-18T20:43:23',
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
                        'breastfeeding': 'Yes',
                        'muac': 25.3,
                        'height': 165.9,
                        'weight': 56.0,
                        'age': 30,
                        'pregnant': 'No',
                        'ante-natal_care': 'Yes',
                        'ever_pregnant': 'Yes'
                    },
                    ...
                ],
                'child_surveys': [
                    {
                        'weight': 45.0,
                        'height_type': 'Child Standing (Height)',
                        'edema': 'No',
                        'birthdate': '2009-10-18',
                        'height': 35.2,
                        'diarrhoea': 'No',
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
        docs = JSONDocument.objects.all()
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
        return [alert.text for alert in alerts]
