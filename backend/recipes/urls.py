from django.urls import include, path
from rest_framework import routers

from recipes.views import (
    RecipeViewSet, TagViewSet,
    IngredientViewSet, FavoriteViewSet, ShoppingListViewSet
)

router_vers1 = routers.DefaultRouter()

# router_vers1.register(
#     r'recipes/(?P<recipe_id>\d+)/favorite',
#     FavoriteViewSet, basename='favorites'
# )

# router_vers1.register(
#     r'recipes/(?P<recipe_id>\d+)/shopping_cart',
#     ShoppingListViewSet, basename='shopping_list'
# )

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
    path('', include(router_vers1.urls)),
]
