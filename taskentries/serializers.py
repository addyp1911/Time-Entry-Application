from rest_framework import serializers
from authentication.serializers import *
from .models import *


class TaskSerializer(serializers.ModelSerializer):
    user = UserShowSerializer(many=False, read_only=True, )

    class Meta:
        model = TaskEntry
        fields = '__all__'


class ProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = '__all__'


class TimeEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeEntry
        fields = '__all__'