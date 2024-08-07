import re
from rest_framework import serializers

from users.validators import username_validator, username_not_me
from users.models import User, Follow
from recipes.serializers import Base64ImageField, RecipeReadSerializer


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username',
            'first_name', 'last_name', 'avatar', 'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Follow.objects.filter(
                user=request.user, following=obj
            ).exists()
        return False


class UserCreateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        validators=[username_validator, username_not_me]
    )
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name',
            'last_name', 'password'
        )

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=password
        )
        return user

    def to_representation(self, instance):
        """Функция убирает поле пароля из ответа"""
        representation = super().to_representation(instance)
        representation.pop('password', None)
        return representation
    
    def validate(self, data):
        """
        Функция проверяет, что связка юзернейм-email уникальна"""
        email = data.get('email')
        username = data.get('username')        
        if username.lower() == 'me':
            raise serializers.ValidationError('Нельзя использовать имя me')

        user_with_email = User.objects.filter(email=email).first()
        # Проверка на то, что нельзя использовать email,
        # уже зарегистрированного пользователя
        if user_with_email:
            if user_with_email.username != username:
                raise serializers.ValidationError(
                    'Пользователь с таким email уже зарегистрирован'
                )

        user_with_username = User.objects.filter(username=username).first()
        # Проверка на то, что нельзя использовать занятый юзернейм
        if user_with_username:
            if user_with_username.email != email:
                raise serializers.ValidationError(
                    'Пользователь с таким именем уже зарегистрирован'
                )
        return data


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(
        label='Изображение',
        required=False, allow_null=True
    )

    class Meta:
        model = User
        fields = ['avatar']


class FollowCreateSerializer(serializers.ModelSerializer):
    """Класс, описывающий сериализатор для подписки на других пользователей"""
    user = serializers.SlugRelatedField(
        read_only=True, slug_field='username',
        default=serializers.CurrentUserDefault()
    )
    following = serializers.SlugRelatedField(
        queryset=User.objects.all(), slug_field='username'
    )
    # recipes = serializers.ListSerializer(
    #     child=serializers.DictField(),
    #     write_only=True
    # )

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

class SubscriptionSerializer(serializers.ModelSerializer):
    """
    Класс отображает информацию о пользователях, на которых юзер подписан,
    при этом показывая все рецепты пользователей и подсчитывая 
    количество рецептов
    """
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'username', 'first_name',
            'last_name', 'email', 'is_subscribed',
            'recipes_count', 'recipes', 'avatar'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Follow.objects.filter(
                user=request.user, following=obj
            ).exists()
        return False

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        recipes = obj.recipes.all()
        return RecipeReadSerializer(recipes, many=True).data