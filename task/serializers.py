from .models import Task
from rest_framework import serializers

class TaskListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = "__all__"