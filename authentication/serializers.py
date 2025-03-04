# from django.contrib.sites.shortcuts import get_current_site
# from django.http import request
# from rest_framework import serializers
#
# from .models import User
# from django.contrib.auth.tokens import PasswordResetTokenGenerator
# from django.utils.encoding import force_str
# from django.utils.http import urlsafe_base64_decode
# from django.contrib import auth
# from django.utils.translation import gettext_lazy as _
# from rest_framework.exceptions import ValidationError
#
#
# class RegisterSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(max_length=68, min_length=6, write_only=True)
#     token = serializers.CharField(max_length=2000, min_length=3, read_only=True)
#     username = serializers.SlugField()
#
#     class Meta:
#         model = User
#         fields = [
#             "email", "phone",
#             "password", "first_name", "country", "state",
#             "token", "last_name", "username", "city"
#         ]
#
#     def validate(self, attrs):
#         email = attrs.get('email', None)
#         if User.objects.filter(email=email.lower()).exists():
#             raise serializers.ValidationError({
#                 "email": _("this email is already exist")
#             })
#
#         if User.objects.filter(username=attrs.get("username")).exists():
#             raise serializers.ValidationError({
#                 "username": _("this merchant name is already exist")
#             })
#         if User.objects.filter(phone=attrs.get("phone")).exists():
#             raise serializers.ValidationError({
#                 "phone": _("this phone is already exist")
#             })
#
#         return super().validate(attrs)
#
#     def create(self, validated_data):
#         kind = validated_data.pop("kind")
#         user = User.objects.create_user(
#             **validated_data
#         )
#         user.kind.set(kind)
#
#         return user
#
#
# class UserInfoSer(serializers.ModelSerializer):
#     image_url = serializers.SerializerMethodField(read_only=True)
#     user_sizes = serializers.SerializerMethodField(read_only=True)
#
#     class Meta:
#         model = User
#         fields = [
#             'first_name', "email", "last_name", "phone", "image", "username", "id", "kind", "is_verified_email",
#             "country", "state", "city", "is_verified_phone", "image_url", "color", "user_sizes"
#         ]
#         read_only_fields = ['email', "provider", "id", "kind"]
#         validators = []
#
#     def get_user_sizes(self, obj):
#         return obj.user_size
#
#
#
#     def update(self, instance, validated_data):
#         if validated_data.get('phone'):
#             instance.is_verified_phone = False
#         return super().update(instance, validated_data)
#
#
# class LoginSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(max_length=68, min_length=6, write_only=True)
#     token = serializers.CharField(max_length=2000, min_length=3, read_only=True)
#     email = serializers.EmailField(required=True, write_only=True)
#     provider = serializers.CharField(read_only=True)
#     image_url = serializers.CharField(read_only=True)
#     kind = serializers.ListField(read_only=True, child=serializers.IntegerField())
#     # id = serializers.IntegerField(read_only=True)
#
#     class Meta:
#         model = User
#         fields = [
#             'first_name', "email", "last_name", "phone", "image", "username", "id", "is_verified_email",
#             "country", "state", "city", "is_verified_phone", "token", "provider",
#             "password", "color", "kind", "image_url"
#         ]
#         read_only_fields = ['first_name', "last_name", "phone", "image", "username", "id",
#                             "is_verified_email",
#                             "country", "state", "city", "is_verified_phone", "color"]
#
#     # def get_image_url(self, obj):
#     #     return get_image_url(obj.image)
#
#
#     def validate_email(self, attrs):
#         email = attrs
#         if not User.objects.filter(email=email).exists():
#             raise ValidationError(_("User does not exist."))
#         return attrs
#
#     def validate(self, attrs):
#         email = attrs.get("email", None)
#         password = attrs.get("password", None)
#         user = auth.authenticate(email=email, password=password)
#         if not user:
#             raise serializers.ValidationError({"password": "incorrect password"})
#         if "staff" in self.context['request'].query_params:
#             if not user.is_staff:
#                 raise serializers.ValidationError({
#                     'email': _('you did not have permission to login as staff')
#                 })
#         ip = get_ip_header(self.context['request'])
#
#         tt, token = TokenWithEx.objects.get_or_create(user=user, IPAddress=ip)
#         # tt, token = TokenWithEx.objects.get_or_create(user=user)
#         data = UserInfoSer(instance=user, context=self.context).data
#         data['token'] = tt.key
#         data['provider'] = user.provider
#         return data
#
#
# class ResetPasswordEmailRequestSerializer(serializers.Serializer):
#     email = serializers.EmailField(min_length=2)
#
#     class Meta:
#         fields = ["email"]
#
#
# class SetNewPasswordSerializer(serializers.Serializer):
#     password = serializers.CharField(min_length=6, max_length=68, write_only=True)
#     token = serializers.CharField(min_length=1, write_only=True)
#     uidb64 = serializers.CharField(min_length=1, write_only=True)
#
#     class Meta:
#         fields = ["password", "token", "uidb64"]
#
#     def validate(self, attrs):
#         try:
#             password = attrs.get("password")
#             token = attrs.get("token")
#             uidb64 = attrs.get("uidb64")
#
#             id = force_str(urlsafe_base64_decode(uidb64))
#             user = User.objects.get(id=id)
#             if not PasswordResetTokenGenerator().check_token(user, token):
#                 raise AuthenticationFailed("The reset link is invalid", 401)
#
#             user.set_password(password)
#             user.save()
#
#             return user
#         except Exception as e:
#             raise AuthenticationFailed("The reset link is invalid", 401)
#
#
# #
# #
#
#
# class LogoutSerializer(serializers.Serializer):
#     token = serializers.CharField()
#     default_error_messages = {"bad_token": _("Token is expired or invalid")}
#
#     def validate(self, attrs):
#         self.token = attrs["token"]
#         return attrs
#
#     def save(self, **kwargs):
#         try:
#             TokenWithEx.objects.get(key=self.token).delete()
#         except:
#             self.fail("bad_token")
#
#
# #
# #
# # class UserSer(serializers.ModelSerializer):
# #     class Meta:
# #         model = User
# #         fields = ['id', "get_username"]
#
#
# class UserBetaInfoSer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = [
#             'first_name', "email", "last_name",
#             "phone", "image", "id"
#         ]
#
#
# class ChangePasswordSer(serializers.Serializer):
#     old_password = serializers.CharField(min_length=6, write_only=True)
#     new_password = serializers.CharField(max_length=68, min_length=6, write_only=True)
#
#     def validate(self, attrs):
#         old_password = attrs.get('old_password', None)
#
#         user = self.context['request'].user
#         if user.check_password(old_password):
#             return attrs
#         raise serializers.ValidationError({"old_password": _("incorrect password")})
#
#     def save(self, **kwargs):
#         user = self.context['request'].user
#         user.set_password(self.validated_data['new_password'])
#         user.save()
#         return user
#
#
# class UserInfoBetaSer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = [
#             'first_name', "email", "last_name",
#             "phone", "image", "last_login",
#             "id", "country", "is_staff"
#         ]
#         extra_kwargs = {
#             'is_staff': {'read_only': True},
#             'email': {'read_only': True}
#         }
#
#     def get_rate(self, obj):
#         return 3.5
#
#     def get_percent(self, obj):
#         return obj.completion_percentage
#
#     def get_is_fav(self, obj):
#         user = self.context['request'].user
#         if user.is_authenticated:
#             if obj in user.fav.all():
#                 return True
#         return False
#
#
# class ChatMessageSer(serializers.ModelSerializer):
#     class Meta:
#         model = ChatMessageModel
#         fields = '__all__'
#
#
# import os
#
#
# class ChatMessageSer_(serializers.ModelSerializer):
#     sender = serializers.HiddenField(default=serializers.CurrentUserDefault())
#
#     class Meta:
#         model = ChatMessageModel
#         fields = '__all__'
#
#     def create(self, validated_data):
#         user_sender = self.context['request'].user
#         # print(user_sender.chat.users.exclude(id=user_sender.id).first().chat, validated_data['chat'])
#         if user_sender.chat.users.exclude(id=user_sender.id).first().chat == validated_data['chat']:
#             validated_data['read'] = True
#             # print('ssss')
#             return super().create(validated_data)
#         return super().create(validated_data)
#
#
# from .register import register_social_user
# from rest_framework.exceptions import AuthenticationFailed
#
#
# class GoogleSocialAuthSerializer(serializers.Serializer):
#     auth_token = serializers.CharField()
#
#     def validate_auth_token(self, auth_token):
#         user_data = google_auth.Google.validate(auth_token)
#         # print(user_data)
#         try:
#             user_data['sub']
#         except:
#             raise serializers.ValidationError(
#                 'The token is invalid or expired. Please login again.'
#             )
#
#         if user_data['aud'] != os.environ.get('GOOGLE_CLIENT_ID'):
#             raise AuthenticationFailed('oops, who are you?')
#         user_id = user_data['sub']
#         email = user_data['email']
#         name = user_data['name']
#         provider = 'google'
#         image = user_data['picture']
#
#         return register_social_user(
#             provider=provider, user_id=user_id,
#             email=email, name=name, image=image, ip=get_ip_header(self.context['request']))
#
#
# class UserKindSer(serializers.ModelSerializer):
#     class Meta:
#         model = UserKindModel
#         fields = "__all__"
#
#
# class AskForVerifyWhatsappSer(serializers.ModelSerializer):
#     user = serializers.HiddenField(default=serializers.CurrentUserDefault())
#     phone = serializers.CharField(min_length=10, max_length=15, required=False)
#
#     class Meta:
#         model = VerifyPhone
#         fields = ['id', "user", "phone"]
#
#     def validate(self, attrs):
#         attrs['phone'] = attrs['user'].phone
#         return attrs
#
#     def create(self, validated_data):
#         VerifyPhone.objects.filter(user=validated_data['user']).delete()
#         return super().create(validated_data)
#
#
# class CheckOTPSer(serializers.Serializer):
#     code = serializers.CharField(min_length=4, max_length=5)
#
#     def validate(self, attrs):
#         code = attrs.get('code')
#         user = self.context['request'].user
#         if not VerifyPhone.objects.filter(user=user, code=code).exists():
#             raise serializers.ValidationError({
#                 'code': _('code is incorrect')
#             })
#         return attrs
#
#     def save(self, **kwargs):
#         user = self.context['request'].user
#         user.is_verified_phone = True
#         user.save()
#         VerifyPhone.objects.filter(user=user).update(verified=True)
#         return user
#
