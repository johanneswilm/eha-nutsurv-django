import uuid, random, json

from django.db import models

from jsonfield import JSONField

class FormhubData(models.Model):
    contents = JSONField(null=True, blank=True, help_text=' ')
    uuid = models.CharField(max_length=256,unique=True)

    def __unicode__(self):
        return self.uuid

    class Meta:
        verbose_name_plural = 'Formhub Data Entries'


class FakeTeams(models.Model):
    """The data from Formhub comes without team member data. For the test
    import through CSV we therefore create fake teams with random team members.
    This should likely be removed before import data from formhub for realworld
    usage.
    """

    contents = JSONField(null=True, blank=True, help_text=' ')
    team_id = models.IntegerField(unique=True)

    def __unicode__(self):
        return self.team_id

    def save(self, *args, **kwargs):
        if not self.contents:
            self.contents = json.loads('{\
            "uuid":"'+str(uuid.uuid4())+'",\
            "created":"2015-02-02T09:57:54.704Z",\
            "_rev":"1-38fe619147fc30ece77cf3ae04b3de78",\
            "modified":"2015-02-02T09:57:54.704Z",\
            "teamID":' + str(self.team_id) + ',\
            "members":[\
            {\
            "designation":"Team Leader",\
            "firstName":"Abubakar",\
            "mobile":"080768884455",\
            "lastName":"Usman",\
            "age":' + str(random.randint(30, 58)) + ',\
            "memberID":' + str(self.team_id * 3) + ',\
            "gender":"M",\
            "email":"abu@gmail.com"\
            },\
            {\
            "designation":"Anthropometrist",\
            "firstName":"Gregory",\
            "mobile":"080766433555",\
            "lastName":"Benson",\
            "age":' + str(random.randint(24, 42)) + ',\
            "memberID":' + str(self.team_id * 3 + 1) + ',\
            "gender":"M",\
            "email":"benson@yahoo.com"\
            },\
            {\
            "designation":"Assistant",\
            "firstName":"Femi",\
            "mobile":"08087874885884",\
            "lastName":"Oni",\
            "age":'+ str(random.randint(17, 35))+',\
            "memberID":'+ str(self.team_id * 3 + 2) + ',\
            "gender":"M",\
            "email":"femi@oni.com"\
            }\
            ],\
            "_id":"'+str(uuid.uuid4())+'"\
            },')
            super(FakeTeams, self).save(*args, **kwargs)
