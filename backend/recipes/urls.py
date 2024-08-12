from django.urls import include, path
from rest_framework import routers

from recipes.views import (
    RecipeViewSet, TagViewSet,
    IngredientViewSet, FavoriteViewSet, ShoppingCartViewSet,
)

router_vers1 = routers.DefaultRouter()


router_vers1.register(
    'recipes', RecipeViewSet, basename='recipes'
)
router_vers1.register(
    'tags', TagViewSet, basename='tags'
)
router_vers1.register(
    'ingredients', IngredientViewSet, basename='ingredients'
)

urlpatterns = [
    path('recipes/download_shopping_cart/', ShoppingCartViewSet.as_view(
        {'get': 'download_shopping_cart'}
    ), name='download_shoppping_cart'),
    path(
        'recipes/<int:id>/favorite/', FavoriteViewSet.as_view(),
        name='favorite'
    ),
    path('recipes/<int:id>/shopping_cart/', ShoppingCartViewSet.as_view(
        {'post': 'post', 'delete': 'delete'}
    ), name='in_shoping_cart'),
    path('', include(router_vers1.urls)),
]
