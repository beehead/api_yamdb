import random
import string

from django.core.mail import send_mail
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.pagination import LimitOffsetPagination

from accounts.models import User
from reviews.models import Categories, Genres, Title, Review
from .filters import TitleFilters
from .mixins import CRUDMixin
from .permissions import (
    IsAdmin,
    IsAdminOrReadOnly,
    IsAuthorOrAdminOrModerator,
)
from .serializers import (
    SendTokenSerializer,
    GetGWTSerializer,
    CategoriesSerializer,
    GenresSerializer,
    TitleSerializer,
    TitleCRUDSerializer,
    UserSerializer,
    AdminSerializer,
    ReviewSerializer,
    CommentSerializer
)


EMAIL_SENDER = 'admin <admin@yamdb.ru>'
RANDOM_STRING_LENGTH = 20


@api_view(['POST'])
def send_token(request):
    """
    Sends a confirmation code to the specified email address.

    If the email address is not associated, a new user is created.
    The confirmation code is stored in the user's confirmation_code field.

    :param request: The HTTP request containing the email address.
    :return: A HTTP response indicating whether the code was sent successfully.
    """
    serializer = SendTokenSerializer(data=request.data)
    email = request.data.get('email', False)
    username = request.data.get('username', False)

    if serializer.is_valid():
        random_string = ''.join(
            random.choices(
                string.ascii_uppercase + string.digits, k=RANDOM_STRING_LENGTH
            )
        )
        user = User.objects.filter(email=email).first()
        user_check = User.objects.filter(username=username).first()
        if ((user or user_check) and user != user_check):
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        if not user:
            User.objects.create_user(
                email=email,
                username=username)
        User.objects.filter(email=email).update(
            confirmation_code=random_string
        )
        mail_subject = 'Код подтверждения на YAMDB'
        message = f'Ваш код подтверждения: {random_string}'
        send_mail(mail_subject, message, EMAIL_SENDER, [email])
        answer = {
            'email': email,
            'username': username,
        }
        return Response(answer, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def get_jwt(request):
    serializer = GetGWTSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data['username']
        confirmation_code = serializer.validated_data['confirmation_code']
        user = get_object_or_404(User, username=username)
        if user.confirmation_code != confirmation_code:
            return Response(
                'Неверный код подтверждения',
                status=status.HTTP_400_BAD_REQUEST
            )
        token = AccessToken.for_user(user)
        return Response(
            {'token': f'{token}'},
            status=status.HTTP_200_OK
        )
    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = AdminSerializer
    permission_classes = (IsAdmin,)
    lookup_field = 'username'
    filter_backends = (SearchFilter, )
    search_fields = ('username', )
    http_method_names = ['get', 'post', 'patch', 'delete']
    pagination_class = LimitOffsetPagination

    @action(
        methods=['get', 'patch'],
        detail=False,
        permission_classes=(IsAuthenticated,),
        url_path='me'
    )
    def get_current_user_info(self, request):
        if request.method == 'PATCH':
            if request.user.is_admin:
                serializer = AdminSerializer(
                    request.user,
                    data=request.data,
                    partial=True)
            else:
                serializer = UserSerializer(
                    request.user,
                    data=request.data,
                    partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class CategoryViewSet(CRUDMixin):
    queryset = Categories.objects.all()
    serializer_class = CategoriesSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class GenreViewSet(CRUDMixin):
    queryset = Genres.objects.all()
    serializer_class = GenresSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all().annotate(rating=Avg('reviews__score'))
    serializer_class = TitleSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilters

    def get_serializer_class(self):
        if self.action in ['create', 'partial_update']:
            return TitleCRUDSerializer
        return TitleSerializer


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrAdminOrModerator,)

    def get_queryset(self):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id')
        )
        serializer.save(author=self.request.user, review=review)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorOrAdminOrModerator,)

    def get_queryset(self):
        title = get_object_or_404(
            Title,
            id=self.kwargs.get('title_id')
        )
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(
            Title,
            id=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)
