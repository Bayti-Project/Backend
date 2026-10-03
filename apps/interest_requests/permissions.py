from rest_framework.permissions import BasePermission


class IsTenant(BasePermission):
    message = 'Only tenants can send interest requests.'

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == 'tenant'
        )