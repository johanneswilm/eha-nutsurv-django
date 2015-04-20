from django.conf.urls import include, patterns, url

from rest_framework import routers

from .views import TrainingSurveyViewset, TrainingRoomViewset, TrainingRoomMemberViewset

router = routers.DefaultRouter()
router.register(r'surveys', TrainingSurveyViewset)
router.register(r'rooms', TrainingRoomViewset)
router.register(r'members', TrainingRoomMemberViewset)

urlpatterns = patterns('',
                       url(r'^', include(router.urls)),
                       )
