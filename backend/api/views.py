from django.contrib.auth import get_user_model
from django.db.models import Exists, OuterRef, Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import (BuyList, Favorite, Ingredient, IngredientRecipe,
                            Recipe, Tag)
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import Subscription

from .filters import CustomFilterBackend, IngredientsSearch, RecipeFilter
from .permissions import IsAuthorOrReadOnly
from .serializers import (BuyListSerializer, CustomUserCreateSerializer,
                          CustomUserSerializer, FavoriteSerializer,
                          IngredientsSerializer, RecipeSerializer,
                          SubscriptionSerializer, TagSerializer)
from .utils import get_ingredients_for_download

User = get_user_model()


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
        context['recipe_id'] = self.kwargs.get('recipe_id')
        return context

    def destroy(self, request, recipe_id):
        user = request.user
        recipe = get_object_or_404(Recipe, id=recipe_id)
        instance = get_object_or_404(self.queryset, user=user, recipe=recipe)
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
            recipe__buylist__user=user
        ).values('ingredient__name', 'ingredient__measurement_unit').annotate(
            amount=Sum('amount')
        )
        response_content: str = get_ingredients_for_download(ingredients)
        response = HttpResponse(response_content, content_type='text/plain')
        response[
            'Content-Disposition'] = 'attachment; filename="ingredients.txt"'
        return response


class CustomUserViewSet(UserViewSet):
    """Обработчик запросов к модели User."""

    serializer_class = CustomUserSerializer

    def get_queryset(self):
        if self.action == 'list':
            return self.queryset
        return super().get_queryset()

    def get_serializer_class(self):
        if self.action == 'create':
            return CustomUserCreateSerializer
        return self.serializer_class

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class SubscriptionViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                          mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """Обработчик для оформления и удаления подписок пользователями."""

    serializer_class = SubscriptionSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        authors = self.request.user.subscribers.values('author').all()
        return User.objects.filter(id__in=authors).prefetch_related('recipes')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        author_id = self.kwargs.get('author_id')
        context['recipes_limit'] = self.request.query_params.get(
            'recipes_limit')
        if author_id:
            context['author'] = get_object_or_404(User, id=author_id)
        context['user'] = self.request.user
        return context

    def perform_create(self, serializer):
        user = self.get_serializer_context().get('user')
        author = self.get_serializer_context().get('author')
        serializer.save(user=user, author=author)

    def destroy(self, request, author_id):
        author = get_object_or_404(User, id=author_id)
        instance = get_object_or_404(Subscription, user=self.request.user,
                                     author=author)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
