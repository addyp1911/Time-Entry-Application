from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register('taskentry', TaskAction, basename="taskentry")
router.register('project', ProjectAction, basename="project")
router.register('timeentry', TimeEntryAction, basename="timeentry")

urlpatterns = [
    path('', include(router.urls))
]