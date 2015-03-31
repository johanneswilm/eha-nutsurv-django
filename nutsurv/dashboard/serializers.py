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
    url = serializers.HyperlinkedIdentityField(view_name='teammember-detail',
                                               lookup_field="member_id")
    mobile = serializers.CharField()
    class Meta:
        model = TeamMember
        fields = ['url',
                  'member_id',
                  'first_name',
                  'last_name',
                  'gender',
                  'year_of_birth',
                  'mobile',
                  'email']


class HouseholdSurveyJSONSerializer(serializers.HyperlinkedModelSerializer):
    team_lead = serializers.HyperlinkedIdentityField(view_name='teammember-detail',
                                               lookup_field="member_id")
    team_assistant = serializers.HyperlinkedIdentityField(view_name='teammember-detail',
                                               lookup_field="member_id")
    team_anthropometrist = serializers.HyperlinkedIdentityField(view_name='teammember-detail',
                                               lookup_field="member_id")
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
