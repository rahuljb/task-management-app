from django import forms
from django.contrib.auth import get_user_model
from django.utils import timezone

from accounts.constants import ROLE_ADMIN, ROLE_SUPERADMIN, ROLE_USER
from tasks.models import Task

User = get_user_model()


class CreateUserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    role = forms.ChoiceField(choices=[
        (ROLE_USER, "User"),
        (ROLE_ADMIN, "Admin"),
        (ROLE_SUPERADMIN, "SuperAdmin"),
    ])

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.is_active = True
        if commit:
            user.save()
        return user


class ChangeRoleForm(forms.Form):
    role = forms.ChoiceField(choices=[
        (ROLE_USER, "User"),
        (ROLE_ADMIN, "Admin"),
        (ROLE_SUPERADMIN, "SuperAdmin"),
    ])


class AssignUserToAdminForm(forms.Form):
    admin = forms.ModelChoiceField(queryset=User.objects.none())
    user = forms.ModelChoiceField(queryset=User.objects.none())

    def __init__(self, *args, **kwargs):
        admins_qs = kwargs.pop("admins_qs")
        users_qs = kwargs.pop("users_qs")
        super().__init__(*args, **kwargs)
        self.fields["admin"].queryset = admins_qs
        self.fields["user"].queryset = users_qs


class TaskCreateForm(forms.ModelForm):
    due_date = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "placeholder": "YYYY-MM-DD",
            }
        ),
    )

    class Meta:
        model = Task
        fields = ["title", "description", "assigned_to", "due_date", "status"]

    def clean_due_date(self):
        due = self.cleaned_data.get("due_date")
        # no past dates allowed
        if due and due < timezone.now().date():
            raise forms.ValidationError("Due date cannot be in the past.")
        return due


class TaskUpdateForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["status", "completion_report", "worked_hours"]

    def clean(self):
        cleaned = super().clean()
        status = cleaned.get("status")

        if status == Task.Status.COMPLETED:
            if not cleaned.get("completion_report"):
                self.add_error("completion_report", "Required when completing a task.")
            hours = cleaned.get("worked_hours")
            if hours is None or hours <= 0:
                self.add_error("worked_hours", "Must be > 0 when completing a task.")
        return cleaned
