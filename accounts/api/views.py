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
    """Creates access and refresh tokens for a given user.

    Args:
        user: A registered and active user.

    Returns:
        dict[str, str]: Dictionary with the keys "access" and "refresh".
    """

    if not user.is_active:
        raise AuthenticationFailed("User is not active")

    refresh = RefreshToken.for_user(user)

    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


def set_tokens_as_cookies(response, tokens):
    """Sets the access and refresh tokens as HttpOnly cookies on the response.

    Args:
        response: DRF Response object the cookies are set on.
        tokens: Dictionary with the keys "access" and "refresh".
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
    """Registration view that creates a new user and logs them in directly
    by setting access/refresh tokens as HttpOnly cookies."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Creates a new user and sets access/refresh tokens as HttpOnly
        cookies, so the user is logged in immediately."""

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
    """Login view that returns JWT access and refresh tokens as HttpOnly
    cookies instead of in the response body.

    Inherits from TokenObtainPairView (SimpleJWT) and overrides post() to
    set the tokens as cookies after successful authentication instead of
    exposing them in the JSON body (protection against XSS access to the
    tokens).
    """

    permission_classes = [AllowAny]
    serializer_class = CookieTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        """Authenticates the user and sets access/refresh tokens as
        HttpOnly cookies."""
        response = super().post(request, *args, **kwargs)

        access = response.data.get("access")
        refresh = response.data.get("refresh")
        user = response.data.get("user")

        set_tokens_as_cookies(response, {"access": access, "refresh": refresh})

        response.data = {"detail": "Login successfully!", "user": user}
        return response


class LogoutView(APIView):
    """Logs the user out by blacklisting the refresh token and deleting
    both token cookies."""

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """Blacklists the refresh token from the cookie and deletes the
        access/refresh token cookies."""

        refresh_token = request.COOKIES.get("refresh_token")

        if refresh_token is None:
            return Response(
                {"detail": "Refresh token not found!"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            RefreshToken(refresh_token).blacklist()
        except TokenError:
            return Response(
                {"detail": "Refresh token is invalid!"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        response = Response(
            {
                "detail": "Log-Out successfully! All Tokens will be deleted. Refresh token is now invalid."
            },
            status=status.HTTP_200_OK,
        )

        response.delete_cookie("access_token", samesite="Lax")
        response.delete_cookie("refresh_token", samesite="Lax")

        return response


class CookieTokenRefreshView(TokenRefreshView):
    """Refresh view that reads the refresh token from the cookie instead of
    the request body and sets the new access token again as an HttpOnly
    cookie."""

    def post(self, request, *args, **kwargs):
        """Reads the refresh token from the cookie, validates it and sets a
        new access token as an HttpOnly cookie."""

        refresh_token = request.COOKIES.get("refresh_token")

        if refresh_token is None:
            return Response(
                {"detail": "Refresh token not found!"},
                status=status.HTTP_401_UNAUTHORIZED,
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

        response = Response({"detail": "Token refreshed"}, status=status.HTTP_200_OK)
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=not settings.DEBUG,
            samesite="Lax",
        )
        return response
