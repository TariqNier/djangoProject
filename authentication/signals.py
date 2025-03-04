import random

from django.conf import settings
import os
from django.db.models.signals import post_save

from .models import ChatMessageModel, VerifyPhone, User
import requests


def send_OTP_verify(sender, instance, created, **kwargs):
    if not instance.verified:
        url = "https://app.wawp.net/api/send"
        data = {
            "number": f"{instance.phone.replace('+', '')}",
            "type": "text",
            "message": f"hello {instance.user.first_name} your code is: {instance.code} ",
            "instance_id": random.choice(["6720059182DD9", "672005C8205F9"]),
            "access_token": "671f9938b1386"
        }
        requests.post(url, data=data)


post_save.connect(send_OTP_verify, sender=VerifyPhone)


def create_social_user(sender, instance, created, **kwargs):
    if created:
        from structure.models import AboutUsModel
        instance.banners.create(
            image="sameh/1730542147434sameh.jpeg",
            title_en="Welcome to our website",
            title_ar="مرحبا بكم في موقعنا",
            subtitle_en="We are happy to serve you",
            subtitle_ar="نحن سعداء بخدمتكم",
            description_en="Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum "
                           "has been the industry's standard dummy text ever since the 1500s, when an unknown printer "
                           "took a galley of type and scrambled it to make a type specimen book. It has survived not "
                           "only five centuries, but also the leap into electronic typesetting, remaining essentially "
                           "unchanged. It was popularised in the 1960s with the release of Letraset sheets containing "
                           "Lorem Ipsum passages, and more recently with desktop publishing software like Aldus "
                           "PageMaker including versions of Lorem Ipsum.",
            description_ar="لوريم إيبسوم هو نص بافتراضي (نص عشوائي) يُستخدم في صناعات الطباعة والتنضيد. كان لوريم ",
        )
        from structure.models import StaticDataModel
        StaticDataModel.objects.create(
            image="sameh/1730481009271sameh.webp",
            user=instance,
            address_ar="العنوان",
            address_en="address",
            email="email@example.com",
            phone="123456789",
            frame="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3455.637706739351!2d31.296302315116"
                  "74!3d30.05604098188073!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x14583d6a8c9f"
                  "b1c3%3A0x2a00c1f6f7e7f1f4!2sNile%20University!5e0!3m2!1sen!2seg!4v1634794128692!5m2!1sen!2seg"
        )
        instance.about_us.create(
            title_en="About Us",
            title_ar="من نحن",
            description_en="Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum "
                           "has been the industry's standard dummy text ever since the 1500s, when an unknown printer "
                           "took a galley of type and scrambled it to make a type specimen book. It has survived not "
                           "only five centuries, but also the leap into electronic typesetting, remaining essentially "
                           "unchanged. It was popularised in the 1960s with the release of Letraset sheets containing "
                           "Lorem Ipsum passages, and more recently with desktop publishing software like Aldus "
                           "PageMaker including versions of Lorem Ipsum.",
            description_ar="لوريم إيبسوم هو نص بافتراضي (نص عشوائي) يُستخدم في صناعات الطباعة والتنضيد. كان لوريم ",
        )
        AboutUsModel.objects.create(
            user=instance,
            description_en="Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum "
                           "has been the industry's standard dummy text ever since the 1500s, when an unknown printer "
                           "took a galley of type and scrambled it to make a type specimen book. It has survived not "
                           "only five centuries, but also the leap into electronic typesetting, remaining essentially "
                           "unchanged. It was popularised in the 1960s with the release of Letraset sheets containing "
                           "Lorem Ipsum passages, and more recently with desktop publishing software like Aldus "
                           "PageMaker including versions of Lorem Ipsum.",
            description_ar="لوريم إيبسوم هو نص بافتراضي (نص عشوائي) يُستخدم في صناعات الطباعة والتنضيد. كان لوريم ",
            image="sameh/1730542147434sameh.jpeg"
        )

        data = [
            {
                "type": "facebook",
                "type_ar": "فيسبوك",
                "url": "https://www.facebook.com/",
                "star": True
            },
            {
                "type": "instagram",
                "type_ar": "انستغرام",
                "url": None,
            },
            {
                "type": "youtube",
                "type_ar": "يوتيوب",
                "url": None,
            },
            {
                "type": "tiktok",
                "type_ar": "تيكتوك",
                "url": None,
            },
            {
                "type": "whatsapp",
                "type_ar": "واتساب",
                "url": None,
            },
            {
                "type": "twitter",
                "type_ar": "تويتر",
                "url": None,
            },
            {
                "type": "phone",
                "type_ar": "هاتف",
                "url": None,
            },
        ]
        for item in data:
            instance.social_links.create(**item)


post_save.connect(create_social_user, sender=User)
