from django.contrib.auth import get_user_model
from django.db.models import Q
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Subscription

User = get_user_model()

class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериализатор для создания объекта модели User."""

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'password')


class CustomUserSerializer(UserSerializer):
    """Сериализатор для получения объектов модели User."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if not user.is_authenticated:
            return False
        return Subscription.objects.filter(user=user, author=obj).exists()


class SubscriptionSerializer(serializers.ModelSerializer):
    """
    Сериализатор данных из модели User c добавлением
    дополнительных полей на основе отношений с моделью Subsription.
    """

    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')
        read_only_fields = ('email', 'id', 'username', 'first_name',
                            'last_name', 'is_subscribed', 'recipes',
                            'recipes_count')

    def get_is_subscribed(self, obj):
        return obj.subscribed.filter(user=self.context['user']).exists()

    def get_recipes(self, obj):
        queryset = obj.recipes.all().values('id', 'name', 'image',
                                            'cooking_time')
        recipes_limit = self.context.get('recipes_limit')
        if recipes_limit is not None:
            return queryset[:recipes_limit]
        return queryset

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def validate(self, attrs):
        attrs = super().validate(attrs)
        user = self.context['user']
        author = self.context['author']

        if Subscription.objects.filter(
                Q(user=user) & Q(author=author)).exists():
            raise ValidationError(
                f'Вы уже подписывались на пользователя {author.username}.')

        if user == author:
            raise serializers.ValidationError(
                'Вы не можете подписываться на себя.')
        return attrs

    def create(self, validated_data):
        user = self.context['user']
        author = self.context['author']
        Subscription.objects.create(user=user, author=author)
        return author
