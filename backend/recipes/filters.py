import django_filters
from rest_framework import filters

from recipes.models import Ingredient, Recipe, Tag


class RecipeFilterBackend(filters.BaseFilterBackend):
    """Фильтрация по избранному и корзине"""
    def filter_queryset(self, request, queryset, view):
        user = request.user
        is_favorited = request.query_params.get('is_favorited')
        is_in_shopping_cart = request.query_params.get('is_in_shopping_cart')

        if user.is_authenticated:
            if is_favorited is not None:
                # queryset = queryset.filter(favorited_by=user)
                if is_favorited.lower() in ['true', '1']:
                    queryset = queryset.filter(favorited_by__user=user)
                elif is_favorited.lower() in ['false', '0']:
                    queryset = queryset.exclude(favorited_by__user=user)

            if is_in_shopping_cart is not None:
                # queryset = queryset.filter(in_shopping_cart=user)
                if is_in_shopping_cart.lower() in ['true', '1']:
                    queryset = queryset.filter(in_shopping_cart__user=user)
                elif is_in_shopping_cart.lower() in ['false', '0']:
                    queryset = queryset.exclude(in_shopping_cart__user=user)
        return queryset


class IngredientFilter(django_filters.FilterSet):
    """Фильтрация по первым буквам названия ингредиента"""
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='istartswith'
    )

    class Meta:
        model = Ingredient
        fields = ['name']


class RecipeFilter(django_filters.FilterSet):
    """Фильтрация по нескольким тегам"""
    tags = django_filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
        lookup_expr='in'
    )

    class Meta:
        model = Recipe
        fields = ['tags']
