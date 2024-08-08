from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from djoser.serializers import SetPasswordSerializer

from recipes.permissions import IsAuthorOrAdmin
from users.serializers import (
    AvatarSerializer,
    UserSerializer, UserCreateSerializer,
    SubscriptionSerializer
)
from users.models import User, Follow


class CreateViewSet(viewsets.GenericViewSet,
                    mixins.CreateModelMixin):
    """Базовый класс, который может создавать объекты и отображать их список"""
    pass


class AvatarView(APIView):
    """Класс для создания и удаления аватара"""
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        user = request.user
        serializer = AvatarSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        user = request.user
        user.avatar.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# class FollowCreate(CreateViewSet):
#     """Класс, описывающий запросы к модели Follow"""
#     queryset = Follow.objects.all()
#     serializer_class = FollowCreateSerializer
#     permission_classes = [IsAuthenticated]
#     # filter_backends = (DjangoFilterBackend, filters.SearchFilter)
#     # filterset_fields = ('user', 'following')
#     # search_fields = ('user__username', 'following__username')

#     # def get_queryset(self):
#     #     return Follow.objects.filter(user=self.request.user)

#     def perform_create(self, serializer):
#         following_username = self.request.data.get('following')
#         following = get_object_or_404(User, username=following_username)
#         serializer.save(user=self.request.user, following=following)

class CustomLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 6


class FollowUserView(APIView):
    """Создает подписку на пользователя"""
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        user = request.user
        following = get_object_or_404(User, id=id)

        if user == following:
            return Response({"detail": "Нельзя подписаться на себя."}, status=status.HTTP_400_BAD_REQUEST)
        
        if Follow.objects.filter(user=user, following=following).exists():
            return Response({"detail": "Вы уже подписаны на этого пользователя."}, status=status.HTTP_400_BAD_REQUEST)
        
        Follow.objects.create(user=user, following=following)
        serialized_following = SubscriptionSerializer(following, context={'request': request})
        return Response(serialized_following.data, status=status.HTTP_201_CREATED)
    

class FollowViewSet(viewsets.ViewSet):
    """Возвращает список пользователей из подписок"""
    permission_classes = [IsAuthenticated]
    pagination_class = LimitOffsetPagination
    # pagination_class = CustomLimitOffsetPagination

    # def get_queryset(self):
    #     queryset = Recipe.objects.annotate(count_recipe=Avg('recipes__score'))
    #     return queryset

    def list(self, request):
        user = request.user
        follows = Follow.objects.filter(user=user)
        followed_users = [follow.following for follow in follows]
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(followed_users, request)

        if page is not None:
            serializer = SubscriptionSerializer(page, many=True, context={'request': request})
            return paginator.get_paginated_response(serializer.data)
        serializer = SubscriptionSerializer(followed_users, many=True, context={'request': request})
        return Response(serializer.data)


class UserViewSet(viewsets.ModelViewSet):
    """Обрабатывает запросы к профилю пользователя"""
    queryset = User.objects.all()
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
    
