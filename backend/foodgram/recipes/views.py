import django_filters
from django.db.models import Q, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import mixins, viewsets, filters, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (IngredientsSerializer, TagSerializer,
                          RecipeSerializer, FavoriteSerializer,
                          BuyListSerializer)
from .models import Ingredient, Tag, Recipe, Favorite, BuyList, IngredientRecipe
from .filters import IngredientsSearch, RecipeFilter, IsFavoriteFilterBackend
from .permissions import IsAuthorOrReadOnly, IsOwnerPage
from .utils import get_ingredients_for_download


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


class BaseRecipeViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin,
                        viewsets.GenericViewSet):
    permission_classes = (IsOwnerPage,)
    pagination_class = None

    def perform_create(self, serializer, model):
        recipe_id = self.kwargs.get('recipe_id')
        recipe = get_object_or_404(Recipe, id=recipe_id)
        user = self.request.user
        if model.objects.filter(
                Q(user=user) & Q(recipe=recipe)).exists():
            raise ValidationError(
                f'Вы уже добавили этот рецепт в {model._meta.verbose_name}.')
        serializer.save(user=user, recipe=recipe)

    def destroy(self, request, recipe_id, model):
        recipe = get_object_or_404(Recipe, id=recipe_id)
        instance = get_object_or_404(model,
                                     user=self.request.user, recipe=recipe)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteViewSet(BaseRecipeViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer

    def perform_create(self, serializer):
        super().perform_create(serializer, Favorite)

    def destroy(self, request, recipe_id):
        return super().destroy(request, recipe_id, Favorite)


class BuyListViewSet(BaseRecipeViewSet):
    queryset = BuyList.objects.all()
    serializer_class = BuyListSerializer

    def perform_create(self, serializer):
        super().perform_create(serializer, BuyList)

    def destroy(self, request, recipe_id):
        return super().destroy(request, recipe_id, BuyList)


class DownloadShoppingCart(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = self.request.user
        ingredients = IngredientRecipe.objects.filter(
            recipe__buylist__user=user
        ).values('ingredient__name', 'ingredient__measurement_unit').annotate(
            amount=Sum('amount')
        )
        response_content = get_ingredients_for_download(ingredients)
        response = HttpResponse(response_content, content_type='text/plain')
        response[
            'Content-Disposition'] = 'attachment; filename="ingredients.txt"'
        return response
