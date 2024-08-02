from django.shortcuts import render, get_object_or_404

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly, AllowAny
from djoser.views import UserViewSet
from recipes.models import Recipe, Tag, Ingredient, Follow, Favorite, ShoppingList
from users.models import User
from recipes.permissions import IsOwnerOrReadOnly, IsAuthorOrAdmin
from recipes.serializers import (
    TagSerializer, RecipeSerializer, 
    IngredientSerializer, FollowSerializer,
    ShoppingListSerializer,
    FavoriteSerializer, RecipeReadSerializer,
    RecipeCreateSerizalizer
)




class RecipeViewSet(viewsets.ModelViewSet):
    """Класс, описывающий запросы к модели Recipe """
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrAdmin]

    # def get_queryset(self):
    #     queryset = Recipe.objects.annotate(rating=Avg('reviews__score'))
    #     return queryset

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipeCreateSerizalizer


class TagViewSet(viewsets.ModelViewSet):
    """Класс, описывающий запросы к модели Tag """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminUser]


class IngredientViewSet(viewsets.ModelViewSet):
    """Класс, описывающий запросы к модели Ingredient """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [IsAdminUser]
    


class FavoriteViewSet(viewsets.ModelViewSet):
    """Класс, описывающий запросы к модели избранного """
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer


class ShoppingListViewSet(viewsets.ModelViewSet):
    """Класс, описывающий запросы к модели списка покупок """
    queryset = ShoppingList.objects.all()
    serializer_class = ShoppingListSerializer


