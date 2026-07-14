from rest_framework.permissions import BasePermission


class IsQuizOwner(BasePermission):
    """Object permission: only allows access if the quiz belongs to the request user."""

    def has_object_permission(self, request, view, obj):
        """Checks whether obj.user matches the logged-in user."""
        return obj.user == request.user
