from rest_framework import serializers
from django.contrib.auth.models import User

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
            'first_name',
            'gender',
            'muac',
            'birthdate',
            'weight',
            'height',
        ]


class HouseholdSurveyJSONSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = HouseholdSurveyJSON
        extra_kwargs = {
            'team_lead': {'lookup_field': 'member_id'},
            'team_assistant': {'lookup_field': 'member_id'},
            'team_anthropometrist': {'lookup_field': 'member_id'},
        }
        fields = (
            'url',
            'uuid',
            'household_number',
            'members',
            'team_lead',
            'team_assistant',
            'team_anthropometrist',
        )


class TeamMemberSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='teammember-detail',
                                               lookup_field="member_id")
    mobile = serializers.CharField()
    memberID = serializers.CharField(source='member_id', read_only=True)
    last_survey = HouseholdSurveyJSONSerializer(many=False, read_only=True)

    class Meta:

        model = TeamMember
        fields = ['url',
                  'memberID',
                  'first_name',
                  'last_name',
                  'gender',
                  'birth_year',
                  'mobile',
                  'last_survey_position',
                  'last_survey_created',
                  'last_survey_cluster',
                  'last_survey_cluster_name',
                  'last_survey',
                  'email',
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

        extra_kwargs = {
            'team_lead': {
                'lookup_field': 'member_id'
            },
        }
