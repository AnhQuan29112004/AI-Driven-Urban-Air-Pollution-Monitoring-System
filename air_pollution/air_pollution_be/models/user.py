from django.db import models
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.hashers import make_password, check_password
# from constants.constants import Constants
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.utils import timezone
from constants.user_constants import UserConstants
import time
from datetime import datetime
from utils.base_model import BaseModel
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)

        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("status", 1)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        user = self.create_user(username, email, password, **extra_fields)
        user.user_permissions.set(Permission.objects.all())
        user.save()

        return user
    


class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    objects = UserManager()
    all_objects = models.Manager()
    username = models.CharField(max_length=150, unique=True)
    full_name = models.CharField(max_length=255, null=True, blank=True)
    avatar = models.TextField(null=True, blank=True)
    gender = models.CharField(max_length=10, null=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    password = models.CharField(max_length=128, null=True)
    status = models.PositiveSmallIntegerField(choices=UserConstants.USER_STATUS, default=1)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True)
    birthday = models.DateField(null=True)
    classification = models.CharField(max_length=20, null=True, blank=True, default="CLUB1")
    is_deleted = models.BooleanField(default=False)
    delete_at = models.DateTimeField(null=True,blank=True)
    role =models.IntegerField(choices=UserConstants.ROLE, default=3)
    
    groups = models.ManyToManyField(
        Group,
        related_name="custom_users",
        blank=True,
    )

    user_permissions = models.ManyToManyField(
        Permission, related_name="custom_users", blank=True
    )

    created_by = models.ForeignKey(
    'self',
    related_name="created_users",
    null=True,
    blank=True,
    on_delete=models.SET_NULL,
    )
    updated_by = models.ForeignKey(
        'self',
        related_name="updated_users",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    USERNAME_FIELD = "username"
    EMAIL_FIELD = "email"
    
    @staticmethod
    def datetime_to_unix(time:datetime) ->int:
        if time.tzinfo is None:
            time = time.replace(tzinfo=timezone.utc)
        return int(time.timestamp())

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
    
    def soft_delete(self):
        self.is_deleted = True
        self.delete_at = timezone.now()
        self.save()
    
    def restore(self):
        self.is_deleted = False
        self.delete_at = None
        self.save()

    

    class Meta:
        app_label = "air_pollution_be"
        db_table = "user"

    @property
    def is_authenticated(self):
        return self.status