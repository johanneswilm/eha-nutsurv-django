from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_gis.serializers import GeoModelSerializer

from .models import Alert, HouseholdSurveyJSON, TeamMember, HouseholdMember


class UserSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = User
        fields = ['url', 'username', 'email']


class SimpleUserSerializer(UserSerializer):

    class Meta:
        model = User
        fields = ['username', 'email']


class HouseholdMemberSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = HouseholdMember
        fields = [
            'index',
            'first_name',
            'gender',
            'muac',
            'birthdate',
            'weight',
            'height',
        ]


class HouseholdSurveyJSONSerializer(serializers.HyperlinkedModelSerializer, GeoModelSerializer):

    class Meta:
        model = HouseholdSurveyJSON
        geo_field = "location"

        fields = (
            'url',
            'uuid',
            'household_number',
            'members',
            'team_lead',
            'team_assistant',
            'team_anthropometrist',
            'first_admin_level',
            'second_admin_level',
            'cluster',
            'cluster_name',
            'start_time',
            'end_time',
            'location',
        )


class TeamMemberSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='teammember-detail')
    mobile = serializers.CharField(required=False)
    last_survey = HouseholdSurveyJSONSerializer(many=False, read_only=True)

    class Meta:

        model = TeamMember
        fields = ['url',
                  'id',
                  'first_name',
                  'last_name',
                  'gender',
                  'birth_year',
                  'mobile',
                  'email',
                  'last_survey',
                  ]


class AlertSerializer(serializers.HyperlinkedModelSerializer):
    team_lead = TeamMemberSerializer(many=False, read_only=True)

    class Meta:
        model = Alert
        fields = (
            'url',
            'id',

            # fields
            'category',
            'archived',
            'created',
            'completed',
            'team_lead',
            'survey',

            # TODO fields still in json
            'cluster_id',
            'location',
            'type',
            'survey_id',
        )
