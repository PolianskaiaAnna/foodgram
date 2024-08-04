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
        fields = ('name', 'slug', 'recipes')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ('name', 'measurement_unit', 'recipes')



class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения рецептов"""
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientSerializer(many=True, read_only=True)

    class Meta:
        model = Recipe
        exclude = ('id',)

    def to_representation(self, instance):
        return RecipeReadSerializer(instance).data


class RecipeCreateSerizalizer(serializers.ModelSerializer):
    """Сериализатор для создания рецептов"""
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    # tags = serializers.SlugRelatedField(
    #     slug_field='slug', many=True,
    #     queryset=Tag.objects.all()
    # )
    # ingredients = serializers.StringRelatedField(many=True)
    ingredients = serializers.ListSerializer(child=serializers.DictField(), write_only=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True, write_only=True)
    image = Base64ImageField()


    class Meta:
        model = Recipe
        exclude = ('id',)

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        
        recipe = Recipe.objects.create(**validated_data)
        
        # Проверить добавление тегов!
        existing_tags = Tag.objects.filter(id__in=tags_data)
        recipe.tags.add(*existing_tags)
        
        for ingredient_data in ingredients_data:
            ingredient, status = Ingredient.objects.get_or_create(
                name=ingredient_data['name'],
                measurement_unit=ingredient_data['measurement_unit']
            )
            IngredientRecipe.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=ingredient_data.get('amount', 1)
            )

        return recipe



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
