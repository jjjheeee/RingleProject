# study/apis.py

from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from users.permissions import IsTutor, IsStudent

from .serializers import TutorClassSerializer, StudentClassSerializer
from .models import TutorClass, StudentClass

from datetime import datetime, timedelta, time
import pytz

from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from django.contrib.auth import get_user_model
User = get_user_model()

class TutorClassAPI(APIView):
    permission_classes = [IsTutor]

    @swagger_auto_schema(
        responses = {
            200:openapi.Response(
                description="나의 수업 리스트 조회 완료",
                examples={
                    "application/json": {
                        "message": "수업 리스트 조회 완료",
                        "data": [
                            {
                                "id": 13,
                                "tutor": 5,
                                "start_time": "2025-06-07T13:00:00+09:00",
                                "duration": 30
                            }
                        ]
                    }
                }
            ), 
            400:"수업 리스트 조회 실패"
        }
    )
    def get(self, request):
        """
            나의 수업 리스트를 조회 합니다.

            나의 수업 리스트를 조회 합니다.
        """
        tutor = request.user
        available_slots = tutor.open_class_times.all()

        serializer = TutorClassSerializer(available_slots, many=True)

        data = {
            "message": "수업 리스트 조회 완료", 
            "data": serializer.data
        }
        return Response(data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        request_body = openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["start_time", "duration"],
            properties={
                "start_time":openapi.Schema(type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_DATETIME,  # "YYYY-MM-DDTHH:MM:SSZ" 형식
                    example="2025-06-07T13:00:00+09:00"  # 예시 날짜 및 시간
                ),
                "duration":openapi.Schema(type=openapi.TYPE_INTEGER, example=30),
            }
        ),
        responses = {
            200:openapi.Response("수업이 생성되었습니다."), 
            400:"수업 생성 실패."
        }
    )
    def post(self, request):
        """
            가능한 시간대에 수업을 생성합니다.

            수업 가능한 "현지 시간"을 입력하면 utc의 시간으로 db에 저장된다.
            다른 api에서 시간을 출력 할때는 TIME_ZONE에 해당하는 시간으로 변환되어 보여진다.
        """

        serializer = TutorClassSerializer(data=request.data, context={"request": request})

        if serializer.is_valid():
            try:
                serializer.save(tutor=request.user)
            except IntegrityError:
                return Response({"message":"이미 해당 시간에 등록된 수업이 있습니다."}, status=400)
            
            return Response({"message":"수업이 생성되었습니다."}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=400)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "class_id", openapi.IN_QUERY,
                description="삭제할 수업의 ID",
                type=openapi.TYPE_INTEGER,
                required=True,
                example=1
            )
        ],
        responses={
            200:openapi.Response("수업이 삭제되었습니다."),
            403:"권한이 없는 수업입니다.",
            404:"존재하지 않는 수업입니다.",
            500:"수강생이 존재하는 수업입니다. 삭제할 수 없습니다.",
        }
    )
    def delete(self, request):
        """
            수업을 삭제합니다.

            수업을 삭제합니다.
        """

        class_id = request.query_params.get("class_id")

        instance = get_object_or_404(TutorClass, pk=class_id)

        if instance.tutor != request.user:
            return Response({"message":"권한이 없는 수업입니다."}, status=status.HTTP_403_FORBIDDEN)

        if not instance.status:
            instance.delete()
            return Response({"message":"수업이 삭제되었습니다."}, status=status.HTTP_200_OK)
        else:
            return Response({"message":"수강생이 존재하는 수업입니다. 삭제할 수 없습니다."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class StudentClassAPI(APIView):

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={
            200:openapi.Response(
                description="신청한 수업 리스트",
                schema=StudentClassSerializer(many=True)  # 실제 사용하는 serializer로 대체
            )
        }
    )
    def get(self, request):
        """
            내가 신청한 수업을 조회합니다.

            내가 신청한 수업을 조회합니다.
        """
        student = request.user

        classes = StudentClass.objects.filter(student=student)
        serializer = StudentClassSerializer(classes, many=True)

        data = {
            "data" : serializer.data
        }

        return Response(data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["class_id"],
            properties={
                "class_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="신청할 수업 ID"),
            }
        ),
        responses={
            201:"수업 신청 완료", 
            400:"신청 실패", 
            404:"존재하지 않는 수업입니다."
        }
    )
    def post(self, request):
        """
            선택한 수업을 신청합니다.

            선택한 수업을 신청합니다.
        """
        class_id = request.data.get("class_id")
        tutor_class = get_object_or_404(TutorClass, id=class_id)

        if tutor_class.status:  # 이미 신청된 수업
            return Response({"message":"이미 신청된 수업입니다."}, status=400)

        StudentClass.objects.create(student=request.user, tutor_class=tutor_class)

        return Response({"message":"수업신청이 완료되었습니다."}, status=201)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "class_id", openapi.IN_QUERY,
                description="취소할 수업의 ID",
                type=openapi.TYPE_INTEGER,
                required=True,
                example=1
            )
        ],
        responses={
            200: "수업이 취소되었습니다.",
            403: "권한이 없는 수업입니다.",
            404: "존재하지 않는 수업입니다."
        }
    )
    def delete(self, request):
        """
            신청한 수업을 취소합니다.

            신청한 수업을 취소합니다.
        """

        class_id = request.query_params.get("class_id")

        instance = get_object_or_404(StudentClass, pk=class_id)

        if instance.student != request.user:
            return Response({"message": "권한이 없는 수업입니다."}, status=status.HTTP_403_FORBIDDEN)

        instance.delete()
        return Response({"message": "수업이 취소되었습니다."}, status=status.HTTP_200_OK)

@swagger_auto_schema(
    method="get",
    manual_parameters=[
        openapi.Parameter(
            "date",
            openapi.IN_QUERY,
            description="조회할 날짜 (YYYY-MM-DD)",
            type=openapi.TYPE_STRING,
            required=True,
            example="2025-04-27"
        ),
        openapi.Parameter(
            "duration",
            openapi.IN_QUERY,
            description="수업 길이 (30 또는 60분)",
            type=openapi.TYPE_INTEGER,
            required=True,
            example=30
        )
    ],
    responses={
        200: openapi.Response(
            description="사용 가능한 시간대 목록",
            examples={
                "application/json": {
                    "message": "사용 가능한 시간대입니다.",
                    "available_times": [
                        "2025-04-27 13:30",
                        "2025-04-27 14:00",
                        "2025-04-27 14:30",
                    ]
                }
            }
        ),
        400: "잘못된 날짜 또는 파라미터 오류",
    }
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def available_time(request):
    """
        선택한 날짜 기준으로 현재 사용자의 role에 따라 가능한 시간대를 조회합니다.

        tutor : 해당 날짜에 duration길이 만큼의 수업을 생성할 수 있는 시간대
        
        student : 해당 날짜에 duration길이의 신청 가능한 수업 시간대
                tutor가 생성한 수업이 해당 날짜에 없을경우 빈 list가 return 된다.
    """
    date_str = request.GET.get("date")
    duration_str = request.GET.get("duration")

    if not date_str or not duration_str:
        return Response({"message": "날짜와 duration을 입력하세요."}, status=400)

    try:
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return Response({"message": "날짜 형식이 잘못되었습니다. (YYYY-MM-DD 형식)"}, status=400)

    try:
        duration = int(duration_str)
        if duration not in (30, 60):
            raise ValueError
    except ValueError:
        return Response({"message": "duration은 30 또는 60만 가능합니다."}, status=400)

    user = request.user
    now = timezone.now()

    if date < now.date():
        return Response({"message": "이미 지난 날짜입니다."}, status=400)
    
    start_of_day = timezone.make_aware(datetime.combine(date, time.min))
    end_of_day = timezone.make_aware(datetime.combine(date, time(hour=23, minute=30)))

    # 오늘이라면 현재 시간 기준 30분 이후부터 시작 => 현재 18:10 일경우 18:30 부터 시작
    if date == now.date():
        minute = ((now.minute // 30) + 1) * 30
        hour = now.hour + (minute // 60)
        minute %= 60
        start_of_day = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

    # 30분 단위 시간대 생성
    total_slots = int((end_of_day - start_of_day).total_seconds() // (30 * 60))
    all_slots = [start_of_day + timedelta(minutes=30 * i) for i in range(total_slots + 1)]

    available_slots = []

    match user.role:

        case "tutor":

            my_classes = TutorClass.objects.filter(tutor=user, start_time__date=date)

            for i in range(len(all_slots)):
                slot = all_slots[i]
                end_slot = slot + timedelta(minutes=duration)

                if end_slot > end_of_day:
                    continue

                conflict = any(
                    cls.start_time < end_slot and cls.end_time > slot
                    for cls in my_classes
                )
                if not conflict:
                    available_slots.append(timezone.localtime(slot))

        case "student":

            classes = TutorClass.objects.filter(start_time__date=date, status=False, duration=duration)
            my_classes = StudentClass.objects.filter(student=user)
            my_times = [(sc.tutor_class.start_time, sc.tutor_class.end_time) for sc in my_classes]

            for tutor_class in classes:
                conflict = any(
                    my_start < tutor_class.end_time and my_end > tutor_class.start_time
                    for my_start, my_end in my_times
                )
                if not conflict:
                    available_slots.append(timezone.localtime(tutor_class.start_time))
    
    available_slots = sorted(set(available_slots))

    data = {
        "message": f"{user.role} 사용 가능한 시간대입니다.",
        "available_times": [slot.strftime("%Y-%m-%d %H:%M") for slot in available_slots]
    }
    return Response(data, status=200)

@swagger_auto_schema(
    method="get",
    manual_parameters=[
        openapi.Parameter(
            name="start_time",
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_DATETIME,
            required=True,
            description="수업 신청할 날짜",
            example="2025-06-07T13:00:00"
        ),
        openapi.Parameter(
            name="duration",
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER,
            required=True,
            description="조회할 수업의 길이 (분)",
            example=30
        )
    ],
    responses={
        200: openapi.Response(
            description="신청 가능한 수업 목록",
            examples={
                "application/json": {
                    "message": "신청 가능한 수업 목록입니다.",
                    "available_classes": [
                        {
                            "id": 1,
                            "tutor": "tutor_username",
                            "start_time": "2025-04-27 13:00",
                            "duration": 30
                        }
                    ]
                }
            }
        ),
        400: "잘못된 입력 형식"
    }
)
@api_view(["GET"])
@permission_classes([IsStudent])
def available_classe(request):
    """
        시간대와 수업 길이로 신청 가능한 수업을 조회합니다.

        시간대와 수업 길이로 신청 가능한 수업을 조회합니다.
    """
    start_time_str = request.GET.get("start_time")
    duration = request.GET.get("duration")

    if not start_time_str or not duration:
        return Response({"message": "start_time과 duration은 필수입니다."}, status=400)

    try:
        # 입력 문자열을 TIME_ZONE 시간대로 파싱 및 UTC 변경
        local_tz = pytz.timezone(settings.TIME_ZONE)
        naive_dt = datetime.fromisoformat(start_time_str)
        start_time = local_tz.localize(naive_dt) # local time
        start_time_utc = start_time.astimezone(pytz.UTC) # utc time
    except Exception as e:
        return Response({"message": "start_time 형식이 올바르지 않습니다. 예: 2025-04-27T13:00:00"}, status=400)

    try:
        duration = int(duration)
    except ValueError:
        return Response({"message": "duration은 정수여야 합니다."}, status=400)

    my_class_ids = StudentClass.objects.filter(student=request.user).values_list("tutor_class_id", flat=True)

    # 해당 시간에 신청 가능한 수업 필터링
    classes = TutorClass.objects.filter(
        start_time=start_time_utc,
        duration=duration,
        status=False
    ).exclude(id__in=my_class_ids)

    # 응답 데이터 구성
    serializer = TutorClassSerializer(classes, many=True)

    data = {
        "message": "신청 가능한 수업 목록입니다.",
        "available_classes": serializer.data
    }

    return Response(data, status=200)