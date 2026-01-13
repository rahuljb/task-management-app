from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from accounts.constants import ROLE_ADMIN, ROLE_SUPERADMIN, ROLE_USER
from accounts.permissions import is_admin, is_superadmin
from tasks.models import Task
from .forms import (
    AssignUserToAdminForm,
    ChangeRoleForm,
    CreateUserForm,
    TaskCreateForm,
    TaskUpdateForm,
)

User = get_user_model()


# ---------------- Auth ----------------
def panel_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("panel_dashboard")

        return render(request, "adminpanel/login.html", {"error": "Invalid credentials"})

    return render(request, "adminpanel/login.html")


@login_required
def panel_logout(request):
    logout(request)
    return redirect("panel_login")


@login_required
def dashboard(request):
    return render(request, "adminpanel/dashboard.html")


# ---------------- Helpers ----------------
def superadmin_required(request):
    if not is_superadmin(request.user):
        return False
    return True


def admin_or_superadmin_required(request):
    if not (is_admin(request.user) or is_superadmin(request.user)):
        return False
    return True


# ---------------- SuperAdmin: Users/Admins ----------------
@login_required
def users_list(request):
    if not superadmin_required(request):
        return HttpResponseForbidden("SuperAdmin only")

    users = User.objects.select_related("profile", "profile__assigned_admin").order_by("username")
    return render(request, "adminpanel/users_list.html", {"users": users})


@login_required
def user_create(request):
    if not superadmin_required(request):
        return HttpResponseForbidden("SuperAdmin only")

    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            role = form.cleaned_data["role"]

            user.profile.role = role
            if role != ROLE_USER:
                user.profile.assigned_admin = None
            user.profile.save()

            messages.success(request, f"Created {user.username} as {role}")
            return redirect("panel_users_list")
    else:
        form = CreateUserForm()

    return render(request, "adminpanel/user_create.html", {"form": form})


@login_required
def user_delete(request, id):
    if not superadmin_required(request):
        return HttpResponseForbidden("SuperAdmin only")

    target = get_object_or_404(User, id=id)

    # Professional safety: prevent deleting self
    if target.id == request.user.id:
        return HttpResponseForbidden("You cannot delete your own account.")

    if request.method == "POST":
        username = target.username
        target.delete()
        messages.success(request, f"Deleted user {username}")
        return redirect("panel_users_list")

    return render(request, "adminpanel/user_confirm_delete.html", {"target": target})


@login_required
def user_change_role(request, id):
    if not superadmin_required(request):
        return HttpResponseForbidden("SuperAdmin only")

    target = get_object_or_404(User, id=id)

    if request.method == "POST":
        form = ChangeRoleForm(request.POST)
        if form.is_valid():
            new_role = form.cleaned_data["role"]

            profile = target.profile
            profile.role = new_role

            # If not USER, clear assignment
            if new_role != ROLE_USER:
                profile.assigned_admin = None

            try:
                profile.save()
                messages.success(request, f"Role updated for {target.username} -> {new_role}")
                return redirect("panel_users_list")
            except Exception as e:
                messages.error(request, f"Could not update role: {e}")
    else:
        form = ChangeRoleForm(initial={"role": target.profile.role})

    return render(request, "adminpanel/user_change_role.html", {"form": form, "target": target})


@login_required
def assign_user_to_admin(request):
    if not superadmin_required(request):
        return HttpResponseForbidden("SuperAdmin only")

    admins_qs = User.objects.filter(profile__role=ROLE_ADMIN).order_by("username")
    users_qs = User.objects.filter(profile__role=ROLE_USER).order_by("username")

    if request.method == "POST":
        form = AssignUserToAdminForm(request.POST, admins_qs=admins_qs, users_qs=users_qs)
        if form.is_valid():
            admin = form.cleaned_data["admin"]
            user = form.cleaned_data["user"]

            user.profile.assigned_admin = admin
            user.profile.save()

            messages.success(request, f"Assigned {user.username} to admin {admin.username}")
            return redirect("panel_users_list")
    else:
        form = AssignUserToAdminForm(admins_qs=admins_qs, users_qs=users_qs)

    return render(request, "adminpanel/assign_user_to_admin.html", {"form": form})


# ---------------- Tasks: Admin + SuperAdmin ----------------
@login_required
def tasks_list(request):
    if not admin_or_superadmin_required(request):
        return HttpResponseForbidden("Admin/SuperAdmin only")

    if is_superadmin(request.user):
        tasks = Task.objects.select_related("assigned_to").all().order_by("-updated_at")
    else:
        tasks = Task.objects.select_related("assigned_to").filter(
            assigned_to__profile__assigned_admin=request.user
        ).order_by("-updated_at")

    return render(request, "adminpanel/tasks_list.html", {"tasks": tasks})


@login_required
def task_create(request):
    if not admin_or_superadmin_required(request):
        return HttpResponseForbidden("Admin/SuperAdmin only")

    if request.method == "POST":
        form = TaskCreateForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)

            # Admin can assign only to their users
            if is_admin(request.user):
                if task.assigned_to.profile.assigned_admin_id != request.user.id:
                    return HttpResponseForbidden("You can assign tasks only to your users.")

            task.save()
            messages.success(request, "Task created")
            return redirect("panel_tasks_list")
    else:
        form = TaskCreateForm()

        # Admin sees only their users in dropdown
        if is_admin(request.user):
            form.fields["assigned_to"].queryset = User.objects.filter(
                profile__role=ROLE_USER,
                profile__assigned_admin=request.user,
            )

    return render(request, "adminpanel/task_create.html", {"form": form})


@login_required
def task_detail(request, id):
    if not admin_or_superadmin_required(request):
        return HttpResponseForbidden("Admin/SuperAdmin only")

    task = get_object_or_404(Task, id=id)

    if is_admin(request.user):
        if task.assigned_to.profile.assigned_admin_id != request.user.id:
            return HttpResponseForbidden("Not allowed.")

    return render(request, "adminpanel/task_detail.html", {"task": task})


@login_required
def task_update(request, id):
    if not admin_or_superadmin_required(request):
        return HttpResponseForbidden("Admin/SuperAdmin only")

    task = get_object_or_404(Task, id=id)

    if is_admin(request.user):
        if task.assigned_to.profile.assigned_admin_id != request.user.id:
            return HttpResponseForbidden("Not allowed.")

    if request.method == "POST":
        form = TaskUpdateForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, "Task updated")
            return redirect("panel_task_detail", id=task.id)
    else:
        form = TaskUpdateForm(instance=task)

    return render(request, "adminpanel/task_update.html", {"form": form, "task": task})
