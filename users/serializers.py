# users/serializers.py

from rest_framework import serializers
from django.contrib.auth import get_user_model
import re

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
        print(1111)
        return User.objects.create_user(**validated_data)