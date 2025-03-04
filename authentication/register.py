import requests
from django.contrib.auth import authenticate
from django.core.files.base import ContentFile

from authentication.models import User, TokenWithEx
import os
import random
from rest_framework.exceptions import AuthenticationFailed
from django.core.files.temp import NamedTemporaryFile
from django.core.files import File
from authentication.serializers import UserInfoSer


def generate_username(name):
    username = "".join(name.split(' ')).lower()
    random_username = username + str(random.randint(0, 1000))
    return generate_username(random_username)


def download_image(url):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        img_temp = NamedTemporaryFile()
        img_temp.write(response.content)
        img_temp.flush()
        return File(img_temp)
    else:
        raise Exception("Failed to download image")


def register_social_user(provider, user_id, email, name, image, ip=None):
    filtered_user_by_email = User.objects.filter(email=email)

    if filtered_user_by_email.exists():

        registered_user = filtered_user_by_email[0]

        tt, token = TokenWithEx.objects.get_or_create(user=registered_user, IPAddress=ip)
        data = UserInfoSer(instance=registered_user).data
        if not registered_user.is_verified:
            registered_user.is_verified = True
            registered_user.save()
        return {
            "token": tt.key,
            "data": data
        }


    else:
        username = name.split(' ')
        user = {
            'first_name': username[0], "last_name": username[1], 'email': email,
            "provider": provider}
        user = User.objects.create_user(**user)

        user.is_verified = True
        user.save()

        tt, token = TokenWithEx.objects.get_or_create(user=user, IPAddress=ip)
        data = UserInfoSer(instance=user).data
        return {
            "token": tt.key,
            "data": data
        }
