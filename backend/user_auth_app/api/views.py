from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .serializers import RegistrationSerializer, UserSerializer, CustomTokenObtainPairSerializer


class RegistrationView(APIView):
    """API view for registering a new user account."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Create a new user account."""
        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            saved_account = serializer.save()
            data = {"username": saved_account.username, "email": saved_account.email, "user_id": saved_account.pk}
            return Response(data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """API view to log out the current user by deleting auth cookies."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Delete the access and refresh token cookies."""
        response = Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
        response.delete_cookie("access_token", path="/", samesite="LAX")
        response.delete_cookie("refresh_token", path="/", samesite="LAX")
        return response


class ProfileView(APIView):
    """API view to read or update the authenticated user's profile."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return the profile of the current user."""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        """Partially update the profile of the current user."""
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CookieTokenObtainPairView(TokenObtainPairView):
    """Login view that sets JWT tokens as httpOnly cookies instead of returning them in the body."""

    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        """Authenticate the user and set access and refresh token cookies."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        refresh = serializer.validated_data["refresh"]
        access = serializer.validated_data["access"]

        response = Response({"message": "Login successful."})

        response.set_cookie(key="access_token", value=access, path="/", httponly=True, secure=False, samesite="LAX")
        response.set_cookie(key="refresh_token", value=refresh, path="/", httponly=True, secure=False, samesite="LAX")

        response.data = {"message": "Login successful."}
        return response


def _get_refresh_token_from_request(request):
    """Extract refresh token from request cookies.

    Returns token or raises Response error."""
    refresh_token = request.COOKIES.get("refresh_token")
    if refresh_token is None:
        raise Response(
            {"detail": "Refresh token not found."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    return refresh_token


def _validate_and_get_access_token(serializer):
    """Validate serializer and extract access token.

    Returns access token or raises Response error."""
    try:
        serializer.is_valid(raise_exception=True)
    except ValidationError:
        raise Response(
            {"detail": "Refresh token is invalid."},
            status=status.HTTP_401_UNAUTHORIZED,
        )
    return serializer.validated_data.get("access")


class CookieTokenRefreshView(TokenRefreshView):
    """Token refresh view that reads the refresh token from a cookie."""

    def post(self, request, *args, **kwargs):
        """Issue a new access token using the refresh_token cookie."""
        refresh_token = _get_refresh_token_from_request(request)
        serializer = self.get_serializer(data={"refresh": refresh_token})
        access_token = _validate_and_get_access_token(serializer)

        response = Response({"message": "Access token refreshed."})
        response.set_cookie(
            key="access_token", value=access_token, path="/", httponly=True, secure=False, samesite="LAX"
        )
        return response
