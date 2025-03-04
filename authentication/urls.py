from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter

routers = DefaultRouter()
routers.register("user-kind", UserKindView)
routers.register("users", UserView)


app_name = "auth"
urlpatterns = [
    path('register/', RegisterView.as_view(), name="register"),
    path('login/', LoginAPIView.as_view(), name="login"),
    path('logout/', LogoutAPIView.as_view(), name="logout"),
    path('profile/', UserInfoView.as_view(), name="profile"),
    path('change-password/', ChangePasswordView.as_view(), name="change-password"),
    path("google/", GoogleSocialAuthView.as_view(), name="google"),
    path('verify-phone/', AskForVerifyWhatsappView.as_view()),

    path('get_url_patterns/', GeneratePresignedUrl.as_view(), name="search"),

    # path('verify/', UserVerifyView.as_view(), name="verify"),
    # path('users/', GetUserForDepartment.as_view(), name="users"),
    path('request-reset-email/', RequestPasswordResetEmail.as_view()),
    path('reset-email/', SetNewPasswordAPIView.as_view()),

    # path('login_super/', LoginAPIView.as_view(), name="login_super"),
    path('', include(routers.urls))

]
