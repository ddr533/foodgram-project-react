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

    def filter_tags(self, queryset, name, value):
        tags = self.request.GET.getlist('tags')
        return queryset.filter(tag__slug__in=tags)

    class Meta:
        model = Recipe
        fields = ['author', 'tags']
