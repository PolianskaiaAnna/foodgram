from django.db import models
from django.contrib.auth.models import AbstractUser

LENG_EMAIL = 254
LENG_USER = 150


class User(AbstractUser):
    """Класс, описывающий кастомную модель пользователя"""
   
    username = models.CharField(
        'Имя пользователя',
        max_length=LENG_USER,
        unique=True
    )
    password = models.CharField(
        'Имя', blank=True, max_length=LENG_USER
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
        upload_to='users/avatars/',
        null=True, blank=True
    )
   
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username
    
    
class Follow(models.Model):
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
