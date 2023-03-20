import re

from accounts.models import User
from rest_framework import serializers


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
        raise serializers.ValidationError('Already exists!')
    return value
