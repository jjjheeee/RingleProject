# users/serializers.py

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.response import Response
from rest_framework import status

from django.contrib.auth import get_user_model
User = get_user_model()

class UserSignupSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True)

    class Meta:

        model = User
        fields = ("email", "password", "role")

    def validate_role(self, value):

        if value not in [User.Role.STUDENT, User.Role.TUTOR]:
            raise serializers.ValidationError("role은 'student' 또는 'tutor'여야 합니다.")
        
        return value
    
    def validate_password(self, value):

        if len(value) < 8:
            raise serializers.ValidationError("비밀번호는 8자 이상이어야 합니다.")
        
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
    
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):

        # 사용자 인증 시도를 위해 이메일과 비밀번호 가져오기
        email = attrs.get("email")
        password = attrs.get("password")

        user_instance = User.objects.filter(email=email).first()

        # 이메일 존재 여부 확인
        if not user_instance:
            return Response({"message": "사용자를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        # 비밀번호 확인
        # user = authenticate(email=email, password=password)
        if not user_instance.check_password(password):
            return Response({"message": "비밀번호가 틀렸습니다."}, status=status.HTTP_400_BAD_REQUEST)

        # if not user_instance.is_active:
        #     return Response(
        #         msg="이메일 인증을 진행해주세요.",
        #         status=403
        #     )

        # 기본 JWT 토큰 생성 로직 실행
        tokens = super().validate(attrs)

        # 추가 사용자 정보 포함 (선택)
        tokens["user"] = {
            "id" : user_instance.id,
            "email" : user_instance.email,
            "role" :user_instance.role
        }

        return Response({"data": tokens}, status=status.HTTP_200_OK)