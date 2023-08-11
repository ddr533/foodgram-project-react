from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import IsAuthenticated

from .models import Favorite


class IsAuthorOrReadOnly(permissions.IsAuthenticatedOrReadOnly):
    """
    Изменять рецепт может только автор и администратор.
    Для редактирования доступен только метод PATCH.
    """

    message = ('Изменять контент может только его автор или админ.'
               ' Для редактирования доступен только метод PATCH.')

    def has_permission(self, request, view):
        if request.method == 'PUT':
            raise MethodNotAllowed(method=request.method)
        return super().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        return any((request.method in permissions.SAFE_METHODS,
                    request.user == obj.author,
                    request.user.is_superuser,))


class IsOwnerPage(IsAuthenticated):
    """
    Добавлять рецепт в избранное и список покупок может только
    авторизованный пользователь. Удалять рецепт из избранного
    и списка покупок может только владелец страницы.
    """

    message = 'Удалить рецепт можно только со своей страницы.'

    def has_permission(self, request, view):
        model = view.queryset.model
        if request.method == 'DELETE':
            recipe_id = view.kwargs.get('recipe_id')
            user=request.user
            return model.objects.filter(user=user, recipe=recipe_id).exists()
        return super().has_permission(request, view)
