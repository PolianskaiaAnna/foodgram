from django.contrib.auth.models import AbstractUser
from django.db import models
from users.validators import username_not_me, username_validator

LENG_EMAIL = 254
LENG_USER = 150


class User(AbstractUser):
    """Класс, описывающий кастомную модель пользователя"""

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    username = models.CharField(
        'Имя пользователя',
        max_length=LENG_USER,
        unique=True,
        validators=[username_validator, username_not_me]
    )
    email = models.EmailField(
        'Email', max_length=LENG_EMAIL, unique=True
    )
    first_name = models.CharField(
        'Имя', blank=True, max_length=LENG_USER
    )
    last_name = models.CharField(
        'Фамилия', blank=True, max_length=LENG_USER
    )
    avatar = models.ImageField(
        upload_to='static/avatars/',
        null=True
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.email


class Subscribe(models.Model):
    """Модель подписки пользователей друг на друга"""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='follows'
    )
    following = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Подписки',
        related_name='followers'
    )

    class Meta:
        verbose_name = 'Подписки'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user.email} подписан на {self.following.email}'
