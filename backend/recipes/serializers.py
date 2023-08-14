import base64
import binascii

from django.core.files.base import ContentFile
from django.db.models import F, Q
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from users.serializers import CustomUserSerializer

from .models import (BuyList, Favorite, Ingredient, IngredientRecipe, Recipe,
                     Tag)


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
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.favorites.filter(user=request.user).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.buylist.filter(user=request.user).exists()
        return False

    def create(self, validated_data):
        ingredients_data = validated_data.pop('recipe_ingredients')
        tags = validated_data.pop('tag')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient_data in ingredients_data:
            ingredient = ingredient_data['ingredient']
            amount = ingredient_data['amount']
            IngredientRecipe.objects.create(
                recipe=recipe, ingredient=ingredient, amount=amount)
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
        instance.recipe_ingredients.all().delete()
        for ingredient_data in ingredients_data:
            ingredient = ingredient_data['ingredient']
            amount = ingredient_data['amount']
            IngredientRecipe.objects.create(
                recipe=instance, ingredient=ingredient, amount=amount)
        return instance

    def validate(self, attrs):
        attrs = super().validate(attrs)
        # Проверяем, что поле 'tags' не является пустым списком.
        tags = attrs.get('tag')
        if not tags:
            raise serializers.ValidationError(
                'Поле "tags" должно содержать хотя бы один элемент.')

        # Проверяем, что поле 'ingredients' не является пустым списком.
        ingredients = attrs.get('recipe_ingredients')
        if not ingredients:
            raise serializers.ValidationError(
                'Поле "ingredients" не должно быть пустым списком.'
            )
        # Проверяем, что у автора нет такого же рецепта.
        name = attrs['name']
        author = self.context['request'].user
        method = self.context['request'].method
        if (method == 'POST' and Recipe.objects.filter(
                name=name, author=author).exists()):
            raise ValidationError(
                'У вас уже есть рецепт с таким названием.')
        return attrs

    def to_representation(self, instance):
        """Добавляет в сериализованный объект данные из связанных таблиц."""

        representation = super().to_representation(instance)
        tags = instance.tag.all()
        representation['tags'] = TagSerializer(tags, many=True).data
        annotated_ingredients = IngredientRecipe.objects.filter(
            recipe=instance).annotate(
            name=F('ingredient__name'),
            measurement_unit=F('ingredient__measurement_unit')
        ).values('id', 'name', 'measurement_unit', 'amount')
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