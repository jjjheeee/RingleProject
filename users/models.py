# users/models.py

from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, role=None, **extra_fields):
        
        if not email:
            raise ValueError("email은 필수입니다.")
        
        if role not in ["tutor","student"]:
            raise ValueError("학생 또는 교사여야 합니다.")
        
        email = self.normalize_email(email)
        user = self.model(email=email, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password, **extra_fields):

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(email, password, role="tutor", **extra_fields)
    
class User(AbstractBaseUser, PermissionsMixin):

    class Role(models.TextChoices):
        STUDENT = "student", "학생"
        TUTOR = "tutor", "튜터"

    email = models.EmailField(
        unique=True, 
        db_index=True
    )
    
    role = models.CharField(
        max_length=10, 
        choices=Role.choices, 
        db_index=True
    )

    is_active = models.BooleanField(
        default=True
    )

    is_staff = models.BooleanField(
        default=False
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
