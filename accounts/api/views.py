from django.conf import settings
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import AuthenticationFailed, TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

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
        return response


class LogoutView(APIView):
    """Loggt den User aus, indem das Refresh-Token blacklisted und beide
    Token-Cookies gelöscht werden."""

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """Blacklistet das Refresh-Token aus dem Cookie und löscht die
        Access-/Refresh-Token-Cookies."""

        refresh_token = request.COOKIES.get("refresh_token")

        if refresh_token is None:
            return Response(
                {"detail": "Refresh token not found!"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            RefreshToken(refresh_token).blacklist()
        except TokenError:
            return Response(
                {"detail": "Refresh token is invalid!"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        response = Response(
            {
                "detail": "Abmeldung erfolgreich! Alle Tokens werden gelöscht. Das Refresh-Token ist nun ungültig."
            }
        )

        response.delete_cookie("access_token", samesite="Lax")
        response.delete_cookie("refresh_token", samesite="Lax")

        return response


class CookieTokenRefreshView(TokenRefreshView):
    """Refresh-View, die den Refresh-Token aus dem Cookie statt aus dem
    Request-Body liest und das neue Access-Token wieder als HttpOnly-Cookie
    setzt.

    Nötig, weil der Refresh-Token als HttpOnly-Cookie gespeichert ist und
    daher von JavaScript nicht ausgelesen und in den Request-Body gepackt
    werden kann - die Standard-TokenRefreshView erwartet ihn aber im Body.
    """

    def post(self, request, *args, **kwargs):
        """Liest das Refresh-Token aus dem Cookie, validiert es und setzt
        ein neues Access-Token als HttpOnly-Cookie."""

        refresh_token = request.COOKIES.get("refresh_token")

        if refresh_token is None:
            return Response(
                {"detail": "Refresh token not found!"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data={"refresh": refresh_token})
        try:
            serializer.is_valid(raise_exception=True)
        except (TokenError, ValidationError):
            return Response(
                {"detail": "Refresh token is invalid!"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        access_token = serializer.validated_data.get("access")

        response = Response({"detail": "Access-Token refreshed"})
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=not settings.DEBUG,
            samesite="Lax",
        )
        return response
