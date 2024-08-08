from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from rest_framework import filters, status, viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from recipes.models import Recipe, Tag, Ingredient, Favorite, ShoppingList
from recipes.permissions import IsAuthorOrAdmin, IsAdminOrReadOnly
from recipes.serializers import (
    TagSerializer,
    IngredientSerializer,
    ShoppingListSerializer,
    FavoriteSerializer, RecipeReadSerializer,
    RecipeCreateSerizalizer
)


class RecipeViewSet(viewsets.ModelViewSet):
    """Класс, описывающий запросы к модели Recipe """
    queryset = Recipe.objects.all()
    serializer_class = RecipeReadSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrAdmin]
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('author', 'tags')

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipeCreateSerizalizer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid()
        self.perform_create(serializer)
        read_serializer = RecipeReadSerializer(
            instance=serializer.instance,
            context={'request': request}
        )
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid()
        self.perform_update(serializer)
        read_serializer = RecipeReadSerializer(
            instance=serializer.instance,
            context={'request': request}
        )
        return Response(read_serializer.data, status=status.HTTP_200_OK)


class TagViewSet(viewsets.ModelViewSet):
    """Класс, описывающий запросы к модели Tag """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    """Класс, описывающий запросы к модели Ingredient """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)
    pagination_class = None


class FavoriteViewSet(APIView):
    """Класс, описывающий запросы к модели избранного """
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        user = request.user
        recipe = get_object_or_404(Recipe, id=id)
        
        if Favorite.objects.filter(user=user, recipe=recipe).exists():
            return Response({"detail": "Вы уже добавили этот рецепт в избранное"}, status=status.HTTP_400_BAD_REQUEST)
        
        favorite = Favorite.objects.create(user=user, recipe=recipe)
        
        serialized_favorited = FavoriteSerializer(favorite, context={'request': request})
        return Response(serialized_favorited.data, status=status.HTTP_201_CREATED)
    
    def delete(self, request, *args, **kwargs):
        user = request.user
        recipe_id = kwargs.get('id')
        recipe = get_object_or_404(Recipe, id=recipe_id)
        favorite = get_object_or_404(Favorite, user=user, recipe=recipe)
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class ShoppingListViewSet(APIView):
    """Класс, описывающий запросы к модели списка покупок """
    pass
    # def post(self, request, id):
    #     user = request.user
    #     following = get_object_or_404(User, id=id)

    #     if user == following:
    #         return Response({"detail": "Нельзя подписаться на себя."}, status=status.HTTP_400_BAD_REQUEST)
        
    #     if Follow.objects.filter(user=user, following=following).exists():
    #         return Response({"detail": "Вы уже подписаны на этого пользователя."}, status=status.HTTP_400_BAD_REQUEST)
        
    #     Follow.objects.create(user=user, following=following)
    #     serialized_following = SubscriptionSerializer(following, context={'request': request})
    #     return Response(serialized_following.data, status=status.HTTP_201_CREATED)
