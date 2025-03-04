from django.contrib import admin
from .models import User, TokenWithEx, ChatModel, ChatMessageModel, UserKindModel, VerifyPhone

# Register your models here.
admin.site.register(User)


@admin.register(TokenWithEx)
class TokenWithEcAdmin(admin.ModelAdmin):
    pass


@admin.register(ChatModel)
class ChatModelAdmin(admin.ModelAdmin):
    pass


@admin.register(ChatMessageModel)
class ChatMessageModelAdmin(admin.ModelAdmin):
    pass

@admin.register(UserKindModel)
class UserKindModelAdmin(admin.ModelAdmin):
    pass


@admin.register(VerifyPhone)
class VerifyPhoneAdmin(admin.ModelAdmin):
    pass

