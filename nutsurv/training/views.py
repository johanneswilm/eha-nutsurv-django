from django.shortcuts import render, get_object_or_404

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import detail_route
from rest_framework.reverse import reverse

from .models import TrainingSurvey, TrainingRoom
from .serializers import TrainingSurveySerializer, TrainingRoomSerializer


class TrainingSurveyViewset(viewsets.ModelViewSet):
    queryset = TrainingSurvey.objects.all()
    serializer_class = TrainingSurveySerializer

class TrainingRoomViewset(viewsets.ModelViewSet):
    queryset = TrainingRoom.objects.all().order_by('-created')
    serializer_class = TrainingRoomSerializer

    template_name = 'training/room_list.html'

    def retrieve(self, request, pk=None, format=None):
        queryset = TrainingRoom.objects.all()
        instance = get_object_or_404(queryset, pk=pk)
        instance_serializer = TrainingRoomSerializer(
            instance,
            context={
              'request':request
            },
        )

        surveys = TrainingSurvey.objects.filter(household_number=pk)
        survey_serializer = TrainingSurveySerializer(
            surveys,
            many=True,
            context={
                'request':request
            },
        )

        data = instance_serializer.data
        data['surveys'] = survey_serializer.data

        return Response(data, template_name='training/room_detail.html')
