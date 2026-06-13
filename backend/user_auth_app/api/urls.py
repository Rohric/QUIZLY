from django.urls import path

from .views import (
    CookieTokenObtainView,
    CookieTokenRefreshView,
    CustomLoginView,
    HElloWorldView,
    LogoutView,
    ProfileView,
    RegistrationView,
)

urlpatterns = [
    path("registration/", RegistrationView.as_view(), name="registration"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("token/", CookieTokenObtainView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", CookieTokenRefreshView.as_view(), name="token_refresh"),
    path("hello/", HElloWorldView.as_view(), name="hello"),
]
