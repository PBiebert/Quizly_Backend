from rest_framework.permissions import BasePermission


class IsQuizOwner(BasePermission):
    """Objekt-Permission: erlaubt Zugriff nur, wenn das Quiz dem Request-User gehört."""

    def has_object_permission(self, request, view, obj):
        """Prüft, ob obj.user mit dem eingeloggten User übereinstimmt.

        Args:
            request: Der aktuelle Request mit dem authentifizierten User.
            view: Die aufrufende View (ungenutzt).
            obj: Die Quiz-Instanz, deren Owner geprüft wird.

        Returns:
            True, wenn obj.user == request.user, sonst False (führt zu 403).
        """
        return obj.user == request.user
