# study/urls.py

from django.urls import path

from .apis import TutorClassAPI, StudentClassAPI, available_time, available_classe

urlpatterns = [
    path("tutor/", TutorClassAPI.as_view(), name="tutor_view"),
    path("student/", StudentClassAPI.as_view(), name="student_view"),
    path("available-time/", available_time, name="available_time"),
    path("available-class/", available_classe, name="available_class"),
]