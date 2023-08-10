import django_filters
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, Exists, OuterRef, When, Case
from django.forms import BooleanField
from django.shortcuts import get_object_or_404
from rest_framework import mixins, viewsets, filters, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .serializers import (IngredientsSerializer,
                          TagSerializer,
                          RecipeSerializer, FavoriteSerializer)
from .models import Ingredient, Tag, Recipe, Favorite
from .filters import IngredientsSearch, RecipeFilter, IsFavoriteFilterBackend
from .permissions import IsAuthorOrReadOnly, IsOwnerPage


class IngredientViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientsSerializer
    filter_backends = (IngredientsSearch,)
    pagination_class = None


class TagViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,
                       filters.OrderingFilter, IsFavoriteFilterBackend)
    filterset_class = RecipeFilter
    ordering_fields = ('pub_date', )
    ordering = ('pub_date',)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class FavoriteViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = (IsOwnerPage,)
    pagination_class = None

    def perform_create(self, serializer):
        recipe_id = self.kwargs.get('recipe_id')
        recipe = get_object_or_404(Recipe, id=recipe_id)
        user = self.request.user
        if Favorite.objects.filter(
                Q(user=user) & Q(favorite_recipe=recipe)).exists():
            raise ValidationError(
                'Вы уже добавили эту подписку в избранное.')
        serializer.save(user=user, favorite_recipe=recipe)

    def destroy(self, request, recipe_id):
        try:
            instance = Favorite.objects.get(
                user=self.request.user,
                favorite_recipe=recipe_id)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
