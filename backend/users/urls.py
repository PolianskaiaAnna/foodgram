from django.urls import include, path
from rest_framework.routers import DefaultRouter
from users.views import AvatarView, FollowViewSet, UserViewSet, FollowCreate

router_vers1 = DefaultRouter()
router_vers1.register('users', UserViewSet, basename='users')
# router_vers1.register(
#     r'recipes/(?P<recipe_id>\d+)/favorite',
#     FavoriteViewSet, basename='favorites'
# )

urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router_vers1.urls)),
    path('users/me/avatar/', AvatarView.as_view(), name='avatar'),
    path(
        'users/subscriptions/', FollowViewSet.as_view(
            {'get': 'list'}
        ), name='following'
    ),
    path('users/<int:id>/subscribe/', FollowCreate.as_view(
        {'post': 'create'}
    ), name='follow'
    ),
]
