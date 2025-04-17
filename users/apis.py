# users/apis.py

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from django.contrib.auth import get_user_model
User = get_user_model()

from users.serializers import UserSignupSerializer

class SignupAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        request_body=UserSignupSerializer,
        responses={201: openapi.Response('회원가입 성공'), 400: '잘못된 요청'}
    )
    def post(self, request):
        """
        회원가입 API
        비밀번호 8자 이상, 이메일 형식 검증
        student or tutor 회원 분기
        """
        email = request.data.get("email")

        if User.objects.filter(email=email).exists():
            return Response({"msg": "이미 가입된 이메일입니다."}, status=400)

        serializer = UserSignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "회원가입 성공"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)