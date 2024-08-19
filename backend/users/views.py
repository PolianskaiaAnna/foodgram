from django.db.models import Count
from django.shortcuts import get_object_or_404
from djoser.serializers import SetPasswordSerializer
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import Subscribe, User
from users.serializers import (AvatarSerializer, SubscribeSerializer,
                               SubscriptionSerializer, UserCreateSerializer,
                               UserSerializer)


class CreateViewSet(viewsets.GenericViewSet,
                    mixins.CreateModelMixin):
    """Базовый класс, который может создавать объекты и отображать их список"""
    pass


class AvatarView(APIView):
    """Класс для создания и удаления аватара"""
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        user = request.user
        if 'avatar' not in request.data:
            return Response(
                {'detail': 'Поле `avatar` отсутствует в запросе'},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = AvatarSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        user = request.user
        user.avatar.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscribeUserView(APIView):
    """Создает и удаляет подписку на пользователя"""
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        user = request.user
        following = get_object_or_404(User, id=id)

        data = {
            'user': user.id,
            'following': following.id
        }

        serializer = SubscribeSerializer(
            data=data,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            serialized_following = SubscriptionSerializer(
                following, context={'request': request}
            )
            return Response(
                serialized_following.data, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        user = request.user
        following = get_object_or_404(User, id=id)

        if not Subscribe.objects.filter(
            user=user, following=following
        ).exists():
            return Response(
                {"detail": "Этого пользователя нет в подписках"},
                status=status.HTTP_400_BAD_REQUEST
            )
        subscription = get_object_or_404(
            Subscribe, user=user, following=following
        )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscribeViewSet(viewsets.ViewSet):
    """Возвращает список пользователей из подписок"""
    permission_classes = [IsAuthenticated]
    pagination_class = LimitOffsetPagination

    def list(self, request):
        user = request.user
        follows = Subscribe.objects.filter(user=user)
        followed_users = [
            follow.following for follow in follows
        ]
        paginator = self.pagination_class()
        paginated_users = paginator.paginate_queryset(followed_users, request)

        serializer = SubscriptionSerializer(
            paginated_users, many=True, context={'request': request}
        )
        return paginator.get_paginated_response(serializer.data)


class UserViewSet(viewsets.ModelViewSet):
    """Обрабатывает запросы к профилю пользователя"""
    serializer_class = UserSerializer

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve', 'get_me'):
            return UserSerializer
        if 'subscriptions' in self.request.query_params:
            return SubscriptionSerializer
        return UserCreateSerializer

    def get_queryset(self):
        queryset = User.objects.annotate(Count('recipes'))
        return queryset

    @action(
        detail=False, methods=['post'],
        url_path='set_password',
        permission_classes=[permissions.IsAuthenticated],
    )
    def set_password(self, request):
        user = request.user
        serializer = SetPasswordSerializer(
            data=request.data, context={'request': request}
        )
        if serializer.is_valid():
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False, methods=['get'],
        permission_classes=[permissions.IsAuthenticated],
        url_path='me'
    )
    def get_me(self, request):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data)
