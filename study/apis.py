# study/apis.py

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from users.permissions import IsStudent, IsTutor

from .serializers import TutorClassSerializer, StudentClassSerializer
from .models import TutorClass, StudentClass

from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from django.contrib.auth import get_user_model
User = get_user_model()

class TutorClassAPI(APIView):
    permission_classes = [IsTutor]

    @swagger_auto_schema(
        responses = {200 : openapi.Response("수업 리스트 조회 완료."), 400 : "수업 리스트 조회 실패."}
    )
    def get(self, request):
        """
            나의 수업 리스트를 조회 합니다.
        """
        tutor = request.user
        available_slots = tutor.open_class_times.all()

        serializer = TutorClassSerializer(available_slots, many=True)

        data = {
            "message": "수업 리스트 조회 완료.", 
            "data": serializer.data
        }
        return Response(data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        request_body = openapi.Schema(
            type = openapi.TYPE_OBJECT,
            required = ["start_time", "duration"],
            properties = {
                "start_time" : openapi.Schema(type=openapi.TYPE_STRING,
                    format = openapi.FORMAT_DATETIME,  # "YYYY-MM-DDTHH:MM:SSZ" 형식
                    example = "2025-06-07T13:00:00Z"  # 예시 날짜 및 시간
                ),
                "duration" : openapi.Schema(type=openapi.TYPE_INTEGER, example=30),
            }
        ),
        responses = {200 : openapi.Response("수업이 생성되었습니다."), 400 : "수업 생성 실패."}
    )
    def post(self, request):
        """
            가능한 시간대에 수업을 생성합니다.
        """
        # if request.user.role != "tutor":
        #     return Response({"msg": "튜터만 수업을 등록할 수 있습니다."}, status=403)

        serializer = TutorClassSerializer(data=request.data, context={"request": request})

        if serializer.is_valid():
            try:
                serializer.save(tutor=request.user)
            except IntegrityError:
                return Response({"msg": "이미 해당 시간에 등록된 수업이 있습니다."}, status=400)
            
            return Response({"message": "수업이 생성되었습니다."}, status=status.HTTP_201_CREATED)

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
            200: openapi.Response("수업이 삭제되었습니다."),
            403: "권한이 없는 수업입니다.",
            404: "존재하지 않는 수업입니다."
        }
    )
    def delete(self, request):
        """
            수업을 삭제합니다.
        """

        class_id = request.query_params.get("class_id")

        instance = get_object_or_404(TutorClass, pk=class_id)

        if instance.tutor != request.user:
            return Response({"message": "권한이 없는 수업입니다."}, status=status.HTTP_403_FORBIDDEN)

        instance.delete()
        return Response({"message": "수업이 삭제되었습니다."}, status=status.HTTP_200_OK)
    
# @swagger_auto_schema(
#     method="get",
#     manual_parameters=[
#         openapi.Parameter(
#             "class_date", openapi.IN_QUERY,
#             description="생성할 수업의 날짜(YYYY-MM-DD)",
#             type=openapi.TYPE_STRING,
#             required=True,
#             example="2025-06-07"
#         )
#     ],
#     responses={
#         200:"수업생성 가능한 시간대 조회 완료",
#         404:"해당 날짜에 수업 가능한 시간대가 없습니다."
#     }
# )
# @api_view(["GET"])
# @permission_classes([IsTutor])
# def available_time(self, request):
#     data = {
        
#     }
#     return Response(data=data, status=status.HTTP_200_OK)

class StudentClassAPI(APIView):

    permission_classes=[IsAuthenticated]

    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                description="신청한 수업 리스트",
                schema=StudentClassSerializer(many=True)  # 실제 사용하는 serializer로 대체
            )
        }
    )
    def get(self, request):
        """
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
        responses={201: "수업 신청 완료", 400: "신청 실패", 404: "존재하지 않는 수업입니다."}
    )
    def post(self, request):
        """
            수업신청
        """
        class_id = request.data.get("class_id")
        tutor_class = get_object_or_404(TutorClass, id=class_id)

        if tutor_class.status:  # 이미 신청된 수업
            return Response({"message": "이미 신청된 수업입니다."}, status=400)

        StudentClass.objects.create(student=request.user, tutor_class=tutor_class)

        return Response({"message": "수업신청이 완료되었습니다."}, status=201)

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
            200: openapi.Response("수업이 취소되었습니다."),
            403: "권한이 없는 수업입니다.",
            404: "존재하지 않는 수업입니다."
        }
    )
    def delete(self, request):
        """
            신청한 수업을 취소합니다.
        """

        class_id = request.query_params.get("class_id")

        instance = get_object_or_404(StudentClass, pk=class_id)

        if instance.student != request.user:
            return Response({"message": "권한이 없는 수업입니다."}, status=status.HTTP_403_FORBIDDEN)

        instance.delete()
        return Response({"message": "수업이 취소되었습니다."}, status=status.HTTP_200_OK)
