import shortuuid
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet

from recipes.filters import IngredientFilter, RecipeFilter, RecipeFilterBackend
from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingCart, Tag)
from recipes.permissions import IsAuthorOrAdmin
from recipes.serializers import (FavoriteSerializer, IngredientSerializer,
                                 RecipeCreateSerizalizer, RecipeReadSerializer,
                                 ShoppingCartSerializer, TagSerializer)


class RecipeViewSet(viewsets.ModelViewSet):
    """Класс, описывающий запросы к модели Recipe """
    serializer_class = RecipeReadSerializer
    filter_backends = (DjangoFilterBackend, RecipeFilterBackend)
    filterset_class = RecipeFilter

    def get_queryset(self):
        queryset = Recipe.objects.all()
        return queryset.distinct()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated, IsAuthorOrAdmin]
        else:
            self.permission_classes = [IsAuthenticatedOrReadOnly]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipeCreateSerizalizer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            read_serializer = RecipeReadSerializer(
                instance=serializer.instance,
                context={'request': request}
            )
            return Response(
                read_serializer.data, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        if not instance:
            return Response(
                {"detail": "Рецепт не найден"},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial
        )
        if serializer.is_valid():
            self.perform_update(serializer)
            read_serializer = RecipeReadSerializer(
                instance=serializer.instance,
                context={'request': request}
            )
            return Response(read_serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_short_link(self, request, pk=None):
        recipe = self.get_object()
        if not recipe.short_link:
            recipe.short_link = shortuuid.uuid()
            recipe.save()

        # TODO: Заменить на адрес сайта!
        short_link_url = f"127.0.0.1:8000/s/{recipe.short_link}"
        return Response(
            {'short-link': short_link_url}, status=status.HTTP_200_OK
        )


class TagViewSet(viewsets.ModelViewSet):
    """Класс, описывающий запросы к модели Tag """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    http_method_names = ["get", ]


class IngredientViewSet(viewsets.ModelViewSet):
    """Класс, описывающий запросы к модели Ingredient """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    filterset_class = IngredientFilter
    search_fields = ('^name',)
    pagination_class = None
    http_method_names = ["get", ]


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
        if not Favorite.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                {"detail": "Этого рецепта нет в избранном"},
                status=status.HTTP_400_BAD_REQUEST
            )
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

        shopping_cart = ShoppingCart.objects.create(user=user, recipe=recipe)

        serialized_shopping_cart = ShoppingCartSerializer(
            shopping_cart, context={'request': request}
        )
        return Response(
            serialized_shopping_cart.data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['delete'])
    def delete(self, request, *args, **kwargs):
        """Удаление из списка покупок"""
        user = request.user
        recipe_id = kwargs.get('id')
        recipe = get_object_or_404(Recipe, id=recipe_id)
        if not ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                {"detail": "Этого рецепта нет в списке покупок"},
                status=status.HTTP_400_BAD_REQUEST
            )
        shopping_cart = get_object_or_404(
            ShoppingCart, user=user, recipe=recipe
        )
        shopping_cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def download_shopping_cart(self, request):
        """Получение файла со списком покупок"""
        user = request.user
        return download_shopping_cart(user)


class DecodeView(View):
    """Функция открывает рецепт по переданной короткой ссылке"""
    def get(self, request, short_link, *args, **kwargs):
        recipe = get_object_or_404(Recipe, short_link=short_link)
        return redirect('recipe-detail', pk=recipe.pk)


def download_shopping_cart(user):
    """Создание файла со списком покупок"""
    shopping_lists = ShoppingCart.objects.filter(user=user)
    ingredients = {}

    for shopping_list in shopping_lists:
        recipe = shopping_list.recipe
        for ingredient_recipe in IngredientRecipe.objects.filter(
            recipe=recipe
        ):
            ingredient_name = ingredient_recipe.ingredient.name
            ingredient_unit = ingredient_recipe.ingredient.measurement_unit
            ingredient_amount = ingredient_recipe.amount
            if ingredient_name in ingredients:
                ingredients[ingredient_name]['amount'] += ingredient_amount
            else:
                ingredients[ingredient_name] = {
                    'amount': ingredient_amount,
                    'measurement_unit': ingredient_unit
                }

    file_content = generate_txt(ingredients)
    response = HttpResponse(file_content, content_type='text/plain')
    response['Content-Disposition'] = (
        'attachment; filename="shopping_cart.txt"'
    )
    return response


def generate_txt(ingredients):
    lines = []
    for ingredient, details in ingredients.items():
        lines.append(
            f"{ingredient}: {details['amount']} "
            f"{details['measurement_unit']}"
        )
    return "\n".join(lines)
