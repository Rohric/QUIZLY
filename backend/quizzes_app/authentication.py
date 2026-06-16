from rest_framework_simplejwt.authentication import JWTAuthentication


class CookieJWTAuthentication(JWTAuthentication):
    """JWT authentication that reads the access token from an httpOnly cookie."""

    def authenticate(self, request):
        """Validate the JWT from the access_token cookie.

        Returns a (user, token) tuple or None if no token is present."""
        access_token = request.COOKIES.get("access_token")
        if not access_token:
            return None
        validated_token = self.get_validated_token(access_token)
        return self.get_user(validated_token), validated_token
