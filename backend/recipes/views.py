import io
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.http import FileResponse
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly, IsAuthenticated
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet

from recipes.models import (
    Recipe, Tag, Ingredient, Favorite, ShoppingCart, IngredientRecipe
)
from recipes.permissions import IsAuthorOrAdmin, IsAdminOrReadOnly
from recipes.serializers import (
    TagSerializer,
    IngredientSerializer,
    ShoppingCartSerializer,
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
            return Response(
                {"detail": "Вы уже добавили этот рецепт в избранное"},
                status=status.HTTP_400_BAD_REQUEST
            )

        favorite = Favorite.objects.create(user=user, recipe=recipe)

        serialized_favorited = FavoriteSerializer(
            favorite, context={'request': request}
        )
        return Response(
            serialized_favorited.data,
            status=status.HTTP_201_CREATED
        )

    def delete(self, request, *args, **kwargs):
        user = request.user
        recipe_id = kwargs.get('id')
        recipe = get_object_or_404(Recipe, id=recipe_id)
        favorite = get_object_or_404(Favorite, user=user, recipe=recipe)
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartViewSet(ViewSet):
    """Класс, описывающий запросы к модели списка покупок """
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def post(self, request, id):
        """Добавление в список покупок"""
        user = request.user
        recipe = get_object_or_404(Recipe, id=id)

        if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                {"detail": "Вы уже добавили этот рецепт в список покупок"},
                status=status.HTTP_400_BAD_REQUEST
            )

        favorite = ShoppingCart.objects.create(user=user, recipe=recipe)

        serialized_favorited = ShoppingCartSerializer(
            favorite, context={'request': request}
        )
        return Response(
            serialized_favorited.data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['delete'])
    def delete(self, request, *args, **kwargs):
        """Удаление из списка покупок"""
        user = request.user
        recipe_id = kwargs.get('id')
        recipe = get_object_or_404(Recipe, id=recipe_id)
        favorite = get_object_or_404(ShoppingCart, user=user, recipe=recipe)
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def download_shopping_cart(self, request):
        user = request.user
        shopping_lists = ShoppingCart.objects.filter(user=user)
        ingredients = {}

        for shopping_list in shopping_lists:
            recipe = shopping_list.recipe
            for ingredient_recipe in IngredientRecipe.objects.filter(
                recipe=recipe
            ):
                ingredient_name = ingredient_recipe.ingredient.name
                ingredient_amount = ingredient_recipe.amount
                if ingredient_name in ingredients:
                    ingredients[ingredient_name] += ingredient_amount
                else:
                    ingredients[ingredient_name] = ingredient_amount

        file_content = self.generate_txt(ingredients)
        content_type = 'text/plain'
        extension = 'txt'

        response = FileResponse(
            io.BytesIO(file_content),
            content_type=content_type
        )
        response[
            'Content-Disposition'
        ] = f'attachment; filename="shopping_cart.{extension}"'
        return response

    def generate_txt(self, ingredients):
        content = ""
        for name, amount in ingredients.items():
            content += f"{name} — {amount}\n"
        return content.encode('utf-8')
