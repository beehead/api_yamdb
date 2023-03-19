from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class User(AbstractUser):
    """Custom user model."""
    USER_ROLE = (
        ('user', 'user'),
        ('moderator', 'moderator'),
        ('admin', 'admin'),
    )
    role = models.CharField(
        max_length=20,
        choices=USER_ROLE,
        default='user',
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
        blank=False,
    )
    username = models.CharField(
        max_length=150,
        unique=True,
    )
    bio = models.TextField(max_length=255, blank=True)
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    confirmation_code = models.CharField(
        max_length=20,
        blank=False,
        null=True,
        unique=True,
        editable=False,
    )
    is_active = models.BooleanField(default=True)

    REQUIRED_FIELDS = ['email']

    @property
    def is_user(self):
        return self.role == 'user'

    @property
    def is_admin(self):
        return self.role == 'admin' or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == 'moderator'

    def __str__(self):
        return f'{self.username}'
