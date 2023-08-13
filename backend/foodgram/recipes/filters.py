import django_filters
from django.db.models import Q
from rest_framework import filters
from rest_framework.exceptions import PermissionDenied

from .models import Recipe


class IngredientsSearch(filters.BaseFilterBackend):
    """Поиск по вхождени. в начало имени ингредиента."""

    def filter_queryset(self, request, queryset, view):
        search_query = request.query_params.get('name', None)
        if search_query:
            queryset = queryset.filter(name__istartswith=search_query)
        return queryset


class RecipeFilter(django_filters.FilterSet):
    """Фильтры по тегам и автору рецепта для запросов к ресурсу recipes."""

    author = django_filters.CharFilter(field_name='author__id')
    tags = django_filters.CharFilter(method='filter_tags')

    class Meta:
        model = Recipe
        fields = ['author', 'tags']

    def filter_tags(self, queryset, name, value):
        tags = self.request.GET.getlist('tags')
        return queryset.filter(tag__slug__in=tags).distinct()


class CustomFilterBackend(filters.BaseFilterBackend):
    """Фильтры по наличию рецепта в избранном и в корзине."""

    def filter_queryset(self, request, queryset, view):
        is_favorite = request.query_params.get('is_favorited')
        is_in_shopping_cart = request.query_params.get('is_in_shopping_cart')
        user = request.user

        if is_favorite is not None:
            if not user.is_authenticated:
                raise PermissionDenied(
                    'Для просмотра избранного авторизируйтесь.')
            is_favorite = bool(int(is_favorite))
            if is_favorite:
                queryset = queryset.filter(favorites__user=user)
            else:
                queryset = queryset.exclude(favorites__user=user)

        if is_in_shopping_cart is not None:
            if not user.is_authenticated:
                raise PermissionDenied(
                    'Для просмотра карзины авторизируйтесь.')
            is_in_shopping_cart = bool(int(is_in_shopping_cart))
            if is_in_shopping_cart:
                queryset = queryset.filter(buylist__user=user)
            else:
                queryset = queryset.exclude(buylist__user=user)

        return queryset
