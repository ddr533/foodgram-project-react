from django.core.cache import cache
from django.db.models import Sum, OuterRef, Exists
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .permissions import IsAuthorOrReadOnly
from .utils import get_ingredients_for_download
from .filters import CustomFilterBackend, IngredientsSearch, RecipeFilter
from .serializers import (BuyListSerializer, FavoriteSerializer, TagSerializer,
                         IngredientsSerializer, RecipeSerializer)
from recipes.models import (BuyList, Favorite, Ingredient, IngredientRecipe,
                            Recipe, Tag)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientsSerializer
    filter_backends = (IngredientsSearch, )
    pagination_class = None


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.select_related('author').prefetch_related(
        'tag', 'ingredient').all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend, OrderingFilter,
                       CustomFilterBackend)
    filterset_class = RecipeFilter
    ordering_fields = ('pub_date')
    ordering = ('-pub_date',)

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return super().get_queryset()

        queryset = super().get_queryset().annotate(
            is_favorited=Exists(
                Favorite.objects.filter(
                    user=self.request.user,
                    recipe_id=OuterRef('pk')
                )
            ),
            is_in_shopping_cart=Exists(
                BuyList.objects.filter(
                    user=self.request.user,
                    recipe_id=OuterRef('pk')
                )
            )
        )
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class BaseAddRecipeViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):
    """
    Базовый класс представлений для удаления и добавления
    рецептов в корзину, в избранное и т.п.
    """

    pagination_class = None
    lookup_field = 'recipe_id'
    permission_classes = (IsAuthenticated,)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        recipe_id = self.kwargs.get('recipe_id')
        if recipe_id:
            recipe = cache.get(f'recipe_{recipe_id}')
            if not recipe:
                recipe = get_object_or_404(Recipe, id=recipe_id)
                cache.set(f'recipe_{recipe_id}', recipe, 300)
            context['recipe'] = recipe
        return context

    def destroy(self, request, recipe_id):
        # При запросе DELETE get_serializer_context не вызывается, как я понял
        # Но добавил кеш, чтобы не ходить к Recipe дважды
        try:
            user = request.user
            recipe = cache.get(f'recipe_{recipe_id}')
            if not recipe:
                recipe = get_object_or_404(Recipe, id=recipe_id)
                cache.set(f'recipe_{recipe_id}', recipe, 300)
            instance = get_object_or_404(self.queryset, user=user,
                                         recipe=recipe)
        except Exception:
            raise ValidationError('Такой рецепт не найден в списке.')
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteViewSet(BaseAddRecipeViewSet):
    """Обработчик добавления рецептов в избранное."""

    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer


class BuyListViewSet(BaseAddRecipeViewSet):
    """Обработчик добавления рецептов в корзину."""

    queryset = BuyList.objects.all()
    serializer_class = BuyListSerializer


class DownloadShoppingCart(APIView):
    """
    Обработчик выгрузки рецептов из корзины.
    Выдает response с текстовым файлом.
    """

    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = self.request.user
        ingredients = IngredientRecipe.objects.filter(
            recipe__buylist_set__user=user
        ).values('ingredient__name', 'ingredient__measurement_unit').annotate(
            amount=Sum('amount')
        )
        # Получаем строковое представление ingredients
        response_content: str = get_ingredients_for_download(ingredients)
        response = HttpResponse(response_content, content_type='text/plain')
        response[
            'Content-Disposition'] = 'attachment; filename="ingredients.txt"'
        return response
