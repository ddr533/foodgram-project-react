from rest_framework import pagination


class CustomPagination(pagination.PageNumberPagination):
    """Класс пагинатора с параметрами page и limit."""

    page_query_param = 'page'
    page_size_query_param = 'limit'
