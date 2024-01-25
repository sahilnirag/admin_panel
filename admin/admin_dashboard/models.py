from django.db import models
from django.contrib.auth.models import AbstractUser
from .manager import UserManager


# Create your models here.

class Users(AbstractUser):

    username = None
    email = models.EmailField("email address", blank=True,unique=True)
    social_id = models.CharField(max_length=500, null=True, blank=True)
    login_type = models.CharField(default="normal", max_length=255, choices=(
        ("normal", "Normal"), ("google", "Google"), ("facebook", "Facebook")
    ))
    is_one_time_login = models.BooleanField(default=False)
    is_pd_distance = models.BooleanField(default=False)
    is_reading_distance = models.BooleanField(default=False)
    is_f_meter = models.BooleanField(default=False)
    objects = UserManager()
    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ["first_name", "last_name"]
    image = models.ImageField(null=True, blank=True)

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
