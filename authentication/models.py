import boto3
import requests
from botocore.config import Config
from django.contrib.auth.hashers import make_password
from django.db import models
from simple_history.models import HistoricalRecords
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)
from datetime import datetime, timedelta
from rest_framework.authtoken.models import Token
import random
import string
from django.utils.translation import gettext_lazy as _
from main_.models import custom_upload_to, Model
from photographer.settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_S3_REGION_NAME, AWS_S3_ENDPOINT_URL, \
    AWS_STORAGE_BUCKET_NAME

s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            config=Config(region_name=AWS_S3_REGION_NAME),
            endpoint_url=AWS_S3_ENDPOINT_URL
        )

bucket_name = AWS_STORAGE_BUCKET_NAME


class UserManager(BaseUserManager):

    def create_user(
            self, email, first_name,
            last_name=None,
            password=None, is_verified=True, **extra_fields):

        if email is None:
            raise TypeError('Users should have a Email')

        user = self.model(first_name=first_name,
                          last_name=last_name,
                          email=self.normalize_email(email), **extra_fields)
        if password is None:
            user.password = make_password(None)
        else:
            user.set_password(password)
        user.is_verified = is_verified
        user.save()
        return user

    def create_user_unverified(self, email, first_name,
                               last_name, password=None, **extra_fields):

        if email is None:
            raise TypeError('Users should have a Email')

        user = self.model(first_name=first_name, last_name=last_name,
                          email=self.normalize_email(email), **extra_fields)
        if password:
            user.set_password(password)
        else:
            password = self.make_random_password()
            user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, first_name, last_name, password=None, **extra_fields):
        if password is None:
            raise TypeError('Password should not be none')

        user = self.create_user(email, first_name, last_name, password, **extra_fields)
        user.is_superuser = True
        user.is_active = True
        user.is_staff = True
        user.is_verified = True
        # user.kind = 'admin'
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):
    choices = [
        ("user", "user"),
        ("photographer", "photographer"),
    ]
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=150, null=True)
    image = models.CharField(max_length=255, null=True, blank=True)
    provider = models.CharField(max_length=100, default="email")
    username = models.SlugField(max_length=15, null=True, blank=True)
    kind = models.ManyToManyField("UserKindModel", blank=True)
    email = models.EmailField(
        max_length=255,
        verbose_name=_("Email"),
        error_messages={"unique": _("This email is already exist"), },
        unique=True, db_index=True)
    is_verified = models.BooleanField(default=True)
    is_verified_email = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    is_verified_phone = models.BooleanField(default=False)
    city = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    color = models.CharField(max_length=100, default="#b90808")
    history = HistoricalRecords()
    groups = None
    user_permissions = None

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', "last_name"]

    objects = UserManager()

    def __str__(self):
        return self.first_name

    def generate_password(self=15):
        characters = string.ascii_letters + string.digits
        password = (''.join(random.choice(characters) for i in range(0, self)))
        return password

    def tokens(self):
        return TokenWithEx.objects.create(user=self).key

    @property
    def user_size(self):
        folder_prefix = f'{self.username}'  # تأكد من أن ينتهي بـ /
        folder_prefix1200 = f'1200/{self.username}'  # تأكد من أن ينتهي بـ /
        folder_prefix400 = f'400/{self.username}'  # تأكد من أن ينتهي بـ /
        folder_prefix50 = f'50/{self.username}'  # تأكد من أن ينتهي بـ /

        # جمع حجم الملفات في المجلد
        total_size = 0

        total_size = self.get_sizes(folder_prefix, total_size)

        total_size = self.get_sizes(folder_prefix1200, total_size)

        total_size = self.get_sizes(folder_prefix400, total_size)

        total_size = self.get_sizes(folder_prefix50, total_size)

        return total_size / (1024 * 1024)

    def get_sizes(self, folder_prefix, total_size):
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=folder_prefix)
        if 'Contents' in response:
            for obj in response['Contents']:
                total_size += obj['Size']
        return total_size


def add_month_to_current_date():
    # الحصول على تاريخ اليوم الحالي
    current_date = datetime.now()

    new_date = current_date + timedelta(days=30)

    formatted_date = new_date.strftime("%Y-%m-%d")
    return str(formatted_date)


class TokenWithEx(Token):
    expire = models.DateField(blank=True, null=True)
    user = models.ForeignKey(
        User, related_name='auth_token',
        on_delete=models.CASCADE, verbose_name=_("User")
    )
    IPAddress = models.CharField(max_length=150, null=True, blank=True)
    location = models.JSONField(null=True, blank=True)

    class Meta:
        unique_together = ['user', 'IPAddress']

    def save(self, *args, **kwargs):
        if not self.expire and not self.pk:
            self.expire = add_month_to_current_date()
        if self.IPAddress:
            self.location = requests.get(f"http://ip-api.com/json/{self.IPAddress}").json()
        return super().save(*args, **kwargs)


class ChatModel(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    users = models.ManyToManyField(User, related_name="chats")


class ChatMessageModel(models.Model):
    chat = models.ForeignKey(ChatModel, on_delete=models.SET_NULL, null=True, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="messages")
    message = models.CharField(max_length=255, null=True, blank=True)
    file = models.FileField(upload_to=custom_upload_to, null=True, blank=True)
    read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    # def save(self, *args, **kwargs):
    #     if self.file:
    #         if self.file.name.endswith('blob'):
    #
    #             self.file.name = self.file.name + '.m4a'
    #     return super().save(*args, **kwargs)


class NotificationModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    message_en = models.TextField()
    message_ar = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    read = models.BooleanField(default=False)
    kind = models.CharField(max_length=100)
    url = models.TextField(null=True, blank=True)


class UserKindModel(models.Model):
    name_ar = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100)


class VerifyPhone(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="verify_phone")
    phone = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=100, unique=True)
    updated = models.DateTimeField(auto_now=True)
    verified = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.code = self.generate_key()
        return super().save(*args, **kwargs)

    @classmethod
    def generate_key(cls):
        return random.randint(10000, 99999)
