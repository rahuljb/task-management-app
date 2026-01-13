from rest_framework.permissions import BasePermission
from accounts.permissions import is_admin, is_superadmin


class IsAdminOrSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return is_admin(request.user) or is_superadmin(request.user)


class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return is_superadmin(request.user)
