from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework import permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import (CreateModelMixin, ListModelMixin,
                                   DestroyModelMixin)
from rest_framework.response import Response

from .models import Subscription
from .serializers import (CustomUserCreateSerializer, CustomUserSerializer,
                          SubscriptionSerializer)

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    serializer_classes = {
        'create': CustomUserCreateSerializer,
        'retrieve': CustomUserSerializer,
        'list': CustomUserSerializer,
        'me': CustomUserSerializer,
    }

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    def get_queryset(self):
        if self.action == 'list':
            return self.queryset
        return super().get_queryset()

    def get_serializer_class(self):
        if self.action in self.serializer_classes:
            return self.serializer_classes[self.action]
        return super().get_serializer_class()


class SubscriptionViewSet(ListModelMixin, CreateModelMixin, DestroyModelMixin,
                          viewsets.GenericViewSet):
    """Обработчик для оформления и удаления подписок пользователями."""

    serializer_class = SubscriptionSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return User.objects.filter(subscribed__user=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        author_id = self.kwargs.get('author_id')
        recipes_limit = self.request.query_params.get('recipes_limit')
        if recipes_limit is not None and int(recipes_limit) >= 0:
            context['recipes_limit'] = int(recipes_limit)
        if author_id:
            context['author'] = get_object_or_404(User, id=author_id)
        context['user'] = self.request.user
        return context

    def perform_create(self, serializer):
        user = self.get_serializer_context().get('user')
        author = self.get_serializer_context().get('author')
        serializer.save(user=user, author=author)

    def destroy(self, request, author_id):
        # Если автора нет в БД, то вызываем ошибку 404
        author = get_object_or_404(User, id=author_id)
        try:
            instance = Subscription.objects.get(user=self.request.user,
                                                author=author)
        except Exception:
            # Если нет подписки и пр.,то вызываем ошибку 400
            raise ValidationError()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
