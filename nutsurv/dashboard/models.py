# Python
import datetime
import dateutil.parser
import dateutil.relativedelta
import uuid
import random
from functools import wraps
import logging

# 3rd party
import numpy
import scipy.stats
import validictory
import json
import parse_python_indentation

# django core
from django.utils.translation import ugettext as _
import django.contrib.gis.db.models as gismodels
from django.db import models
from django.contrib.gis.geos import Point
from django.db.models import Q


# django 3rd party
from rest_framework.reverse import reverse
from phonenumber_field.modelfields import PhoneNumberField
from django_extensions.db.fields import (
    CreationDateTimeField, ModificationDateTimeField,
)
from django_pgjson.fields import JsonBField
from jsonfield import JSONField

# Internal
from fields import UniqueActiveField

logger = logging.getLogger(__name__)


class TeamMember(models.Model):
    MALE = 'M'
    FEMALE = 'F'
    GENDER_CHOICES = (
        (MALE, _('Male')),
        (FEMALE, _('Female')),
    )
    first_name = models.CharField(blank=False, max_length=50)
    last_name = models.CharField(blank=False, max_length=50)
    mobile = PhoneNumberField(blank=True)
    email = models.EmailField(blank=True)
    birth_year = models.IntegerField(blank=False)
    gender = models.CharField(choices=GENDER_CHOICES, max_length=3, blank=True)

    created = CreationDateTimeField()
    modified = ModificationDateTimeField()

    _last_survey = None

    def last_survey(self):
        # TODO: maybe get the reverse relationship instead

        # Poor mans cache
        if self._last_survey:
            return self._last_survey

        survey = (HouseholdSurveyJSON.objects.filter(
            Q(team_lead=self)
            | Q(team_assistant=self)
            | Q(team_anthropometrist=self)
        ).order_by('-id') or [None])[0]

        self._last_survey = survey
        return survey

    def last_survey_position(self):
        last_survey = self.last_survey()
        if last_survey:
            for position in ['team_lead', 'team_assistant', 'team_anthropometrist']:
                if self.id == getattr(last_survey, position).id:
                    return position

            raise "TeamMember has last_survey but no position, this shouldn't happen."

    def last_survey_created(self):
        last_survey = self.last_survey()
        if last_survey:
            return last_survey.get_start_time()

    def last_survey_cluster_name(self):
        last_survey = self.last_survey()
        if last_survey:
            return last_survey.json['cluster_name']

    def last_survey_cluster(self):
        last_survey = self.last_survey()
        if last_survey:
            return last_survey.json['cluster']

    class Meta:
        get_latest_by = 'modified'
        ordering = ('-modified', '-created',)

    @property
    def random_id(self):
        return random.randint(10000, 100000)

    def __unicode__(self):
        return u'%s-%s %s' % (self.id, self.first_name, self.last_name)

    def get_absolute_url(self):
        return reverse('teammember-detail', kwargs={'pk': str(self.pk)})


def validate_json(spec_file):
    survey_schema = None
    try:
        survey_schema = json.load(open(spec_file))
    except IOError as e:
        # log the error but it's ok if the spec is missing
        # if the validator is never called
        logger.exception(
            "Could not load the json spec %s. \nThis is ok if you are just setting up.\n%s" % (spec_file, e.message))

    @wraps(validate_json)
    def wrapped(value):
        assert survey_schema, "Trying to validate a non existant JSON schema file %s" % spec_file
        # It really should exist by now.
        validictory.validate(value, survey_schema, required_by_default=False)
    return wrapped


from django.db.models import F, Count, Func


class Age(Func):
    function = 'AGE'


class FullMonths(Func):
    # yes, it's sad that postgres doesn't have a `justify_months` fun
    template = '(( 12 * EXTRACT(years FROM %(expressions)s)) + EXTRACT(months FROM %(expressions)s))::integer'
    output_field = models.IntegerField()


class FullYears(Func):
    template = '(EXTRACT(years FROM %(expressions)s))::integer'
    output_field = models.IntegerField()


class HouseholdMemberQuerySet(models.QuerySet):

    def by_teamlead(self, team_lead):
        return self.filter(household_survey__team_lead=team_lead)

    def by_cluster_num(self, cluster_num):
        return self.filter(household_survey__cluster=cluster_num)

    def age_distribution_in_years(self):
        return self.annotate(
            age_in_years=FullYears(Age(F('household_survey__start_time'), F('birthdate')))
        ).values('age_in_years').order_by('age_in_years').annotate(count=Count('age_in_years'))

    def age_distribution_in_months(self):
        return self.annotate(
            age_in_months=FullMonths(Age(F('household_survey__start_time'), F('birthdate')))
        ).values('age_in_months').order_by('age_in_months').annotate(count=Count('age_in_months'))

HouseholdMemberManager = models.Manager.from_queryset(HouseholdMemberQuerySet)


class ChildrenManager(HouseholdMemberManager):

    def get_queryset(self):
        return super(ChildrenManager, self).get_queryset().annotate(
            age_in_years=FullYears(Age(F('household_survey__start_time'), F('birthdate')))
        ).filter(
            age_in_years__lt=6,
        )


class WomenManager(HouseholdMemberManager):

    def get_queryset(self):
        return super(WomenManager, self).get_queryset().annotate(
            age_in_years=FullYears(Age(F('household_survey__start_time'), F('birthdate')))
        ).filter(
            age_in_years__gt=15,
            age_in_years__lt=49,
            gender='F',
        )


class BaseHouseholdMember(models.Model):

    # TODO add the following fields to the model that were present in the legacy
    # json field:
    # women:
    #   "breastfeeding",
    #   "age",
    #   "pregnant",
    #
    # children:
    #   "heightType",
    #   "edema",
    #   "birthDate",
    #   "ageInMonths",
    #
    # household_members:
    #   "age",

    REQUESTED_SURVEY_FIELDS = {
        'women': [
            "muac",
            "height",
            "weight",
            "birthdate",
            "edema",
        ],
        'children': [
            "muac",
            "weight",
            "birthdate",
            "height",
        ],
        'household_members': [
            "birthdate",
            "gender",
        ]
    }

    GENDER = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )
    gender = models.CharField(max_length=1, choices=GENDER, blank=True)

    first_name = models.TextField(blank=True)
    index = models.SmallIntegerField(blank=True)
    birthdate = models.DateField(blank=True, null=True)

    muac = models.SmallIntegerField(null=True)  # in millimeter ?
    weight = models.FloatField(null=True)       # probably in kilograms ?
    height = models.FloatField(null=True)       # probably in centimeters ?
    edema = models.NullBooleanField()

    objects = HouseholdMemberManager()
    household_members = HouseholdMemberManager()

    @classmethod
    def missing_data_for_fields(cls, reference, requested_fields):
        total = reference.count()
        d = {}

        hardcoded_fields = cls._meta.get_all_field_names()
        # TODO replace with
        # hardcoded_fields [f.name for f in cls._meta.get_fields()]
        # in django 1.8

        for key in requested_fields:

            if key in hardcoded_fields:
                existing_data_count = reference.exclude(
                    **dict(((key, None),),)).count()
            else:
                existing_data_count = reference.extra(
                    where=["extra_questions ? %s"], params=[key]).count()

            d[key] = {
                'existing': existing_data_count,
                'total': total,
            }

        return d

    @classmethod
    def missing_data(cls, reference=None):
        if reference is None:
            reference = cls.household_members

        d = {}
        for member_type, requested_fields in cls.requested_survey_fields().items():
            reference = getattr(cls, member_type)
            d[member_type] = cls.missing_data_for_fields(reference, requested_fields)
        return d

    @classmethod
    def requested_survey_fields(cls):

        survey_fields = cls.REQUESTED_SURVEY_FIELDS
        qsl = QuestionnaireSpecification.get_active()

        if not qsl:
            return survey_fields

        parsed_qsl = parse_python_indentation.parse_indentation(qsl.specification)

        for member_type in survey_fields.keys():
            extra_fields = next((item for item in parsed_qsl if item["key"] == "{}:".format(member_type)), False)
            if extra_fields:
                for field in extra_fields['offspring']:
                    survey_fields[member_type].append(field['key'])

        return survey_fields

    class Meta:
        abstract = True


class HouseholdMember(BaseHouseholdMember):
    household_survey = models.ForeignKey('HouseholdSurveyJSON', related_name='members')
    extra_questions = JsonBField(default={})

    objects = HouseholdMemberManager()
    women = WomenManager()
    children = ChildrenManager()

    def get_absolute_url(self):
        return reverse('householdmember-detail', args=[str(self.id)])


class BaseHouseholdSurveyJSON(gismodels.Model):

    class Meta:
        verbose_name = 'household survey'
        abstract = True

    team_assistant = models.ForeignKey('TeamMember', related_name='%(class)s_surveys_as_team_assistant')
    team_anthropometrist = models.ForeignKey('TeamMember', related_name='%(class)s_surveys_as_team_anthropometrist')
    household_number = models.SmallIntegerField()

    json = JSONField(
        # validators=[validate_json(settings.BOWER_COMPONENTS_ROOT
        #                          + '/data-models/schemas/NutritionSurvey.json')],
        null=False,
        blank=False,
        help_text='A JSON document containing data acquired from one '
                  'household.  Typically not edited here but uploaded from a '
                  'mobile application used by a team of surveyors in the '
                  'field.  If in doubt, do not edit.'
    )

    second_admin_level = models.CharField(max_length=60, blank=True)
    first_admin_level = models.CharField(max_length=60, blank=True)

    # With knowledge comes pain.
    # Normalize yourself
    # smile with hope.

    cluster_population = models.IntegerField(null=True)
    cluster_segment_population = models.IntegerField(null=True)

    cluster = models.IntegerField(blank=True, null=True)
    cluster_name = models.CharField(max_length=60, blank=True)
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    uuid = models.CharField(
        max_length=255, unique=True,
        help_text='A unique identifier of an individual household survey.  '
                  'Typically assigned by a mobile application before the data '
                  'is uploaded to the server.  If in doubt, do no edit.'
    )

    def parse_team(self, position):

        # TODO this still depends on self.json, while aiming to replace it.

        team_members = self.json['team']['members']
        for m in team_members:
            designation = m['designation']
            if designation == position:
                return m

    def parse_and_set_team_members(self):

        def make_team_member(parsed):
            tm, created = TeamMember.objects.get_or_create(
                id=parsed['memberID'],
                defaults={
                    'gender': parsed['gender'],
                    'first_name': parsed['firstName'],
                    'last_name': parsed['lastName'],
                    'mobile': parsed['mobile'],
                    'email': parsed['email'],
                    'birth_year': parsed['birthYear']
                }
            )
            return tm

        lead = self.parse_team('Team Leader')
        self.team_lead = make_team_member(lead)

        assistant = self.parse_team('Assistant')
        self.team_assistant = make_team_member(assistant)

        anthro = self.parse_team('Anthropometrist')
        self.team_anthropometrist = make_team_member(anthro)

    def __unicode__(self):
        return u'cluster: {}; household: {}; team: {}; start time: {}'.format(
            getattr(self, 'cluster'),
            getattr(self, 'household_number'),
            getattr(self, 'team_lead'),
            getattr(self, 'start_time'),
        )

    def _get_time_stamp(self, key):
        try:
            time_string = self.json[key]
        except KeyError:
            return None
        try:
            time_stamp = dateutil.parser.parse(time_string)
        except TypeError:
            return None
        else:
            return time_stamp

    def get_start_time(self):
        return self._get_time_stamp('startTime')

    def get_end_time(self):
        return self._get_time_stamp('endTime')

    def get_survey_duration(self):
        """This method calculates duration of the survey in minutes (i.e. the
        difference between the survey end time and its start time).  If any of
        the two time stamps is missing or invalid or the difference is less
        than zero, it returns None.
        """
        start_time = self.get_start_time()
        end_time = self.get_end_time()
        if isinstance(start_time, datetime.datetime) and \
                isinstance(end_time, datetime.datetime):
            delta = end_time - start_time
            if delta.total_seconds() >= 0:
                # Return the survey duration in minutes.
                return delta.total_seconds() / 60.0
            else:
                return None
        else:
            return None

    @classmethod
    def find_all_surveys_by_team(cls, team_id):
        """This method finds all teams buy the team leader id. This is after
        clarification that the team_id is based on the id of th team leader.
        """
        docs = cls.objects.filter(team_lead__id=team_id)
        return docs

    def find_all_surveys_by_this_team(self):
        """This method finds all instances of HouseholdSurveyJSON which were created
        by team who created this instance.  If this document is does not have
        a valid team/team_id or the team_id is None (in both cases the document
        is not a valid survey data structure), it returns an empty list.
        """
        team_id = self.get_team_id()
        if team_id is None:
            return []
        else:
            return self.find_all_surveys_by_team(team_id)

    def get_team_id(self):
        try:
            team_id = self.team_lead.pk
        except TypeError:
            return None
        else:
            return team_id

    def get_location(self):
        try:
            location = self.json['location']
        except TypeError:
            return None
        else:
            return location

    def get_cluster_id(self):
        try:
            location = self.json['cluster']
        except TypeError:
            return None
        else:
            return location

    def get_team_leader_name(self):
        """Returns a team leader name or None if no team leader name found.
        """
        last_name = None
        try:
            team_members = self.json['team']['members']
            for m in team_members:
                designation = m['designation']
                if designation is not None:
                    if 'Leader' in designation:
                        last_name = m['lastName']
                        break
        except KeyError:
            return None
        if last_name:
            return last_name
        else:
            return None

    def get_team_name(self):
        """Returns a team leader name or team ID if no team leader name found or
         'UNNAMED'.
        """
        team_leader = self.get_team_leader_name()
        if team_leader is not None:
            return team_leader
        team_id = self.get_team_id()
        if team_id is not None:
            return str(team_id)
        else:
            return 'UNNAMED'

    def _get_records_for_survey_types(self, survey_types):
        if not isinstance(survey_types, (list, tuple, set)) and \
                isinstance(survey_types, basestring):
            survey_types = (survey_types,)
        output = []
        if 'members' in self.json:
            # Get the survey date to calculate age based on date of birth.
            if 'startTime' in self.json:
                survey_start_time = self.json['startTime']
            else:
                survey_start_time = None
            for member in self.json['members']:
                if 'surveyType' in member and member['surveyType'] in survey_types:
                    member['survey_start_time'] = survey_start_time
                    output.append(member)
        return output

    def get_child_records(self):
        return self._get_records_for_survey_types(survey_types='child')

    def get_women_records(self):
        return self._get_records_for_survey_types(survey_types='women')

    def get_women_and_child_records(self):
        return self._get_records_for_survey_types(
            survey_types=('child', 'women')
        )

    @staticmethod
    def get_household_member_gender(household_member):
        if 'gender' in household_member:
            return household_member['gender']
        else:
            return None

    @staticmethod
    def get_household_members_age_in_years(household_member):
        """This function returns a recorded age in years as integer or None if
        no valid age was recorded.
        """
        if 'age' in household_member:
            try:
                age = int(household_member['age'])
            except ValueError:
                return None
            else:
                return age
        else:
            return None

    @staticmethod
    def get_childs_age_in_months(child):
        """This function tries to calculate the child's age in months based on
        their date of birth and the date when the survey was conducted.  If the
        recorded data does not allow that, the function tries to use the age in
        months recorded during the survey.

        N.B. The age in years is not used by this function as a fallback even
        if it was recorded by the surveying team.

        On success, it returns an integer representing the child's age in
        months.
        On failure, it returns None.
        """
        if 'survey' not in child:
            return None
        # Start by trying to calculate the child's age based on their date of
        # birth, if it has been recorder, as it has higher priority than the
        # recorder age in months.
        # On success, the following if-statement FINISHES the function execution
        # and returns a computed value.
        if 'birthDate' in child['survey']:
            dob = child['survey']['birthDate']
            # Try to get the survey start date to use it later for the child's
            # age computations.
            survey_start_time_string = child['survey_start_time']
            try:
                survey_date = dateutil.parser.parse(survey_start_time_string)
            except TypeError:
                # It is impossible to compute the age at the time without
                # knowing when the survey was conducted.
                survey_date = None
            else:
                # if it worked, get rid of the TZ information and time
                survey_date = survey_date.date()

            if survey_date is not None:
                try:
                    dob = dateutil.parser.parse(dob)
                except TypeError:
                    # It is impossible to compute the age at the time without
                    # knowing the person's date of birth.
                    dob = None
                else:
                    # if it worked, get rid of the TZ info and time
                    dob = dob.date()

            if isinstance(dob, datetime.date) and \
                    isinstance(survey_date, datetime.date):
                delta = dateutil.relativedelta.relativedelta(survey_date, dob)
                # return the computed age in months
                return delta.years * 12 + delta.months

        # The following lines should be executed only if the attempt to
        # calculate the child's age based on their date of birth (above) was
        # unsuccessful.
        if 'ageInMonths' not in child['survey']:
            return None

        try:
            age_in_months = int(child['survey']['ageInMonths'])
        except ValueError:
            return None

        return age_in_months

    def get_uuid(self):
        try:
            uuid = self.json['uuid']
        except KeyError:
            return None
        else:
            return uuid


class HouseholdSurveyJSON(BaseHouseholdSurveyJSON):
    team_lead = models.ForeignKey('TeamMember', related_name='%(class)s_as_team_lead')
    location = gismodels.PointField(null=True)

    def get_absolute_url(self):
        return reverse('householdsurveyjson-detail', args=[str(self.id)])


class Alert(models.Model):

    """
    New alerts are only created if there is no unarchived alert having the
    same content of the json field.  The user may still create alerts manually
    using the admin interface.
    """

    team_lead = models.ForeignKey('dashboard.TeamMember', null=True, on_delete=models.CASCADE)
    survey = models.ForeignKey('dashboard.HouseholdSurveyJSON', null=True, on_delete=models.CASCADE)
    text = models.TextField()

    json = JSONField(
        null=True, blank=True,
        help_text='A JSON document containing data for one alert.'
    )

    ALERT_CATEGORIES = (
        'general',
        'map',
        'sex',
        'age_distribution',
        'number_distribution',
        'timing',
        'missing_data',
    )

    category = models.CharField(
        max_length=255,
        default='general',
        choices=zip(ALERT_CATEGORIES, ALERT_CATEGORIES),
    )

    ALERT_TYPES = (
        'mapping_check_missing_cluster_id',
        'mapping_check_missing_location',
        'mapping_check_unknown_cluster',
        'mapping_check_wrong_location_first_admin_level',
        'mapping_check_wrong_location_second_admin_level',
        'sex_ratio',
        'child_age_in_months_ratio',
        'child_age_displacement',
        'woman_age_14_15_displacement',
        'woman_age_4549_5054_displacement',
        'digit_preference',
        'data_collection_time',
        'time_to_complete_single_survey',
        'daily_data_collection_duration',
    )

    alert_type = models.CharField(
        max_length=255,
        choices=zip(ALERT_TYPES, ALERT_TYPES),
    )

    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    completed = models.BooleanField(default=False)
    archived = models.BooleanField(default=False)

    def cluster_id(self):
        return self.json.get('cluster_id')

    def location(self):
        return self.json.get('location')

    def type(self):
        return self.alert_type

    def survey_id(self):
        return self.json.get('survey_id')

    def __unicode__(self):
        if self.archived:
            archived = u', archived'
        else:
            archived = u''
        return u'{} (alert #{}{})'.format(self.text, self.pk, archived)

    def get_absolute_url(self):
        return reverse('alert-detail', args=[str(self.id)])

    @classmethod
    def get_or_create_alert(cls, **values):

        # TODO yes, this still contains a race condition, we should really
        # think about how we can use .get_or_create here.

        filter_values = {'archived': False}
        filter_values.update(values)
        filter_values.pop('json')

        if not cls.objects.filter(**filter_values):
            cls.objects.create(**values)

    @classmethod
    def run_alert_checks_on_document(cls, household_survey):
        """This method runs all the defined alert checks which leads to
        relevant alerts being created in case they are triggered by data stored
        in household_survey.
        """

        alert_generators = [
            cls.mapping_check_missing_cluster,
            cls.mapping_check_missing_location,
            cls.mapping_check_unknown_cluster,
            cls.mapping_check_wrong_location_first_admin_level,
            cls.mapping_check_wrong_location_second_admin_level,
            cls.missing_data_alert,
            cls.sex_ratio_alert,
            cls.child_age_in_months_ratio_alert,
            cls.child_age_displacement_alert,
            cls.woman_age_14_15_displacement_alert,
            cls.woman_age_4549_5054_displacement_alert,
            cls.digit_preference_alert,
            cls.data_collection_time_alert,
        ]

        for fun in alert_generators:
            for alert in fun(household_survey):
                cls.get_or_create_alert(**alert)

    @classmethod
    def mapping_check_missing_cluster(cls, household_survey):
        """
        Generates alert if cluster is missing
        """

        if household_survey.get_cluster_id():
            return

        alert_text = 'No cluster ID for survey of team {} (survey {})'.format(
            household_survey.get_team_id(),
            household_survey.pk)

        alert_type = 'mapping_check_missing_cluster_id'

        alert_json = {
            'type': alert_type,
            'survey_id': household_survey.id,
            'location': [
                household_survey.location[0],
                household_survey.location[1],
            ],
        }

        yield dict(
            category='map',
            alert_type=alert_type,
            team_lead=household_survey.team_lead,
            survey=household_survey,
            text=alert_text,
            json=alert_json,
        )

    @classmethod
    def mapping_check_missing_location(cls, household_survey):
        """
        Generates alert if location is missing
        """

        if household_survey.get_location():
            return

        alert_text = 'No location for survey of team {} (survey {})'.format(
            household_survey.get_team_id(),
            household_survey.id)

        alert_type = 'mapping_check_missing_location'

        alert_json = {
            'type': alert_type,
            'team_name': household_survey.get_team_name(),
            'team_id': household_survey.get_team_id(),
            'survey_id': household_survey.id,
            'location': [
                household_survey.location[0],
                household_survey.location[1],
            ],
        }

        if household_survey.get_cluster_id():
            alert_json['cluster_id'] = household_survey.get_cluster_id()

        yield dict(
            category='map',
            alert_type=alert_type,
            team_lead=(household_survey.team_lead),
            text=alert_text,
            json=alert_json,
        )

    @classmethod
    def mapping_check_unknown_cluster(cls, household_survey):
        """
        Generates alert if cluster is given, but it's unknown to the server
        """

        if not (household_survey.get_cluster_id() and household_survey.get_location()):
            return

        # get cluster data
        cluster = Clusters.get_cluster_from_active(household_survey.get_cluster_id())

        # if cluster data not found, assume location incorrect
        if cluster:
            return

        alert_text = 'Unknown cluster ID {} for team {} (survey {})'.format(
            household_survey.get_cluster_id(),
            household_survey.get_team_id(),
            household_survey.id)

        alert_type = 'mapping_check_unknown_cluster',
        alert_json = {
            'type': alert_type,
            'team_name': household_survey.get_team_name(),
            'team_id': household_survey.get_team_id(),
            'cluster_id': household_survey.get_cluster_id(),
            'survey_id': household_survey.id,
            'location': [
                household_survey.location[0],
                household_survey.location[1],
            ],
        }

        yield dict(
            category='map',
            alert_type=alert_type,
            team_lead=(household_survey.team_lead),
            text=alert_text,
            json=alert_json,
        )

    @classmethod
    def mapping_check_wrong_location_first_admin_level(cls, household_survey):
        """
        cluster and location are given and known
        to the server, but the location is not inside the boundaries of the
        first admin level area that the data supposedly comes from.
        """

        cluster = Clusters.get_cluster_from_active(household_survey.cluster)

        # If no cluster has been found, assume database inconsistencies and abort
        if not cluster:
            return

        # if cluster data found, get first admin level
        ideal_first_admin_level_name = cluster.get('first_admin_level_name', None)

        # if first admin level names not found, assume database inconsistencies and abort
        if not ideal_first_admin_level_name:
            return

        second_admin_levels = SecondAdminLevel.objects.filter(mpoly__contains=household_survey.location)

        found = len(second_admin_levels)

        # The point was part of several second level admin areas, assume database insonsistencies and abort
        if found > 1:
            return
        elif found == 1:
            actual_first_admin_level_name = second_admin_levels[0].get_first_admin_level_name()

            # The name of the actual first level admin level and that of where it should be are the same, no alert needs to be created
            if actual_first_admin_level_name == ideal_first_admin_level_name:
                return

        alert_text = 'Wrong first admin level location for team {} (survey {})'.format(
            household_survey.get_team_id(),
            household_survey.id,
        )

        alert_type = 'mapping_check_wrong_location_first_admin_level'

        alert_json = {
            'type': alert_type,
            'team_name': household_survey.team_lead.last_name,
            'team_id': household_survey.team_lead.id,
            'location': [
                household_survey.location[0],
                household_survey.location[1],
            ]
        }

        yield dict(
            category='map',
            alert_type=alert_type,
            team_lead=household_survey.team_lead,
            survey=household_survey,
            text=alert_text,
            json=alert_json,
        )

    @classmethod
    def mapping_check_wrong_location_second_admin_level(cls, household_survey):
        """
        cluster and location are given and known
        to the server, but the location is not inside the boundaries of the
        second admin level area that the data supposedly comes from.
        """

        cluster = Clusters.get_cluster_from_active(household_survey.cluster)

        # If no cluster has been found, assume database inconsistencies and abort
        if not cluster:
            return

        # if cluster data found, get first and second admin level
        second_admin_level_name = cluster.get('second_admin_level_name', None)
        first_admin_level_name = cluster.get('first_admin_level_name', None)

        # if first and second admin level names not found, assume database inconsistencies and abort
        if not (first_admin_level_name and second_admin_level_name):
            return

        # if first and second admin level found, check the location
        second_admin_level = SecondAdminLevel.find_second_admin_level(
            name=second_admin_level_name, first_admin_level_name=first_admin_level_name)

        if second_admin_level is None:
            # if no second admin level found, assume database inconsistencies and abort
            return

        if second_admin_level.contains_location(household_survey.location):
            return

        alert_text = 'Wrong second admin level location for team {} (survey {})'.format(
            household_survey.get_team_id(),
            household_survey.id,
        )

        alert_type = 'mapping_check_wrong_location_second_admin_level'

        alert_json = {
            'type': alert_type,
            'team_name': household_survey.team_lead.last_name,
            'second_admin_level_name': second_admin_level_name,
            'first_admin_level_name': first_admin_level_name,
            'survey_id': household_survey.id,
            'location': [
                household_survey.location[0],
                household_survey.location[1],
            ]
        }

        yield dict(
            category='map',
            alert_type=alert_type,
            team_lead=(household_survey.team_lead),
            survey=household_survey,
            text=alert_text,
            json=alert_json,
        )

    @classmethod
    def missing_data_alert(cls, household_survey, test='missing-data'):
        """
        In the data we expect that any piece of data is entered in at least
        95% of cases. If a field has been left blank for more than 5% of women,
        children or household members, an alert is created.
        """

        existing_data = HouseholdMember.missing_data(
            HouseholdMember.objects.by_teamlead(household_survey.team_lead)
        )

        for member_type, data in existing_data.items():
            for field_name, field_data in data.items():

                if field_data['total'] == 0:
                    continue

                if float(field_data['existing']) / float(field_data['total']) < 0.95:
                    alert_text = 'Missing data issue on field {} for {} in team {}'.format(
                        field_name,
                        member_type,
                        household_survey.team_lead.pk
                    )
                    alert_type = 'missing_data'
                    alert_json = {
                        'type': 'missing_data',
                        'team_name': household_survey.team_lead.first_name,
                        'team_id': household_survey.team_lead.pk,
                        'member_type': member_type,
                        'field': field_name,
                    }

                    yield dict(
                        category='missing_data',
                        alert_type=alert_type,
                        team_lead=household_survey.team_lead,
                        survey=household_survey,
                        text=alert_text,
                        json=alert_json,
                    )

    @classmethod
    def sex_ratio_alert(cls, household_survey, test='chi-squared'):
        """In the data of children from 0-59 months of age, we expect to find
        an even number boys and girls. If chi-square of sex ratio < 0.001 then
        report an alert on dashboard "Sex-ratio issue in team NAME".
        This method implements both binomial two-tailed test and chi-square
        test.  The latter is the default (as per client's request).
        """

        surveys = household_survey.find_all_surveys_by_this_team()
        team_lead = household_survey.team_lead
        children = []

        for survey in surveys:
            children.extend(survey.get_child_records())

        boys = 0
        girls = 0
        for child in children:
            age = HouseholdSurveyJSON.get_childs_age_in_months(child)
            if age is None:
                continue
            elif age < 60:
                gender = HouseholdSurveyJSON.get_household_member_gender(child)
                if gender == 'M':
                    boys += 1
                elif gender == 'F':
                    girls += 1

        if boys + girls == 0:
            # Chi-square impossible to compute (expected value is 0 which would
            # cause division by zero) and binomial equals 1 so no alert
            # necessary.
            return

        if test == 'binomial':
            p = scipy.stats.binom_test([boys, girls], p=0.5)
        else:
            expected = (boys + girls) / 2.0
            chi2, p = scipy.stats.chisquare([boys, girls], [expected, expected])

        if p >= 0.001:
            return

        team_name = household_survey.get_team_name()

        team_id = household_survey.get_team_id()

        alert_text = 'Sex ratio issue in team {}'.format(team_id)
        alert_type = 'sex_ratio'

        alert_json = {
            'type': alert_type,
            'team_name': team_name,
            'team_id': team_id,
            'location': [
                household_survey.location[0],
                household_survey.location[1],
            ],
        }

        yield dict(
            category='sex',
            alert_type=alert_type,
            team_lead=team_lead,
            text=alert_text,
            json=alert_json,
        )

    @classmethod
    def child_age_in_months_ratio_alert(cls, household_survey,
                                        test='chi-squared'):
        """In the data of children from 6-59 months of age, we expect an age
        ratio of 6-29 months to 30-59 months to be around 0.85. If a chi-square
        test of the age ratio 6-29 months / 30-59 months is significantly
        < 0.001 from expected 0.85 then report an alert on dashboard "Age ratio
        issue in team NAME".
        This method implements both binomial two-tailed test and chi-square
        test.  The latter is the default (as per client's request).
        """

        surveys = household_survey.find_all_surveys_by_this_team()
        team_lead = household_survey.team_lead
        children = []

        for survey in surveys:
            children.extend(survey.get_child_records())

        age6to29 = 0
        age30to59 = 0
        for child in children:
            age = HouseholdSurveyJSON.get_childs_age_in_months(child)
            if age is None:
                continue
            elif 5 < age < 30:
                age6to29 += 1
            elif 29 < age < 60:
                age30to59 += 1

        # The theoretical probability of the 'positive' outcome (i.e. the
        # child being 6 to 29 months old).
        p629 = 0.45945945945945954
        # The theoretical probability of the 'negative' outcome (i.e. the
        # child being 30 to 59 months old).
        # p3059 = 1 - p629 = 0.5405405405405405

        if age6to29 + age30to59 == 0:
            # Chi-square impossible to compute (expected value is 0 which would
            # cause division by zero) and binomial equals 1 so no alert
            # necessary.
            return
        if test == 'binomial':
            p = scipy.stats.binom_test([age6to29, age30to59], p=p629)
        else:
            expected6to29 = (age6to29 + age30to59) * p629
            expected30to59 = (age6to29 + age30to59) - expected6to29
            chi2, p = scipy.stats.chisquare(
                [age6to29, age30to59],
                [expected6to29, expected30to59]
            )

        if p >= 0.001:
            return

        team_name = household_survey.get_team_name()

        team_id = household_survey.get_team_id()

        alert_text = 'Age ratio issue in team {}'.format(team_id)
        alert_type = 'child_age_in_months_ratio'

        alert_json = {
            'type': alert_type,
            'team_name': team_name,
            'team_id': team_id
        }

        yield dict(
            category='age_distribution',
            alert_type=alert_type,
            team_lead=team_lead,
            text=alert_text,
            json=alert_json,
        )

    @classmethod
    def child_age_displacement_alert(cls, household_survey, test='chi-squared'):
        """Ratio of children aged 5 years / children aged 4 years is expected
        to equal 1. If the chi-square of this ratio is significantly < 0.001
        from expected 1 then report an alert on dashboard "Child age
        displacement issue in team NAME".
        This method implements both binomial two-tailed test and chi-square
        test.  The latter is the default (as per client's request).
        """
        surveys = household_survey.find_all_surveys_by_this_team()
        team_lead = household_survey.team_lead
        children = []
        for survey in surveys:
            children.extend(survey.get_child_records())
        age4 = 0
        age5 = 0
        for child in children:
            age = HouseholdSurveyJSON.get_household_members_age_in_years(child)
            if age is None:
                continue
            elif age == 4:
                age4 += 1
            elif age == 5:
                age5 += 1

        if age4 + age5 == 0:
            # Chi-square impossible to compute (expected value is 0 which would
            # cause division by zero) and binomial equals 1 so no alert
            # necessary.
            return
        if test == 'binomial':
            p = scipy.stats.binom_test([age4, age5], p=0.5)
        else:
            expected = (age4 + age5) / 2.0
            chi2, p = scipy.stats.chisquare([age4, age5], [expected, expected])

        if p >= 0.001:
            return

        team_name = household_survey.get_team_name()
        team_id = household_survey.get_team_id()
        alert_text = 'Child age displacement issue in team {}'.format(team_id)

        alert_type = 'child_age_displacement'

        alert_json = {
            'type': alert_type,
            'team_name': team_name,
            'team_id': team_id,
            'location': [
                household_survey.location[0],
                household_survey.location[1],
            ],
        }

        yield dict(
            category='age_distribution',
            alert_type=alert_type,
            team_lead=team_lead,
            text=alert_text,
            json=alert_json,
        )

    @classmethod
    def woman_age_14_15_displacement_alert(
            cls, household_survey, test='chi-squared'):
        """Ratio of women aged 14 / women aged 15 is expected to equal 1. If
        the chi-square of this ratio is significantly < 0.001 from expected 1
        then report an alert on dashboard "Woman age displacement issue (14/15)
        in team NAME".
        This method implements both binomial two-tailed test and chi-square
        test.  The latter is the default (as per client's request).
        """
        surveys = household_survey.find_all_surveys_by_this_team()
        team_lead = household_survey.team_lead
        women = []
        for survey in surveys:
            women.extend(survey.get_women_records())
        age14 = 0
        age15 = 0
        for woman in women:
            age = HouseholdSurveyJSON.get_household_members_age_in_years(woman)
            if age is None:
                continue
            elif age == 14:
                age14 += 1
            elif age == 15:
                age15 += 1

        if age14 + age15 == 0:
            # Chi-square impossible to compute (expected value is 0 which would
            # cause division by zero) and binomial equals 1 so no alert
            # necessary.
            return
        if test == 'binomial':
            p = scipy.stats.binom_test([age14, age15], p=0.5)
        else:
            expected = (age14 + age15) / 2.0
            chi2, p = scipy.stats.chisquare(
                [age14, age15], [expected, expected])

        if p >= 0.001:
            return

        team_name = household_survey.get_team_name()
        team_id = household_survey.get_team_id()
        alert_text = \
            'Woman age displacement issue (14/15) in team {}'.format(team_id)

        alert_type = 'woman_age_14_15_displacement'

        alert_json = {
            'type': alert_type,
            'team_name': team_name,
            'team_id': team_id,
            'location': [
                household_survey.location[0],
                household_survey.location[1],
            ],
        }

        yield dict(
            category='age_distribution',
            alert_type=alert_type,
            team_lead=team_lead,
            text=alert_text,
            json=alert_json,
        )

    @classmethod
    def woman_age_4549_5054_displacement_alert(cls, household_survey,
                                               test='chi-squared'):
        """Ratio of women aged 45-49 / women aged 50-54 is expected to equal 1.
        If the chi-square of this ratio is significantly < 0.001 from expected
        1 then report an alert on dashboard "Woman age displacement issue
        (45-49/50-54) in team NAME".
        This method implements both binomial two-tailed test and chi-square
        test.  The latter is the default (as per client's request).
        """
        surveys = household_survey.find_all_surveys_by_this_team()
        team_lead = household_survey.team_lead
        women = []
        for survey in surveys:
            women.extend(survey.get_women_records())
        age4549 = 0
        age5054 = 0

        for woman in women:
            age = HouseholdSurveyJSON.get_household_members_age_in_years(woman)
            if age is None:
                continue
            elif 44 < age < 50:
                age4549 += 1
            elif 49 < age < 55:
                age5054 += 1

        if age4549 + age5054 == 0:
            # Chi-square impossible to compute (expected value is 0 which would
            # cause division by zero) and binomial equals 1 so no alert
            # necessary.
            return
        if test == 'binomial':
            p = scipy.stats.binom_test([age4549, age5054], p=0.5)
        else:
            expected = (age4549 + age5054) / 2.0
            chi2, p = scipy.stats.chisquare(
                [age4549, age5054], [expected, expected])

        if p >= 0.001:
            return

        team_name = household_survey.get_team_name()
        team_id = household_survey.get_team_id()
        alert_text = 'Woman age displacement issue (45-49/50-54) in team ' \
                     '{}'.format(team_id)

        alert_type = 'woman_age_4549_5054_displacement'
        alert_json = {
            'alert': alert_type,
            'team_id': team_id,
            'team_name': team_name,
            'location': [
                household_survey.location[0],
                household_survey.location[1],
            ],

        }

        yield dict(
            category='age_distribution',
            alert_type=alert_type,
            team_lead=team_lead,
            text=alert_text,
            json=alert_json,
        )

    @classmethod
    def digit_preference_alert(cls, household_survey):
        """If terminal digit preference score for weight, height or MUAC > 20,
        then report alert on dashboard "Digit preference issue in Team NAME".
        N.B. this function calculates and checks TDPS for each variable (i.e.
        weight, height and MUAC) independently.  If only one of the calculated
        terminal digit preferences scores satisfies the condition then the
        alert is triggered.
        """
        surveys = household_survey.find_all_surveys_by_this_team()
        team_lead = household_survey.team_lead
        data_points = {'muac': [], 'weight': [], 'height': []}
        for survey in surveys:
            subjects = survey.get_women_and_child_records()
            for subject in subjects:
                # If there is no survey section then there is no data for this
                # subject.
                if 'survey' not in subject:
                    continue
                # Add the subject's muac, weight and height to data_points.
                # Append None where the value is missing.
                for k in data_points:
                    data_points[k].append(subject['survey'].get(k, None))

        # Extract and count terminal digits for each variable of interest.
        terminal_digit_counts = {
            'muac': [0] * 10,
            'weight': [0] * 10,
            'height': [0] * 10
        }
        terminal_digit_preference_score = {
            'muac': 0,
            'weight': 0,
            'height': 0
        }
        for k in terminal_digit_counts:
            for v in data_points[k]:
                try:
                    v = float(v)
                except (TypeError, ValueError):
                    # Get rid of all None objects and other invalid values.
                    continue
                else:
                    terminal_digit = int(
                        ('{:.1f}'.format(float(int(v * 10) / 10.0)))[-1]
                    )
                    terminal_digit_counts[k][terminal_digit] += 1
        # Calculate terminal digit preference scores
        for k in terminal_digit_preference_score:
            total_number_of_digits = sum(terminal_digit_counts[k])
            if total_number_of_digits > 0:
                expected = total_number_of_digits / 10.0
                chi2 = sum(
                    [
                        (i - expected) ** 2 / expected
                        for i in terminal_digit_counts[k]
                    ]
                )
                terminal_digit_preference_score[k] =\
                    100 * (chi2 / (9 * total_number_of_digits)) ** 0.5

        # Check if any of the computed scores triggers the alert.
        for k in terminal_digit_preference_score:
            if terminal_digit_preference_score[k] > 20:
                team_name = household_survey.get_team_name()
                team_id = household_survey.get_team_id()
                alert_text = 'Digit preference issue in team {}'.format(team_id)

                alert_type = 'digit_preference'

                alert_json = {
                    'type': alert_type,
                    'team_id': team_id,
                    'team_name': team_name,
                    'location': [
                        household_survey.location[0],
                        household_survey.location[1],
                    ],
                }

                yield dict(
                    category='number_distribution',
                    alert_type=alert_type,
                    team_lead=team_lead,
                    text=alert_text,
                    json=alert_json,
                )

                # Only one alert should be emitted so no need to finish the
                # loop.
                break

    @classmethod
    def data_collection_time_alert(cls, household_survey):
        """If timestamp for any data point in data collection is < 06:00 AM
        or > 8:00 PM then report alert on dashboard "Data collection time
        issue in team NAME (survey: UUID)".
        If any of the time stamps is not a valid date, the alert is triggered
        too.
        N.B. This function performs these checks for both the start time and
        the end time.  The alert is triggered if any of them satisfies the
        condition mentioned above.
        """
        minimum_time = datetime.time(6)  # 6:00 AM
        maximum_time = datetime.time(20)  # 8:00 PM
        start = household_survey.get_start_time()
        end = household_survey.get_end_time()
        triggered = False

        for t in (start, end):
            if t is None:
                triggered = True
                break
            elif t.time() < minimum_time or t.time() > maximum_time:
                triggered = True
                break

        if not triggered:
            return

        team_name = household_survey.get_team_name()
        team_id = household_survey.get_team_id()
        team_lead = household_survey.team_lead
        alert_text = u'Data collection time issue in team {} (survey: {})'.\
            format(team_id, household_survey.id)

        alert_type = 'data_collection_time'
        alert_json = {
            'type': alert_type,
            'team_name': team_name,
            'team_id': team_id,
            'survey': household_survey.id,
            'location': [
                household_survey.location[0],
                household_survey.location[1],
            ],
        }

        yield dict(
            category='timing',
            alert_type=alert_type,
            survey=household_survey,
            team_lead=team_lead,
            text=alert_text,
            json=alert_json,
        )

    @classmethod
    def children_under_five_alerts(cls):
        """This method is meant to be run once a day (or every few days),
        typically after midnight.  It processes all household surveys and
        performs the following check (and emits the following alert if
        appropriate) for each detected team:

        If the mean number of children under age five for a team are 50% under
        the median median number of children under age five.
        """
        # Process all household surveys.
        number_children = []
        by_team = {}
        surveys = HouseholdSurveyJSON.objects.all()
        for survey in surveys:
            children_in_survey = len(survey.get_child_records())
            number_children.append(children_in_survey)
            team_id = survey.get_team_id()
            if team_id is None:
                continue
            if team_id not in by_team:
                by_team[team_id] = {
                    'team_lead': survey.team_lead,
                    'team_name': survey.get_team_name(),
                    'number_children': []
                }
            by_team[team_id]['number_children'].append(children_in_survey)

        median_children = numpy.median(number_children)

        for team_id, team_info in by_team.iteritems():
            mean_children = numpy.mean(team_info['number_children'])
            if mean_children < (median_children / 2):
                alert_text = u'Child under 5 number issue in team {}'.\
                    format(team_id)
                alert_json = {
                    'type': 'children_under_five',
                    'team_id': team_id,
                    'team_name': team_info['team_name'],
                }

                yield dict(
                    team_lead=by_team[team_id]['team_lead'],
                    text=alert_text,
                    json=alert_json,
                    category='age_distribution'
                )

    @classmethod
    def time_to_complete_single_survey_alerts(cls):
        """This method is meant to be run once a day (or every few days),
        typically after midnight.  It processes all household surveys and
        performs the following check (and emits the following alert if
        appropriate) for each detected team and each day since the beginning to
        the day (inclusive) before the method is run:

        If daily average of time in minutes to complete HH interview by team
        <50% of survey median, create alert "Time to complete household survey
        issue in team NAME on day DATE-IN-ISO-FORMAT"

        N.B. The alert is not emitted if identical (team, date) alert already
        present.

        N.B. In case the start and end time for the survey indicate different
        days, it is the end time which allocates the survey to a particular day.

        N.B. Per Robert's request (https://sprint.ly/product/17761/item/161),
        the median is calculated using all available surveys (i.e. including
        the surveys from the day when the method is run).
        """
        # Get the current date to make sure that only earlier surveys are
        # included.
        today = datetime.date.today()
        # Prepare storage for intermediate data.
        by_team = {}
        survey_durations = []

        # Process all household surveys.
        surveys = HouseholdSurveyJSON.objects.all()
        for survey in surveys:
            duration = survey.get_survey_duration()
            # Check if it is possible to include this data point (duration must
            # be a number).
            if not isinstance(duration, (int, float)):
                continue
            # Store duration for median calculations.
            survey_durations.append(duration)

            team_id = survey.get_team_id()
            team_name = survey.get_team_name()
            team_lead = survey.team_lead
            # If no valid team id, the duration can only be used to calculate
            # the median.
            if team_id is None:
                continue
            # At this point we know that the survey contained a valid end time
            # so no need to check that.  Get the date.
            collection_date = survey.get_end_time().date()
            # If collection date earlier than today, store the data for further
            # processing.
            if collection_date < today:
                if team_id not in by_team:
                    by_team[team_id] = {
                        'team_name': team_name,
                        'team_lead': team_lead
                    }
                if collection_date not in by_team[team_id]:
                    by_team[team_id][collection_date] = {
                        'average': duration,
                        'n': 1,
                    }
                else:
                    n = by_team[team_id][collection_date]['n'] + 1.0
                    old = by_team[team_id][collection_date]['average']
                    new = (n - 1) / n * old + 1 / n * duration
                    by_team[team_id][collection_date]['n'] = n
                    by_team[team_id][collection_date]['average'] = new

        # Calculate the value to check the averages against (50% of median).
        half_median = numpy.median(survey_durations) / 2.0

        # Process all data collected above and produce alerts when triggered.
        for team_id in by_team:
            for day in by_team[team_id]:
                if by_team[team_id][day]['average'] < half_median:
                    alert_text = u'Time to complete household survey issue ' \
                                 u'in team {} ' \
                                 u'on day {}'.format(team_id, day.isoformat())

                    alert_type = 'time_to_complete_single_survey'

                    alert_json = {
                        'type': alert_type,
                        'team_id': team_id,
                        'team_name': by_team[team_id]['team_name'],
                        'day': day.isoformat(),
                    }

                    yield dict(
                        category='timing',
                        alert_type=alert_type,
                        team_lead=by_team[team_id]['team_lead'],
                        text=alert_text,
                        json=alert_json,
                    )

    @classmethod
    def daily_data_collection_duration_alerts(cls):
        """This method is meant to be run once a day (or every few days),
        typically after midnight.  It processes all household surveys and
        performs the following check (and emits the following alert if
        appropriate) for each detected team and each day since the beginning to
        the day (inclusive) before the method is run:

        If daily average of hours to complete daily data collection by team
        <50% of survey median, create alert "Duration of data collection issue
        in team NAME"

        Invalid data points are ignored:
            - cases when the start and end time for the survey indicate
              different days
            - both start and end time missing or invalid
            - the end precedes the start

        N.B. The alert is not emitted if identical (team, date) alert already
        present.
        """
        # Get the current date to make sure that only earlier surveys are
        # included.
        today = datetime.date.today()
        # Prepare storage for intermediate data.
        by_team = {}

        # Process all household surveys.
        surveys = HouseholdSurveyJSON.objects.all()
        for survey in surveys:
            team_id = survey.get_team_id()
            team_name = survey.get_team_name()
            # If no valid team id then this data point cannot be used.
            if team_id is None:
                continue
            start = survey.get_start_time()
            end = survey.get_end_time()
            # Ignore invalid data points.
            if start is not None and end is not None:
                if start.date() != end.date():
                    continue
                elif start > end:
                    continue
            if start is None and end is None:
                continue
            # At this point at least one time is not None and in case both are
            # valid time stamps then both are set to the same day.

            # Get the collection date.
            if start is not None:
                day = start.date()
            else:
                day = end.date()

            # If collection date earlier than today, store the data for further
            # processing.  Otherwise, ignore.
            if day >= today:
                continue

            if team_id not in by_team:
                # Previously unseen team detected.  Initialise storage.
                by_team[team_id] = {
                    'team_name': team_name,
                    'team_lead': survey.team_lead,
                }
            if day not in by_team[team_id]:
                # Previously unseen day detected.  Initialise data for this day
                # with the current values of start and end (possible Nones).
                by_team[team_id][day] = {
                    'start': start,
                    'end': end,
                }
            # A different survey for the same day has been previously processed.
            else:
                # Detect the earliest start time for a given day.
                if not (by_team[team_id][day]['start'] is None or start is None):
                    if start < by_team[team_id][day]['start']:
                        by_team[team_id][day]['start'] = start
                elif start is not None:
                    by_team[team_id][day]['start'] = start
                # Detect the latest end time for a given day.
                if not (by_team[team_id][day]['end'] is None or end is None):
                    if end > by_team[team_id][day]['end']:
                        by_team[team_id][day]['end'] = end
                elif end is not None:
                    by_team[team_id][day]['end'] = end

        # Delete invalid data points and create a vector of all durations to
        # calculate the median.
        durations = []
        for team_id in by_team.keys():
            team_durations = []
            for day in by_team[team_id].keys():
                start = by_team[team_id][day]['start']
                end = by_team[team_id][day]['end']
                # Delete invalid dates.
                if start is None or end is None:
                    del by_team[team_id][day]
                    continue
                elif start > end:
                    del by_team[team_id][day]
                    continue
                # Compute and store durations.
                delta = end - start
                duration = delta.total_seconds()
                team_durations.append(duration)
                # Delete the processed data for this day.  No longer needed.
                del by_team[team_id][day]

            # Delete the team if no valid data points available and proceed to
            # the next.
            if len(team_durations) < 1:
                del by_team[team_id]
                continue

            # Update the durations vector with the just processed team data.
            durations.extend(team_durations)

            # Compute the daily average for the team.
            by_team[team_id]['daily average'] = numpy.average(team_durations)
        # Stop here if no valid data points found (nothing to check and the
        # median would be NaN).
        if len(durations) < 1:
            return
        # Calculate the value to check the averages against (50% of median).
        half_median = numpy.median(durations) / 2.0

        # Process all data collected above and produce alerts when triggered.
        for team_id in by_team:
            if by_team[team_id]['daily average'] < half_median:
                alert_text = u'Duration of data collection issue ' \
                             u'in team {}'.format(team_id)

                alert_type = 'daily_data_collection_duration'

                alert_json = {
                    'type': alert_type,
                    'team_id': team_id,
                    'team_name': by_team[team_id]['team_name'],
                }

                yield dict(
                    category='timing',
                    alert_type=alert_type,
                    team_lead=by_team[team_id]['team_name'],
                    text=alert_text,
                    json=alert_json,
                )

    @classmethod
    def archive_all_alerts(cls):
        """This method marks all existing alerts as archived.
        """
        cls.objects.filter(archived=False).update(archived=True)

    @classmethod
    def delete_alerts_by_text(cls, text, archived=False):
        """This method tries to find alerts having the same content as given by
        text and delete them.
        """
        cls.objects.filter(text=text, archived=archived).delete()


class UniqueActiveDocument(models.Model):
    active = UniqueActiveField(
        default=False,
        help_text=u'Activate this document.  Only one document of this type '
                  u'may be active at any given time.')
    created = models.DateTimeField(auto_now_add=True, null=True)
    last_modified = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        abstract = True

    @classmethod
    def get_active(cls):
        active_instances = cls.objects.filter(active__exact=True)
        c = active_instances.count()
        if c == 1:
            return active_instances[0]
        elif c == 0:
            return None
        else:
            raise RuntimeError(
                u'More than one active "{}" found.  This should not happen.  '
                u'Please check the database.'.format(cls._meta.verbose_name))

    @classmethod
    def get_most_recently_created(cls):
        instances = cls.objects.all().order_by('-created')
        if instances:
            return instances[0]
        else:
            return None

    @classmethod
    def get_most_recently_modified(cls):
        instances = cls.objects.all().order_by('-last_modified')
        if instances:
            return instances[0]
        else:
            return None


class UniqueActiveNamedDocument(UniqueActiveDocument):
    name_or_id = models.CharField(
        max_length=255, unique=True, blank=False, default=uuid.uuid1,
        help_text=u'Please enter a unique name or id of your new document.')

    def __unicode__(self):
        return self.name_or_id

    class Meta:
        abstract = True


class Clusters(UniqueActiveNamedDocument):

    """A JSON document containing information about clusters in the format
    shown below:
    {
            "723": {
                "cluster_name": "Share",
                "second_admin_level_name": "Ifelodun",
                "first_admin_level_name": "Kwara"
            },
            "318": {
                "cluster_name": "Emadadja",
                "second_admin_level_name": "Udu",
                "first_admin_level_name": "Delta"
            }
            ...
    }
    """

    def __unicode__(self):
        return self.name_or_id

    json = JSONField(
        null=True, blank=True,
        help_text=u'Please enter the JSON structure describing all the '
                  u'clusters for the planned survey.',
        default={}
    )

    @classmethod
    def get_cluster_from_active(cls, cluster_id):
        clusters = cls.get_active()
        if clusters:
            return clusters.get_cluster(cluster_id)
        else:
            return None

    def get_cluster(self, cluster_id):
        cluster = None
        # The cluster JSON data provided stores cluster_ids as strings and some
        # other parts of the system use integers for that.
        cluster_id = str(cluster_id)
        if cluster_id in self.json:
            cluster = self.json[cluster_id]
        return cluster


class Area(gismodels.Model):

    """Written for a geospatial data set containing the following fields:
    name_0 - country (top level)
    name_1 - 1st Admin (middle level, contained in area name_0)
    name_2 - 2nd Admin (subarea of name_1)
    varname_2 - an alternative name for area name_2 (optional, can be empty)
    """
    # Attributes of interest from the shapefile.
    name_0 = gismodels.CharField(
        max_length=255,
        help_text='The area two levels higher than this one (i.e. the area '
                  'containing the area which contains this area (e.g. the name '
                  'of a country))'
    )
    name_1 = gismodels.CharField(
        max_length=255,
        help_text='The area one level higher than this one (i.e. the area '
                  'containing this area (e.g. the name of a 1st Admin))'
    )
    name_2 = gismodels.CharField(
        max_length=255,
        help_text='The name of this area (e.g. the name of an 2nd Admin))'
    )
    varname_2 = gismodels.CharField(
        max_length=255, blank=True,
        help_text='Alternative name for this area (optional, can be left blank)'
    )
    # A GeoDjango-specific geometry field.
    mpoly = gismodels.MultiPolygonField(
        help_text='A multi-polygon field defining boundaries of this area'
    )
    # Override the model's default manager to enable spatial queries.
    objects = gismodels.GeoManager()

    def contains_location(self, location):
        """Returns True if location (longitude, latitude) lies within this area.
        Otherwise, it returns False.  Assumes that the location argument uses
        the same srid as the area.
        """
        longitude = float(location[0])
        latitude = float(location[1])
        point = Point(longitude, latitude, srid=self.mpoly.srid)
        output = self.mpoly.contains(point)
        return output

    def __unicode__(self):
        if self.varname_2:
            aka = u' (a.k.a. {})'.format(self.varname_2)
        else:
            aka = u''
        return u'{}/{}/{}{}'.format(self.name_0, self.name_1, self.name_2, aka)


class SecondAdminLevel(Area):

    def get_second_admin_level_name(self):
        return self.name_2

    def get_second_admin_level_alternative_name(self):
        return self.varname_2

    def get_second_admin_level_names(self):
        return [self.get_second_admin_level_name(), self.get_second_admin_level_alternative_name()]

    def get_first_admin_level_name(self):
        return self.name_1

    def get_country_name(self):
        return self.name_0

    @classmethod
    def find_second_admin_level(cls, name, first_admin_level_name, country_name=None):
        if country_name:
            query = {'name_0': country_name, 'name_1': first_admin_level_name}
        else:
            query = {'name_1': first_admin_level_name}
        found = 0
        query_result = []
        for second_admin_level_name_field in ('name_2', 'varname_2'):
            query[second_admin_level_name_field] = name
            query_result = cls.objects.filter(**query)
            found = query_result.count()
            if found == 0:
                del query[second_admin_level_name_field]
            else:
                break
        if found == 0:
            return None
        elif found == 1:
            return query_result[0]
        else:
            if country_name:
                country_part = u' and country "{}"'.format(country_name)
            else:
                country_part = u''
            raise RuntimeError(u'More than one 2nd Admin named "{}" in 1st Admin "{}"{} '
                               u'found!'.format(name, first_admin_level_name, country_part))


class QuestionnaireSpecification(UniqueActiveNamedDocument):

    specification = models.TextField(
        blank=False,
        help_text=u'Please enter or copy & paste your new questionnaire '
                  u'specification written in the QSL (Questionnaire '
                  u'Specification Language). <br />'
                  u'Please pay particular attention to indentation as '
                  u'indentation levels are part of the QSL and incorrect '
                  u'indentation will most likely produce nonsensical '
                  u'specification.<br />'
                  u'To familiarise yourself with the version of QSL used here '
                  u'please read <a href="/static/qsl.html" target="_blank">'
                  u'this document</a>.')

    def __unicode__(self):
        return self.name_or_id


class ClustersPerFirstAdminLevel(UniqueActiveNamedDocument):

    """
    For example:

    {
            "Kano": {
                "standard": 5,
                "reserve": 3
                },
            "Lagos": {
                "standard": 7,
                "reserve": 3
                },
            "Kaduna": {
                "standard": 15,
                "reserve": 3
                },
            "Katsina": {
                "standard": 15,
                "reserve": 3
                },
            "Oyo": {
                "standard": 8,
                "reserve": 3
                },
            "Rivers": {
                "standard": 6,
                "reserve": 3
                },
            "Bauchi": {
                "standard": 3,
                "reserve": 3
                },
            "Jigawa": {
                "standard": 8,
                "reserve": 3
                },
            "Benue": {
                "standard": 9,
                "reserve": 3
                },
            "Anambra": {
                "standard": 10,
                "reserve": 3
                },
            "Borno": {
                "standard": 11,
                "reserve": 3
                },
            "Delta": {
                "standard": 12,
                "reserve": 3
                },
            "Imo": {
                "standard": 13,
                "reserve": 3
                },
            "Niger": {
                "standard": 14,
                "reserve": 3
                },
            "Akwa Ibom": {
                "standard": 11,
                "reserve": 3
                },
            "Ogun": {
                "standard": 10,
                "reserve": 3
                },
            "Sokoto": {
                "standard": 3,
                "reserve": 3
                },
            "Ondo": {
                "standard": 20,
                "reserve": 3
                },
            "Osun": {
                "standard": 1,
                "reserve": 3
                },
            "Kogi": {
                "standard": 7,
                "reserve": 3
                },
            "Zamfara": {
                "standard": 6,
                "reserve": 3
                },
            "Enugu": {
                "standard": 8,
                "reserve": 3
                },
            "Kebbi": {
                "standard": 9,
                "reserve": 3
                },
            "Edo": {
                "standard": 7,
                "reserve": 2
                },
            "Plateau": {
                "standard": 10,
                "reserve": 4
                },
            "Adamawa": {
                "standard": 15,
                "reserve": 3
                },
            "Cross River": {
                "standard": 15,
                "reserve": 3
                },
            "Abia": {
                "standard": 15,
                "reserve": 3
                },
            "Ekiti": {
                "standard": 12,
                "reserve": 5
                },
            "Kwara": {
                "standard": 15,
                "reserve": 6
                },
            "Gombe": {
                "standard": 7,
                "reserve": 3
                },
            "Yobe": {
                "standard": 8,
                "reserve": 3
                },
            "Taraba": {
                "standard": 15,
                "reserve": 3
                },
            "Ebonyi": {
                "standard": 12,
                "reserve": 3
                },
            "Nasarawa": {
                "standard": 13,
                "reserve": 3
                },
            "Bayelsa": {
                "standard": 14,
                "reserve": 3
                },
            "Abuja Federal Capital Territory": {
                "standard": 30,
                "reserve": 3
                }
    }
    """

    json = JSONField(
        null=True, blank=True,
        help_text=u'Please enter the JSON structure defining the number of '
                  u'standard and reserve clusters per 1st Admin.  E.g.: { "first_admin_levels":'
                  u' { "Kano": { "standard": 5, "reserve": 3 }, "Lagos": { '
                  u'"standard": 7, "reserve": 3 } } }',
        default={}
    )


class FirstAdminLevels(UniqueActiveNamedDocument):

    """
        For example:

        [
            "Kano", "Lagos", "Kaduna",
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
    """

    json = JSONField(
        null=True, blank=True,
        help_text=u'Please enter the JSON structure defining the 1st Admin area data.',
        default=[]
    )


class FirstAdminLevelsReserveClusters(UniqueActiveNamedDocument):

    """
        For example:

        [
            "Kano",
            "Gombe",
            "Yobe",
            "Abuja Federal Capital Territory"
        ]
    """

    json = JSONField(
        null=True, blank=True,
        help_text=u'Please enter the JSON structure describing the 1st Admin with '
                  u'reserve clusters enabled.',
        default=[]
    )
