from rest_framework.permissions import BasePermission


class IsQuizOwner(BasePermission):
    """Objekt-Permission: erlaubt Zugriff nur, wenn das Quiz dem Request-User gehört."""

    def has_object_permission(self, request, view, obj):
        """Prüft, ob obj.user mit dem eingeloggten User übereinstimmt."""
        return obj.user == request.user
