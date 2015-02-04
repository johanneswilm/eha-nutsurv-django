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
        converted_json = {
            "uuid":"d7a6fab3-7c41-4257-afac-4583b391cfe2",
            "syncDate":"2015-02-02T10:18:40.829Z",
            "startTime":"2015-02-02T10:14:01.056Z",
            "created":"2015-02-02T10:18:07.903Z",
            "_rev":"5-ca06629e1b7879f9642ee4791cc623ae",
            "modified":"2015-02-02T12:14:08.916Z",
            "householdID":945,
            "cluster":45,
            "endTime":"2015-02-02T10:18:40.270Z",
            "location":[
                12.0201484,
                8.5637308
            ],
            "members":[],
            "team":{},
            "_id":"d7a6fab3-7c41-4257-afac-4583b391cfe2",
            "tools":{
                "scale":{
                    "toolID":876,
                    "measurement":45
                },
                "uuid":"131bfef0-a5b2-4f6a-f717-d9e2572b65d9",
                "created":"2015-02-02T10:05:26.745Z",
                "_rev":"1-39cf84d5c729b84d3fd8e1bbc6bff78b",
                "childMUAC":{
                    "toolID":557,
                    "measurement":76
                },
                "modified":"2015-02-02T10:05:26.745Z",
                "heightBoard":{
                    "toolID":24,
                    "measurement":23
                },
                "_id":"131bfef0-a5b2-4f6a-f717-d9e2572b65d9",
                "adultMUAC":{
                    "toolID":145,
                    "measurement":43
                }},
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
