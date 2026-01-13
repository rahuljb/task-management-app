from django.urls import path
from .views import TaskListView, TaskUpdateView, TaskReportView

urlpatterns = [
    path("tasks/", TaskListView.as_view(), name="tasks_list"),
    path("tasks/<int:id>/", TaskUpdateView.as_view(), name="tasks_update"),
    path("tasks/<int:id>/report/", TaskReportView.as_view(), name="tasks_report"),
]
