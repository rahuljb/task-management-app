from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import is_admin_or_superadmin
from .models import Task
from .serializers import TaskListSerializer, TaskUpdateSerializer, TaskReportSerializer
from .utils import can_view_task_report


class TaskListView(APIView):
    """
    GET /api/tasks/ -> Fetch tasks assigned to logged-in user only.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tasks = Task.objects.filter(assigned_to=request.user).order_by("-updated_at")
        return Response(TaskListSerializer(tasks, many=True).data, status=status.HTTP_200_OK)


class TaskUpdateView(APIView):
    """
    PUT /api/tasks/<id>/ -> Update status of a task (only own task).
    If setting COMPLETED => completion_report and worked_hours required.
    """
    permission_classes = [IsAuthenticated]

    def put(self, request, id):
        task = get_object_or_404(Task, id=id, assigned_to=request.user)

        serializer = TaskUpdateSerializer(task, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(TaskReportSerializer(task).data, status=status.HTTP_200_OK)


class TaskReportView(APIView):
    """
    GET /api/tasks/<id>/report/ -> Admin/SuperAdmin can view report (completed only).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        if not is_admin_or_superadmin(request.user):
            return Response({"detail": "Not authorized."}, status=status.HTTP_403_FORBIDDEN)

        task = get_object_or_404(Task, id=id)

        if task.status != Task.Status.COMPLETED:
            return Response(
                {"detail": "Report is only available for completed tasks."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not can_view_task_report(request.user, task):
            return Response({"detail": "Not authorized for this task."}, status=status.HTTP_403_FORBIDDEN)

        return Response(TaskReportSerializer(task).data, status=status.HTTP_200_OK)
