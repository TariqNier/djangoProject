import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from datetime import datetime, timedelta

from authentication.models import ChatModel, ChatMessageModel, NotificationModel
from main_.permissions import QueryAuthMiddleware


class NotificationConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.room_group_name = None
        self.room_name = None

    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"notification_{self.room_name}"

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )
        self.scope = QueryAuthMiddleware(scope=self.scope)
        user = self.scope['user']
        if user.is_authenticated:
            self.accept()
        else:
            self.close()

    @staticmethod
    @receiver(post_save, sender=NotificationModel)
    def notification_handler(sender, instance, created, *args, **kwargs):
        if created:
            message = {
                'notification_type': "single",
                'message_en': instance.message_en,
                'message_ar': str(instance.message_ar),
                "kind": str(instance.kind),
                "url": instance.url
            }
            user = str(instance.user.pk)
            groupname = f"notification_{user}"
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                groupname, {"type": "chat_messages", "message": message}
            )

    def disconnect(self, close_code):
        # Leave room group
        self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        # async_to_sync(self.channel_layer.group_send)(
        #     self.room_group_name, {"type": "chat_messages", "message": "message"}
        # )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {"type": "chat_messages", "message": message}
        )

    # Receive message from room group
    def chat_messages(self, event):
        message = event["message"]
        # Send message to WebSocket
        self.send(text_data=json.dumps({"message": message, "test": message}))


class ChatConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.room_group_name = None
        self.room_name = None

    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"
        # print(self.scope)
        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )
        self.scope = QueryAuthMiddleware(scope=self.scope)
        self.user = self.scope['user']
        user = self.user
        try:
            self.chat = ChatModel.objects.get(id=self.room_name)
            if not user in self.chat.users.all():
                self.close()
        except ChatModel.DoesNotExist:
            self.close()
        if user.is_authenticated:
            user.chat = self.chat
            user.save(update_fields=['chat'])
            chats = self.chat.messages.exclude(sender=self.user).all()
            for chat in chats:
                if not chat.read:
                    chat.read = True
                    chat.save(update_fields=['read'])
            self.accept()
        else:
            self.close()

    # @staticmethod
    # @receiver(post_save, sender=NotificationModel)
    # def notification_handler(sender, instance, created, *args, **kwargs):
    #     if created:
    #         message = {
    #             'notification_type': "single",
    #             'message_en': instance.message_en,
    #             'message_ar': str(instance.message_ar),
    #             "type": instance.type,
    #             "kind": str(instance.kind),
    #             "url": instance.url
    #         }
    #         user = str(instance.user.pk)
    #         groupname = f"chat_{user}"
    #         channel_layer = get_channel_layer()
    #         print(channel_layer)
    #         async_to_sync(channel_layer.group_send)(
    #             groupname, {"type": "chat_messages", "message": message}
    #         )

    def disconnect(self, close_code):
        # Leave room group
        self.user.chat = None
        # self.user.last_login = datetime.now()
        self.user.save(update_fields=['chat'])
        self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        # async_to_sync(self.channel_layer.group_send)(
        #     self.room_group_name, {"type": "chat_messages", "message": "message"}
        # )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        # print(self.chat.users.exclude(id=self.user.id).)
        chat_ = self.chat.users.exclude(id=self.user.id).first().chat
        # print(chat_.id, self.room_name, bool(chat_))
        if chat_ and chat_.id == int(self.room_name):
            self.chat.messages.create(
                sender=self.user,
                message=message,
                read=True
            )
        else:
            self.chat.messages.create(
                sender=self.user,
                message=message,
            )
        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {"type": "chat_messages", "message": message, "id": self.user.id}
        )

    # Receive message from room group
    def chat_messages(self, event):
        message = event["message"]
        # Send message to WebSocket
        self.send(text_data=json.dumps({"message": message, "type": "new_message", "user_id": event['id']}))


class AllChatConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.room_group_name = None
        self.room_name = None

    def connect(self):
        # self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.scope = QueryAuthMiddleware(scope=self.scope)
        self.user = self.scope['user']
        self.room_group_name = f"all_chat_{self.user.id}"
        # print(self.scope)
        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )
        user = self.user
        if user.is_authenticated:
            user.login = True
            user.save(update_fields=['login'])
            self.accept()
        else:
            self.close()

    @staticmethod
    @receiver(post_save, sender=ChatMessageModel)
    def notification_handler(sender, instance, created, *args, **kwargs):
        message = {
            "type": "chat",
            "message": "changed",
        }
        users = instance.chat.users.all()
        for user in users:
            groupname = f"all_chat_{user.id}"
            channel_layer = get_channel_layer()
            if created:
                async_to_sync(channel_layer.group_send)(
                    groupname, {"type": "chat_messages", "message": message, "user_id": instance.sender.id}
                )
            else:
                async_to_sync(channel_layer.group_send)(
                    groupname, {"type": "chat_messages", "message": message, "user_id": user.id}
                )

    def disconnect(self, close_code):
        # Leave room group
        if self.user.is_authenticated:
            self.user.login = False
            self.user.last_login = datetime.now()
            self.user.save(update_fields=['login', 'last_login'])
        self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        # async_to_sync(self.channel_layer.group_send)(
        #     self.room_group_name, {"type": "chat_messages", "message": "message"}
        # )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        # print(self.chat.users.exclude(id=self.user.id).)

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {"type": "chat_messages", "message": message, "user_id": self.user.id}
        )

    # Receive message from room group
    def chat_messages(self, event):
        message = event["message"]
        # Send message to WebSocket
        self.send(text_data=json.dumps({"message": message, "type": "new_message",
                                        "user_id": event.get('user_id', None)}))
