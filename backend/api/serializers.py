import base64
import binascii

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db import transaction
from django.db.models import F, Q
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from recipes.models import (BuyList, Favorite, Ingredient, IngredientRecipe,
                            Recipe, Tag)
from users.models import Subscription

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    """Класс для работы с изображениями в формате base64."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            try:
                image_type, image_data = data.split(';base64,')
                image_extension = image_type.split('/')[-1]
                decoded_image = base64.b64decode(image_data)
                file_name = f'image.{image_extension}'
                data = ContentFile(decoded_image, name=file_name)
            except (ValueError, TypeError, binascii.Error):
                raise serializers.ValidationError('Invalid base64 format')
        return super().to_internal_value(data)


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


class IngredientsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('__all__')


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('__all__')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), source='ingredient')

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Recipe."""

    image = Base64ImageField()
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all(), source='tag')
    author = CustomUserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        many=True, source='recipe_ingredients')
    is_favorited = serializers.BooleanField(read_only=True, default=False)
    is_in_shopping_cart = serializers.BooleanField(read_only=True,
                                                   default=False)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')

    def _create_ingredients(self, recipe, ingredients_data):
        ingredients = [
            IngredientRecipe(recipe=recipe,
                             ingredient=ingredient_data['ingredient'],
                             amount=ingredient_data['amount'])
            for ingredient_data in ingredients_data
        ]
        IngredientRecipe.objects.bulk_create(ingredients)

    def create(self, validated_data):
        ingredients_data = validated_data.pop('recipe_ingredients')
        tags = validated_data.pop('tag')
        with transaction.atomic():
            recipe = Recipe.objects.create(**validated_data)
            self._create_ingredients(recipe, ingredients_data)
            recipe.tag.set(tags)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tag', [])
        ingredients_data = validated_data.pop('recipe_ingredients', [])
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time',
                                                   instance.cooking_time)
        instance.image = validated_data.get('image', instance.image)
        instance.save()
        instance.tag.set(tags)
        with transaction.atomic():
            instance.recipe_ingredients.all().delete()
            self._create_ingredients(instance, ingredients_data)
        return instance

    def validate(self, attrs):
        attrs = super().validate(attrs)
        tags = attrs.get('tag')
        name = attrs['name']
        author = self.context['request'].user
        method = self.context['request'].method

        if not tags:
            raise serializers.ValidationError(
                'Поле "tags" должно содержать хотя бы один элемент.')

        ingredients = attrs.get('recipe_ingredients')
        if not ingredients:
            raise serializers.ValidationError(
                'Поле "ingredients" не должно быть пустым списком.'
            )

        if (method == 'POST' and Recipe.objects.filter(
                name=name, author=author, tag__in=tags).exists()):
            raise ValidationError(
                'У вас уже есть рецепт с таким названием и тегами.')

        return attrs

    def to_representation(self, instance):
        """Добавляет в сериализованный объект данные из связанных таблиц."""

        representation = super().to_representation(instance)
        tags = instance.tag.all()
        representation['tags'] = TagSerializer(tags, many=True).data
        annotated_ingredients = IngredientRecipe.objects.filter(
            recipe=instance).annotate(
            id_ingredient=F('ingredient'),
            name=F('ingredient__name'),
            measurement_unit=F('ingredient__measurement_unit')
        ).values('id_ingredient', 'name', 'measurement_unit', 'amount')
        for ingredient in annotated_ingredients:
            ingredient['id'] = ingredient.pop('id_ingredient')
        representation['ingredients'] = annotated_ingredients
        return representation


class RepresentBaseRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для представления отдельных полей модели Recipe.
    Используется в методах to_representation всевозможных сериализаторов
    для добавления рецептов на разные страницы.
    """

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class BaseAddRecipeSerializer(serializers.ModelSerializer):
    """
    Базовый класс для добавления авторизованным пользоватлем
    рецепта в избранное, корзину и т.п. Response передается
    как объект класса RepresentBaseRecipeSerializer.
    """

    class Meta:
        model = None
        fields = ('__all__')
        read_only_fields = ('user', 'recipe')

    def validate(self, attrs):
        # Как я выяснил, UniqueTogetherValidator ищет поля из тела запроса,
        # но мы по ТЗ ничего не передаем в теле. Поэтому пришлось оставить
        # метод validate на уровне сериализатора, а в моделях уже использовать
        # UniqueConstraint в Meta для валидации уникальности.
        model = self.Meta.model
        user = self.context['request'].user
        recipe = self.context['recipe']

        if model.objects.filter(
                Q(user=user) & Q(recipe=recipe)).exists():
            raise ValidationError(
                f'Вы уже добавили этот рецепт в {model._meta.verbose_name}.')
        return super().validate(attrs)

    def create(self, validated_data):
        model = self.Meta.model
        user = self.context['request'].user
        recipe = self.context['recipe']
        model.objects.create(user=user, recipe=recipe)
        return recipe

    def to_representation(self, instance):
        return RepresentBaseRecipeSerializer(instance).data


class FavoriteSerializer(BaseAddRecipeSerializer):
    """Сериализатор для добавления рецептов в избранное."""

    class Meta(BaseAddRecipeSerializer.Meta):
        model = Favorite


class BuyListSerializer(BaseAddRecipeSerializer):
    """Сериализатор для добавления рецептов в корзину."""

    class Meta(BaseAddRecipeSerializer.Meta):
        model = BuyList


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериализатор для создания объекта модели User."""

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'password')


class RecipeRepresentateForSuscribe(serializers.ModelSerializer):
    """Сериализатор для представления отдельных данных о рецепте."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


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
        recipes_limit = self.context.get('recipes_limit')
        queryset = obj.recipes.all()[:recipes_limit]
        recipes = RecipeRepresentateForSuscribe(queryset, many=True).data
        if recipes_limit is not None:
            return recipes
        return recipes

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
