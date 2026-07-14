from rest_framework_simplejwt.authentication import JWTAuthentication


class CookieJWTAuthentication(JWTAuthentication):
    """Authentifiziert Requests über das Access-Token im HttpOnly-Cookie
    statt über den Authorization-Header."""

    def authenticate(self, request):
        """Validiert das access_token-Cookie und ermittelt den zugehörigen User.

        Returns:
            Ein (User, validated_token)-Tupel bei gültigem Token, sonst
            None (kein Cookie vorhanden -> Request bleibt unauthentifiziert).
        """
        raw_token = request.COOKIES.get("access_token")
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token
