from django.contrib.auth.hashers import make_password
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)
from datetime import  timedelta
from rest_framework.authtoken.models import Token

from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now
from django.db.utils import IntegrityError

# Create your models here


class UserManager(BaseUserManager):
    
    def create_user(self,username,email,password=None,is_verified=True,**extra_fields):
        
        if username==None:
            raise TypeError("Username field is empty")
        
        if email==None:
            raise TypeError("Email field is empty")
        

        user=self.model(username=username,
                        email=self.normalize_email(email),
                        is_verified=is_verified,
                        
                        **extra_fields)
        if password is None:
            user.password = None
        else:
            user.set_password(password)
        user.save()
        return user
        
    def create_superuser(self,username,email,password,**extra_fields):
        
        if password==None:
            raise ValueError("Password field is empty")

        user=self.create_user(username,email,password,**extra_fields)
        user.is_superuser = True
        user.is_active = True
        user.is_staff = True
        user.is_verified = True
        user.save()
        return user
  
  
  
    
class User(AbstractBaseUser,PermissionsMixin):
    
    username=models.CharField(max_length=65,unique=True,db_index=True)
    email=models.EmailField(max_length=65,unique=True,db_index=True)
    is_verified=models.BooleanField(default=True)
    is_active=models.BooleanField(default=True)  
    is_staff=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    reset_password_token = models.CharField(max_length=50,default="",blank=True)
    reset_password_expire = models.DateTimeField(null=True,blank=True)
    
    
    
    USERNAME_FIELD='email'
    REQUIRED_FIELDS=['username']
    
    objects=UserManager()
    
    def __str__(self):
        return self.email
    
    # def tokens(self):
    #     return "" #incomplete
    


class YearsModel(models.Model):
    year = models.CharField(max_length=4)
    def __str__(self):
        return self.year
    class Meta:
        verbose_name= 'Year'
   
    
            
        

class TeachersModel(models.Model):
    name = models.CharField(max_length=100)
    image = models.TextField()
    description = models.TextField()
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True, null=True)

    
            
            
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name= 'Teacher'
    



class CoursesModel(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = models.TextField()
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True, null=True)
    teacher = models.ForeignKey(TeachersModel, on_delete=models.SET_NULL,null=True, related_name="courses")
    year = models.ForeignKey(YearsModel, on_delete=models.SET_NULL,null=True, related_name="courses")

    

    def __str__(self):
        return self.title
    class Meta:
        verbose_name= 'Course'


class LessonsModel2(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    video = models.FileField(upload_to="lessons/",blank=True)
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True, null=True)
    course = models.ForeignKey(CoursesModel, on_delete=models.CASCADE, related_name="lessons")
    price = models.IntegerField(null=True)
    button = models.URLField(null=True, max_length=500, verbose_name="Click here to buy",blank=True)
    users = models.ManyToManyField(User, related_name="lessons", blank=True)  # Users who have access
    
    
    
    class Meta:
        verbose_name= 'Lesson'

    def __str__(self):
        return self.title

class AccessLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="lesson_access")
    lesson = models.ForeignKey(LessonsModel2, on_delete=models.CASCADE, related_name="access_logs")
    first_access_time = models.DateTimeField(auto_now_add=True)

    def has_expired(self):
        return now() >= self.first_access_time + timedelta(hours=2) 

    def remaining_time(self):
        expiration_time = self.first_access_time + timedelta(hours=2)
        remaining = expiration_time - now()
        return max(remaining.total_seconds(), 0)
    
    

class BannersModel(models.Model):
    image = models.ImageField(upload_to="banners/")
    class Meta:
        verbose_name= 'Banner'
        
    


class MajorsModel(models.Model):
    major=models.CharField(max_length=30,null=True)
    class Meta:
        verbose_name= 'Major'
        
    
    
    
class StudentModel(models.Model):
    name = models.CharField(max_length=100,null=True)
    image = models.TextField(max_length=50,null=True)
    description = models.TextField(max_length=500,null=True)
    major = models.ForeignKey(MajorsModel, on_delete=models.PROTECT, related_name='student', default=1)
    year=models.ForeignKey(YearsModel,on_delete=models.PROTECT,related_name='student',default=1)
    
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True, null=True)
    class Meta:
        verbose_name= 'Student'
        
    
    

    def __str__(self):
        return self.name





class CodeModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="codes",null=True)
    code = models.CharField(max_length=100)
    used = models.BooleanField(default=False)
    video = models.ForeignKey(LessonsModel2, on_delete=models.CASCADE, related_name="codes")
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True, null=True)
    expire = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name= 'Code'

    def __str__(self):
        return self.code






