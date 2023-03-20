# Generated by Django 3.2 on 2023-03-20 13:39

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0002_auto_20230318_1842'),
    ]

    operations = [
        migrations.AlterField(
            model_name='title',
            name='year',
            field=models.PositiveIntegerField(validators=[django.core.validators.MaxValueValidator(2023, message='Год не может быть больше текущего!')], verbose_name='Год'),
        ),
    ]