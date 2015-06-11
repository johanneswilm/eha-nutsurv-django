from django.test import TestCase, Client
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from django.contrib.gis.geos import Point, Polygon, MultiPolygon
import json
import warnings
import collections
from datetime import datetime

from dashboard.parse_python_indentation import parse_indentation
from dashboard.serializers import HouseholdMemberSerializer
from dashboard.models import (
    Alert, HouseholdSurveyJSON, TeamMember, HouseholdMember,
    SecondAdminLevel, Clusters, QuestionnaireSpecification,
)


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

    def test_unicode_for_survey_with_some_fields(self):
        survey = HouseholdSurveyJSON.objects.create(
            team_lead=self.team_member,
            team_assistant=self.team_member,
            team_anthropometrist=self.team_member,
            household_number=763,
        )
        self.assertEqual(unicode(survey), 'cluster: None; household: 763; team: 4- ; start time: None')

    def test_unicode_for_survey_with_all_fields(self):
        survey = HouseholdSurveyJSON.objects.create(
            team_lead=self.team_member,
            team_assistant=self.team_member,
            team_anthropometrist=self.team_member,
            household_number=832,
            cluster=232,
            start_time=datetime(2010, 1, 1),
        )
        self.assertEqual(unicode(survey), 'cluster: 232; household: 832; team: 3- ; start time: 2010-01-01 00:00:00')

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

    def test_missing_data_alert(self):

        survey = HouseholdSurveyJSON.objects.create(
            team_lead=self.team_member,
            team_assistant=self.team_member,
            team_anthropometrist=self.team_member,
            household_number=12,
            location=Point(52.503713, 13.424559),
            start_time=datetime(2010, 1, 1),
        )
        survey.save()

        self.woman, created_woman = HouseholdMember.objects.get_or_create(
            index=1,
            household_survey=survey,
            birthdate=datetime(1970, 1, 1),
            gender='F',
            height=23,
            weight=199,
        )

        self.woman2, created_woman2 = HouseholdMember.objects.get_or_create(
            index=2,
            household_survey=survey,
            birthdate=datetime(1971, 1, 1),
            gender='F',
            height=24,
            muac=198,
        )

        result = list(Alert.missing_data_alert(survey))

        self.assertEqual(len(result), 3)

        alert_titles = [a['text'] for a in result]

        self.maxDiff = 2322

        self.assertEqual(alert_titles, [
            'Missing data issue on field muac for women in team {}'.format(self.team_member.pk),
            'Missing data issue on field edema for women in team {}'.format(self.team_member.pk),
            'Missing data issue on field weight for women in team {}'.format(self.team_member.pk),
        ])

        self.assertTrue(
            'Missing data issue on field height for women in team {}'.format(
                self.team_member.pk) not in alert_titles
        )


EXAMPLE_QSL = """\
# This (and any other line starting with #) is a comment and will be ignored.
# The above line will also be ignored as all empty lines are.

# The next line is the title (compulsory)
The Christmas Survey

# The next section means that, unless explicitly specified, answers to all
# the questions are required. They could also be optional.
defaults
  required

# The following part defines the order in which the questionnaire sections you
# define will be executed (and thus the order in which the questions you define
# should be asked as the questionnaire sections are just containers for questions).
# Only the sections mentioned in the section execution order will be executed
# (unless one of the mentioned sections uses an inclusion directive to execute
# some other section).
section execution order
  # The following means that you want a section called "household" to be
  # executed first and that it should only be executed once per an interview.
  household
    single
  # Please note what we have mentioned before: the indentation matters.
  # The following will execute a questionnaire section labeled
  # "household members" and indicates that it may need to be executed more
  # than once (i.e. for multiple subjects (probably for each member?), hence
  # the name)
  household members
    multiple

# Now it is time to define our first questionnaire section. Let us call it
# "household" (please note that the section label starts at indentation level 0
# (zero, i.e. no indentation) and ends with a colon).
household:
  # The first question we define just says "Location" and does not even end
  # with a question mark.
  Presents Hiding Location
    # The answer to this question is required (remember the defaults we
    # set a little earlier?) and must be a GPS location.
    gps
  # Let us define a few more questions. As you can see the question label may be
  # whatever you want but the data types like integer, gps or datetime are
  # predefined (see the Data types section of the QSL spec).
  Christmas Club ID
    integer
  Number Of Christmas Presents Requested
    integer
  Preferred Delivery time
    datetime
# We have just finished defining our first questionnaire section!

# Let us define a few more questionnaire sections called "household members",
# "children" and "women"
household members:
  Favorite Reindeer
  # We did not define the data type for the above question which means that we
  # want it to be just text.
  Age (in years)
    integer
  Gender
    gender
  Favorite Reindeer has a red nose?
    yes/no
      # Let us mark this question as optional (i.e. no answer is
      # required unless the interviewee really wants to answer.)
      optional
  Joined during recall?
    yes/no
  # The following section is an inclusion directive. It says that at this
  # point in the interview we want to ask questions defined in another
  # questionnaire section called "children" but we want this to happen only
  # if the current subject responded to an earlier question about age (see
  # the question label we defined before?) giving a number 5 or less. This
  # is called a constraint.
  [children]
    Age (in years)
      answer < 6
  # We will use the inclusion directive again. This time we will specify two
  # constraints. The section "women" will only be activated if both
  # constraints are fulfilled.
  [women]
    Age (in years)
      answer > 5
    Gender
      answer = F

children:
  naughty
    yes/no
  # The next two questions are associated using a "skip" relation. We prefer
  # to get the date of birth of each child but if it is unavailable, we can
  # settle for their age in months. To model this, we make the date of birth
  # optional (i.e. override the defaults for this question) and keep the age
  # in month required but we skip the latter each time we have got an answer
  # to the former.
  Naughty since
    date
      optional
  Naughty time in months
    integer
    skip
      Date of birth
        answered
  Presents Allowed
    integer
  Weight of Presents
    integer
  Height of Presents
    integer
  # We define a new data type for the next question. We use a special keyword
  # "enumeration" and then enter a list of two possible answers.
  Height type
    enumeration
      Standing height
      Recumbent length

women:
  Christmas Tree?
    yes/no
  Christmas Carols?
    yes/no
  White christmas?
    yes/no
  Weight of Presents (kg)
    integer
  Height of Presents (cm)
    integer

# This example ends here.
"""


class HouseholdMemberTest(TestCase):

    def setUp(self):
        self.maxDiff = 2000
        self.team_member, created_teammember = TeamMember.objects.get_or_create(
            birth_year=2000,
        )
        assert created_teammember

        self.team_member2, created_teammember2 = TeamMember.objects.get_or_create(
            birth_year=1980,
        )
        assert created_teammember2

        self.survey, created_survey = HouseholdSurveyJSON.objects.get_or_create(
            team_lead=self.team_member,
            team_assistant=self.team_member,
            team_anthropometrist=self.team_member,
            household_number=12,
            start_time=datetime(2000, 1, 1),
        )
        assert created_survey

        self.child1, created_child1 = HouseholdMember.objects.get_or_create(
            index=1,
            household_survey=self.survey,
            birthdate=datetime(1999, 1, 1),
            gender='F',
            weight=454,
            extra_questions={
                'naughty': True
            },
        )

        self.child2, created_child2 = HouseholdMember.objects.get_or_create(
            index=2,
            household_survey=self.survey,
            birthdate=datetime(1999, 1, 1),
            gender='M',
            muac=29,
            extra_questions={
                'naughty': False
            },
        )

        self.woman, created_woman = HouseholdMember.objects.get_or_create(
            index=3,
            household_survey=self.survey,
            birthdate=datetime(1980, 1, 1),
            gender='F',
            height=23,
            muac=199,
            extra_questions={
                'Christmas Tree?': True
            }
        )

    def test_managers(self):
        self.assertEqual(3, HouseholdMember.objects.all().count())

        self.assertEqual(1, HouseholdMember.women.all().count())
        self.assertEqual(2, HouseholdMember.children.all().count())

    def test_by_teamlead(self):
        self.assertEqual(3, HouseholdMember.objects.by_teamlead(self.team_member).count())
        self.assertEqual(0, HouseholdMember.objects.by_teamlead(self.team_member2).count())

    def test_missing_data(self):

        expected = (
            {'children': {
                'muac': {'total': 2, 'existing': 1},
                'birthdate': {'total': 2, 'existing': 2},
                'weight': {'total': 2, 'existing': 1},
                'height': {'total': 2, 'existing': 0}},
             'household_members': {
                'gender': {'total': 3, 'existing': 3},
                 'birthdate': {'total': 3, 'existing': 3}},
             'women': {
                'muac': {'total': 1, 'existing': 1},
                 'edema': {'total': 1, 'existing': 0},
                 'birthdate': {'total': 1, 'existing': 1},
                 'weight': {'total': 1, 'existing': 0},
                 'height': {'total': 1, 'existing': 1}
            }
            }
        )

        self.assertEqual(
            expected,
            HouseholdMember.missing_data(
                HouseholdMember.objects.by_teamlead(self.team_member))
        )

    def test_requested_survey_fields(self):
        qsl = QuestionnaireSpecification(
            specification=EXAMPLE_QSL,
            active=True,
        )
        qsl.save()

        self.assertEqual([
            'muac',
            'weight',
            'birthdate',
            'height',
            u'naughty',
            u'Naughty since',
            u'Naughty time in months',
            u'Presents Allowed',
            u'Weight of Presents',
            u'Height of Presents',
            u'Height type'
        ], HouseholdMember.requested_survey_fields()['children'])

        self.assertEqual([
            'muac',
            'height',
            'weight',
            'birthdate',
            'edema',
            u'Christmas Tree?',
            u'Christmas Carols?',
            u'White christmas?',
            u'Weight of Presents (kg)',
            u'Height of Presents (cm)',
            u'Christmas Tree?',
            u'Christmas Carols?',
            u'White christmas?',
            u'Weight of Presents (kg)',
            u'Height of Presents (cm)',
        ], HouseholdMember.requested_survey_fields()['women'])

        self.assertEqual([
            'birthdate',
            'gender',
        ], HouseholdMember.requested_survey_fields()['household_members'])

        missing_data = HouseholdMember.missing_data(
            HouseholdMember.objects.by_teamlead(self.team_member))

        self.assertEqual(
            {'existing': 2, 'total': 2},
            missing_data['children']['naughty'],
        )

        self.assertEqual(
            {'existing': 0, 'total': 2},
            missing_data['children']['Naughty since'],
        )

        self.assertEqual(
            {'existing': 1, 'total': 1},
            missing_data['women']['Christmas Tree?'],
        )

    def test_age_distribution_years(self):
        self.assertEqual([
            {'count': 2, 'age_in_years': 1},
            {'count': 1, 'age_in_years': 20}
        ], list(HouseholdMember.objects.age_distribution_in_years()))

    def test_age_distribution_months(self):
        self.assertEqual(
            [{'count': 2, 'age_in_months': 12}],
            list(HouseholdMember.children.age_distribution_in_months())
        )


class AgeDistributionTest(TestCase):

    def setUp(self):
        self.maxDiff = 2000
        self.team_member, created_teammember = TeamMember.objects.get_or_create(
            birth_year=2000,
        )
        assert created_teammember

        self.team_member2, created_teammember2 = TeamMember.objects.get_or_create(
            birth_year=1980,
        )
        assert created_teammember2

        self.survey1, created_survey1 = HouseholdSurveyJSON.objects.get_or_create(
            uuid='12',
            team_lead=self.team_member,
            team_assistant=self.team_member,
            team_anthropometrist=self.team_member,
            household_number=12,
            start_time=datetime(2000, 1, 1),
        )
        assert created_survey1

        self.survey2, created_survey2 = HouseholdSurveyJSON.objects.get_or_create(
            uuid='13',
            team_lead=self.team_member2,
            team_assistant=self.team_member,
            team_anthropometrist=self.team_member,
            household_number=12,
            start_time=datetime(2000, 1, 1),
        )
        assert created_survey2

        self.child1, created_child1 = HouseholdMember.objects.get_or_create(
            index=1,
            household_survey=self.survey1,
            birthdate=datetime(1999, 1, 1),
            gender='F',
            weight=454,
        )

        self.child2, created_child2 = HouseholdMember.objects.get_or_create(
            index=2,
            household_survey=self.survey2,
            birthdate=datetime(1999, 3, 1),
            gender='M',
            muac=29,
        )

        self.client = Client()
        self.username = 'test'
        self.email = 'test@example.com'
        self.password = 'test'
        self.test_user = User.objects.create_superuser(self.username, self.email, self.password)
        login = self.client.login(username=self.username, password=self.password)
        self.assertEqual(login, True)

    def test_age_distribution(self):
        response = self.client.get('/dashboard/householdmember/age_distribution/.json')
        self.assertEqual(response.status_code, 200)

        # there should be two children

        self.assertEqual(json.loads(response.content), {
            u'ageDistribution': {
                u'householdMember': [{u'count': 1, u'age_in_years': 0}, {u'count': 1, u'age_in_years': 1}],
                u'children': [{u'count': 1, u'age_in_months': 10}, {u'count': 1, u'age_in_months': 12}]}})

    def test_age_distribution_by_team_lead(self):
        response = self.client.get('/dashboard/householdmember/age_distribution/.json?team_lead={}'.format(self.team_member.pk))

        # there's just one child that was interviewed by this team member

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {
            u'ageDistribution': {
                u'householdMember': [{u'count': 1, u'age_in_years': 1}],
                u'children': [{u'count': 1, u'age_in_months': 12}]}})

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
