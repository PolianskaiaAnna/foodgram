from django.urls import include, path
from rest_framework.routers import DefaultRouter
from users.views import ChangePasswordView, AvatarView, FollowViewSet, UserViewSet

router_vers1 = DefaultRouter()
router_vers1.register('users', UserViewSet, basename='users')
# router_vers1.register(
#     r'recipes/(?P<recipe_id>\d+)/favorite',
#     FavoriteViewSet, basename='favorites'
# )

urlpatterns = [
    #path('v1/users/me/', UserProfileAPIView.as_view(), name='profile'),
    path('', include(router_vers1.urls)),    
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('users/me/avatar/', AvatarView.as_view(), name='avatar'),
    path('users/me/set_password/', ChangePasswordView.as_view(), name='change-password'),
    # path('api/users/subscriptions/', SubscriptionViewSet, name='subscriptions'),
    # path('api/users/<int:id>/subscribe/', FollowViewSet, name='follow'),
]