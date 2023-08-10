from rest_framework import permissions
from rest_framework.exceptions import MethodNotAllowed


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
