"""Кастомный миксин для приложения Api."""

from rest_framework import mixins, viewsets


class CRUDMixin(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    pass
