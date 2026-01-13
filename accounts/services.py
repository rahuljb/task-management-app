from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model

from .constants import ROLE_TO_GROUP, GROUP_ADMIN, GROUP_SUPERADMIN, GROUP_USER

User = get_user_model()


def ensure_role_groups_exist():
    """
    Create groups if they don't exist. You can call this from AppConfig.ready().
    """
    for group_name in [GROUP_SUPERADMIN, GROUP_ADMIN, GROUP_USER]:
        Group.objects.get_or_create(name=group_name)


def set_user_group_for_role(user: User, role: str):
    """
    Ensure user is in exactly one role group based on role.
    """
    ensure_role_groups_exist()

    desired_group_name = ROLE_TO_GROUP[role]
    desired_group = Group.objects.get(name=desired_group_name)

    # remove user from all role groups
    role_groups = Group.objects.filter(name__in=ROLE_TO_GROUP.values())
    user.groups.remove(*role_groups)

    # add to desired group
    user.groups.add(desired_group)
