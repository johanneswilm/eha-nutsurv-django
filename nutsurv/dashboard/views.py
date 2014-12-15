import json

from django.shortcuts import render, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.generic import View

from models import Alert


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
        # todo: Get rid of teams_dict below when we know the data format used
        # todo: in a new mobile app.  Replace this mock-up with code querying
        # todo: the database and computing the data.
        teams_dict = {
            '1': 'John, Daisy & Flint',
            '2': 'Patrick, Abigail & Stephanie',
            '3': 'Rose, Hannah & Chris',
        }
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
        # todo: Get rid of clusters_per_team_dict below when we know the data
        # todo: format used in a new mobile app.  Replace this mock-up with
        # todo: code querying the database and computing the data.
        clusters_per_team_dict = {
            '1': 5,
            '2': 15,
            '3': 17
        }
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
    def _find_all_surveys():
        """Computes and returns a dictionary containing team data in the format
        requested by Johannes and shown in the following example:
        {
            '1': {
                'location': [6.9249100685,
                             8.6650104523
                ],
                'correct_area': True,
                'cluster': 657,
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
        # todo: Get rid of survey_data below when we know the data format used
        # todo: in a new mobile app.  Replace this mock-up with code querying
        # todo: the database and computing the data.
        survey_data = {
            '1': {
                'location': [6.9249100685,
                             8.6650104523
                ],
                'correct_area': True,
                'cluster': 657,
                'end_time': '2014-10-18T20:43:23',
                'team': 1,
                'members': [{
                                'gender': 'M',
                                'age': 40
                            }, {
                                'gender': 'M',
                                'age': 17
                            }, {
                                'gender': 'M',
                                'age': 15
                            }, {
                                'gender': 'M',
                                'age': 10
                            }, {
                                'gender': 'M',
                                'age': 4
                            }, {
                                'gender': 'F',
                                'age': 30
                            }, {
                                'gender': 'F',
                                'age': 18
                            }, {
                                'gender': 'F',
                                'age': 23
                            }],
                'women_surveys': [{
                                      'breastfeeding': 'Yes',
                                      'muac': 25.3,
                                      'height': 165.9,
                                      'weight': 56.0,
                                      'age': 30,
                                      'pregnant': 'No',
                                      'ante-natal_care': 'Yes',
                                      'ever_pregnant': 'Yes'
                                  }, {
                                      'breastfeeding': 'Yes',
                                      'muac': 35.2,
                                      'height': 157.9,
                                      'weight': 61.0,
                                      'age': 18,
                                      'pregnant': 'Yes',
                                      'ante-natal_care': 'Yes',
                                      'ever_pregnant': 'Yes'
                                  }, {
                                      'breastfeeding': 'No',
                                      'muac': 29.8,
                                      'height': 170.9,
                                      'weight': 75.0,
                                      'age': 23,
                                      'pregnant': 'Yes',
                                      'ante-natal_care': 'No',
                                      'ever_pregnant': 'Yes'
                                  }],
                'child_surveys': [{
                                      'muac': 25.1,
                                      'gender': 'M',
                                      'weight': 45.0,
                                      'height_type': 'Child Standing (Height)',
                                      'edema': 'No',
                                      'birthdate': '2009-10-18',
                                      'height': 35.2,
                                      'diarrhoea': 'No',
                                      'zscores': {
                                          'WAZ': 4.4,
                                          'HAZ': 0.9,
                                          'WHZ': 0.8
                                      }
                                  }]
            },
            '2': {
                'location': [6.8249100685,
                             8.1650104523
                ],
                'correct_area': True,
                'cluster': 657,
                'end_time': '2014-10-18T20:57:23',
                'team': 1,
                'members': [{
                                'gender': 'M',
                                'age': 40
                            }, {
                                'gender': 'M',
                                'age': 17
                            }, {
                                'gender': 'M',
                                'age': 4
                            }, {
                                'gender': 'F',
                                'age': 32
                            }, {
                                'gender': 'F',
                                'age': 19
                            }, {
                                'gender': 'F',
                                'age': 17
                            }],
                'women_surveys': [{
                                      'breastfeeding': 'No',
                                      'muac': 15.2,
                                      'height': 155.9,
                                      'weight': 55.0,
                                      'age': 32,
                                      'pregnant': 'No',
                                      'ante-natal_care': 'Yes',
                                      'ever_pregnant': 'No'
                                  }, {
                                      'breastfeeding': 'Yes',
                                      'muac': 35.2,
                                      'height': 157.9,
                                      'weight': 61.0,
                                      'age': 19,
                                      'pregnant': 'Yes',
                                      'ante-natal_care': 'Yes',
                                      'ever_pregnant': 'Yes'
                                  }, {
                                      'breastfeeding': 'No',
                                      'muac': 29.8,
                                      'height': 170.9,
                                      'weight': 75.0,
                                      'age': 17,
                                      'pregnant': 'Yes',
                                      'ante-natal_care': 'No',
                                      'ever_pregnant': 'Yes'
                                  }],
                'child_surveys': [{
                                      'muac': 18.9,
                                      'gender': 'M',
                                      'weight': 45.0,
                                      'height_type': 'Child Standing (Height)',
                                      'edema': 'No',
                                      'birthdate': '2009-04-18',
                                      'height': 35.2,
                                      'diarrhoea': 'No',
                                      'zscores': {
                                          'WAZ': 0.4,
                                          'HAZ': 1.1,
                                          'WHZ': 0.4
                                      }
                                  }]
            },
            '3': {
                'location': [6.9049100685,
                             8.7650104523
                ],
                'correct_area': False,
                'cluster': 658,
                'end_time': '2014-10-18T20:56:23',
                'team': 1,
                'members': [{
                                'gender': 'M',
                                'age': 34
                            }, {
                                'gender': 'F',
                                'age': 18
                            }, {
                                'gender': 'F',
                                'age': 19
                            }, {
                                'gender': 'F',
                                'age': 17
                            }],
                'women_surveys': [{
                                      'breastfeeding': 'No',
                                      'muac': 47.7,
                                      'height': 155.9,
                                      'weight': 55.0,
                                      'pregnant': 'No',
                                      'ante-natal_care': 'No',
                                      'ever_pregnant': 'No'
                                  }, {
                                      'breastfeeding': 'No',
                                      'muac': 25.3,
                                      'height': 165.9,
                                      'weight': 56.0,
                                      'pregnant': 'No',
                                      'ante-natal_care': 'No',
                                      'ever_pregnant': 'No'
                                  }, {
                                      'breastfeeding': 'No',
                                      'muac': 29.8,
                                      'height': 170.9,
                                      'weight': 75.0,
                                      'pregnant': 'Yes',
                                      'ante-natal_care': 'No',
                                      'ever_pregnant': 'No'
                                  }]
            },
            '4': {
                'location': [6.8749100685,
                             8.8650104523
                ],
                'correct_area': False,
                'cluster': 659,
                'end_time': '2014-10-18T21:33:23',
                'team': 2,
                'members': [{
                                'gender': 'M',
                                'age': 18
                            }, {
                                'gender': 'M',
                                'age': 15
                            }, {
                                'gender': 'F',
                                'age': 16
                            }, {
                                'gender': 'F',
                                'age': 16
                            }, {
                                'gender': 'F',
                                'age': 16
                            }],
                'women_surveys': [{
                                      'breastfeeding': 'No',
                                      'muac': 15.2,
                                      'height': 155.9,
                                      'weight': 55.0,
                                      'pregnant': 'No',
                                      'ante-natal_care': 'Yes',
                                      'ever_pregnant': 'No'
                                  }, {
                                      'breastfeeding': 'Yes',
                                      'muac': 25.3,
                                      'height': 165.9,
                                      'weight': 56.0,
                                      'pregnant': 'No',
                                      'ante-natal_care': 'Yes',
                                      'ever_pregnant': 'Yes'
                                  }, {
                                      'breastfeeding': 'Yes',
                                      'muac': 35.2,
                                      'height': 157.9,
                                      'weight': 61.0,
                                      'pregnant': 'Yes',
                                      'ante-natal_care': 'Yes',
                                      'ever_pregnant': 'Yes'
                                  }]
            },
            '5': {
                'location': [6.9920101166,
                             8.7965202332
                ],
                'correct_area': True,
                'cluster': 659,
                'end_time': '2014-10-18T18:23:23',
                'team': 3,
                'members': [{
                                'gender': 'M',
                                'age': 15
                            }, {
                                'gender': 'M',
                                'age': 0
                            }, {
                                'gender': 'F',
                                'age': 2
                            }, {
                                'gender': 'F',
                                'age': 18
                            }, {
                                'gender': 'F',
                                'age': 23
                            }, {
                                'gender': 'F',
                                'age': 21
                            }],
                'women_surveys': [{
                                      'breastfeeding': 'No',
                                      'muac': 15.2,
                                      'height': 155.9,
                                      'weight': 55.0,
                                      'pregnant': 'No',
                                      'ante-natal_care': 'Yes',
                                      'ever_pregnant': 'No'
                                  }, {
                                      'breastfeeding': 'Yes',
                                      'muac': 25.3,
                                      'height': 165.9,
                                      'weight': 56.0,
                                      'pregnant': 'No',
                                      'ante-natal_care': 'Yes',
                                      'ever_pregnant': 'Yes'
                                  }, {
                                      'breastfeeding': 'No',
                                      'muac': 29.8,
                                      'height': 170.9,
                                      'weight': 75.0,
                                      'pregnant': 'Yes',
                                      'ante-natal_care': 'No',
                                      'ever_pregnant': 'Yes'
                                  }],
                'child_surveys': [{
                                      'weight': 45.0,
                                      'gender': 'M',
                                      'height_type': 'Child Standing (Height)',
                                      'edema': 'No',
                                      'birthdate': '2012-09-19',
                                      'height': 35.2,
                                      'diarrhoea': 'No',
                                      'zscores': {
                                          'WAZ': 0.1,
                                          'HAZ': 0.2,
                                          'WHZ': 0.1
                                      }
                                  }, {
                                      'muac': 28.9,
                                      'gender': 'F',
                                      'weight': 45.0,
                                      'height_type': 'Child Standing (Height)',
                                      'edema': 'No',
                                      'birthdate': '2014-11-02',
                                      'height': 35.2,
                                      'diarrhoea': 'No',
                                      'zscores': {
                                          'WAZ': -8.4,
                                          'HAZ': -2.3,
                                          'WHZ': 1.5
                                      }
                                  }]
            },
            '6': {
                'location': [6.9920101166,
                             8.8165202332
                ],
                'correct_area': False,
                'cluster': 659,
                'end_time': '2014-10-18T18:28:14',
                'team': 3,
                'members': [{
                                'gender': 'M',
                                'age': 25
                            }, {
                                'gender': 'M',
                                'age': 20
                            }, {
                                'gender': 'F',
                                'age': 28
                            }, {
                                'gender': 'F',
                                'age': 33
                            }, {
                                'gender': 'F',
                                'age': 31
                            }, {
                                'gender': 'F',
                                'age': 2
                            }, {
                                'gender': 'M',
                                'age': 2
                            }],
                'women_surveys': [{
                                      'breastfeeding': 'No',
                                      'muac': 17.2,
                                      'height': 157.8,
                                      'weight': 54.0,
                                      'pregnant': 'No',
                                      'ante-natal_care': 'No',
                                      'ever_pregnant': 'No'
                                  }, {
                                      'muac': 25.3,
                                      'height': 165.9,
                                      'weight': 56.0,
                                      'pregnant': 'No',
                                      'ante-natal_care': 'Yes',
                                      'ever_pregnant': 'Yes'
                                  }, {
                                      'muac': 35.2,
                                      'height': 157.9,
                                      'weight': 61.0,
                                      'pregnant': 'Yes',
                                      'ante-natal_care': 'Yes',
                                      'ever_pregnant': 'Yes'
                                  }]
            },
            '7': {
                'location': [6.9920101166,
                             8.5965202332
                ],
                'correct_area': True,
                'cluster': 659,
                'end_time': '2014-10-18T19:02:56',
                'team': 3,
                'members': [{
                                'gender': 'M',
                                'age': 15
                            }, {
                                'gender': 'M',
                                'age': 2
                            }, {
                                'gender': 'F',
                                'age': 30
                            }],
                'women_surveys': [{
                                      'breastfeeding': 'No',
                                      'muac': 29.8,
                                      'height': 170.9,
                                      'pregnant': 'Yes',
                                      'ante-natal_care': 'No',
                                      'ever_pregnant': 'Yes'
                                  }],
                'child_surveys': [{
                                      'muac': 28.4,
                                      'gender': 'M',
                                      'height_type': 'Child Standing (Height)',
                                      'edema': 'No',
                                      'birthdate': '2012-06-08',
                                      'height': 35.2,
                                      'diarrhoea': 'No',
                                      'zscores': {
                                          'WAZ': 1.1,
                                          'HAZ': -1.7,
                                          'WHZ': 1.3
                                      }
                                  }]
            }
        }
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
