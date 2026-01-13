from .constants import GROUP_ADMIN, GROUP_SUPERADMIN, GROUP_USER


def is_superadmin(user) -> bool:
    return user.is_authenticated and user.groups.filter(name=GROUP_SUPERADMIN).exists()


def is_admin(user) -> bool:
    return user.is_authenticated and user.groups.filter(name=GROUP_ADMIN).exists()


def is_user(user) -> bool:
    return user.is_authenticated and user.groups.filter(name=GROUP_USER).exists()


def is_admin_or_superadmin(user) -> bool:
    return is_admin(user) or is_superadmin(user)
