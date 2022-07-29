from django.urls import include, path
from rest_framework.routers import SimpleRouter
from lesson.lesson.views import LessonViewSet

app_name = 'lesson'

router = SimpleRouter()
router.register('lesson', LessonViewSet, basename='lesson')


urlpatterns = [
    path('', include((router.urls))),
]
