# study/models.py

from django.db import models
from django.core.exceptions import ValidationError

from datetime import timedelta

from django.contrib.auth import get_user_model
User = get_user_model()

# Create your models here.
class TutorClass(models.Model):
    DURATION_CHOICES = (
        (30, "30분"),
        (60, "60분"),
    )

    tutor = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "open_class_times")
    start_time = models.DateTimeField()
    duration = models.IntegerField(choices = DURATION_CHOICES, db_index = True)
    status = models.BooleanField(default = False, db_index = True)

    class Meta:
        ordering = ["start_time"]
        unique_together = ("tutor", "start_time")  # 같은 시간 중복 방지

    def clean(self):
        # 겹치는 시간 검증
        end_time = self.end_time
        overlapping = TutorClass.objects.filter(
            tutor = self.tutor,
            start_time__lt = end_time,
        ).exclude(id = self.id)

        for slot in overlapping:
            if slot.end_time > self.start_time:
                raise ValidationError("이미 겹치는 수업이 존재합니다.")

    @property
    def end_time(self):
        return self.start_time + timedelta(minutes = self.duration)

class StudentClass(models.Model):

    tutor_class = models.OneToOneField(  # 수업 하나당 한 명만 신청 가능하게
        TutorClass,
        on_delete = models.CASCADE,
        related_name = "student_class"
    )
    student = models.ForeignKey(User, on_delete = models.CASCADE)
    created_at = models.DateTimeField(auto_now_add = True)

    class Meta:
        unique_together = ('tutor_class', 'student')  # 중복 신청 방지
