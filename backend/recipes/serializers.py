import base64
import datetime as dt

from django.core.files.base import ContentFile
from rest_framework import serializers
from djoser.serializers import UserSerializer

from recipes.models import Ingredient, Tag, Recipe, Follow, User


class Base64ImageField(serializers.ImageField):
    """Сериализатор для обработки изображений, закодированных в Base64"""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class CustomUserSerializer(UserSerializer):
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'password', 'avatar')

    def create(self, validated_data):
        """
        Функция создает нового пользователя или
        получает уже зарегистрированного из базы
        """
        email = validated_data['email']
        password = validated_data['password']
        user, created = User.objects.get_or_create(
            password=password, defaults={'email': email}
        )
        self.send_activation_email(user)

        return user


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов."""

    class Meta:
        model = Tag
        fields = ('name', 'slug')

    # def create()

    # def update()


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ('name', 'measurement_unit')

    # def create()

    # def update()


        
class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов"""

    class Meta:
        model = Recipe
        exclude = ('id',)


class FollowSerializer(serializers.ModelSerializer):
    """Класс, описывающий сериализатор для модели Follow"""
    user = serializers.SlugRelatedField(
        read_only=True, slug_field='username',
        default=serializers.CurrentUserDefault()
    )
    following = serializers.SlugRelatedField(
        queryset=User.objects.all(), slug_field='username'
    )

    class Meta:
        model = Follow
        fields = '__all__'

    def validate(self, data):
        current_user = self.context['request'].user
        following = data['following']
        if current_user == following:
            raise serializers.ValidationError("Нельзя подписаться на себя.")
        if Follow.objects.filter(
            user=current_user,
            following=following
        ).exists():
            raise serializers.ValidationError(
                "Вы уже подписаны на этого пользователя."
            )
        return data