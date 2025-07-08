from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone
from django.contrib.auth.base_user import BaseUserManager
from django.conf import settings
from django.core.exceptions import ValidationError
import random

class CustomUserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValidationError("An email address is required to create a user.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            raise ValidationError("Password must be set for a user.")
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_active", False)
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField("Email address", unique=True)
    phone_number = models.CharField("Phone Number", max_length=15, blank=True, null=True)
    gender = models.CharField("Gender", max_length=10, blank=True, null=True)
    date_of_birth = models.DateField("Date of Birth", blank=True, null=True)
    country = models.CharField("Country", max_length=100, blank=True, null=True)

    total_focus_time = models.PositiveIntegerField("Total Focus Time (minutes)", default=0)
    average_focus_time = models.FloatField("Average Focus Time (minutes)", default=0.0)
    total_sessions = models.PositiveIntegerField("Total Sessions", default=0)

    is_active = models.BooleanField("Active", default=True)
    is_staff = models.BooleanField("Staff status", default=False)
    is_superuser = models.BooleanField("Superuser status", default=False)

    date_joined = models.DateTimeField("Date Joined", default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def __str__(self):
        return f"{self.email} ({'Staff' if self.is_staff else 'User'})"
    
    otp_code = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)

    def generate_otp(self):
        otp = f"{random.randint(1000, 9999)}"
        self.otp_code = otp
        self.otp_created_at = timezone.now()
        self.save()
        return otp


class Project(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    color = models.CharField(max_length=20, default="#FFFFFF")  # Hex color code

    def __str__(self):
        return self.name



class Tag(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=20, default="#FFFFFF")

    def __str__(self):
        return self.name
    
    
    
class Task(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('disabled', 'Disabled'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    estimated_pomodoros = models.PositiveIntegerField(default=1)
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')
    tags = models.ManyToManyField(Tag, blank=True, related_name='tasks')
    color = models.CharField(max_length=20, default="#FFFFFF")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')

    def __str__(self):
        return self.name



class Session(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, blank=True, related_name='sessions')
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)
    duration = models.PositiveIntegerField(default=0) 

    def __str__(self):
        return f"Session for {self.user.email} - {self.duration} min"