from rest_framework import serializers, status
from rest_framework.response import Response

from django.utils import timezone

from .models import TutorClass, StudentClass

from django.utils import timezone
from django.conf import settings
import pytz

class TutorClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = TutorClass
        fields = ("id", "tutor", "start_time", "duration")
        read_only_fields = ["tutor"]

    def validate_start_time(self, value):
        # 만약 timezone 정보가 없거나 local time이라면, settings.TIME_ZONE으로 간주하고 UTC로 변환
        if timezone.is_naive(value):
            local_tz = pytz.timezone(settings.TIME_ZONE)
            value = local_tz.localize(value)  # timezone 붙이기
            value = value.astimezone(pytz.UTC)  # UTC로 변환

        # 정각/30분 체크
        if value.minute not in (0, 30):
            raise serializers.ValidationError("수업 시작 시간은 정각 또는 30분만 가능합니다.")

        # 과거 시간인지 체크 (UTC 기준으로 비교)
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