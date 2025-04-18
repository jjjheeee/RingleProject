# study/urls.py

from django.urls import path, include

from rest_framework_simplejwt.views import TokenRefreshView

from .apis import TutorClassAPI

urlpatterns = [
    path("tutor/", TutorClassAPI.as_view(), name="tutor_view"),
    # path("tutor/available-time", available_time, name="available_time"),
]