import uuid, random, json

from datetime import datetime
from jsonfield import JSONField

from django.db import models

from dashboard.models import JSONDocument


class FormhubData(models.Model):
    contents = JSONField(null=True, blank=True, help_text=' ')
    uuid = models.CharField(max_length=256,unique=True)
    converted_json_document = models.ForeignKey(JSONDocument, null=True, blank=True)

    def __unicode__(self):
        return self.uuid

    class Meta:
        verbose_name_plural = 'Formhub Data Entries'


    def convert_to_json_document (self):
        if not self.converted_json_document:
            self.converted_json_document = JSONDocument.objects.create()
        if not self.contents.viewkeys() & {'hh_number', '_gps_latitude', '_gps_longitude', 'cluster', 'team_num', 'starttime', 'endtime', '_submission_time', '_uuid'}:
            raise ValueError #TODO: log error
        converted_json = {
            "uuid": self.contents['_uuid'],
            "syncDate": self.contents['_submission_time'],
            "startTime": self.contents['starttime'],
            "created": self.contents['_submission_time'],
            "_rev": str(uuid.uuid4()), # TODO: Using a UUID here for now. not sure this is good enough.
            "modified": self.contents['_submission_time'],
            "householdID": self.contents['hh_number'],
            "cluster": self.contents['cluster'],
            "endTime": self.contents['endtime'],
            "location": [
                self.contents['_gps_latitude'],
                self.contents['_gps_longitude']
            ],
            "members": [],
            "team": FakeTeams.objects.get_or_create(team_id = self.contents['team_num']),
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
                "created": datetime.now().isoformat(),
                "_rev": str(uuid.uuid4()), # TODO: Using a UUID here for now. not sure this is good enough.
                "modified": datetime.now().isoformat(),
                "teamID": self.team_id,
                "members":[
                    {
                        "designation":"Team Leader",
                        "firstName":team_leader[0][0],
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
