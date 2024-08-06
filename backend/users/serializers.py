from rest_framework import serializers

from users.models import User, Follow
# from recipes.serializers import RecipeReadSerializer


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


class AvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['avatar']


class FollowSerializer(serializers.ModelSerializer):
    """Класс, описывающий сериализатор для модели Follow"""
    user = serializers.SlugRelatedField(
        read_only=True, slug_field='username',
        default=serializers.CurrentUserDefault()
    )
    following = serializers.SlugRelatedField(
        queryset=User.objects.all(), slug_field='username'
    )
    recipe = serializers.ListSerializer(
        child=serializers.DictField(),
        write_only=True
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

#class SubscriptionSerializer(serializers.ModelSerializer):
