from rest_framework import serializers
from django.contrib.auth.models import User

from .models import Alert, HouseholdSurveyJSON, TeamMember



class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = [ 'url', 'username', 'email']


class SimpleUserSerializer(UserSerializer):
    class Meta:
        model = User
        fields = [ 'username', 'email' ]


class TeamMemberSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = TeamMember
        fields = [ 'url', 'id', 'name', 'phone', 'email']


class HouseholdSurveyJSONSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = HouseholdSurveyJSON


class AlertSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Alert
        fields = (

            'url',

            'id',

            # fields
            'category',
            'text',
            'archived',
            'created',
            'completed',

            # TODO fields still in json
            'team_id',
            'team_name',
            'cluster_id',
            'location',
            'type',
            'survey_id',
        )
