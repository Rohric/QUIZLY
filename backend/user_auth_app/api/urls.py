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
    path("register/", RegistrationView.as_view(), name="registration"),
    path("login/", CookieTokenObtainPairView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("token/refresh/", CookieTokenRefreshView.as_view(), name="token_refresh"),
    path("auth/profile/", ProfileView.as_view(), name="profile"),
    path("hello/", HelloWorldView.as_view(), name="hello"),
]
