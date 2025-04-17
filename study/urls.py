# study/urls.py

from django.urls import path, include

from rest_framework_simplejwt.views import TokenRefreshView

from .apis import TutorClassAPI

urlpatterns = [
    path('tutor/', TutorClassAPI.as_view(), name='token_refresh'),
    # path('logout/', TutorClassAPI, name='logout'),
]