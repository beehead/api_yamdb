"""Сериализаторы для приложения Api."""
import datetime
import re

from rest_framework import serializers
from accounts.models import User
from reviews.models import Categories, Genres, Title, Comment, Review

from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError


def validate_username(value):
    regex = r'^[\w.@+-]+$'
    if value == 'me' or not re.match(regex, value):
        raise serializers.ValidationError('Invalid username format')
    return value


def validate_role(value):
    roles = ['user', 'admin', 'moderator']
    if value not in roles:
        raise serializers.ValidationError('Invalid role')
    return value


def validate_dublicates(value):
    if (
        User.objects.filter(username__iexact=value).exists()
        or User.objects.filter(email__iexact=value).exists()
    ):
        raise serializers.ValidationError('Дубликат!')
    return value

class UserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(
        max_length=150,
        required=False
    )
    last_name = serializers.CharField(
        max_length=150,
        required=False
    )
    username = serializers.CharField(
        max_length=150,
        required=True,
        validators=[validate_username]
    )

    class Meta:
        fields = (
            'first_name',
            'last_name',
            'username',
            'bio',
            'email',
            'role'
        )
        read_only_fields = ('role',)
        model = User


class AdminSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(
        max_length=150,
        required=False
    )
    last_name = serializers.CharField(
        max_length=150,
        required=False
    )
    username = serializers.CharField(
        max_length=150,
        required=True,
        validators=[validate_username, validate_dublicates],
    )
    email = serializers.EmailField(
        max_length=254,
        required=True,
        validators=[validate_dublicates]
    )

    class Meta:
        fields = (
            'first_name',
            'last_name',
            'username',
            'bio',
            'email',
            'role'
        )
        model = User


class SendTokenSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, max_length=254)
    username = serializers.CharField(
        required=True,
        max_length=150,
        validators=[validate_username]
    )


class GetGWTSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)


class CategoriesSerializer(serializers.ModelSerializer):
    """Сериализатор для категорий."""

    class Meta:
        model = Categories
        fields = ('name', 'slug')


class GenresSerializer(serializers.ModelSerializer):
    """Сериализатор для жанров."""

    class Meta:
        model = Genres
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    """GET-cериализатор для произведений."""

    category = CategoriesSerializer(many=False, read_only=True)
    genre = GenresSerializer(many=True, read_only=True)
    rating = 'заглушка для рейтинга'

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'description', 'genre', 'category',
        )
        read_only_fields = (
            'id', 'name', 'year', 'description',
        )


class TitleCRUDSerializer(serializers.ModelSerializer):
    """CRUD-cериализатор для произведений."""

    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Categories.objects.all()
    )
    genre = serializers.SlugRelatedField(
        many=True,
        slug_field='slug',
        queryset=Genres.objects.all()
    )

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'description', 'genre', 'category'
        )

    def validate_year(self, value):
        """Проверка чтобы год не был больше текущего."""
        if value > datetime.datetime.now().year:
            raise serializers.ValidationError(
                'Год не может быть больше текущего!')
        return value


class ReviewSerializer(serializers.ModelSerializer):
    title = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    def validate_score(self, value):
        if 0 > value > 10:
            raise serializers.ValidationError('Оценка по 10-бальной шкале!')
        return value

    def validate(self, data):
        request = self.context['request']
        author = request.user
        title_id = self.context.get('view').kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        if (
            request.method == 'POST'
            and Review.objects.filter(title=title, author=author).exists()
        ):
            raise ValidationError('Может существовать только один отзыв!')
        return data

    class Meta:
        fields = '__all__'
        model = Review


class CommentSerializer(serializers.ModelSerializer):
    review = serializers.SlugRelatedField(
        slug_field='text',
        read_only=True
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        fields = '__all__'
        model = Comment
