import base64
import datetime as dt

from django.core.files.base import ContentFile
from rest_framework import serializers

from recipes.models import (
    Ingredient, Tag, Recipe,
    Favorite, ShoppingList, TagRecipe,
    IngredientRecipe
)
from users.models import User, Follow

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
    id = serializers.PrimaryKeyRelatedField(source='ingredient', queryset=Ingredient.objects.all())
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')


    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')

class AuthorSerializer(serializers.ModelSerializer):
    """Сериализатор для автора рецепта"""
    # recipes = RecipeReadSerializer(many=True, read_only=True)
    # recipes_count = serializers.SerializerMethodField()    
    is_subscribed = serializers.SerializerMethodField()
    # is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.ImageField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'avatar', 'is_subscribed')

    # def get_recipes_count(self, obj):
    #     """Получение общего количества рецептов пользователя"""
    #     return obj.recipes.count()
    
    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Follow.objects.filter(user=request.user, following=obj).exists()
        return False



    # class Meta:
    #     model = User
    #     fields = ('id', 'username', 'first_name', 'last_name', 'email', 'is_subscribed', 'avatar')

    # def get_is_subscribed(self, obj):
    #     current_user = self.context['request'].user
    #     return current_user.is_authenticated and Follow.objects.filter(user=current_user, following=obj).exists()

class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения рецептов"""   
    ingredients = IngredientRecipeSerializer(source='ingredientrecipe_set', many=True)
    tags = TagSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField('get_is_favorited')
    is_in_shopping_cart = serializers.SerializerMethodField('get_is_in_shopping_cart')
    author = AuthorSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time'
        )

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        return user.is_authenticated and Favorite.objects.filter(user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return user.is_authenticated and ShoppingList.objects.filter(user=user, recipe=obj).exists()


class RecipeCreateSerizalizer(serializers.ModelSerializer):
    """Сериализатор для создания рецептов"""
    is_favorited = serializers.SerializerMethodField('get_is_favorited')
    is_in_shopping_cart = serializers.SerializerMethodField('get_is_in_shopping_cart')
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    ingredients = IngredientRecipeSerializer(many=True, write_only=True, label='Ингредиенты')
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True, write_only=True, label='Теги')
    image = Base64ImageField(label='Изображение', required=False, allow_null=True)


    class Meta:
        model = Recipe
        fields = ('id', 'name', 'ingredients', 'tags', 'image', 'text', 'cooking_time', 'is_favorited', 'is_in_shopping_cart', 'author')

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')

        recipe = Recipe.objects.create(**validated_data)

        for tag in tags_data:
            TagRecipe.objects.create(recipe=recipe, tag=tag)

        for ingredient_data in ingredients_data:
            ingredient_id = ingredient_data.get('ingredient').id
            ingredient = Ingredient.objects.get(id=ingredient_id)
            # amount = ingredient_data.get('amount', 1)

            IngredientRecipe.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=ingredient_data.get('amount', 1)
            )

        return recipe

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        return user.is_authenticated and Favorite.objects.filter(user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return user.is_authenticated and ShoppingList.objects.filter(user=user, recipe=obj).exists()

    # # Проверить добавление тегов!
        # existing_tags = Tag.objects.filter(id__in=tags_data)
        # recipe.tags.add(*existing_tags)
#для картинок
# image_url = serializers.SerializerMethodField(
    #     'get_image_url',
    #     read_only=True,
    # )


    # def get_image_url(self, obj):
    #     if obj.image:
    #         return obj.image.url
    #     return None
class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для избранного"""

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

class ShoppingListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка покупок"""

    class Meta:
        model = ShoppingList
        fields = ('user', 'recipe')

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


# class RecipeCreateSerializer(serializers.ModelSerializer):
#     """Сериализатор для создания рецептов"""

#     ingredients = serializers.ListSerializer(child=serializers.DictField(), write_only=True)
#     tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True, write_only=True)
#     image = Base64ImageField()

#     class Meta:
#         model = Recipe
# #         fields = ('id', 'name', 'test', 'cooking_time', 'ingredients', 'tags', 'image')

#     def create(self, validated_data):
#         ingredients_data = validated_data.pop('ingredients', [])
#         tags_data = validated_data.pop('tags', [])

#         recipe = Recipe.objects.create(**validated_data)

#         existing_tags = Tag.objects.filter(id__in=tags_data)
#         recipe.tags.add(*existing_tags)

#         for ingredient_data in ingredients_data:
#             ingredient, _ = Ingredient.objects.get_or_create(
#                 name=ingredient_data['name'],
#                 measurement_unit=ingredient_data['measurement_unit']
#             )
#             IngredientRecipe.objects.create(
#                 recipe=recipe,
#                 ingredient=ingredient,
#                 amount_ingredient=ingredient_data.get('amount_ingredient', 1)
#             )

#         return recipe

#     def update(self, instance, validated_data):
#         ingredients_data = validated_data.pop('ingredients', [])
#         tags_data = validated_data.pop('tags', [])

#         instance.name = validated_data.get('name', instance.name)
#         instance.test = validated_data.get('test', instance.test)
#         instance.cooking_time = validated_data.get('cooking_time', instance.cooking_time)
#         instance.image = validated_data.get('image', instance.image)
#         instance.save()


        # existing_tags = Tag.objects.filter(id__in=tags_data)
        # instance.tags.set(existing_tags)  # Установка нового набора тего

#         # Удаление старых ингредиентов
#         IngredientRecipe.objects.filter(recipe=instance).delete()

#         for ingredient_data in ingredients_data:
#             ingredient, _ = Ingredient.objects.get_or_create(
#                 name=ingredient_data['name'],
#                 measurement_unit=ingredient_data['measurement_unit']
#             )
#             IngredientRecipe.objects.create(
#                 recipe=instance,
#                 ingredient=ingredient,
#                 amount_ingredient=ingredient_data.get('amount_ingredient', 1)
#             )

#         return instance
