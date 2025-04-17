# study/apis.py

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from users.serializers import CustomTokenObtainPairSerializer
from users.permisstions import IsStudent, IsTutor

from django.contrib.auth import get_user_model
User = get_user_model()

class TutorClassAPI(APIView):
    permission_classes = [IsTutor]

    def get(self, request):
        print(request.user)
        return Response({"message": "로그아웃 되었습니다."}, status=status.HTTP_200_OK)