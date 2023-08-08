from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Case, When, Value, BooleanField
from djoser.views import UserViewSet
from rest_framework import permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin, ListModelMixin, \
    DestroyModelMixin
from rest_framework.response import Response

from .models import Subscription
from .serializers import CustomUserCreateSerializer, CustomUserSerializer, \
    SubscriptionListSerializer, SubscriptionCreateSerializer

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
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        subscribed_users = User.objects.filter(
            subscribed__user=self.request.user).annotate(
                    is_subscribed=Case(
                    When(subscribed__user=self.request.user, then=True),
                    default=False,
                    output_field=BooleanField()
                    )
                    )
        return subscribed_users

    def create(self, request, author_id):
        data = {'user': request.user.id, 'author': author_id}
        serializer = SubscriptionCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        instance = User.objects.filter(id=author_id).annotate(
            is_subscribed=Value(True, output_field=BooleanField())).first()
        response_serializer = SubscriptionListSerializer(instance)
        return Response(response_serializer.data,
                        status=status.HTTP_201_CREATED)

    def destroy(self, request, author_id):
        try:
            instance = Subscription.objects.get(user=self.request.user,
                                                author=author_id)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
