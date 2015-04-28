from django.test import TestCase, Client
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from django.contrib.gis.geos import Point
import json

from .models import Alert, HouseholdSurveyJSON, TeamMember


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


class TeamMemberTest(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_new_teammember(self):
        team_member_data = {
            "memberID": "2",
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
            "memberID": "2",
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
            "memberID": "2",
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
            "memberID": "2",
            "first_name": "Bob",
            "last_name": "Smitty",
            "gender": "M",
            "birth_year": 1901,
            "email": "wef@asdf.com"
        }
        response = self.client.post('/dashboard/teammembers/', team_member_data, format='json')
        self.assertEqual(response.status_code, 201)


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
