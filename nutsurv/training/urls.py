from django.conf.urls import include, patterns, url

from rest_framework import routers

from .views import TrainingSurveyViewset, TrainingSessionViewset, TrainingSubjectViewset

router = routers.DefaultRouter()
router.register(r'surveys', TrainingSurveyViewset)
router.register(r'sessions', TrainingSessionViewset)
router.register(r'members', TrainingSubjectViewset)

urlpatterns = patterns('',
                       url(r'^', include(router.urls)),
                       )
