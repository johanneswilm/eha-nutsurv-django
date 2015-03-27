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
