from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager


LENG_EMAIL = 254
LENG_USER = 150


# class CustomUserManager(BaseUserManager):
#     def create_user(self, email, username, first_name, last_name, password=None, **extra_fields):
#         if not email:
#             raise ValueError('Поле имейл обязательно для заполнения')
#         email = self.normalize_email(email)
#         user = self.model(email=email, username=username, first_name=first_name, last_name=last_name, **extra_fields)
#         user.set_password(password)
#         user.save(using=self._db)
#         return user

    # def create_superuser(self, email, username, first_name, last_name, password=None, **extra_fields):
    #     extra_fields.setdefault('is_staff', True)
    #     extra_fields.setdefault('is_superuser', True)

    #     if extra_fields.get('is_staff') is not True:
    #         raise ValueError('Superuser must have is_staff=True.')
    #     if extra_fields.get('is_superuser') is not True:
    #         raise ValueError('Superuser must have is_superuser=True.')

    #     return self.create_user(email, username, first_name, last_name, password, **extra_fields)


class User(AbstractUser):
    """Класс, описывающий кастомную модель пользователя"""
   
    username = models.CharField(
        'Имя пользователя',
        max_length=LENG_USER,
        unique=True
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
        return self.email
    
    
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
