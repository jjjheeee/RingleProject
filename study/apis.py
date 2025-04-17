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

    @swagger_auto_schema(
        # request_body=openapi.Schema(
        #     type=openapi.TYPE_OBJECT,
        #     required=['email', 'password'],
        #     properties={
        #         'email': openapi.Schema(type=openapi.TYPE_STRING, example='tutor@example.com'),
        #         'password': openapi.Schema(type=openapi.TYPE_STRING, example='test1234'),
        #     }
        # ),

        responses={200: openapi.Response("수업 리스트 조회 완료."), 400: "수업 리스트 조회 실패."}
    )
    def get(self, request):
        print(request.user)
        return Response({"message": "수업 리스트 조회 완료."}, status=status.HTTP_200_OK)