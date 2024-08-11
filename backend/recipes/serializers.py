import base64
import shortuuid
from django.core.files.base import ContentFile
from rest_framework import serializers

from recipes.models import (
    Ingredient, Tag, Recipe,
    Favorite, ShoppingCart, TagRecipe,
    IngredientRecipe
)
from recipes.mixins import RecipeStatusMixin
from recipes.validators import validation_cooking_time
from users.models import User, Subscribe


class Base64ImageField(serializers.ImageField):
    """Сериализатор для обработки изображений, закодированных в Base64"""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для связи между рецептом и ингредиентом."""

    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class AuthorSerializer(serializers.ModelSerializer):
    """Сериализатор для автора рецепта"""
    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.ImageField()

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name',
            'last_name', 'avatar', 'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        """Проверка подписки"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscribe.objects.filter(
                user=request.user, following=obj
            ).exists()
        return False


class RecipeReadSerializer(RecipeStatusMixin, serializers.ModelSerializer):
    """Сериализатор для чтения рецептов"""
    ingredients = IngredientRecipeSerializer(
        source='ingredientrecipe_set', many=True
    )
    tags = TagSerializer(many=True, read_only=True)
    author = AuthorSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image',
            'text', 'cooking_time'
        )


class RecipeCreateSerizalizer(RecipeStatusMixin, serializers.ModelSerializer):
    """Сериализатор для создания рецептов"""
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    ingredients = IngredientRecipeSerializer(
        many=True, write_only=True,
        label='Ингредиенты',
        required=True
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True,
        write_only=True, label='Теги',
        required=True
    )
    image = Base64ImageField(
        label='Изображение',
        required=True,
    )
    name = serializers.CharField(
        max_length=256,
        required=True
    )
    text = serializers.CharField(required=True)
    cooking_time = serializers.IntegerField(
        required=True,
        validators=(validation_cooking_time,)
    )

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'ingredients', 'tags',
            'image', 'text', 'cooking_time',
            'is_favorited', 'is_in_shopping_cart', 'author'
        )

    def validate(self, data):
        """
        Проверка на отсутствие повторяющихся тегов
        и ингредиентов, их нулевое количество
        """
        tags = data.get('tags', [])
        if not tags:
            raise serializers.ValidationError(
                "Теги обязательны для заполнения."
            )
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError(
                "Теги не могут использоваться повторно"
            )

        ingredients = data.get('ingredients', [])
        ingredient_list = [
            ingredient['ingredient'].id for ingredient in ingredients
        ]
        if not ingredients:
            raise serializers.ValidationError(
                "Ингредиенты обязательны для заполнения."
            )
        if len(ingredient_list) != len(set(ingredient_list)):
            raise serializers.ValidationError(
                "Ингредиенты не могут использоваться повторно"
            )

        for ingredient_data in ingredients:
            if ingredient_data.get('amount') <= 0:
                raise serializers.ValidationError(
                    "Количество ингредиента должно быть больше 0"
                )
        return data

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')

        if not ingredients_data or not tags_data:
            raise serializers.ValidationError(
                "Поля `ingredients` и `tags` обязательны для заполнения!"
            )

        recipe = Recipe.objects.create(**validated_data)
        # Создание короткой ссылки
        if not validated_data.get('short_link'):
            validated_data['short_link'] = shortuuid.uuid()

        for tag in tags_data:
            TagRecipe.objects.create(recipe=recipe, tag=tag)

        for ingredient_data in ingredients_data:
            ingredient_id = ingredient_data.get('ingredient').id
            ingredient = Ingredient.objects.get(id=ingredient_id)

            IngredientRecipe.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=ingredient_data.get('amount', 1)
            )

        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')

        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.image = validated_data.get('image', instance.image)
        instance.save()

        if not instance.short_link:
            instance.short_link = shortuuid.uuid()

        if tags_data:
            tag_ids = [tag.id for tag in tags_data]
            existing_tags = Tag.objects.filter(id__in=tag_ids)
            instance.tags.set(existing_tags)

        IngredientRecipe.objects.filter(recipe=instance).delete()

        for ingredient_data in ingredients_data:
            ingredient_id = ingredient_data.get('ingredient').id
            ingredient = Ingredient.objects.get(id=ingredient_id)
            IngredientRecipe.objects.create(
                recipe=instance,
                ingredient=ingredient,
                amount=ingredient_data.get('amount', 1)
            )

        return instance


class RecipeSubscribeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения рецепта из подписок,
    избранного, списка покупок
    """

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'image',
            'cooking_time'
        )


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для избранного"""
    id = serializers.IntegerField(source='recipe.id')
    name = serializers.CharField(source='recipe.name')
    image = serializers.CharField(source='recipe.image')
    cooking_time = serializers.IntegerField(source='recipe.cooking_time')

    class Meta:
        model = Favorite
        fields = ('id', 'name', 'image', 'cooking_time')


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для списка покупок"""

    id = serializers.IntegerField(source='recipe.id')
    name = serializers.CharField(source='recipe.name')
    image = serializers.CharField(source='recipe.image')
    cooking_time = serializers.IntegerField(source='recipe.cooking_time')

    class Meta:
        model = ShoppingCart
        fields = ('id', 'name', 'image', 'cooking_time')
