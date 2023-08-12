import django_filters
from django.db.models import Sum
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
from .filters import IngredientsSearch, RecipeFilter, CustomFilterBackend
from .permissions import IsAuthorOrReadOnly
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
                       filters.OrderingFilter, CustomFilterBackend)
    filterset_class = RecipeFilter
    ordering_fields = ('pub_date', )
    ordering = ('-pub_date',)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class BaseAddRecipeViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin,
                        viewsets.GenericViewSet):
    pagination_class = None
    lookup_field = 'recipe_id'
    permission_classes = (IsAuthenticated,)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        recipe_id = self.kwargs.get('recipe_id')
        if recipe_id:
            context['recipe'] = get_object_or_404(Recipe, id=recipe_id)
        return context

    def destroy(self, request, recipe_id):
        try:
            user = request.user
            recipe = Recipe.objects.get(id=recipe_id)
            instance = self.queryset.get(user=user, recipe=recipe)
        except Exception:
            raise ValidationError()
        instance.delete()
        return Response(status=status.HTTP_200_OK)

class FavoriteViewSet(BaseAddRecipeViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer


class BuyListViewSet(BaseAddRecipeViewSet):
    queryset = BuyList.objects.all()
    serializer_class = BuyListSerializer


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
