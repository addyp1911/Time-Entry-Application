from rest_framework import permissions


class IsSuperAdminOrStaff(permissions.BasePermission):
    """
    A custom class to check if user is admin or staff
    """
    def has_permission(self, request, view):
        return request.user.is_staff or request.user.is_superuser


class BaseViewSetPermissionMixin:
    def get_permissions(self):
        if self.action in ['login', 'register']:
            permission_class = []
        else:
            permission_class = [
                permissions.IsAuthenticated
            ]
        return [permission() for permission in permission_class]
