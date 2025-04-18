# users/apis.py

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .serializers import CustomTokenObtainPairSerializer

from django.contrib.auth import get_user_model
User = get_user_model()

from users.serializers import UserSignupSerializer

class SignupAPIView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=UserSignupSerializer,
        responses={
            201:"회원가입 성공", 
            400:"잘못된 요청"
        }
    )
    def post(self, request):
        """
            회원가입 API

            비밀번호 8자 이상, 이메일 형식 검증
            student or tutor 회원 분기
        """
        email = request.data.get("email")

        if User.objects.filter(email=email).exists():
            return Response({"msg":"이미 가입된 이메일입니다."}, status=400)

        serializer = UserSignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"회원가입 성공"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomTokenObtainPairAPI(TokenObtainPairView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["email", "password"],
            properties={
                "email":openapi.Schema(type=openapi.TYPE_STRING, example="tutor@example.com"),
                "password":openapi.Schema(type=openapi.TYPE_STRING, example="test1234"),
            }
        ),

        responses={
            200:openapi.Response(
                description="로그인 성공",
                examples={
                    "application/json": {
                        "refresh": "refresh token",
                        "access": "access token",
                        "user": {
                            "id": 1,
                            "email": "tutor@example.com",
                            "role": "tutor"
                        }
                    }
                }
            ),
            400:"잘못된 비밀번호", 
            404:"가입되지 않은 이메일"
        }
    )
    def post(self, request):
        """
            jwt 로그인 api

            jwt 로그인 api
        """
        serializer = CustomTokenObtainPairSerializer(data=request.data)

        if serializer.is_valid():
            response_data = serializer.validated_data
            
            return response_data  # Response 내부에서 반환된 값을 그대로 전달
        else:
            # 실패 시 errors 반환
            return Response({"message":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method="post",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["refresh"],
        properties={
            "refresh":openapi.Schema(type=openapi.TYPE_STRING, description="Refresh 토큰"),
        },
    ),
    responses={
        200:"로그아웃 성공",
        403:"Refresh 토큰 없음 또는 유효하지 않음",
    }
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_api(request):
    """
        로그아웃 api

        로그아웃 api
    """
    refresh_token = request.data.get("refresh")

    if not refresh_token:
        return Response({"message": "Refresh token이 없습니다."}, status=status.HTTP_403_FORBIDDEN)

    try:
        token = RefreshToken(refresh_token)
        token.blacklist()  
    except TokenError as e:
        return Response({"message": "유효한 Refresh Token이 아닙니다."}, status=status.HTTP_403_FORBIDDEN)

    return Response({"message": "로그아웃 되었습니다."}, status=status.HTTP_200_OK)



