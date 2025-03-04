import os

import boto3
from botocore.config import Config
from django.template.loader import render_to_string
from django.utils.encoding import smart_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework import generics, status, permissions
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from main_.permissions import IsOwnerOrReadOnly
from main_.viewset import ModelViewSetIndividual
from authentication.models import TokenWithEx, User, UserKindModel
from authentication.serializers import LoginSerializer, LogoutSerializer, UserInfoSer, RegisterSerializer, \
    ChangePasswordSer, ResetPasswordEmailRequestSerializer, UserKindSer, \
    SetNewPasswordSerializer, AskForVerifyWhatsappSer, CheckOTPSer
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _
from dotenv import load_dotenv

from photographer.settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_S3_REGION_NAME, AWS_S3_ENDPOINT_URL, \
    AWS_STORAGE_BUCKET_NAME
from structure.models import CategoryModel, ProjectFilesModel
from structure.serializers import ProjectFilesSerializer
from . import Utils

load_dotenv()


class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    # permission_classes = [HasAPIKey]

    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data, context={"request": request})
        if serializer.is_valid():
            user = serializer.save()
        else:
            return Response(
                {
                    "status": False,
                    "message": serializer.errors,
                    "data": None,
                },
                status=status.HTTP_406_NOT_ACCEPTABLE,
            )
        data = serializer.data
        data['token'] = TokenWithEx.objects.create(user=user).key
        return Response(
            {
                "status": True,
                "message": _('all is done'),
                'data': data
            },
            status=status.HTTP_200_OK,
        )


class LoginAPIView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    # permission_classes = [HasAPIKey]

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        if serializer.is_valid():
            return Response(
                {
                    "status": True,
                    "message": _("logged successfully"),
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        else:
            # r = serializer.data.get("email")
            return Response(
                {"status": False, "message": serializer.errors, "data": {}}, status=status.HTTP_400_BAD_REQUEST
            )


class RequestPasswordResetEmail(generics.GenericAPIView):
    serializer_class = ResetPasswordEmailRequestSerializer

    def post(self, request):
        email = request.data.get("email", "")
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            current_site = f"localhost:3000/en/reset-password?uidb64={uidb64}&sub={token}"

            # absurl = "https://" + current_site + relativeLink
            # email_body = "Hello, \n Use link below to reset your password  \n" + absurl
            context = {"url": f"https://{current_site}"}
            rendered = render_to_string("reset-password.html", context=context)
            data = {
                "body": rendered,
                "to": [user.email],
                "subject": "Reset your password",
            }
            Utils.send_email_without_file(**data, html=True)
            return Response(
                {
                    "status": True,
                    "message": _("We have sent you a link to reset your password"),
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {"status": False, "message": _("this email is not register")},
            status=status.HTTP_200_OK,
        )


class SetNewPasswordAPIView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        if serializer.is_valid():
            return Response(
                {"status": True, "message": _("Password reset success")},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"status": False, "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )


class LogoutAPIView(generics.GenericAPIView):
    serializer_class = LogoutSerializer

    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()

            return Response(
                {"status": True, "message": "logout done"}, status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"status": False, "message": serializer.errors},
                status=status.HTTP_200_OK,
            )


class UserInfoView(generics.GenericAPIView):
    serializer_class = UserInfoSer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        ser = self.serializer_class(request.user, context={"request": request})
        return Response({
            "status": True,
            "message": _("all is done"),
            "results": ser.data
        })

    def patch(self, request):
        ser = self.serializer_class(data=request.data,
                                    instance=request.user, context={"request": request}, partial=True)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response({
            "status": True,
            "message": _("all is done"),
            "results": ser.data
        })


class ChangePasswordView(generics.GenericAPIView):
    serializer_class = ChangePasswordSer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": True,
                "message": _("password changed successfully"),
            })
        return Response({
            "status": False,
            "message": serializer.errors,
        })


from .serializers import GoogleSocialAuthSerializer


class GoogleSocialAuthView(generics.GenericAPIView):
    serializer_class = GoogleSocialAuthSerializer

    def post(self, request):
        """

        POST with "auth_token"

        Send an idtoken as from google to get user information

        """

        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data['auth_token']
        return Response(
            {
                "status": True,
                "message": _("logged successfully"),
                "data": data,
            },
            status=status.HTTP_200_OK,
        )


class UserKindView(ModelViewSetIndividual):
    queryset = UserKindModel.objects.all()
    serializer_class = UserKindSer
    permission_classes = [IsOwnerOrReadOnly]
    # http_method_names = ['get']


class AskForVerifyWhatsappView(generics.GenericAPIView):
    serializer_class = AskForVerifyWhatsappSer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": True,
                    "message": _("we send an OTP to your whatsapp"),
                },
                status=status.HTTP_200_OK,
            )
        else:
            # r = serializer.data.get("email")
            return Response(
                {"status": False, "message": serializer.errors, "data": {}}, status=status.HTTP_400_BAD_REQUEST
            )

    def patch(self, request):
        serializer = CheckOTPSer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": True,
                    "message": _("Your phone verified successfully"),
                },
                status=status.HTTP_200_OK,
            )
        else:
            # r = serializer.data.get("email")
            return Response(
                {"status": False, "message": serializer.errors, "data": {}}, status=status.HTTP_400_BAD_REQUEST
            )


class GeneratePresignedUrl(APIView):
    # permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            config=Config(region_name=AWS_S3_REGION_NAME),
            endpoint_url=AWS_S3_ENDPOINT_URL
        )

        bucket_name = AWS_STORAGE_BUCKET_NAME
        object_name = request.query_params.get('file_name')  # اسم الملف الذي سيتم رفعه
        # file_type = request.query_params.get('file_type')  # اسم الملف الذي سيتم رفعه

        try:
            # توليد رابط موقّع
            presigned_url = s3_client.generate_presigned_url(
                'put_object',
                Params={
                    'Bucket': bucket_name,
                    'Key': object_name,
                    # "ContentType": "image/webp",
                    # "conditions": [{"Content-Type": "image/webp"}]

                },
                ExpiresIn=3600  # صلاحية الرابط لمدة ساعة
            )
            return Response({"url": presigned_url}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserView(ModelViewSetIndividual):
    queryset = User.objects.all()
    serializer_class = UserInfoSer
    permission_classes = [IsOwnerOrReadOnly]
    http_method_names = ['get']
    lookup_field = "username"
    search_fields = ["first_name", "email", "phone"]

    @action(detail=True, methods=['get'],
            url_path='files_category', url_name='files_category'
            )
    def get_files_category(self, request, username=None):
        user = self.get_object()
        if "categories__id" in request.query_params:
            categories = CategoryModel.objects.filter(user=user, id=request.query_params.get("categories__id"))
        else:
            categories = CategoryModel.objects.filter(user=user)
        queryset = ProjectFilesModel.objects.filter(categories__in=categories)
        page = self.paginate_queryset(queryset)
        self.serializer_class = ProjectFilesSerializer
        if page is not None:
            serializer = ProjectFilesSerializer(page, many=True, context={"request": request})
            data = self.get_paginated_response(serializer.data).data
            data['status'] = True
            data['message'] = _("all is done")
            return Response(data)
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "status": True,
            "results": serializer.data
        })

