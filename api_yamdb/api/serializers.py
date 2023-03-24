"""Сериализаторы для приложения Api."""
import datetime

from accounts.models import User
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from reviews.models import Categories, Comment, Genres, Review, Title

from .validators import validate_dublicates, validate_role, validate_username


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователей."""
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
    role = serializers.CharField(
        required=False,
        validators=[validate_role],
    )

    def update(self, instance, validated_data):
        if self.context['request'].user.is_admin:
            instance.role = validated_data.get('role', instance.role)
        instance.first_name = validated_data.get(
            'first_name',
            instance.first_name
        )
        instance.last_name = validated_data.get(
            'last_name',
            instance.last_name
        )
        instance.email = validated_data.get('email', instance.email)
        instance.bio = validated_data.get('bio', instance.bio)
        instance.save()
        return instance

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
    """Сериализатор для данных отправки кода подтверждения."""
    email = serializers.EmailField(
        required=True,
        max_length=254,
    )
    username = serializers.CharField(
        required=True,
        max_length=150,
        validators=[validate_username],
    )

    def validate(self, attrs):
        email = attrs.get('email')
        username = attrs.get('username')

        if User.objects.filter(email__iexact=email).exists():
            user = User.objects.get(email__iexact=email)
            if user.username != username:
                raise serializers.ValidationError(
                    'Пользователь с таким email уже существует'
                )
        if User.objects.filter(username__iexact=username).exists():
            user = User.objects.get(username__iexact=username)
            if user.email != email:
                raise serializers.ValidationError(
                    'Пользователь с таким username уже существует'
                )
        return attrs


class GetJWTSerializer(serializers.Serializer):
    """Получение JWT."""
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
    rating = serializers.IntegerField()

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category',
        )
        read_only_fields = (
            'id', 'name', 'year', 'rating', 'description',
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
