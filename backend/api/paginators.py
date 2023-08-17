from rest_framework import pagination

from .constants import MAX_PAGE_SIZE, PAGE_SIZE


class CustomPagination(pagination.PageNumberPagination):
    """Класс пагинатора с параметрами page и limit."""

    page_query_param = 'page'
    page_size_query_param = 'limit'
    page_size = PAGE_SIZE
    max_page_size = MAX_PAGE_SIZE
