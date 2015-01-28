import datetime
import dateutil.parser
import dateutil.relativedelta

import scipy.stats

from django.db import models
from django.core.validators import MinValueValidator

import django.contrib.gis.db.models as gismodels
from django.contrib.gis.geos import Point

from jsonfield import JSONField
from jsonschema import validate, ValidationError

from fields import MaxOneActiveQuestionnaireField
from fields import UniqueActiveField


class JSONDocument(models.Model):
    class Meta:
        verbose_name_plural = 'JSON documents'

    # Set help_text to something else than empty but still invisible so that
    # the JSONField does not set it to its custom default (we want nothing
    # displayed).
    json = JSONField(null=True, blank=True, help_text=' ')

    def __unicode__(self):
        # Try to build a name describing a survey.
        if 'householdID' in self.json:
            household = self.json['householdID']
        else:
            household = None
        if 'cluster' in self.json:
            cluster = self.json['cluster']
        else:
            cluster = None
        if 'startTime' in self.json:
            start_time = self.json['startTime']
        else:
            start_time = None
        team_name = self.get_team_name()

        return u'cluster: {}; household: {}; team: {}; start time: {}'.format(
            cluster, household, team_name, start_time
        )

    def guess_type(self, list_of_json_document_types):
        """Matches the stored JSON document with the document types provided
        using list_of_json_document_types.  The order of the JSONDocumentType
        objects determines their priority as the method stops as soon as the
        first match is found.

        :param list_of_json_document_types:
        :return: the matched JSONDocumentType or None if no match found
        """
        for json_document_type in list_of_json_document_types:
            if json_document_type.matches(self):
                return json_document_type
        return None

    @classmethod
    def find_all_surveys_by_team(cls, team_id):
        """This method finds all instances of JSONDocument which can be
        associated with team given by team_id.  If team_id is None, the method
        finds those where team_id is None (unlikely) or where the JSON document
        does not contain an object named 'team' containing another object named
        'team_id' (useful to find filter out documents non conforming with the
        survey data structure specification).
        """
        docs = cls.objects.all()
        output = []
        for doc in docs:
            tid = doc.get_team_id()
            if tid == team_id:
                output.append(doc)
        return output

    def find_all_surveys_by_this_team(self):
        """This method finds all instances of JSONDocument which were created
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
            team_id = self.json['team']['teamID']
        except KeyError:
            return None
        else:
            return team_id

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

    def _get_records_for_survey_type(self, survey_type):
        output = []
        if 'members' in self.json:
            # Get the survey date to calculate age based on date of birth.
            if 'startTime' in self.json:
                survey_start_time = self.json['startTime']
            else:
                survey_start_time = None
            for member in self.json['members']:
                if member['surveyType'] == survey_type:
                    member['survey_start_time'] = survey_start_time
                    output.append(member)
        return output

    def get_child_records(self):
        return self._get_records_for_survey_type(survey_type='child')

    def get_women_records(self):
        return self._get_records_for_survey_type(survey_type='women')

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
        # Start by trying to calculate the child's age based on their date of
        # birth, if it has been recorder, as it has higher priority than the
        # recorder age in months.
        dob = child['survey']['birthDate']
        # On success, the following if-statement FINISHES the function execution
        # and returns a computed value.
        if dob:
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
            else:
                dob = None  # something must have gone wrong

        # The following lines should be executed only if the attempt to
        # calculate the child's age based on their date of birth (above) was
        # unsuccessful.
        if dob is None:
            try:
                age_in_months = int(child['survey']['ageInMonths'])
            except ValueError:
                return None
            else:
                return age_in_months


class JSONDocumentType(models.Model):
    class Meta:
        verbose_name_plural = 'JSON document types'

    name = models.CharField(max_length=255)
    schema = JSONField(null=True, blank=True, help_text=' ')
    priority = models.IntegerField(unique=True, blank=True, null=True,
                                   default=10,
                                   validators=[MinValueValidator(0)],
                                   help_text='Leave empty for the lowest '
                                             'priority'
                                   )

    def matches(self, json_document):
        try:
            validate(json_document.json, self.schema)
        except ValidationError:
            matches = False
        else:
            matches = True
        return matches

    @staticmethod
    def get_all_by_priority():
        return JSONDocumentType.objects.all().order_by('priority')

    def __unicode__(self):
        return self.name


class Alert(models.Model):
    """New alerts are only created if there is no unarchived alert having the
    same content of the text field.  The user may still create alerts manually
    using the admin interface.
    """
    text = models.TextField()
    archived = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        if self.archived:
            archived = u', archived'
        else:
            archived = u''
        return u'{} (alert #{}{})'.format(self.text, self.pk, archived)

    @classmethod
    def run_alert_checks_on_document(cls, json_document):
        """This method runs all the defined alert checks which leads to
        relevant alerts being created in case they are triggered by data stored
        in json_document.
        """
        cls.sex_ratio_alert(json_document)
        cls.child_age_in_months_ratio_alert(json_document)
        cls.child_age_displacement_alert(json_document)
        cls.woman_age_14_15_displacement_alert(json_document)
        cls.woman_age_4549_5054_displacement_alert(json_document)

    @classmethod
    def sex_ratio_alert(cls, json_document, test='binomial'):
        """In the data of children from 0-59 months of age, we expect to find
        an even number boys and girls. If chi-square of sex ratio < 0.001 then
        report an alert on dashboard "Sex-ratio issue in team NAME".
        N.B. This method uses binomial two-tailed test by default.  Chi-square
        test is used only if argument test is not set to 'binomial'.
        """
        surveys = json_document.find_all_surveys_by_this_team()
        children = []
        for survey in surveys:
            children.extend(survey.get_child_records())
        boys = 0
        girls = 0
        for child in children:
            age = JSONDocument.get_childs_age_in_months(child)
            if age is None:
                continue
            elif age < 60:
                gender = JSONDocument.get_household_member_gender(child)
                if gender == 'M':
                    boys += 1
                elif gender == 'F':
                    girls += 1
        if test == 'binomial':
            p = scipy.stats.binom_test([boys, girls], p=0.5)
        else:
            expected = (boys + girls) / 2.0
            chi2, p = scipy.stats.chisquare([boys, girls], [expected, expected])
        if p < 0.001:
            team = json_document.get_team_name()
            alert_text = 'Sex-ratio issue in team {}'.format(team)
            # Only add if there is no same alert among unarchived.
            if not Alert.objects.filter(text=alert_text, archived=False):
                Alert.objects.create(text=alert_text)

    @classmethod
    def child_age_in_months_ratio_alert(cls, json_document, test='binomial'):
        """In the data of children from 6-59 months of age, we expect an age
        ratio of 6-29 months to 30-59 months to be around 0.85. If a chi-square
        test of the age ratio 6-29 months / 30-59 months is significantly
        < 0.001 from expected 0.85 then report an alert on dashboard "Age ratio
        issue in team NAME".
        N.B. This method uses binomial two-tailed test by default.  Chi-square
        test is used only if argument test is not set to 'binomial'.
        """
        surveys = json_document.find_all_surveys_by_this_team()
        children = []
        for survey in surveys:
            children.extend(survey.get_child_records())
        age6to29 = 0
        age30to59 = 0
        for child in children:
            age = JSONDocument.get_childs_age_in_months(child)
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

        if test == 'binomial':
            p = scipy.stats.binom_test([age6to29, age30to59], p=p629)
        else:
            expected6to29 = (age6to29 + age30to59) * p629
            expected30to59 = (age6to29 + age30to59) - expected6to29
            chi2, p = scipy.stats.chisquare(
                [age6to29, age30to59],
                [expected6to29, expected30to59]
            )
        if p < 0.001:
            team = json_document.get_team_name()
            alert_text = 'Age ratio issue in team {}'.format(team)
            # Only add if there is no same alert among unarchived.
            if not Alert.objects.filter(text=alert_text, archived=False):
                Alert.objects.create(text=alert_text)

    @classmethod
    def child_age_displacement_alert(cls, json_document, test='binomial'):
        """Ratio of children aged 5 years / children aged 4 years is expected
        to equal 1. If the chi-square of this ratio is significantly < 0.001
        from expected 1 then report an alert on dashboard "Child age
        displacement issue in team NAME".
        N.B. This method uses binomial two-tailed test by default.  Chi-square
        test is used only if argument test is not set to 'binomial'.
        """
        surveys = json_document.find_all_surveys_by_this_team()
        children = []
        for survey in surveys:
            children.extend(survey.get_child_records())
        age4 = 0
        age5 = 0
        for child in children:
            age = JSONDocument.get_household_members_age_in_years(child)
            if age is None:
                continue
            elif age == 4:
                age4 += 1
            elif age == 5:
                age5 += 1

        if test == 'binomial':
            p = scipy.stats.binom_test([age4, age5], p=0.5)
        else:
            expected = (age4 + age5) / 2.0
            chi2, p = scipy.stats.chisquare([age4, age5], [expected, expected])
        if p < 0.001:
            team = json_document.get_team_name()
            alert_text = 'Child age displacement issue in team {}'.format(team)
            # Only add if there is no same alert among unarchived.
            if not Alert.objects.filter(text=alert_text, archived=False):
                Alert.objects.create(text=alert_text)

    @classmethod
    def woman_age_14_15_displacement_alert(cls, json_document, test='binomial'):
        """Ratio of women aged 14 / women aged 15 is expected to equal 1. If
        the chi-square of this ratio is significantly < 0.001 from expected 1
        then report an alert on dashboard "Woman age displacement issue (14/15)
        in team NAME".
        N.B. This method uses binomial two-tailed test by default.  Chi-square
        test is used only if argument test is not set to 'binomial'.
        """
        surveys = json_document.find_all_surveys_by_this_team()
        women = []
        for survey in surveys:
            women.extend(survey.get_women_records())
        age14 = 0
        age15 = 0
        for woman in women:
            age = JSONDocument.get_household_members_age_in_years(woman)
            if age is None:
                continue
            elif age == 14:
                age14 += 1
            elif age == 15:
                age15 += 1

        if test == 'binomial':
            p = scipy.stats.binom_test([age14, age15], p=0.5)
        else:
            expected = (age14 + age15) / 2.0
            chi2, p = scipy.stats.chisquare(
                [age14, age15], [expected, expected])
        if p < 0.001:
            team = json_document.get_team_name()
            alert_text = \
                'Woman age displacement issue (14/15) in team {}'.format(team)
            # Only add if there is no same alert among unarchived.
            if not Alert.objects.filter(text=alert_text, archived=False):
                Alert.objects.create(text=alert_text)

    @classmethod
    def woman_age_4549_5054_displacement_alert(cls, json_document,
                                               test='binomial'):
        """Ratio of women aged 45-49 / women aged 50-54 is expected to equal 1.
        If the chi-square of this ratio is significantly < 0.001 from expected
        1 then report an alert on dashboard "Woman age displacement issue
        (45-49/50-54) in team NAME".
        N.B. This method uses binomial two-tailed test by default.  Chi-square
        test is used only if argument test is not set to 'binomial'.
        """
        surveys = json_document.find_all_surveys_by_this_team()
        women = []
        for survey in surveys:
            women.extend(survey.get_women_records())
        age4549 = 0
        age5054 = 0
        for woman in women:
            age = JSONDocument.get_household_members_age_in_years(woman)
            if age is None:
                continue
            elif 44 < age < 50:
                age4549 += 1
            elif 49 < age < 55:
                age5054 += 1

        if test == 'binomial':
            p = scipy.stats.binom_test([age4549, age5054], p=0.5)
        else:
            expected = (age4549 + age5054) / 2.0
            chi2, p = scipy.stats.chisquare(
                [age4549, age5054], [expected, expected])
        if p < 0.001:
            team = json_document.get_team_name()
            alert_text = 'Woman age displacement issue (45-49/50-54) in team ' \
                         '{}'.format(team)
            # Only add if there is no same alert among unarchived.
            if not Alert.objects.filter(text=alert_text, archived=False):
                Alert.objects.create(text=alert_text)

    @classmethod
    def delete_alerts_by_text(cls, text, archived=False):
        """This method tries to find alerts having the same content as given by
        text and delete them.
        """
        cls.objects.filter(text=text, archived=archived).delete()


class ClustersJSON(models.Model):
    """A JSON document containing information about clusters in the format
    requested by Johannes and shown below:
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
    class Meta:
        verbose_name_plural = 'The "Clusters" JSON documents'

    json = JSONField(
        null=True, blank=True,
        help_text=u'Please enter the JSON structure describing all the '
                  u'clusters for the planned survey.',
        default="""
        For example:

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
            }
        }
        """
        )
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'JSON Data for Clusters (pk: {}; created: {}; last modified: ' \
               u'{})'.format(self.pk, self.created, self.last_modified)

    @classmethod
    def get_most_recently_created(cls):
        clusters = cls.objects.order_by('-created')
        if clusters:
            return clusters[0]
        else:
            return None

    @classmethod
    def get_most_recently_modified(cls):
        clusters = cls.objects.order_by('-last_modified')
        if clusters:
            return clusters[0]
        else:
            return None

    @classmethod
    def get_cluster_from_most_recently_modified(cls, cluster_id):
        clusters = cls.get_most_recently_modified()
        if clusters:
            return clusters.get_cluster(cluster_id)
        else:
            return None

    @classmethod
    def get_cluster_from_most_recently_created(cls, cluster_id):
        clusters = cls.get_most_recently_created()
        if clusters:
            return clusters.get_cluster(cluster_id)
        else:
            return None

    def get_cluster(self, cluster_id):
        cluster = None
        # The cluster JSON data provided stores cluster_ids as strings and some
        # other parts of the system use integers for that.
        cluster_id = str(cluster_id)
        if 'clusters' in self.json:
            if cluster_id in self.json['clusters']:
                cluster = self.json['clusters'][cluster_id]
        return cluster


class Area(gismodels.Model):
    """Written for a geospatial data set containing the following fields:
    name_0 - country (top level)
    name_1 - state (middle level, contained in area name_0)
    name_2 - LGA (subarea of name_1)
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
                  'containing this area (e.g. the name of a state))'
    )
    name_2 = gismodels.CharField(
        max_length=255,
        help_text='The name of this area (e.g. the name of an LGA))'
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


class LGA(Area):
    class Meta:
        verbose_name = 'LGA'

    def get_lga_name(self):
        return self.name_2

    def get_lga_alternative_name(self):
        return self.varname_2

    def get_lga_names(self):
        return [self.get_lga_name(), self.get_lga_alternative_name()]

    def get_state_name(self):
        return self.name_1

    def get_country_name(self):
        return self.name_0

    @classmethod
    def find_lga(cls, name, state_name, country_name=None):
        if country_name:
            query = {'name_0': country_name, 'name_1': state_name}
        else:
            query = {'name_1': state_name}
        found = 0
        query_result = []
        for lga_name_field in ('name_2', 'varname_2'):
            query[lga_name_field] = name
            query_result = cls.objects.filter(**query)
            found = query_result.count()
            if found == 0:
                del query[lga_name_field]
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
            raise RuntimeError(u'More than one LGA named "{}" in state "{}"{} '
                               u'found!'.format(name, state_name, country_part))


class QuestionnaireSpecification(models.Model):
    class Meta:
        verbose_name_plural = 'The "Questionnaire Specification" documents'

    name_or_id = models.CharField(
        max_length=255, unique=True, blank=False,
        help_text=u'Please enter a unique name or id of your new questionnaire '
                  u'specification.')
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
    active = MaxOneActiveQuestionnaireField(
        default=False,
        help_text=u'Activate this questionnaire specification.  Only one '
                  u'questionnaire specification may be active at any given '
                  u'time.')
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name_or_id

    @classmethod
    def get_active(cls):
        active_qss = cls.objects.filter(active__exact=True)
        c = active_qss.count()
        if c == 1:
            return active_qss[0]
        elif c == 0:
            return None
        else:
            raise RuntimeError(u'More than one active questionnaire '
                               u'specification found.  This should not happen. '
                               u'Please check the database.')

    @classmethod
    def get_most_recently_created(cls):
        questionnaire_specifications = cls.objects.order_by('-created')
        if questionnaire_specifications:
            return questionnaire_specifications[0]
        else:
            return None

    @classmethod
    def get_most_recently_modified(cls):
        questionnaire_specifications = cls.objects.order_by('-last_modified')
        if questionnaire_specifications:
            return questionnaire_specifications[0]
        else:
            return None


class UniqueActiveDocument(models.Model):
    active = UniqueActiveField(
        default=False,
        help_text=u'Activate this document.  Only one document of this type '
                  u'may be active at any given time.')
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

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
    def get_most_recently_created(cls, category_string):
        instances = cls.objects.filter(
            category=category_string).order_by('-created')
        if instances:
            return instances[0]
        else:
            return None

    @classmethod
    def get_most_recently_modified(cls, category_string):
        instances = cls.objects.filter(
            category=category_string).order_by('-last_modified')
        if instances:
            return instances[0]
        else:
            return None


class UniqueActiveNamedDocument(UniqueActiveDocument):
    name_or_id = models.CharField(
        max_length=255, unique=True, blank=False,
        help_text=u'Please enter a unique name or id of your new document.')

    def __unicode__(self):
        return self.name_or_id


class ClustersPerState(UniqueActiveNamedDocument):
    class Meta:
        verbose_name_plural = 'The "Clusters per State" documents'

    json = JSONField(
        null=True, blank=True,
        help_text=u'Please enter the JSON structure defining the number of '
                  u'standard and reserve clusters per state.  E.g.: { "states":'
                  u' { "Kano": { "standard": 5, "reserve": 3 }, "Lagos": { '
                  u'"standard": 7, "reserve": 3 } } }',
        default="""
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
    )


class States(UniqueActiveNamedDocument):
    class Meta:
        verbose_name_plural = 'The "States" documents'

    json = JSONField(
        null=True, blank=True,
        help_text=u'Please enter the JSON structure defining the states data.',
        default="""
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
    )


class StatesWithReserveClusters(UniqueActiveNamedDocument):
    class Meta:
        verbose_name_plural = 'The "States with Reserve Clusters" documents'

    json = JSONField(
        null=True, blank=True,
        help_text=u'Please enter the JSON structure describing the states with '
                  u'reserve clusters.',
        default="""
            For example:

            [
                "Kano",
                "Gombe",
                "Yobe",
                "Abuja Federal Capital Territory"
            ]
        """
    )


class ClustersPerTeam(UniqueActiveNamedDocument):
    class Meta:
        verbose_name_plural = 'The "Clusters per Team" documents'

    json = JSONField(
        null=True, blank=True,
        help_text=u'Please enter the JSON structure defining the (planned) '
                  u'number of clusters per each team.',
        default="""
            For example:

            {
                "1": 5,
                "2": 15,
                "3": 17
            }
        """
    )
