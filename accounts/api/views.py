from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import CookieTokenObtainPairSerializer


class CookieTokenObtainPairView(TokenObtainPairView):
    serializer_class = CookieTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        access = response.data.get("access")
        refresh = response.data.get("refresh")
        user = response.data.get("user")

        # Access-Token als HttpOnly-Cookie
        response.set_cookie(
            key="access_token",
            value=access,
            httponly=True,
            secure=True,
            samesite="Lax",
        )

        # Refresh-Token als HttpOnly-Cookie
        response.set_cookie(
            key="refresh_token",
            value=refresh,
            httponly=True,
            secure=True,
            samesite="Lax",
        )

        # Optional: Token nicht im Response-Body zurückgeben
        response.data = {"detail": "Login successfully!", "user": user}
        return response
