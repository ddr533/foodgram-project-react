import django_filters
from django.db.models import Q
from rest_framework import filters

from .models import Recipe


class IngredientsSearch(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        search_query = request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(
                Q(name__istartswith=search_query) |
                Q(name__icontains=search_query)
            )
        return queryset


class RecipeFilter(django_filters.FilterSet):
    author = django_filters.CharFilter(field_name='author__username')
    tags = django_filters.CharFilter(method='filter_tags')

    class Meta:
        model = Recipe
        fields = ['author', 'tags']

    def filter_tags(self, queryset, name, value):
        tags = self.request.GET.getlist('tags')
        return queryset.filter(tag__slug__in=tags)


class IsFavoriteFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        is_favorite = request.query_params.get('is_favorite')
        if is_favorite is not None:
            is_favorite = bool(int(is_favorite))
            user = request.user
            if is_favorite:
                queryset = queryset.filter(favorites__user=user)
            else:
                queryset = queryset.exclude(favorites__user=user)
        return queryset
