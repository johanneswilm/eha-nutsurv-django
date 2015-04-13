from django.conf.urls import include, patterns, url

from rest_framework import routers

from .views import TrainingSurveyViewset, TrainingRoomViewset

router = routers.DefaultRouter()
router.register(r'surveys', TrainingSurveyViewset)
router.register(r'rooms', TrainingRoomViewset)

urlpatterns = patterns('',
    url(r'^', include(router.urls)),
)
