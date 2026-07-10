from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class RegistrationSerializer(serializers.ModelSerializer):
    """serializer für die Registrierung eines neuen Benutzers."""

    password = serializers.CharField(write_only=True)
    confirmed_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("username", "email", "password", "confirmed_password")

    def validate(self, data):
        """prüft ob die eingegbenen passwörter übereinstimmen"""

        if data["password"] != data["confirmed_password"]:
            raise serializers.ValidationError(
                {"password_confirm": "Die Passwörter stimmen nicht überein."}
            )

        return data

    def validate_email(self, value):
        """prüft ob die Email schon existiert"""

        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Diese Email existiert bereits.")

        return value

    def create(self, validated_data):
        """
        erstellt einen neuen Benutzer mit den validierten Daten und verschlüsselt
        das Passwort.
        """

        user = User(username=validated_data["username"], email=validated_data["email"])
        user.set_password(validated_data["password"])
        user.save()
        return user


class CookieTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    serializer, der die Standard-TokenObtainPairSerializer von SimpleJWT
    erweitert, um zusätzliche Informationen über den authentifizierten Benutzer
    zurückzugeben.
    """

    def validate(self, data):
        """
        validiert die Login date und gibt die Token zusammen mit den
        Benutzerinformationen zurück.
        """

        data = super().validate(data)

        data["user"] = {
            "id": self.user.id,
            "username": self.user.username,
            "email": self.user.email,
        }
        return data
