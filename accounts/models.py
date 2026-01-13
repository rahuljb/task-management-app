from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth import get_user_model

from .constants import ROLE_ADMIN, ROLE_SUPERADMIN, ROLE_USER

User = get_user_model()


class Profile(models.Model):
    class Role(models.TextChoices):
        SUPERADMIN = ROLE_SUPERADMIN, "SuperAdmin"
        ADMIN = ROLE_ADMIN, "Admin"
        USER = ROLE_USER, "User"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.USER,
        db_index=True,
    )

    assigned_admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_users",
        help_text="Admin responsible for this user (scoping).",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.role != self.Role.USER and self.assigned_admin is not None:
            raise ValidationError({"assigned_admin": "Only USER profiles can be assigned to an Admin."})

        if self.assigned_admin is not None:
            admin_profile = getattr(self.assigned_admin, "profile", None)
            if not admin_profile or admin_profile.role != self.Role.ADMIN:
                raise ValidationError({"assigned_admin": "assigned_admin must be a user with ADMIN role."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.user.username} ({self.role})"
