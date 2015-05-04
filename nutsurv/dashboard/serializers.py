from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_gis.serializers import GeoModelSerializer

from .models import Alert, HouseholdSurveyJSON, TeamMember, HouseholdMember


class JSONSerializerField(serializers.Field):
    """ Serializer for JSONField -- required to make field writable"""
    def to_internal_value(self, data):
        return data

    def to_representation(self, value):
        return value


class UserSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = User
        fields = ['url', 'username', 'email']


class SimpleUserSerializer(UserSerializer):

    class Meta:
        model = User
        fields = ['username', 'email']


class HouseholdMemberSerializer(serializers.HyperlinkedModelSerializer):
    extra_questions = JSONSerializerField()

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
            'extra_questions',
            'household_survey',
        ]


class HouseholdSurveyJSONSerializer(serializers.HyperlinkedModelSerializer, GeoModelSerializer):
    members = HouseholdMemberSerializer(many=True, read_only=False)

    def create(self, validated_data):

        family_members = validated_data.pop('members', [])
        instance = super(HouseholdSurveyJSONSerializer, self).create(validated_data)
        validated_data['members'] = family_members
        self.update(instance, validated_data)

        return instance

    def update(self, instance, validated_data):

        family_members = validated_data.pop('members', [])
        super(HouseholdSurveyJSONSerializer, self).update(instance, validated_data)
        instance.members.all().delete()
        new_family = [HouseholdMember(household_survey=instance, **family_member)
                      for family_member in family_members]

        HouseholdMember.objects.bulk_create(new_family)

        return instance

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


class SimpleTeamMemberSerializer(TeamMemberSerializer):
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
                  ]


class AlertSerializer(serializers.HyperlinkedModelSerializer):
    team_lead = SimpleTeamMemberSerializer(many=False, read_only=True)

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
