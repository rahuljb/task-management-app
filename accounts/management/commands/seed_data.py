from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from accounts.constants import ROLE_SUPERADMIN, ROLE_ADMIN, ROLE_USER
from tasks.models import Task

User = get_user_model()


class Command(BaseCommand):
    help = "Seed sample users, admins, and tasks"

    def handle(self, *args, **options):
        # SuperAdmin
        superadmin, _ = User.objects.get_or_create(username="superadmin")
        superadmin.set_password("pass123")
        superadmin.is_active = True
        superadmin.save()
        superadmin.profile.role = ROLE_SUPERADMIN
        superadmin.profile.assigned_admin = None
        superadmin.profile.save()

        # Admin
        admin, _ = User.objects.get_or_create(username="admin1")
        admin.set_password("pass123")
        admin.is_active = True
        admin.save()
        admin.profile.role = ROLE_ADMIN
        admin.profile.assigned_admin = None
        admin.profile.save()

        # Users
        for username in ["user1", "user2"]:
            user, _ = User.objects.get_or_create(username=username)
            user.set_password("pass123")
            user.is_active = True
            user.save()
            user.profile.role = ROLE_USER
            user.profile.assigned_admin = admin
            user.profile.save()

        # Task
        user1 = User.objects.get(username="user1")
        Task.objects.get_or_create(
            title="Sample Task",
            assigned_to=user1,
            defaults={
                "description": "Complete assigned feature",
                "status": Task.Status.PENDING,
            },
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Seed data created:\n"
                "superadmin / pass123\n"
                "admin1 / pass123\n"
                "user1 / pass123\n"
                "user2 / pass123"
            )
        )
