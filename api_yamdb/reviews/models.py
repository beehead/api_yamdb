"""Модели для приложения reviews."""

from datetime import datetime

from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

from accounts.models import User


class Categories(models.Model):
    """Модель для категорий."""
    name = models.CharField(
        max_length=256,
        verbose_name='Имя категории'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Слаг категории'
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Genres(models.Model):
    """Модель для жанров."""
    name = models.CharField(
        max_length=256,
        verbose_name='Название'
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        unique=True,
    )

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Title(models.Model):
    """Модель для произведений."""
    name = models.CharField(
        max_length=256,
        verbose_name='Название'
    )
    year = models.PositiveIntegerField(
        verbose_name='Год',
        validators=[
            MaxValueValidator(
                int(datetime.now().year),
                message='Год не может быть больше текущего!')
        ],
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Описание'
    )
    category = models.ForeignKey(
        Categories,
        on_delete=models.SET_NULL,
        related_name='titles',
        null=True,
        verbose_name='Категория'
    )
    genre = models.ManyToManyField(
        Genres,
        through='TitleGenres',
        related_name='titles',
        verbose_name='Жанр'
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(fields=['name', 'year', 'category'],
                                    name='unique_media')
        ]

    def __str__(self):
        return self.name


class TitleGenres(models.Model):
    """Вспомогательная таблица многое-ко-многим - произведения и жанры."""
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение',)
    genre = models.ForeignKey(
        Genres,
        on_delete=models.CASCADE,
        verbose_name='Жанр'
    )

    class Meta:
        verbose_name = 'Произведение-Жанр'
        verbose_name_plural = 'Произведения-Жанры'

    def __str__(self):
        return f'{self.title}-{self.genre}'


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='произведение'
    )
    text = models.CharField(
        max_length=200
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='автор'
    )
    score = models.IntegerField(
        'оценка',
        validators=(
            MinValueValidator(1),
            MaxValueValidator(10)
        ),
        error_messages={'validators': 'Оценка от 1 до 10!'}
    )
    pub_date = models.DateTimeField(
        'дата публикации',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=('title', 'author', ),
                name='unique review'
            )]
        ordering = ('pub_date',)

    def __str__(self):
        return self.text


class Comment(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='отзыв'
    )
    text = models.CharField(
        'текст комментария',
        max_length=200
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='автор'
    )
    pub_date = models.DateTimeField(
        'дата публикации',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self
