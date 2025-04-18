# users/urls.py

from django.urls import path, include

from rest_framework_simplejwt.views import TokenRefreshView

from .apis import SignupAPIView, CustomTokenObtainPairAPI, logout_api

urlpatterns = [
    path("signup/", SignupAPIView.as_view(), name="signup"),
    path("signin/", CustomTokenObtainPairAPI.as_view(), name="signin"),
    path("token/refresh", TokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", logout_api, name="logout"),
]