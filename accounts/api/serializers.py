from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class RegistrationSerializer(serializers.ModelSerializer):
    """Serializer for registering a new user."""

    password = serializers.CharField(write_only=True)
    confirmed_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("username", "email", "password", "confirmed_password")

    def validate(self, data):
        """Checks that the given passwords match."""

        if data["password"] != data["confirmed_password"]:
            raise serializers.ValidationError(
                {"password_confirm": "Passwords do not match."}
            )

        return data

    def validate_email(self, value):
        """Checks that the email is not already registered."""

        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email already exists.")

        return value

    def create(self, validated_data):
        """Creates a new user from the validated data and hashes the password."""

        user = User(username=validated_data["username"], email=validated_data["email"])
        user.set_password(validated_data["password"])
        user.save()
        return user


class CookieTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Extends SimpleJWT's TokenObtainPairSerializer to also return
    information about the authenticated user."""

    def validate(self, data):
        """Validates the login data and returns the tokens together with
        the user information."""

        data = super().validate(data)

        data["user"] = {
            "id": self.user.id,
            "username": self.user.username,
            "email": self.user.email,
        }
        return data
