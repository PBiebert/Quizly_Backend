import token

from django.conf import settings
from regex import R
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import CookieTokenObtainPairSerializer, RegistrationSerializer


def get_tokens_for_user(user):
    """Erzeugt Access- und Refresh-Token für einen gegebenen User.

    Args:
        user: Registrierter und aktiver User.

    Returns:
        dict[str, str]: Dictionary mit den Schlüsseln "access" und "refresh".
    """

    if not user.is_active:
        raise AuthenticationFailed("User is not active")

    refresh = RefreshToken.for_user(user)

    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


def set_tokens_as_cookies(response, tokens):
    """Setzt die Access- und Refresh-Token als HttpOnly-Cookies im Response-Objekt.

    Args:
        response: DRF-Response-Objekt, auf dem die Cookies gesetzt werden.
        tokens: Dictionary mit den Schlüsseln "access" und "refresh".
    """

    response.set_cookie(
        key="access_token",
        value=tokens["access"],
        httponly=True,
        secure=not settings.DEBUG,
        samesite="Lax",
    )

    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh"],
        httponly=True,
        secure=not settings.DEBUG,
        samesite="Lax",
    )


class RegistrationView(APIView):
    """Registrierungs-View, die einen neuen User anlegt und ihn direkt
    einloggt, indem Access-/Refresh-Token als HttpOnly-Cookies gesetzt werden."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Legt einen neuen User an und setzt Access-/Refresh-Token als
        HttpOnly-Cookies, sodass der User direkt eingeloggt ist."""

        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            tokens = get_tokens_for_user(user)

            response = Response(
                {"detail": "User created successfully!"},
                status=status.HTTP_201_CREATED,
            )

            set_tokens_as_cookies(response, tokens)
            return response

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(TokenObtainPairView):
    """Login-View, die JWT Access- und Refresh-Token statt im Response-Body
    als HttpOnly-Cookies zurückgibt.

    Erbt von TokenObtainPairView (SimpleJWT) und überschreibt post(), um die
    Token nach erfolgreicher Authentifizierung in Cookies zu setzen anstatt
    sie im JSON-Body preiszugeben (Schutz vor XSS-Zugriff auf die Token).
    """

    permission_classes = [AllowAny]
    serializer_class = CookieTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        """Authentifiziert den User und setzt Access-/Refresh-Token als
        HttpOnly-Cookies."""
        response = super().post(request, *args, **kwargs)

        access = response.data.get("access")
        refresh = response.data.get("refresh")
        user = response.data.get("user")

        set_tokens_as_cookies(response, {"access": access, "refresh": refresh})

        response.data = {"detail": "Login successfully!", "user": user}
        print(request.COOKIES)
        return response


class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        token = RefreshToken(request.COOKIES.get("refresh_token"))
        token.blacklist()

        response = Response(
            {
                "detail": "Abmeldung erfolgreich! Alle Tokens werden gelöscht. Das Refresh-Token ist nun ungültig."
            }
        )

        response.delete_cookie("access_token", samesite="Lax")
        response.delete_cookie("refresh_token", samesite="Lax")

        return response
