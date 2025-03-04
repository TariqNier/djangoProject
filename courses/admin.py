from django.contrib import admin
# Register your models here.
from .models import BannersModel,YearsModel,CoursesModel,TeachersModel,LessonsModel2,StudentModel,User,CodeModel


admin.site.register(BannersModel)
admin.site.register(YearsModel)
admin.site.register(CoursesModel)
admin.site.register(TeachersModel)
admin.site.register(LessonsModel2)
admin.site.register(StudentModel)
admin.site.register(CodeModel)
admin.site.register(User)





