from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.panel_login, name="panel_login"),
    path("logout/", views.panel_logout, name="panel_logout"),
    path("", views.dashboard, name="panel_dashboard"),

    # SuperAdmin user/admin management
    path("users/", views.users_list, name="panel_users_list"),
    path("users/create/", views.user_create, name="panel_user_create"),
    path("users/<int:id>/delete/", views.user_delete, name="panel_user_delete"),
    path("users/<int:id>/role/", views.user_change_role, name="panel_user_change_role"),
    path("assign-user/", views.assign_user_to_admin, name="panel_assign_user_to_admin"),

    # Tasks (Admin + SuperAdmin)
    path("tasks/", views.tasks_list, name="panel_tasks_list"),
    path("tasks/create/", views.task_create, name="panel_task_create"),
    path("tasks/<int:id>/", views.task_detail, name="panel_task_detail"),
    path("tasks/<int:id>/update/", views.task_update, name="panel_task_update"),
]
