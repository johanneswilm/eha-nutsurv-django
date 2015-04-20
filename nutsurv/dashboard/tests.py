from django.test import TestCase, Client
from django.contrib.auth.models import User


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


class TeamMemberTest(TestCase):

    def setUp(self):
        self.client = Client()

    def test_new_teammember(self):
        team_member_data = {
            "url": "http://tim-watts-dev.eocng.org:8004/dashboard/teammembers/2/.api",
            "memberID": "2",
            "first_name": "Bob",
            "last_name": "Smitty",
            "gender": "M",
            "birth_year": 1901,
            "mobile": "+4917579",
            "email": "wef@asdf.com"
        }
        response = self.client.post('/dashboard/teammembers/', team_member_data, format='json')
        self.assertEqual(response.status_code, 201)

    def test_cannot_delete(self):
        team_member_data = {
            "url": "http://tim-watts-dev.eocng.org:8004/dashboard/teammembers/2/.api",
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
        self.assertEqual(response.status_code, 405)
