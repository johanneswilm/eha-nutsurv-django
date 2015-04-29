from rest_framework import viewsets
from rest_framework.response import Response

from .models import TrainingSurvey, TrainingSession, TrainingSubject
from .serializers import TrainingSurveySerializer, TrainingSurveySerializerWithMemberDetails, TrainingSessionSerializer, TrainingSubjectSerializer


class TrainingSubjectViewset(viewsets.ModelViewSet):
    queryset = TrainingSubject.objects.all()
    serializer_class = TrainingSubjectSerializer


class TrainingSurveyViewset(viewsets.ModelViewSet):
    queryset = TrainingSurvey.objects.all()
    serializer_class = TrainingSurveySerializer
    permission_classes = ()  # Allow Any


class TrainingSessionViewset(viewsets.ModelViewSet):
    queryset = TrainingSession.objects.all().order_by('-created')
    serializer_class = TrainingSessionSerializer

    template_name = 'training/session_list.html'

    def retrieve(self, request, pk=None, format=None):

        instance = TrainingSession.objects.get(pk=pk)
        instance_serializer = TrainingSessionSerializer(
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

        return Response(data, template_name='training/session_detail.html')
