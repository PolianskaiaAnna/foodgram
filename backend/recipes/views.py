from django.shortcuts import render, get_object_or_404

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly, AllowAny
from djoser.views import UserViewSet
from recipes.models import Recipe, Tag, Ingredient, Follow, User, Favorite, ShoppingList
from recipes.permissions import IsOwnerOrReadOnly, IsAuthorOrAdmin
from recipes.serializers import (
    TagSerializer, RecipeSerializer, 
    IngredientSerializer, FollowSerializer,
    CustomUserSerializer, ShoppingListSerializer,
    FavoriteSerializer, RecipeReadSerializer,
    RecipeCreateSerizalizer
)


class CreateViewSet(viewsets.GenericViewSet,
                    mixins.CreateModelMixin,
                    mixins.ListModelMixin):
    """Базовый класс, который может создавать объекты и отображать их список"""
    pass


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
    

class FollowViewSet(CreateViewSet):
    """Класс, описывающий запросы к модели Follow"""
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = (IsAuthorOrAdmin)
    # permission_classes = (permissions.IsAuthenticated,)
    # filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    # filterset_fields = ('user', 'following')
    # search_fields = ('user__username', 'following__username')

    def get_queryset(self):
        return Follow.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        following_username = self.request.data.get('following')
        following = get_object_or_404(User, username=following_username)
        serializer.save(user=self.request.user, following=following)


class CustomUserViewSet(UserViewSet):
    """Класс, описывающий расширенную модель пользователя"""
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer


class FavoriteViewSet(viewsets.ModelViewSet):
    """Класс, описывающий запросы к модели избранного """
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer


class ShoppingListViewSet(viewsets.ModelViewSet):
    """Класс, описывающий запросы к модели списка покупок """
    queryset = ShoppingList.objects.all()
    serializer_class = ShoppingListSerializer
