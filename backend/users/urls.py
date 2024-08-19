from django.urls import include, path
from rest_framework.routers import DefaultRouter
from users.views import (AvatarView, SubscribeUserView, SubscribeViewSet,
                         UserViewSet)

router_vers1 = DefaultRouter()
router_vers1.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('users/me/avatar/', AvatarView.as_view(), name='avatar'),
    path(
        'users/subscriptions/', SubscribeViewSet.as_view(
            {'get': 'list'}
        ), name='following'
    ),
    path(
        'users/<int:id>/subscribe/',
        SubscribeUserView.as_view(), name='follow'
    ),
    path('', include(router_vers1.urls)),
]
