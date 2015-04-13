
from django.conf import settings
from django.db import models

from dashboard.models import BaseHouseholdSurveyJSON
from dashboard.models import BaseHouseholdMember

class TrainingRoom(models.Model):

    creator = models.ForeignKey(settings.AUTH_USER_MODEL)
    created = models.DateTimeField(auto_now_add=True)

class TrainingSurvey(BaseHouseholdSurveyJSON):
    pass

class TrainingRoomMember(BaseHouseholdMember):
    household_survey = models.ForeignKey('TrainingSurvey', related_name='members')
