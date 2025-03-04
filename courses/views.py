

from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.viewsets import ModelViewSet
from .models import BannersModel, CoursesModel, LessonsModel2,AccessLog,TeachersModel
from .models import User
from .serializers import BannersSer,CoursesSer, LessonsSer,LessonAdminSer,UserSer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from datetime import datetime,timedelta
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _



# Create your views here.
from django.conf import settings
import stripe

from django.shortcuts import get_object_or_404


stripe.api_key = settings.STRIPE_SECRET_KEY



class LessonsView(ModelViewSet):
    queryset = LessonsModel2.objects.all()
    serializer_class = LessonsSer 
    permission_classes=[AllowAny]
    
    def get_queryset(self):
        qs = super().get_queryset()
        
        
        
        if self.request.user.is_anonymous:
                raise PermissionDenied("No user provided.")
        
        
        
        if not self.request.user.is_staff:
           user = self.request.user

        
           course_id = self.request.query_params.get("course")
           if course_id:
               qs = qs.filter(course_id=course_id)

        
           return qs.filter(users=user)
       
       
        return qs
        
    def get_serializer_class(self):
        sc= super().get_serializer_class()
        if self.request.user.is_staff:
            return LessonAdminSer 
        return sc
    
    
    
    @action(detail=True, methods=['delete'], url_path="delete")
    def delete_lesson(self, request, pk=None):
        instance = self.get_object()
        instance.delete()  
        return Response({"status": True, "message": "Deleted Successfully"}, status=status.HTTP_204_NO_CONTENT)



        
    @action(detail=True, methods=['post'], url_path="buy")
    def buy_lesson(self, request, pk=None):
        lesson = get_object_or_404(LessonsModel2, pk=pk)
        user = request.user

    
        lesson.users.add(user)

        return Response({"message": _("Lesson purchased successfully!")})
    
    @action(detail=True, methods=['get'], url_path="view-lesson")
    def view_lesson(self, request, pk=None):
        
        lesson = get_object_or_404(LessonsModel2, pk=pk)
        user = request.user

        
        if not lesson.users.filter(id=user.id).exists():
            return Response({"message": _("You have not purchased this lesson.")}, status=status.HTTP_403_FORBIDDEN)

        
        access_log, created = AccessLog.objects.get_or_create(user=user, lesson=lesson)

        if not created:  
            if access_log.has_expired():
                return Response({"message": _("Your access time has expired.")}, status=status.HTTP_403_FORBIDDEN)

        
        return Response({
            "message": _("Access granted"),
            "video_url": lesson.video.url,
            "remaining_time": access_log.remaining_time()
        })

    # @action(detail=True, methods=['get'], url_path="buy-lesson")
    # def buy_lesson(self, request, pk=None):
    #     lesson = get_object_or_404(LessonsModel, pk=pk)  # pk refers to the lesson ID
    #     user = request.user  # Assuming the logged-in user is buying
        
    #     return Response({"lesson_id": lesson.id, "user_id": user.id})
     
     

        
class UsersView(ModelViewSet):
    queryset=User.objects.all() 
    serializer_class=UserSer    
    
    @action(detail=False,methods=['POST'],url_path='resetpassword')
    def reset(self,request):
        data = request.data
        token = data['token']  # Pass token in request body
        user = get_object_or_404(User, reset_password_token=token)
        if user.reset_password_expire.replace(tzinfo=None) <datetime.now():
            return Response({'error':"Token expired"},status=status.HTTP_400_BAD_REQUEST)
        if data['password'] != data['confirmPassword']:
            return Response({'error':"Passwords dont match"},status=status.HTTP_400_BAD_REQUEST)
            
        user.password=make_password(data['password'])
        user.reset_password_token=""
        user.reset_password_expire=None
        user.save()
        return Response({"Details":"Password reset succesfully"})       
    
    @action(detail=False,methods=['POST'],url_path='forgotpassword',permission_classes=[IsAuthenticated])
   
    def forgot(self,request):
        data=request.data
        user=get_object_or_404(User,email=data['email'])
        token=get_random_string(40)
        expire_date=datetime.now() + timedelta(minutes=30)
        user.reset_password_token=token
        user.reset_password_expire=expire_date
        
        user.save()
        
        
        link = f"http://127.0.0.1:8000/resetpassword/",
        body = f"Your password reset link is : {link}, use token: {token}"
        send_mail(
        subject= "Paswword reset from Tarek",
        message= body,
        from_email=  "DjangoAdmin@gmail.com",
        recipient_list=  [data['email']]
        )
        return Response({'details': 'Password reset sent to {email}'.format(email=data['email'])})


    
        

       
    
    
    

class CourseView(ModelViewSet):
    queryset = CoursesModel.objects.all()
    serializer_class = CoursesSer
    #http_method_names=['get',"post"] # this line specifies which operation you want, removing it allows for get and post
    @action(detail=False, methods=['get'], url_path="get")
    def getcourses(self, request):
        queryset = self.queryset  # All courses
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)
  
    @action(detail=True, methods=['delete'], url_path="delete")
    def delete_course(self, request, pk=None):
            instance = self.get_object()  
            instance.delete()
            return Response({"status": True, "message": "Deleted successfully"})
        

    
class BannersView(ModelViewSet):
    queryset = BannersModel.objects.all()
    serializer_class = BannersSer
    http_method_names = ['get']

    #def get_queryset(self):
    #    return BannersModel.objects.filter(is_active=True)
    #
    # def get_serializer_class(self):
    #     if self.action == "retrieve":
    #         return BannersSer
    #     return BannersSer
    #
    # def get_permissions(self):
    #     if self.action in ['create', 'update', 'partial_update', 'destroy']:
    #         return [IsAuthenticated()]
    #     return []
    #
    # # def list(self, request, *args, **kwargs):
    # # def retrieve(self, request, *args, **kwargs):
    # # def create(self, request, *args, **kwargs):
    #
    # def update(self, request, *args, **kwargs):
    #     from rest_framework.exceptions import PermissionDenied
    #     raise PermissionDenied
    #
    # def partial_update(self, request, *args, **kwargs):
    #     from rest_framework.exceptions import PermissionDenied
    #     raise PermissionDenied
    #
    # def destroy(self, request, *args, **kwargs):
    #
    #     from rest_framework.exceptions import PermissionDenied
    #     raise PermissionDenied

    # @action(detail=False, methods=['get'], url_path="sss")
    # def active(self, request):
    #     queryset = BannersModel.objects.filter(id=1)
    #     serializer = BannersSer(queryset, many=True)
    #     return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path="delete")
    def sss2(self, request, pk):
        instance = self.get_object()
        return Response({"status": True, "message": "Deleted Successfully"})

