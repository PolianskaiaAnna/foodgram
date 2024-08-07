from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

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


class FavoriteViewSet(viewsets.ModelViewSet):
    """Класс, описывающий запросы к модели избранного """
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer


class ShoppingListViewSet(viewsets.ModelViewSet):
    """Класс, описывающий запросы к модели списка покупок """
    queryset = ShoppingList.objects.all()
    serializer_class = ShoppingListSerializer
