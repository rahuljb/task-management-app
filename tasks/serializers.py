from rest_framework import serializers
from .models import Task


class TaskListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["id", "title", "description", "due_date", "status", "created_at", "updated_at"]


class TaskUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["status", "completion_report", "worked_hours"]

    def validate(self, attrs):
        if attrs.get("status") != Task.Status.COMPLETED:
            return attrs

        report = attrs.get("completion_report")
        hours = attrs.get("worked_hours")

        if not report or not report.strip():
            raise serializers.ValidationError({"completion_report": "Required when completing a task."})
        if hours is None or hours <= 0:
            raise serializers.ValidationError({"worked_hours": "Must be > 0 when completing a task."})

        return attrs


class TaskReportSerializer(serializers.ModelSerializer):
    assigned_to = serializers.CharField(source="assigned_to.username", read_only=True)

    class Meta:
        model = Task
        fields = ["id", "title", "assigned_to", "status", "completion_report", "worked_hours", "updated_at"]
