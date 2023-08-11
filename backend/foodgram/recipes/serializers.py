import base64
import binascii

from django.core.files.base import ContentFile
from django.db.models import F
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Ingredient, Tag, Recipe, IngredientRecipe, Favorite, BuyList
from users.serializers import CustomUserSerializer


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
        image = Base64ImageField()
        tags = serializers.PrimaryKeyRelatedField(
            many=True, queryset=Tag.objects.all(), source='tag')
        author = CustomUserSerializer(read_only=True)
        ingredients = RecipeIngredientSerializer(
            many=True, source='recipe_ingredients')
        is_favorite = serializers.SerializerMethodField()
        is_in_shopping_cart = serializers.SerializerMethodField()

        class Meta:
            model = Recipe
            fields = ('id', 'tags', 'author', 'ingredients', 'is_favorite',
                      'is_in_shopping_cart', 'name', 'image', 'text',
                      'cooking_time')

        def get_is_favorite(self, obj):
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

        def to_representation(self, instance):
            representation = super().to_representation(instance)
            representation['tags'] = TagSerializer(instance.tag.all(),
                                                   many=True).data
            annotated_ingredients = IngredientRecipe.objects.filter(
                recipe=instance).annotate(
                name=F('ingredient__name'),
                measurement_unit=F('ingredient__measurement_unit')
            ).values('id', 'name', 'measurement_unit', 'amount')
            representation['ingredients'] = annotated_ingredients
            return representation

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

            # Проверяем, что поле 'ingredients' не явлется пустым списком.
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


class RepresentBaseRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')

class BaseRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('__all__')
        read_only_fields = ('user', 'recipe')

    def to_representation(self, instance):
        recipe_data = RepresentBaseRecipeSerializer(
            instance=instance.recipe).data
        return recipe_data


class FavoriteSerializer(BaseRecipeSerializer):

    class Meta(BaseRecipeSerializer.Meta):
        model = Favorite

class BuyListSerializer(BaseRecipeSerializer):

    class Meta(BaseRecipeSerializer.Meta):
        model = BuyList



# class FavoriteSerializer(serializers.ModelSerializer):
#
#     class Meta:
#         model = Favorite
#         fields = ('__all__')
#         read_only_fields = ('user', 'recipe')
#
#     def to_representation(self, instance):
#         recipe_data = RepresentBaseRecipeSerializer(
#             instance=instance.recipe).data
#         return recipe_data
#
#
# class BuyListSerializer(serializers.ModelSerializer):
#
#     class Meta:
#         model = BuyList
#         fields = ('__all__')
#         read_only_fields = ('user', 'recipe')
#
#     def to_representation(self, instance):
#         recipe_data = RecipeForFavoriteSerializer(
#             instance=instance.recipe).data
#         return recipe_data

