from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.urls import path

from user_auth.views import Register


urlpatterns = [
    path("token", TokenObtainPairView.as_view(), name="access_token"),
    path("token/refresh", TokenRefreshView.as_view(), name="refresh"),
    path("register", Register.as_view(), name="register"),
]
