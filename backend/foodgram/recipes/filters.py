from django.db.models import Q
from rest_framework import filters


class IngredientsSearch(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        search_query = request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(
                Q(name__istartswith=search_query) |
                Q(name__icontains=search_query)
            )
        return queryset
