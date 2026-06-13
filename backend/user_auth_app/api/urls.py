from django.urls import path

from .views import (
    CookieTokenObtainPairView,
    CookieTokenRefreshView,
    HelloWorldView,
    LogoutView,
    ProfileView,
    RegistrationView,
)

urlpatterns = [
    path("registration/", RegistrationView.as_view(), name="registration"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("token/", CookieTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", CookieTokenRefreshView.as_view(), name="token_refresh"),
    path("hello/", HelloWorldView.as_view(), name="hello"),
]
