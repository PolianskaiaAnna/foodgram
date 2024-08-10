import io
import shortuuid
import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404, redirect
from django.http import FileResponse
from django.views import View
from rest_framework import filters, status, viewsets
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly, IsAuthenticated
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet

from recipes.filters import RecipeFilterBackend, IngredientFilter, RecipeFilter
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
    # permission_classes = [IsAuthorOrAdmin]
    filter_backends = (DjangoFilterBackend, RecipeFilterBackend)
    filterset_class = RecipeFilter
    # filterset_fields = ('author', 'tags')

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
            return Response(read_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data, partial=partial)
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

        # Заменить на адрес сайта!
        short_link_url = f"127.0.0.1:8000/s/{recipe.short_link}"
        return Response({'short-link': short_link_url}, status=status.HTTP_200_OK)


class TagViewSet(viewsets.ModelViewSet):
    """Класс, описывающий запросы к модели Tag """    
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    http_method_names = ["get",]
    # filter_backends = (DjangoFilterBackend)
    # filterset_fields = ('name')


class IngredientViewSet(viewsets.ModelViewSet):
    """Класс, описывающий запросы к модели Ingredient """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    filterset_class = IngredientFilter
    search_fields = ('^name',)
    pagination_class = None
    http_method_names = ["get",]


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
        shopping_cart = get_object_or_404(ShoppingCart, user=user, recipe=recipe)
        shopping_cart.delete()
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
    

class DecodeView(View):
    """Функция открывает рецепт по переданной короткой ссылке"""
    def get(self, request, short_link, *args, **kwargs):
        recipe = get_object_or_404(Recipe, short_link=short_link)
        return redirect('recipe-detail', pk=recipe.pk)
