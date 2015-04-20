from rest_framework import viewsets
from rest_framework.response import Response

from .models import TrainingSurvey, TrainingRoom, TrainingRoomMember
from .serializers import TrainingSurveySerializer, TrainingSurveySerializerWithMemberDetails, TrainingRoomSerializer, TrainingRoomMemberSerializer


class TrainingRoomMemberViewset(viewsets.ModelViewSet):
    queryset = TrainingRoomMember.objects.all()
    serializer_class = TrainingRoomMemberSerializer


class TrainingSurveyViewset(viewsets.ModelViewSet):
    queryset = TrainingSurvey.objects.all()
    serializer_class = TrainingSurveySerializer
    permission_classes = ()  # Allow Any


class TrainingRoomViewset(viewsets.ModelViewSet):
    queryset = TrainingRoom.objects.all().order_by('-created')
    serializer_class = TrainingRoomSerializer

    template_name = 'training/room_list.html'

    def retrieve(self, request, pk=None, format=None):

        instance = TrainingRoom.objects.get(pk=pk)
        instance_serializer = TrainingRoomSerializer(
            instance,
            context={
                'request': request
            },
        )

        SurveySerializer = TrainingSurveySerializer
        if 'member_detail' in request.GET:
            SurveySerializer = TrainingSurveySerializerWithMemberDetails

        surveys = TrainingSurvey.objects.filter(household_number=pk)
        survey_serializer = SurveySerializer(
            surveys,
            many=True,
            context={
                'request': request
            },
        )

        data = instance_serializer.data
        data['surveys'] = survey_serializer.data

        return Response(data, template_name='training/room_detail.html')
