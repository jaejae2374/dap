from django.urls import include, path
from rest_framework.routers import SimpleRouter
from user.views import UserView
from user.core.academy.views import AcademyViewSet
from user.core.genre.views import GenreViewSet


app_name = 'user'

router = SimpleRouter()
router.register('user', UserView, basename='user')
router.register('academy', AcademyViewSet, basename='academy')
router.register('genre', GenreViewSet, basename='genre')

urlpatterns = [
    path('', include((router.urls))),
]
