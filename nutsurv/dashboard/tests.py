from django.test import TestCase, Client, RequestFactory
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

    def test_aggregatesurveydatajsonview(self):
        response = self.client.get('/dashboard/aggregatesurveydatajsonview/')
        self.assertEqual(response.status_code, 200)

    def test_teamsjsonview(self):
        response = self.client.get('/dashboard/teamsjsonview/')
        self.assertEqual(response.status_code, 200)

    def test_alerts(self):
        response = self.client.get('/dashboard/alerts/')
        self.assertEqual(response.status_code, 200)


