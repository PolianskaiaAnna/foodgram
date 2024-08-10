from rest_framework import serializers
from recipes.models import Favorite, ShoppingCart


class RecipeStatusMixin(serializers.Serializer):
    """
    Миксин для проверки статуса, добавлен ли
    рецепт в избранное или список покупок
    """
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        return user.is_authenticated and Favorite.objects.filter(
            user=user, recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return user.is_authenticated and ShoppingCart.objects.filter(
            user=user, recipe=obj
        ).exists()
