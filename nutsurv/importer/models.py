import uuid, random, json, math

from datetime import datetime
from jsonfield import JSONField

from django.db import models

from dashboard.models import JSONDocument
from importer import anthrocomputation


class FormhubData(models.Model):
    contents = JSONField(null=True, blank=True, help_text=' ')
    uuid = models.CharField(max_length=256,unique=True)
    converted_json_document = models.ForeignKey(JSONDocument, null=True, blank=True)

    def __unicode__(self):
        return self.uuid

    class Meta:
        verbose_name_plural = 'Formhub Data Entries'


    def convert_to_json_document (self):
        if not all (terms in self.contents for terms in ('hh_number', '_gps_latitude', '_gps_longitude', 'cluster', 'team_num', 'starttime', 'endtime', '_submission_time', '_uuid', 'consent/hh_roster')):
            return # Basic info not there, we give up. TODO: log error
        if not self.converted_json_document:
            self.converted_json_document = JSONDocument.objects.create()
        members = []
        for fh_member in self.contents['consent/hh_roster']:
            member = {
                "firstName": fh_member['consent/hh_roster/listing/name'],
                "age": fh_member['consent/hh_roster/listing/age_years'],
                "surveyType": "",
                "survey": {}
            }
            if fh_member['consent/hh_roster/listing/sex'] == 1:
                member["gender"] = "M"
            else:
                member["gender"] = "F"
            members.append(member)

        if 'consent/note_7' in self.contents:
            for fh_woman in self.contents['consent/note_7']:
                if "consent/note_7/womanname1" in fh_woman:
                    name = fh_woman["consent/note_7/womanname1"]
                    member = next((item for item in members if item["firstName"] == name), None)
                else:
                    member = False #TODO: log as non-imported woman survey
                if member:
                    member["surveyType"] = "women"
                    member["survey"] = {}
                    if 'consent/note_7/wom_muac' in fh_woman:
                        member["survey"]["muac"] = fh_woman["consent/note_7/wom_muac"]

        if 'consent/child' in self.contents:
            for fh_child in self.contents['consent/child']:
                if "consent/child/child_name" in fh_child:
                    name = fh_child["consent/child/child_name"]
                    member = next((item for item in members if item["firstName"] == name), None)
                else:
                    member = False #TODO: log as non-imported child survey
                if member:
                    member["surveyType"] = "child"
                    member["survey"] = {}
                    if 'consent/child/child_60/muac' in fh_child:
                        member["survey"]["muac"] = fh_child['consent/child/child_60/muac']
                    if 'consent/child/child_60/height' in fh_child:
                        member["survey"]["height"] = fh_child['consent/child/child_60/height']
                    if 'consent/child/child_60/weight' in fh_child:
                        member["survey"]["weight"] = fh_child['consent/child/child_60/weight']
                    if 'consent/child/child/months' in fh_child:
                        member["survey"]["ageInMonth"] = fh_child['consent/child/months']
                    if 'consent/child/child_60/edema' in fh_child:
                        if fh_child['consent/child/child_60/edema'] == 0:
                            member["survey"]["edema"] = 'N'
                        else:
                            member["survey"]["edema"] = 'Y'
                    #if all (terms in fh_child for terms in ('consent/child/child_60/muac', 'consent/child/child_60/height', 'consent/child/child_60/weight', 'consent/child/child/months', 'consent/child/child_60/edema')):
                    if 'consent/child/months' in fh_child:
                        ageInDays = fh_child['consent/child/months'] * anthrocomputation.DAYSINMONTH
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
                    if 'consent/child/child_60/measure' in fh_child and fh_child['consent/child/child_60/measure'] == 2:
                        isRecumbent = True
                    else:
                        isRecumbent = False
                    if 'consent/child/child_60/edema' in fh_child and fh_child['consent/child/child_60/edema'] > 0:
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
                    zscores = anthrocomputation.getAnthroResult( ageInDays, sex, weight, height, isRecumbent, hasOedema, hc, muac, tsf, ssf)
                    if ('ZLH4A' in zscores and not math.isnan(zscores["ZLH4A"]))
                        or ('ZW4A' in zscores and not math.isnan(zscores["ZW4A"]))
                        or ('ZW4LH' in zscores and not math.isnan(zscores["ZW4LH"])):
                        member["survey"]["zscores"] = {}
                        if 'ZLH4A' in zscores and not math.isnan(zscores["ZLH4A"]):
                            member["survey"]["zscores"]["haz"] = zscores["ZLH4A"]
                        if 'ZW4A' in zscores and not math.isnan(zscores["ZW4A"]):
                            member["survey"]["zscores"]["waz"] = zscores["ZW4A"]
                        if 'ZW4LH' in zscores and not math.isnan(zscores["ZW4LH"]):
                            member["survey"]["zscores"]["whz"] = zscores["ZW4LH"]


        converted_json = {
            "uuid": self.contents['_uuid'],
            "syncDate": self.contents['_submission_time'] + ".000Z", # From simple date/time to datetime with timezone
            "startTime": self.contents['starttime'],
            "created": self.contents['_submission_time']  + ".000Z", # From simple date/time to datetime with timezone
            "_rev": str(uuid.uuid4()), # TODO: Using a UUID here for now. not sure this is good enough.
            "modified": self.contents['_submission_time'],
            "householdID": self.contents['hh_number'],
            "cluster": self.contents['cluster'],
            "endTime": self.contents['endtime'],
            "location": [
                self.contents['_gps_latitude'],
                self.contents['_gps_longitude']
            ],
            "members": members,
            "team": FakeTeams.objects.get_or_create(team_id = self.contents['team_num'])[0].contents,
            "_id": self.contents['_uuid'],
            "tools":{},
            "history":[]
        }
        self.converted_json_document.json = converted_json
        self.converted_json_document.save()



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

    contents = JSONField(null=True, blank=True, help_text=' ')
    team_id = models.IntegerField(unique=True)

    def __unicode__(self):
        return str(self.team_id)

    def save(self, *args, **kwargs):
        if not self.contents:
            # If the team does not yet exist, create random team data.
            team_leader = [random.choice(FIRST_NAMES),random.choice(LAST_NAMES)];
            anthropometrist = [random.choice(FIRST_NAMES),random.choice(LAST_NAMES)];
            assistant = [random.choice(FIRST_NAMES),random.choice(LAST_NAMES)];
            self.contents = {
                "uuid": str(uuid.uuid4()),
                "created": datetime.utcnow().isoformat()[:-3] + 'Z', # Trying to get a date/time stamp as JS outputs it.
                "_rev": str(uuid.uuid4()), # TODO: Using a UUID here for now. not sure this is good enough.
                "modified": datetime.utcnow().isoformat()[:-3] +'Z', # Trying to get a date/time stamp as JS outputs it.
                "teamID": self.team_id,
                "members":[
                    {
                        "designation":"Team Leader",
                        "firstName": team_leader[0][0],
                        "mobile":"0" + str(random.randint(10000000000,99999999999)),
                        "lastName": team_leader[1],
                        "age": random.randint(30, 58),
                        "memberID": self.team_id * 3,
                        "gender": team_leader[0][1],
                        "email": team_leader[0][0] + '.' + team_leader[1] + '@' + random.choice(EMAIL_PROVIDERS)
                    },
                    {
                        "designation":"Anthropometrist",
                        "firstName": anthropometrist[0][0],
                        "mobile":"0" + str(random.randint(10000000000,99999999999)),
                        "lastName": anthropometrist[1],
                        "age": random.randint(24, 42),
                        "memberID": self.team_id * 3 + 1,
                        "gender": anthropometrist[0][1],
                        "email": anthropometrist[0][0] + '.' + anthropometrist[1] + '@' + random.choice(EMAIL_PROVIDERS)
                    },
                    {
                        "designation":"Assistant",
                        "firstName": assistant[0][0],
                        "mobile":"0" + str(random.randint(10000000000,99999999999)),
                        "lastName": assistant[1],
                        "age": random.randint(17, 35),
                        "memberID": self.team_id * 3 + 2,
                        "gender": assistant[0][1],
                        "email": assistant[0][0] + '.' + assistant[1] + '@' + random.choice(EMAIL_PROVIDERS)
                    }],
                "_id":str(uuid.uuid4())
            }
            super(FakeTeams, self).save(*args, **kwargs)
