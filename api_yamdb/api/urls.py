"""Эндпойнты приложения YaMDb."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter
from api.views import (
    send_token,
    get_jwt,
    CategoryViewSet,
    GenreViewSet,
    TitleViewSet,
    UserViewSet,
    CommentViewSet,
    ReviewViewSet,
)

router = DefaultRouter()

router.register('users', UserViewSet, basename='users')
router.register('categories', CategoryViewSet, basename='categories')
router.register('genres', GenreViewSet, basename='genres')
router.register('titles', TitleViewSet, basename='titles')
router.register(r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet,
                basename='reviews')
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet, basename='Comment')

urlpatterns = [
    path("v1/", include(router.urls)),
    path('v1/auth/signup/', send_token, name='send_token'),
    path('v1/auth/token/', get_jwt, name='get_jwt'),
]
