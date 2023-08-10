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

    message = 'Изменять контент может только его автор или админ.'

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
    Добавлять рецепт в избранное может только авторизованный пользователь.
    Удалять рецепт из избранного может только владелец страницы.
    """

    message = 'Удалить рецепт можно только со своей страницы избранного.'

    def has_permission(self, request, view):
        if request.method == 'DELETE':
            recipe_id = view.kwargs.get('recipe_id')
            favorite = get_object_or_404(Favorite, favorite_recipe=recipe_id)
            return favorite.user == request.user
        return super().has_permission(request, view)
