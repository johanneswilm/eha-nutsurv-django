from rest_framework import serializers

from .models import Alert, HouseholdSurveyJSON

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

            # TODO fields still in json
            'team_id',
            'team_name',
            'cluster_id',
            'location',
            'type',
            'survey_id',
        )
