from .views import BannersView , CourseView ,LessonsView,UsersView
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static




router = DefaultRouter()
router.register("banners", BannersView)
router.register("banners1", BannersView, basename="banners1")
router.register("banners2", BannersView, basename="banners2")
router.register("banners3", BannersView, basename="banners3")
router.register("banners4", BannersView, basename="banners4")
router.register("courses",CourseView,basename="courses")
router.register("lessons",LessonsView,basename="lessons")
router.register("users",UsersView,basename="users")



urlpatterns = [
    # path('banners/', BannersView.as_view())
    path('', include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)