import json

from django.test import TestCase, Client
from django.contrib.auth.models import User

from .models import TrainingSurvey
from dashboard.models import HouseholdSurveyJSON, TeamMember


class TrainingSurveyTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.username = 'test'
        self.email = 'test@example.com'
        self.password = 'test'
        self.test_user = User.objects.create_superuser(self.username, self.email, self.password)

        self.team_member, created = TeamMember.objects.get_or_create(
            birth_year=2000,
        )
        assert created

        login = self.client.login(username=self.username, password=self.password)
        self.assertEqual(login, True)

    def test_training_survey_does_not_show_in_regular_surveys(self):

        x = TrainingSurvey(
            team_assistant=self.team_member,
            team_anthropometrist=self.team_member,
            household_number=22,
        )
        x.save()

        self.assertEqual(
            TrainingSurvey.objects.all().count(),
            1,
        )

        self.assertEqual(
            HouseholdSurveyJSON.objects.all().count(),
            0,
        )

        response = self.client.get('/training/surveys/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json.loads(response.content)), 1)

        response = self.client.get('/dashboard/surveys/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, '[]')

    def test_post_training_survey(self):

        response = self.client.post('/training/surveys/', data={
            'uuid': '123',
            'household_number': '22',
            'team_assistant': self.team_member.get_absolute_url(),
            'team_anthropometrist': self.team_member.get_absolute_url(),
        })

        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(HouseholdSurveyJSON.objects.all().count(), 0)
        self.assertEqual(TrainingSurvey.objects.all().count(), 1)

    def test_post_training_with_1_person_family(self):

        person = {
            u'muac': 232,
            u'birthdate': u'2012-01-01',
            u'weight': 89.0,
            u'height': 18.0,
            u'firstName': u'Jusuf',
            u'gender': u'F',
        }

        data = {
            'uuid': '123',
            'household_number': '22',
            'team_assistant': self.team_member.get_absolute_url(),
            'team_anthropometrist': self.team_member.get_absolute_url(),
            'members': [person],
        }

        # test create
        response = self.client.post('/training/surveys/', json.dumps(data), content_type="application/json")
        result = json.loads(response.content)
        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(result['members'], [person])

        # .. and update
        response = self.client.put(result['url'], json.dumps(data), content_type="application/json")
        result = json.loads(response.content)

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(result['members'], [person])

    def test_post_training_with_incomplete_data(self):

        person = {
            u'muac': 1,
            u'weight': 1.50,
            u'height': 1.3,
        }

        data = {
            'uuid': '124',
            'household_number': '23',
            'team_assistant': self.team_member.get_absolute_url(),
            'team_anthropometrist': self.team_member.get_absolute_url(),
            'members': [person],
        }

        # test create
        response = self.client.post('/training/surveys/', json.dumps(data), content_type="application/json")
        json.loads(response.content)
        self.assertEqual(response.status_code, 201, response.content)

