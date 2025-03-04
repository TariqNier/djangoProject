from django.contrib.auth.hashers import make_password
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)
from datetime import datetime, timedelta
from rest_framework.authtoken.models import Token
import random
import string
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):

    def create_user(
            self, email, first_name,
            last_name=None,
            password=None, is_verified=True, **extra_fields):

        if email is None:
            raise TypeError('Users should have a Email')

        user = self.model(first_name=first_name,
                          last_name=last_name,
                          is_verified=is_verified,
                          email=self.normalize_email(email), **extra_fields)
        if password is None:
            user.password = make_password(None)
        else:
            user.set_password(password)
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
