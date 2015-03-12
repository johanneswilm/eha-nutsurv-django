import datetime
import dateutil.parser
import dateutil.relativedelta

import numpy
import scipy.stats

from django.db import models

import django.contrib.gis.db.models as gismodels
from django.contrib.gis.geos import Point

from jsonfield import JSONField

from fields import MaxOneActiveQuestionnaireField
from fields import UniqueActiveField


class HouseholdSurveyJSON(models.Model):
    class Meta:
        verbose_name = 'household survey'

    json = JSONField(
        null=True, blank=True,
        help_text='A JSON document containing data acquired from one '
                  'household.  Typically not edited here but uploaded from a '
                  'mobile application used by a team of surveyors in the '
                  'field.  If in doubt, do not edit.'
    )
    uuid = models.CharField(
        max_length=255, unique=True,
        help_text='A unique identifier of an individual household survey.  '
                  'Typically assigned by a mobile application before the data '
                  'is uploaded to the server.  If in doubt, do no edit.'
    )

    def __unicode__(self):
        # Try to build a name describing a survey.
        if not self.json:
            # If field json is invalid then there is no way to compute the name.
            return u'invalid {}'.format(self._meta.verbose_name)
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
        """This method finds all instances of HouseholdSurveyJSON which can be
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
            team_id = self.json['team']['teamID']
        except TypeError:
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
        if not 'survey' in child:
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
        if not 'ageInMonths' in child['survey']:
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
    def run_alert_checks_on_document(cls, household_survey):
        """This method runs all the defined alert checks which leads to
        relevant alerts being created in case they are triggered by data stored
        in household_survey.
        """
        cls.sex_ratio_alert(household_survey)
        cls.child_age_in_months_ratio_alert(household_survey)
        cls.child_age_displacement_alert(household_survey)
        cls.woman_age_14_15_displacement_alert(household_survey)
        cls.woman_age_4549_5054_displacement_alert(household_survey)
        cls.digit_preference_alert(household_survey)
        cls.data_collection_time_alert(household_survey)

    @classmethod
    def sex_ratio_alert(cls, household_survey, test='chi-squared'):
        """In the data of children from 0-59 months of age, we expect to find
        an even number boys and girls. If chi-square of sex ratio < 0.001 then
        report an alert on dashboard "Sex-ratio issue in team NAME".
        This method implements both binomial two-tailed test and chi-square
        test.  The latter is the default (as per client's request).
        """
        surveys = household_survey.find_all_surveys_by_this_team()
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
        if p < 0.001:
            team = household_survey.get_team_name()
            alert_text = 'Sex-ratio issue in team {}'.format(team)
            # Only add if there is no same alert among unarchived.
            if not Alert.objects.filter(text=alert_text, archived=False):
                Alert.objects.create(text=alert_text)

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
        if p < 0.001:
            team = household_survey.get_team_name()
            alert_text = 'Age ratio issue in team {}'.format(team)
            # Only add if there is no same alert among unarchived.
            if not Alert.objects.filter(text=alert_text, archived=False):
                Alert.objects.create(text=alert_text)

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
        if p < 0.001:
            team = household_survey.get_team_name()
            alert_text = 'Child age displacement issue in team {}'.format(team)
            # Only add if there is no same alert among unarchived.
            if not Alert.objects.filter(text=alert_text, archived=False):
                Alert.objects.create(text=alert_text)

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
        if p < 0.001:
            team = household_survey.get_team_name()
            alert_text = \
                'Woman age displacement issue (14/15) in team {}'.format(team)
            # Only add if there is no same alert among unarchived.
            if not Alert.objects.filter(text=alert_text, archived=False):
                Alert.objects.create(text=alert_text)

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
        if p < 0.001:
            team = household_survey.get_team_name()
            alert_text = 'Woman age displacement issue (45-49/50-54) in team ' \
                         '{}'.format(team)
            # Only add if there is no same alert among unarchived.
            if not Alert.objects.filter(text=alert_text, archived=False):
                Alert.objects.create(text=alert_text)

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
                team = household_survey.get_team_name()
                alert_text = 'Digit preference issue in team {}'.format(team)
                # Only add if there is no same alert among unarchived.
                if not Alert.objects.filter(text=alert_text, archived=False):
                    Alert.objects.create(text=alert_text)
                # Only one alert should be emitted so no need to finish the
                # loop.
                break

    @classmethod
    def data_collection_time_alert(cls, household_survey):
        """If timestamp for any data point in data collection is <07:00 hours
        or >20:00 hours then report alert on dashboard "Data collection time
        issue in team NAME (survey: UUID)".
        If any of the time stamps is not a valid date, the alert is triggered
        too.
        N.B. This function performs these checks for both the start time and
        the end time.  The alert is triggered if any of them satisfies the
        condition mentioned above.
        """
        t700h = datetime.time(7)
        t2000h = datetime.time(20)
        start = household_survey.get_start_time()
        end = household_survey.get_end_time()
        triggered = False
        for t in (start, end):
            if t is None:
                triggered = True
                break
            elif t.time() < t700h or t.time() > t2000h:
                triggered = True
                break
        if triggered:
            team = household_survey.get_team_name()
            alert_text = u'Data collection time issue in team {} (survey: {})'.\
                format(team, household_survey.uuid)
            # Only add if there is no same alert among unarchived.
            if not Alert.objects.filter(text=alert_text, archived=False):
                Alert.objects.create(text=alert_text)

    @classmethod
    def time_to_complete_single_survey_alerts(cls):
        """This method is meant to be run once a day (or every few days),
        typically after midgnight.  It processes all household surveys and
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

            team = survey.get_team_name()
            # If no valid team name, the duration can only be used to calculate
            # the median.
            if team == 'UNNAMED':
                continue
            # At this point we know that the survey contained a valid end time
            # so no need to check that.  Get the date.
            collection_date = survey.get_end_time().date()
            # If collection date earlier than today, store the data for further
            # processing.
            if collection_date < today:
                if team not in by_team:
                    by_team[team] = {}
                if collection_date not in by_team[team]:
                    by_team[team][collection_date] = {
                        'average': duration,
                        'n': 1,
                        }
                else:
                    n = by_team[team][collection_date]['n'] + 1.0
                    old = by_team[team][collection_date]['average']
                    new = (n - 1) / n * old + 1 / n * duration
                    by_team[team][collection_date]['n'] = n
                    by_team[team][collection_date]['average'] = new

        # Calculate the value to check the averages against (50% of median).
        half_median = numpy.median(survey_durations) / 2.0

        # Process all data collected above and produce alerts when triggered.
        for team in by_team:
            for day in by_team[team]:
                if by_team[team][day]['average'] < half_median:
                    alert_text = u'Time to complete household survey issue ' \
                                 u'in team {} ' \
                                 u'on day {}'.format(team, day.isoformat())
                    # Only add if there is no identical alert among unarchived.
                    if not Alert.objects.filter(
                            text=alert_text,
                            archived=False):
                        Alert.objects.create(text=alert_text)

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
            team = survey.get_team_name()
            # If no valid team name or id then this data point cannot be used.
            if team == 'UNNAMED':
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

            if team not in by_team:
                # Previously unseen team detected.  Initialise storage.
                by_team[team] = {}
            if day not in by_team[team]:
                # Previously unseen day detected.  Initialise data for this day
                # with the current values of start and end (possible Nones).
                by_team[team][day] = {
                    'start': start,
                    'end': end,
                    }
            # A different survey for the same day has been previously processed.
            else:
                # Detect the earliest start time for a given day.
                if not (by_team[team][day]['start'] is None or start is None):
                    if start < by_team[team][day]['start']:
                        by_team[team][day]['start'] = start
                elif start is not None:
                    by_team[team][day]['start'] = start
                # Detect the latest end time for a given day.
                if not (by_team[team][day]['end'] is None or end is None):
                    if end > by_team[team][day]['end']:
                        by_team[team][day]['end'] = end
                elif end is not None:
                    by_team[team][day]['end'] = end

        # Delete invalid data points and create a vector of all durations to
        # calculate the median.
        durations = []
        for team in by_team.keys():
            team_durations = []
            for day in by_team[team].keys():
                start = by_team[team][day]['start']
                end = by_team[team][day]['end']
                # Delete invalid dates.
                if start is None or end is None:
                    del by_team[team][day]
                    continue
                elif start > end:
                    del by_team[team][day]
                    continue
                # Compute and store durations.
                delta = end - start
                duration = delta.total_seconds()
                team_durations.append(duration)
                # Delete the processed data for this day.  No longer needed.
                del by_team[team][day]

            # Delete the team if no valid data points available and proceed to
            # the next.
            if len(team_durations) < 1:
                del by_team[team]
                continue

            # Update the durations vector with the just processed team data.
            durations.extend(team_durations)

            # Compute the daily average for the team.
            by_team[team]['daily average'] = numpy.average(team_durations)
        # Stop here if no valid data points found (nothing to check and the
        # median would be NaN).
        if len(durations) < 1:
            return
        # Calculate the value to check the averages against (50% of median).
        half_median = numpy.median(durations) / 2.0

        # Process all data collected above and produce alerts when triggered.
        for team in by_team:
            if by_team[team]['daily average'] < half_median:
                alert_text = u'Duration of data collection issue ' \
                             u'in team {}'.format(team)
                # Only add if there is no identical alert among unarchived.
                if not Alert.objects.filter(
                        text=alert_text,
                        archived=False):
                    Alert.objects.create(text=alert_text)

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
        max_length=255, unique=True, blank=False,
        help_text=u'Please enter a unique name or id of your new document.')

    def __unicode__(self):
        return self.name_or_id


class Clusters(UniqueActiveNamedDocument):
    """A JSON document containing information about clusters in the format
    shown below:
    {
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
    """

    def __unicode__(self):
        return self.name_or_id

    class Meta:
        verbose_name_plural = 'The "Clusters" documents'

    json = JSONField(
        null=True, blank=True,
        help_text=u'Please enter the JSON structure describing all the '
                  u'clusters for the planned survey.',
        default={}
        )


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


class LGA(Area):
    class Meta:
        verbose_name = '2nd Admin'

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
            raise RuntimeError(u'More than one 2nd Admin named "{}" in 1st Admin "{}"{} '
                               u'found!'.format(name, state_name, country_part))


class QuestionnaireSpecification(UniqueActiveDocument):
    class Meta:
        verbose_name_plural = 'The "Questionnaire Specification" documents'


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


class ClustersPerState(UniqueActiveNamedDocument):
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
    class Meta:
        verbose_name_plural = 'The "Clusters per 1st Admin" documents'

    json = JSONField(
        null=True, blank=True,
        help_text=u'Please enter the JSON structure defining the number of '
                  u'standard and reserve clusters per 1st Admin.  E.g.: { "states":'
                  u' { "Kano": { "standard": 5, "reserve": 3 }, "Lagos": { '
                  u'"standard": 7, "reserve": 3 } } }',
        default={}
    )


class States(UniqueActiveNamedDocument):
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
    class Meta:
        verbose_name_plural = 'The "1st Admin" documents'

    json = JSONField(
        null=True, blank=True,
        help_text=u'Please enter the JSON structure defining the 1st Admin area data.',
        default=[]
    )


class StatesWithReserveClusters(UniqueActiveNamedDocument):
    """
        For example:

        [
            "Kano",
            "Gombe",
            "Yobe",
            "Abuja Federal Capital Territory"
        ]
    """

    class Meta:
        verbose_name_plural = 'The "1st Admin with Reserve Clusters" documents'

    json = JSONField(
        null=True, blank=True,
        help_text=u'Please enter the JSON structure describing the 1st Admin with '
                  u'reserve clusters enabled.',
        default=[]
    )


class ClustersPerTeam(UniqueActiveNamedDocument):
    """
        For example:

        {
            "1": 5,
            "2": 15,
            "3": 17
        }
    """
    class Meta:
        verbose_name_plural = 'The "Clusters per Team" documents'

    json = JSONField(
        null=True, blank=True,
        help_text=u'Please enter the JSON structure defining the (planned) '
                  u'number of clusters per each team.',
        default={}
    )
