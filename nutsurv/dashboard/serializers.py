from rest_framework import serializers

from .models import Alert

class AlertSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Alert
        fields = (

            'url',

            # fields
            'category',
            'text',
            'archived',

            # TODO fields still in json
            'team_id',
            'team_name',
            'cluster_id',
            'location',
            'type',
            'survey_id',
        )
