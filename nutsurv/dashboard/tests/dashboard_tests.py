from django.test import TestCase, Client
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from django.contrib.gis.geos import Point, Polygon, MultiPolygon
import json
import warnings
import collections

from dashboard.parse_python_indentation import parse_indentation

from dashboard.models import Alert, HouseholdSurveyJSON, TeamMember, SecondAdminLevel, Clusters
from dashboard.serializers import HouseholdMemberSerializer


class EmptySmokeTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.username = 'test'
        self.email = 'test@example.com'
        self.password = 'test'
        self.test_user = User.objects.create_superuser(self.username, self.email, self.password)
        login = self.client.login(username=self.username, password=self.password)
        self.assertEqual(login, True)

    def _test_empty_200(self, url):
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_empty_200_aggregatesurveydatajsonview(self):
        self._test_empty_200('/dashboard/aggregatesurveydatajsonview/')

    def test_empty_200_teamsjsonview(self):
        self._test_empty_200('/dashboard/teamsjsonview/')

    def test_empty_200_alerts(self):
        self._test_empty_200('/dashboard/alerts/')

    def test_empty_200_surveys(self):
        self._test_empty_200('/dashboard/surveys/')

    def test_empty_200_teammembers(self):
        self._test_empty_200('/dashboard/teammembers/')


class SimpleAccessTest(TestCase):

    def setUp(self):
        self.client = Client()

    def _test_403(self, url):
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 403)

    def test_auth_dashboard(self):
        self._test_403('/dashboard/')


class HouseholdSurveyTest(TestCase):

    def assertDictEqual(self, d1, d2, msg=None):  # assertEqual uses for dicts
        for k, v1 in d1.iteritems():
            self.assertIn(k, d2, msg)
            v2 = d2[k]
            if(isinstance(v1, collections.Iterable) and
               not isinstance(v1, basestring)):
                self.assertItemsEqual(v1, v2, msg)
            else:
                self.assertEqual(v1, v2, msg)
        return True

    def setUp(self):
        self.team_member, created = TeamMember.objects.get_or_create(
            birth_year=2000,
        )
        assert created

    def test_location_is_optional(self):

        survey = HouseholdSurveyJSON.objects.create(
            team_lead=self.team_member,
            team_assistant=self.team_member,
            team_anthropometrist=self.team_member,
            household_number=12,
            location=None,
        )
        survey.save()

    def test_extra_questions(self):
        survey = HouseholdSurveyJSON.objects.create(
            team_lead=self.team_member,
            team_assistant=self.team_member,
            team_anthropometrist=self.team_member,
            household_number=12,
            location=None,
            uuid='1234',
        )
        survey.save()

        household_member_data = {
            "first_name": "Bob",
            "last_name": "Smitty",
            "index": 1,
            "household_survey": survey.get_absolute_url(),
            "extra_questions": {
                "How many road must a man travel?": 42,
                "What is the meaning of life?": "Forty-two",
                "Tabs v spaces": ["tabs are cool", "but spaces are better"],
                "Spirit animal": {
                    "cat": "Lord of the Internet",
                    "dog": "Can't even right now"
                },
            }
        }
        data = HouseholdMemberSerializer(data=household_member_data)
        is_valid = data.is_valid()
        if is_valid is not True:
            print data.errors
        h = data.save()
        self.assertDictEqual(h.extra_questions, household_member_data['extra_questions'])

        username = 'test'
        email = 'test@example.com'
        password = 'test'
        User.objects.create_superuser(username=username, email=email, password=password)

        client = APIClient()
        client.login(username=username, password=password)
        response = client.get(h.get_absolute_url())
        # Some nested extra_question structure that was saved
        self.assertContains(response, "Lord of the Internet")

        response = client.get(survey.get_absolute_url())
        self.assertContains(response, "Lord of the Internet")
        survey_json = json.loads(response.content)

        survey_json['members'][0]['extraQuestions']['New Question'] = 'New Answer'
        response = client.put(survey.get_absolute_url(), survey_json, format='json')
        self.assertContains(response, "New Answer")


class TeamMemberTest(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_new_teammember(self):
        team_member_data = {
            "first_name": "Bob",
            "last_name": "Smitty",
            "gender": "M",
            "birth_year": 1901,
            "mobile": "+4917579",
            "email": "wef@asdf.com"
        }
        response = self.client.post('/dashboard/teammembers/', team_member_data)
        self.assertEqual(response.status_code, 201)

    def test_can_change(self):
        # This makes me sad, but is in the spec currently until we use passwords.
        team_member_data = {
            "first_name": "Bob",
            "last_name": "Smitty",
            "gender": "M",
            "birth_year": 1901,
            "mobile": "+4917579",
            "email": "wef@asdf.com"
        }
        response = self.client.post('/dashboard/teammembers/', team_member_data)

        assert 'Location' in response
        tm_url = response['Location']

        response = self.client.patch(tm_url, {'first_name': 'Robert'})
        self.assertEqual(json.loads(response.content)['firstName'], 'Robert')

    def test_can_delete(self):
        # This makes me sad, but is in the spec currently. At least until we use passwords.
        team_member_data = {
            "first_name": "Bob",
            "last_name": "Smitty",
            "gender": "M",
            "birth_year": 1901,
            "mobile": "+4917579",
            "email": "wef@asdf.com"
        }
        response = self.client.post('/dashboard/teammembers/', team_member_data, format='json')

        response = self.client.delete(response['Location'], format='json')
        self.assertEqual(response.status_code, 204)

    def test_creating_mobile_is_optional(self):
        team_member_data = {
            "first_name": "Bob",
            "last_name": "Smitty",
            "gender": "M",
            "birth_year": 1901,
            "email": "wef@asdf.com"
        }
        response = self.client.post('/dashboard/teammembers/', team_member_data, format='json')
        self.assertEqual(response.status_code, 201)


class IdentationParseTests(TestCase):
    expected_output = [{
        'key': 'green:',
        'offspring': [{
            'key': 'follow',
            'offspring': []
        }, {
            'key': 'blue',
            'offspring': []
        }, {
            'key': 'yellow',
            'offspring': []
        }, {
            'key': 'fishing',
            'offspring': []
        }, {
            'key': 'snowman:',
            'offspring': [{
                'key': 'gardening',
                'offspring': []
            }]
        }, {
            'key': 'street:',
            'offspring': [{
                'key': 'great',
                'offspring': []
            }]
        }]
    }, {
        'key': 'religion',
        'offspring': []
    }, {
        'key': 'flags',
        'offspring': []
    }, {
        'key': 'houses:',
        'offspring': [{
            'key': 'suffering',
            'offspring': []
        }]
    }]
    good_indentation = """
green:
    follow # And it should figure out how many spaces make out one indentation level from the first indentation it finds.
    blue
    yellow
    fishing
    snowman:
        gardening
    street:
        great

religion
flags
houses:
    suffering
    """
    bad_indentation = """
green:
    follow # And it should figure out how many spaces make out one indentation level from the first indentation it finds.
    blue
    yellow
    fishing
    snowman:
          gardening # This line is too indented. We should be able to read the file, but it should output a warning for this line.
    street:
        great

religion
flags
houses:
    suffering
    """

    def test_parsing(self):
        """ Tests whether correctly indented file can be parsed
        """
        a = parse_indentation(self.good_indentation)
        self.assertEqual(a, self.expected_output)

    def test_warning(self):
        """ Tests whether file with two extra indentation spaces is parsed and
        creates a warning.
        """
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            a = parse_indentation(self.bad_indentation)
        self.assertEqual(a, self.expected_output)
        self.assertEqual(len(w), 1)
        self.assertEqual(str(w[0].message), 'Indentation with errors!')


class AlertTest(TestCase):

    def setUp(self):
        self.team_member, created = TeamMember.objects.get_or_create(
            birth_year=2000,
        )
        assert created

    def test_mapping_check_missing_cluster(self):

        survey = HouseholdSurveyJSON.objects.create(
            team_lead=self.team_member,
            team_assistant=self.team_member,
            team_anthropometrist=self.team_member,
            household_number=12,
            location=Point(52.503713, 13.424559),
        )
        survey.save()

        result = list(Alert.mapping_check_missing_cluster(survey))

        self.assertEqual(result[0]['category'], 'map')
        self.assertEqual(result[0]['text'], 'No cluster ID for survey of team {} (survey {})'.format(self.team_member.pk, survey.pk))
        self.assertEqual(result[0]['survey'], survey)
        self.assertEqual(result[0]['team_lead'], self.team_member)


class AlertLocationTest(TestCase):

    def setUp(self):
        self.team_member, created = TeamMember.objects.get_or_create(
            birth_year=1956,
            last_name='Krabappel'
        )
        assert created
        second_admin_level_1 = SecondAdminLevel.objects.create(
            name_0='Country 1',
            name_1='State 1',
            name_2='County 1',
            varname_2='Springfield',
            mpoly=MultiPolygon(Polygon(((0, 0), (0, 100), (100, 100), (100, 0), (0, 0))),)
        )
        second_admin_level_1.save()

        second_admin_level_2 = SecondAdminLevel.objects.create(
            name_0='Country 1',
            name_1='State 1',
            name_2='County 2',
            varname_2='Shelbyville',
            mpoly=MultiPolygon(Polygon(((0, 100), (0, 200), (100, 200), (100, 100), (0, 100))),)
        )
        second_admin_level_2.save()
        second_admin_level_3 = SecondAdminLevel.objects.create(
            name_0='Country 1',
            name_1='State 2',
            name_2='County 3',
            varname_2='Ogdenville',
            mpoly=MultiPolygon(Polygon(((300, 300), (300, 400), (400, 400), (400, 300), (300, 300))),)
        )
        second_admin_level_3.save()
        clusters = Clusters.objects.create(
            json={
                "1": {
                    "cluster_name": "Fast-Food Boulevard",
                    "second_admin_level_name": "County 1",
                    "first_admin_level_name": "State 1"
                },
                "2": {
                    "cluster_name": "Main Street",
                    "second_admin_level_name": "County 1",
                    "first_admin_level_name": "State 1"
                },
                "3": {
                    "cluster_name": "Chinatown",
                    "second_admin_level_name": "County 2",
                    "first_admin_level_name": "State 1"
                },
                "4": {
                    "cluster_name": "Manhattan Square",
                    "second_admin_level_name": "County 2",
                    "first_admin_level_name": "State 1"
                },
                "5": {
                    "cluster_name": "Ogdenville Outlet Mall",
                    "second_admin_level_name": "County 3",
                    "first_admin_level_name": "State 2"
                },
                "6": {
                    "cluster_name": "New Christiana",
                    "second_admin_level_name": "County 3",
                    "first_admin_level_name": "State 2"
                },
            },
            active=True
        )
        clusters.save()
        self.assertNotEqual(Clusters.get_active(), None)

    def test_correct_admin_levels(self):
        survey = HouseholdSurveyJSON.objects.create(
            team_lead=self.team_member,
            team_assistant=self.team_member,
            team_anthropometrist=self.team_member,
            household_number=13,
            location=Point(52.503713, 13.424559),
            first_admin_level='State 1',
            second_admin_level='County 1',
            cluster=1
        )
        survey.save()

        result_first_admin = list(Alert.mapping_check_wrong_location_first_admin_level(survey))
        self.assertEqual(result_first_admin, [])

        result_second_admin = list(Alert.mapping_check_wrong_location_second_admin_level(survey))
        self.assertEqual(result_second_admin, [])

    def test_incorrect_second_admin_level(self):
        survey = HouseholdSurveyJSON.objects.create(
            team_lead=self.team_member,
            team_assistant=self.team_member,
            team_anthropometrist=self.team_member,
            household_number=14,
            location=Point(16.629403, 145.876453),
            first_admin_level='State 1',
            second_admin_level='County 1',
            cluster=2
        )
        survey.save()

        result_first_admin = list(Alert.mapping_check_wrong_location_first_admin_level(survey))
        self.assertEqual(result_first_admin, [])

        result_second_admin = list(Alert.mapping_check_wrong_location_second_admin_level(survey))
        self.assertEqual(len(result_second_admin), 1)
        self.assertEqual(result_second_admin[0]['alert_type'], 'mapping_check_wrong_location_second_admin_level')

    def test_incorrect_first_and_second_admin_levels(self):
        survey = HouseholdSurveyJSON.objects.create(
            team_lead=self.team_member,
            team_assistant=self.team_member,
            team_anthropometrist=self.team_member,
            household_number=15,
            location=Point(387.092593, 375.938294),
            first_admin_level='State 1',
            second_admin_level='County 1',
            cluster=4
        )
        survey.save()

        result_first_admin = list(Alert.mapping_check_wrong_location_first_admin_level(survey))
        self.assertEqual(len(result_first_admin), 1)
        self.assertEqual(result_first_admin[0]['alert_type'], 'mapping_check_wrong_location_first_admin_level')

        result_second_admin = list(Alert.mapping_check_wrong_location_second_admin_level(survey))
        self.assertEqual(len(result_second_admin), 1)
        self.assertEqual(result_second_admin[0]['alert_type'], 'mapping_check_wrong_location_second_admin_level')
