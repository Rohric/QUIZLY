from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class RegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration with password confirmation."""

    confirmed_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "confirmed_password"]
        extra_kwargs = {"password": {"write_only": True}, "email": {"required": True}}

    def validate_confirmed_password(self, value):
        """Check that password and confirmed_password match."""
        password = self.initial_data.get("password")
        if password and value and password != value:
            raise serializers.ValidationError("Passwords do not match.")
        return value

    def validate_email(self, value):
        """Check that the email address is not already in use."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email address is already in use.")
        return value

    def save(self):
        """Create and return a new user with the validated data.

        Returns the saved User instance."""
        pw = self.validated_data["password"]

        account = User(email=self.validated_data["email"], username=self.validated_data["username"])
        account.set_password(pw)
        account.save()
        return account


class UserSerializer(serializers.ModelSerializer):
    """Serializer for reading and updating user profile data."""

    class Meta:
        model = User
        fields = ["id", "username", "email", "birthdate", "address"]


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Token serializer that authenticates by username and password."""

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """Validate credentials and return access and refresh tokens."""
        username = attrs.get("username")
        password = attrs.get("password")

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise AuthenticationFailed("Invalid username or password.")

        if not user.check_password(password):
            raise AuthenticationFailed("Invalid username or password.")

        data = super().validate({"username": user.username, "password": password})
        return data
