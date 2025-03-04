from rest_framework import serializers
from .models import BannersModel, CodeModel, CoursesModel, TeachersModel,LessonsModel2,User
import authentication.models



class UserSer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=("username","email",'is_authenticated','is_staff','reset_password_token','reset_password_expire')

class BannersSer(serializers.ModelSerializer):
    class Meta:
        model = BannersModel
        fields = "__all__"


class CodeSer(serializers.ModelSerializer):
    class Meta:
        model = CodeModel
        fields = "__all__"


        
class LessonsSer(serializers.ModelSerializer):
    title=serializers.CharField(read_only=True)
    users=UserSer(many=True)
    class Meta:
        model=LessonsModel2
        fields= ('id','title','users')
        extra_kwargs={
            'id':{'read_only':False}
        }
class LessonAdminSer(serializers.ModelSerializer):
    class Meta:
        model=LessonsModel2
        fields="__all__"
        
class LessonPurchaseSer(serializers.ModelSerializer):
    class Meta:
        model=LessonsModel2
        fields=['title','description','course','price','button']

class CoursesSer(serializers.ModelSerializer):
    #lessons = LessonsSer(many=True, read_only=True)
    class Meta:
        model = CoursesModel
        fields = "__all__"


