import uuid, random, json, math, logging

from datetime import datetime
from jsonfield import JSONField

from django.db import models

from dashboard import models as dashboard_models
from importer import anthrocomputation

from pytz import timezone
import dateutil.parser

def reset_data():
    FakeTeams.objects.all().delete()
    FormhubSurvey.objects.all().delete()
    dashboard_models.HouseholdSurveyJSON.objects.all().delete()
    dashboard_models.Alert.objects.all().delete()

    dashboard_models.Clusters.objects.all().delete()
    cluster_data = dashboard_models.Clusters()
    cluster_data.json = {}
    cluster_data.name_or_id = 'default_clusters'
    cluster_data.active = True
    cluster_data.save()

    dashboard_models.ClustersPerTeam.objects.all().delete()
    team_data = dashboard_models.ClustersPerTeam()
    team_data.json = {}
    team_data.name_or_id = 'default_clusters_per_team'
    team_data.active = True
    team_data.save()

    dashboard_models.StatesWithReserveClusters.objects.all().delete()
    state_reserve_data = dashboard_models.StatesWithReserveClusters()
    state_reserve_data.json = []
    state_reserve_data.name_or_id = 'default_state_reserve_data'
    state_reserve_data.active = True
    state_reserve_data.save()

    dashboard_models.ClustersPerState.objects.all().delete()
    cluster_state_data = dashboard_models.ClustersPerState()
    cluster_state_data.json = {}
    cluster_state_data.name_or_id = 'default_clusters_per_state'
    cluster_state_data.active = True
    cluster_state_data.save()

    dashboard_models.States.objects.all().delete()
    states_data = dashboard_models.States()
    states_data.json = []
    states_data.name_or_id = 'default_states'
    states_data.active = True

    states_data.save()

def convert_to_utc_js_datestring(date_string):
    """Turn '2014-05-05T17:26:37.401+01' into '2014-05-05T16:26:37.401Z'"""
    parsed_date = dateutil.parser.parse(date_string)
    return parsed_date.astimezone(timezone('UTC')).isoformat()[:-6]+'Z'

def update_mapping_documents_from_new_survey(json):
    # Check whether other pieces of info are there as they should be.

    team_number = str(json['team_num'])
    team_data = dashboard_models.ClustersPerTeam.get_active()

    if not team_number in team_data.json:
        team_data.json[team_number] = 0
        team_data.save()

    for key in ('state', 'cluster', 'cluster_name', 'lga',):
        if key not in json:
            logging.warning('{!r} not in {!r}'.format(key, json)) # just to make sure it's there
            return

    cluster_data = dashboard_models.Clusters.get_active()
    if cluster_data == None:
        return

    cluster_number = str(json['cluster'])
    # We make everything depend on the existence of the cluster number in the cluster db.
    if cluster_number in cluster_data.json:
        return

    cluster_data.json[cluster_number] = {
        "cluster_name": json['cluster_name'],
        "lga_name": str(json['lga']), # These are numbers we turn into strings. We don't have names. Better than nothing.
        "state_name": str(json['state']) # These are numbers we turn into strings. We don't have names. Better than nothing.
    }
    cluster_data.save()

    state_number = str(json['state'])
    cluster_state_data = dashboard_models.ClustersPerState.get_active()
    if state_number not in cluster_state_data.json:
        cluster_state_data.json[state_number] = {
            "standard": 10,
            "reserve": 5
        }
        cluster_state_data.save()

    states_data = dashboard_models.States.get_active()
    if state_number not in states_data.json:
        states_data.json.append(state_number)
        states_data.save()


class FormhubSurvey(models.Model):
    uuid = models.CharField(max_length=256,unique=True)
    json = JSONField(null=True, blank=True, help_text=' ')
    converted_household_survey = models.ForeignKey(dashboard_models.HouseholdSurveyJSON, \
        null=True, blank=True)

    def __unicode__(self):
        return self.uuid

    class Meta:
        verbose_name_plural = 'Formhub Survey Entries'


    def convert_to_household_survey (self):
        """The purpose here is to convert the data as it comes from formhub to
        the format that comes from the nutsurv mobile app.

        """
        if not all (key in self.json for key in ('hh_number', \
            '_gps_latitude', '_gps_longitude', 'cluster', 'team_num', \
            'starttime', 'endtime', '_submission_time', '_uuid', \
            'consent/hh_roster')):
            return # Basic info not there, we give up. TODO: log error
        if not self.converted_household_survey:
            self.converted_household_survey, created = \
                dashboard_models.HouseholdSurveyJSON.objects.get_or_create( \
                    uuid=self.uuid)
        members = []
        for fh_member in self.json['consent/hh_roster']:
            member = {
                "firstName": fh_member['consent/hh_roster/listing/name'],
                "age": fh_member['consent/hh_roster/listing/age_years'],
            }
            if fh_member['consent/hh_roster/listing/sex'] == 1:
                member["gender"] = "M"
            else:
                member["gender"] = "F"
            members.append(member)

        if 'consent/note_7' in self.json:
            for fh_woman in self.json['consent/note_7']:
                if "consent/note_7/womanname1" in fh_woman:
                    name = fh_woman["consent/note_7/womanname1"]
                    member = next((item for item in members \
                        if item["firstName"] == name), None)
                else:
                    member = False #TODO: log as non-imported woman survey
                if member:
                    member["surveyType"] = "women"
                    member["survey"] = {}
                    if 'consent/note_7/wom_muac' in fh_woman:
                        member["survey"]["muac"] = \
                            fh_woman["consent/note_7/wom_muac"]

        if 'consent/child' in self.json:
            for fh_child in self.json['consent/child']:
                if "consent/child/child_name" in fh_child:
                    name = fh_child["consent/child/child_name"]
                    member = next((item for item in members \
                        if item["firstName"] == name), None)
                else:
                    member = False #TODO: log as non-imported child survey
                if member:
                    member["surveyType"] = "child"
                    member["survey"] = {}
                    if 'consent/child/child_60/muac' in fh_child:
                        member["survey"]["muac"] = \
                            fh_child['consent/child/child_60/muac']
                    if 'consent/child/child_60/height' in fh_child:
                        member["survey"]["height"] = \
                            fh_child['consent/child/child_60/height']
                    if 'consent/child/child_60/weight' in fh_child:
                        member["survey"]["weight"] = \
                            fh_child['consent/child/child_60/weight']
                    if 'consent/child/child/months' in fh_child:
                        member["survey"]["ageInMonth"] = \
                            fh_child['consent/child/months']
                    if 'consent/child/child_60/edema' in fh_child:
                        if fh_child['consent/child/child_60/edema'] == 0:
                            member["survey"]["edema"] = 'N'
                        else:
                            member["survey"]["edema"] = 'Y'
                    if 'consent/child/months' in fh_child:
                        member["survey"]["ageInMonths"] = fh_child['consent/child/months']
                        ageInDays = fh_child['consent/child/months'] \
                            * anthrocomputation.DAYSINMONTH
                    else:
                        ageInDays = None
                    sex = member["gender"]
                    if 'consent/child/child_60/weight' in fh_child:
                        weight = fh_child['consent/child/child_60/weight']
                    else:
                        weight = None
                    if 'consent/child/child_60/height' in fh_child:
                        height = fh_child['consent/child/child_60/height']
                    else:
                        height = None
                    if 'consent/child/child_60/measure' in fh_child and \
                        fh_child['consent/child/child_60/measure'] == 2:
                        isRecumbent = True
                    else:
                        isRecumbent = False
                    if 'consent/child/child_60/edema' in fh_child and \
                        fh_child['consent/child/child_60/edema'] > 0:
                        hasOedema = True
                    else:
                        hasOedema = False
                    hc = None # Not used.
                    if 'consent/child/child_60/muac' in fh_child:
                        muac = fh_child['consent/child/child_60/muac']
                    else:
                        muac = None
                    tsf = None # Not used.
                    ssf = None # Not used.
                    zscores = anthrocomputation.getAnthroResult(ageInDays, \
                        sex, weight, height, isRecumbent, hasOedema, hc,  \
                        muac, tsf, ssf)
                    if ('ZLH4A' in zscores \
                            and not math.isnan(zscores["ZLH4A"])) \
                        or ('ZW4A' in zscores \
                            and not math.isnan(zscores["ZW4A"])) \
                        or ('ZW4LH' in zscores
                            and not math.isnan(zscores["ZW4LH"])):
                        member["survey"]["zscores"] = {}
                        if 'ZLH4A' in zscores \
                            and not math.isnan(zscores["ZLH4A"]):
                            member["survey"]["zscores"]["HAZ"] = \
                                zscores["ZLH4A"]
                        if 'ZW4A' in zscores \
                            and not math.isnan(zscores["ZW4A"]):
                            member["survey"]["zscores"]["WAZ"] = \
                                zscores["ZW4A"]
                        if 'ZW4LH' in zscores \
                            and not math.isnan(zscores["ZW4LH"]):
                            member["survey"]["zscores"]["WHZ"] = \
                                zscores["ZW4LH"]


        converted_json = {
            "uuid": self.json['_uuid'],
            # From simple date/time to datetime with timezone
            "syncDate": self.json['_submission_time'] + ".000Z",
            "startTime": convert_to_utc_js_datestring(self.json['starttime']),
            # From simple date/time to datetime with timezone
            "created": self.json['_submission_time']  + ".000Z",
            # TODO: Using a UUID here for now. not sure this is good enough.
            "_rev": str(uuid.uuid4()),
            "modified": self.json['_submission_time'],
            "householdID": self.json['hh_number'],
            "cluster": self.json['cluster'],
            "endTime": convert_to_utc_js_datestring(self.json['endtime']),
            "location": [
                self.json['_gps_latitude'],
                self.json['_gps_longitude']
            ],
            "members": members,
            "team": FakeTeams.objects.get_or_create(team_id =
                self.json['team_num'])[0].json,
            "_id": self.json['_uuid'],
            "tools":{},
            "history":[]
        }
        self.converted_household_survey.json = converted_json
        self.converted_household_survey.parse_and_set_team_members()
        self.converted_household_survey.save()

        update_mapping_documents_from_new_survey(self.json)

        # Check for all relevant household alerts
        if self.converted_household_survey.json != None:
            dashboard_models.Alert.run_alert_checks_on_document(self.converted_household_survey)



FIRST_NAMES = [
    ['Abubakar','M'],
    ['Omoshola','M'],
    ['Eterigho','M'],
    ['Anayuchukwu','M'],
    ['Polonololgombi','M'],
    ['Tolulope','M'],
    ['Adenuga','M'],
    ['Segbuyota','M'],
    ['Toheeb','M'],
    ['Omotoyosi','M'],
    ['Oludare','M'],
    ['Ikor','M'],
    ['Oritsefemi','M'],
    ['Gana','M'],
    ['Umo','F'],
    ['Faderera','F'],
    ['Doris','F'],
    ['Chika','F'],
    ['Safiya','F'],
    ['Olapeju','F'],
    ['Ihuoma','F'],
    ['Chidera','F'],
    ['Rofiat','F'],
    ['Adeola','F'],
    ['Osifo','F'],
    ['Iquo','F'],
    ['Doyinsola','F'],
    ['Agbonrein','F'],
    ['Oselumen','F'],
    ['Adenze','F'],
    ['Idubu','F'],
    ['Ashabi','F'],
]

LAST_NAMES = [
    'Azikiwe',
    'Chahine',
    'Bello',
    'Cisse',
    'Akintola',
    'Okotie',
    'Nzeogwu',
    'Onwuatuegwu',
    'Okafor',
    'Contee',
    'Okeke',
    'Conteh',
    'Okoye',
    'Diallo',
    'Obansanjo',
]

EMAIL_PROVIDERS = [
    'gmail.com',
    'hotmail.com',
    'oni.com',
    'yahoo.com',
]


class FakeTeams(models.Model):
    """The data from Formhub comes without team member data. For the test
    import through CSV we therefore create fake teams with random team members.
    This should likely be removed before import data from formhub for realworld
    usage.
    """

    json = JSONField(null=True, blank=True, help_text=' ')
    team_id = models.IntegerField(unique=True)

    def __unicode__(self):
        return str(self.team_id)

    def save(self, *args, **kwargs):
        if not self.json:
            # If the team does not yet exist, create random team data.
            team_leader = [random.choice(FIRST_NAMES), \
                random.choice(LAST_NAMES)]
            anthropometrist = [random.choice(FIRST_NAMES), \
                random.choice(LAST_NAMES)]
            assistant = [random.choice(FIRST_NAMES), \
                random.choice(LAST_NAMES)]
            self.json = {
                "uuid": str(uuid.uuid4()),
                # Trying to get a date/time stamp as JS outputs it.
                "created": datetime.utcnow().isoformat()[:-3] + 'Z',
                # TODO: Using a UUID here for now. not sure this is OK.
                "_rev": str(uuid.uuid4()),
                # Trying to get a date/time stamp as JS outputs it.
                "modified": datetime.utcnow().isoformat()[:-3] +'Z',
                "teamID": self.team_id,
                "members":[
                    {
                        "designation":"Team Leader",
                        "firstName": team_leader[0][0],
                        "mobile":"0" + \
                            str(random.randint(10000000000,99999999999)),
                        "lastName": team_leader[1],
                        "age": random.randint(30, 58),
                        "memberID": self.team_id * 3,
                        "gender": team_leader[0][1],
                        "email": team_leader[0][0] + '.' + team_leader[1] + \
                            '@' + random.choice(EMAIL_PROVIDERS)
                    },
                    {
                        "designation":"Anthropometrist",
                        "firstName": anthropometrist[0][0],
                        "mobile":"0" + \
                            str(random.randint(10000000000,99999999999)),
                        "lastName": anthropometrist[1],
                        "age": random.randint(24, 42),
                        "memberID": self.team_id * 3 + 1,
                        "gender": anthropometrist[0][1],
                        "email": anthropometrist[0][0] + '.' + \
                            anthropometrist[1] + \
                            '@' + random.choice(EMAIL_PROVIDERS)
                    },
                    {
                        "designation":"Assistant",
                        "firstName": assistant[0][0],
                        "mobile":"0" + \
                            str(random.randint(10000000000,99999999999)),
                        "lastName": assistant[1],
                        "age": random.randint(17, 35),
                        "memberID": self.team_id * 3 + 2,
                        "gender": assistant[0][1],
                        "email": assistant[0][0] + '.' + assistant[1] + \
                            '@' + random.choice(EMAIL_PROVIDERS)
                    }],
                "_id":str(uuid.uuid4())
            }
            super(FakeTeams, self).save(*args, **kwargs)
