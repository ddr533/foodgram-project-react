from django.contrib.auth import get_user_model
from django.db.models import Q
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from .models import Subscription

User = get_user_model()

class CustomUserCreateSerializer(UserCreateSerializer):

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password')


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if (user.is_anonymous or not
        Subscription.objects.filter(user=user, author=obj).exists()):
            return False
        return True


class SubscriptionListSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.BooleanField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed')


class SubscriptionCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscription
        fields = '__all__'

    def validate(self, attrs):
        user = attrs['user']
        author = attrs['author']

        if user == author:
            raise serializers.ValidationError(
                'Вы не можете подписываться на себя.')

        if Subscription.objects.filter(
                Q(user=user) & Q(author=author)).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на этого автора.')

        return attrs



