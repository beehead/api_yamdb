"""Настройка админ-панели приложения reviews."""

from django.contrib import admin
from .models import Categories, Genres, Title, TitleGenres


@admin.register(Categories)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug',)
    search_fields = ('name',)
    list_filter = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    empty_value_display = '-пусто-'


@admin.register(Genres)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug',)
    search_fields = ('name',)
    list_filter = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    empty_value_display = '-пусто-'


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ('name', 'year', 'description', 'category', 'get_genre',)
    search_fields = ('name', 'year', 'category',)
    list_filter = ('name', 'year', 'category',)
    empty_value_display = '-пусто-'

    def get_genre(self, object):
        """Выводит в админку жанр произведения, иначе ошибка."""
        return ',\n'.join((genre.name for genre in object.genre.all()))
    get_genre.short_description = 'Жанр'


@admin.register(TitleGenres)
class GenreTitleAdmin(admin.ModelAdmin):

    list_display = ('genre', 'title')
    list_filter = ('genre',)
    search_fields = ('title',)
    empty_value_display = '-пусто-'
