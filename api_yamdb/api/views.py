from accounts.models import User
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.filters import SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from reviews.models import Categories, Genres, Review, Title

from .filters import TitleFilters
from .mixins import CRUDMixin
from .permissions import IsAdmin, IsAdminOrReadOnly, IsAuthorOrAdminOrModerator
from .serializers import (
    CategoriesSerializer,
    CommentSerializer,
    GenresSerializer,
    GetJWTSerializer,
    ReviewSerializer,
    SendTokenSerializer,
    TitleCRUDSerializer,
    TitleSerializer,
    UserSerializer,
)


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
    serializer.is_valid(raise_exception=True)
    user, _ = User.objects.get_or_create(
        email=email,
        username=username
    )
    token = default_token_generator.make_token(user)
    mail_subject = 'Код подтверждения на YAMDB'
    message = f'Ваш код подтверждения: {token}'
    send_mail(mail_subject, message, settings.EMAIL_HOST_USER, [email])
    answer = {
        'email': email,
        'username': username,
    }
    return Response(answer, status=status.HTTP_200_OK)


@api_view(['POST'])
def get_jwt(request):
    """
    This function generates a JSON Web Token (JWT) for a given user.
    Parameters:
    -----------
    request : HttpRequest object
        The request object that contains the user data.
    Returns:
    --------
    Response object
        The response object that contains the JWT for the user.
    Raises:
    -------
    Http404
        If the user is not found in the database.
    """
    serializer = GetJWTSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data['username']
    confirmation_code = serializer.validated_data['confirmation_code']
    user = get_object_or_404(User, username=username)
    if not default_token_generator.check_token(user, confirmation_code):
        return Response(
            'Неверный код подтверждения',
            status=status.HTTP_400_BAD_REQUEST
        )
    token = AccessToken.for_user(user)
    return Response(
        {'token': f'{token}'},
        status=status.HTTP_200_OK
    )


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
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
    def user_info(self, request):
        """
        Returns and update the current user's information.

        :param request: The HTTP request object.
        :return: The current user's information or update status.
        """
        serializer = UserSerializer(
            request.user,
            data=request.data,
            partial=True,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        if request.method == 'PATCH':
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
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
