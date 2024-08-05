from rest_framework import generics, permissions, status
from django.shortcuts import render, get_object_or_404
from django.db.models import Count
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly, AllowAny
from recipes.permissions import IsAuthorOrAdmin
from users.serializers import AvatarSerializer, ChangePasswordSerializer, FollowSerializer, UserSerializer, UserCreateSerializer
from users.models import User, Follow
from recipes.models import Recipe


class CreateViewSet(viewsets.GenericViewSet,
                    mixins.CreateModelMixin):
    """Базовый класс, который может создавать объекты и отображать их список"""
    pass


class AvatarView(APIView):
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


class ChangePasswordView(generics.UpdateAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def get_object(self):
        return self.request.user
    

class FollowViewSet(CreateViewSet):
    """Класс, описывающий запросы к модели Follow"""
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = (IsAuthorOrAdmin)
    permission_classes = (permissions.IsAuthenticated,)
    # filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    # filterset_fields = ('user', 'following')
    # search_fields = ('user__username', 'following__username')

    def get_queryset(self):
        return Follow.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        following_username = self.request.data.get('following')
        following = get_object_or_404(User, username=following_username)
        serializer.save(user=self.request.user, following=following)


# class SubscriptionViewSet(viewsets.ViewSet):
#     """Возвращает список пользователей из подписок"""
#     permission_classes = [IsAuthenticated]

#     # def get_queryset(self):
#     #     queryset = Recipe.objects.annotate(count_recipe=Avg('recipes__score'))
#     #     return queryset

#     def list(self, request):
#         user = request.user
#         follows = Follow.objects.filter(user=user)
#         serializer = FollowSerializer(follows, many=True)
#         return Response(serializer.data)
    
   
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return UserSerializer
        return UserCreateSerializer
    
    def get_queryset(self):
        queryset = User.objects.annotate(Count('recipe'))
        return queryset

