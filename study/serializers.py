from rest_framework import serializers, status
from rest_framework.response import Response

from django.utils import timezone

from .models import TutorClass, StudentClass

from datetime import timedelta

class TutorClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = TutorClass
        fields = ("tutor", "start_time", "duration")
        read_only_fields = ["tutor"]

    def validate_start_time(self, value):

        # 시작시간은 정각 or 30분
        if value.minute not in (0, 30):
            raise serializers.ValidationError("수업 시작 시간은 정각 또는 30분만 가능합니다.")
        
        # start_time이 이미 과거 시간이라면 유효하지 않게 처리
        if value < timezone.now():
            raise serializers.ValidationError("이미 지난 시간입니다.")
        
        return value

    def validate(self, data):
        # 임시 인스턴스 생성
        instance = TutorClass(
            tutor=self.context["request"].user,
            start_time=data["start_time"],
            duration=data["duration"]
        )

        try:
            instance.clean()
        except Exception as e:
            raise serializers.ValidationError({"message": "이미 겹치는 수업이 존재합니다."})

        return data

class StudentClassSerializer(serializers.ModelSerializer):

    class Meta:
        model = StudentClass
        fields = "__all__"