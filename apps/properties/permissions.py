from rest_framework.permissions import BasePermission


class IsPropertyOwner(BasePermission):
    """
    Allows access only to the owner of the property object.
    """

    def has_object_permission(self, request, view, obj):
        return request.user == obj.owner