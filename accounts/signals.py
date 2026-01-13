from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models.signals import post_save, post_migrate
from django.dispatch import receiver

from .models import Profile
from .constants import ROLE_TO_GROUP

User = get_user_model()


@receiver(post_migrate)
def create_role_groups(sender, **kwargs):
    """
    Ensure role groups exist AFTER migrations are applied (safe time to touch DB).
    """
    for group_name in set(ROLE_TO_GROUP.values()):
        Group.objects.get_or_create(name=group_name)


@receiver(post_save, sender=User)
def create_profile_and_role_group(sender, instance: User, created: bool, **kwargs):
    if created:
        profile = Profile.objects.create(user=instance)
    else:
        profile, _ = Profile.objects.get_or_create(user=instance)

    # Assign group according to profile.role
    desired_group_name = ROLE_TO_GROUP.get(profile.role)
    if desired_group_name:
        # remove from other role groups
        role_groups = Group.objects.filter(name__in=ROLE_TO_GROUP.values())
        instance.groups.remove(*role_groups)

        # add desired group
        desired_group, _ = Group.objects.get_or_create(name=desired_group_name)
        instance.groups.add(desired_group)


@receiver(post_save, sender=Profile)
def sync_groups_when_profile_changes(sender, instance: Profile, created: bool, **kwargs):
    user = instance.user
    desired_group_name = ROLE_TO_GROUP.get(instance.role)
    if desired_group_name:
        role_groups = Group.objects.filter(name__in=ROLE_TO_GROUP.values())
        user.groups.remove(*role_groups)

        desired_group, _ = Group.objects.get_or_create(name=desired_group_name)
        user.groups.add(desired_group)
