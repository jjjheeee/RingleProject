# users/urls.py

from django.urls import path, include

from .apis import SignupAPIView

urlpatterns = [
    path('signup/', SignupAPIView.as_view(), name='signup'),
]