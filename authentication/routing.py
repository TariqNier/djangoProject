from django.urls import re_path

from .consumers import NotificationConsumer, ChatConsumer, AllChatConsumer

websocket_urlpatterns = [
    re_path(r"notification/(?P<room_name>\w+)/$", NotificationConsumer.as_asgi()),
    re_path(r"chat/(?P<room_name>\w+)/$", ChatConsumer.as_asgi()),
    re_path(r"allchat/", AllChatConsumer.as_asgi()),

]
