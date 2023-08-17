from rest_framework import permissions
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import SAFE_METHODS, BasePermission


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


class CustomUserPermission(BasePermission):
    """
    Разрешает только безопасные методы к user-list и user-detail всем
    прользователям. Доступ к эндпоинту /users/me имеет только авторизованный
    владелец профиля.
    """

    def has_permission(self, request, view):
        is_safe_method = request.method in SAFE_METHODS

        if not is_safe_method:
            raise MethodNotAllowed(method=request.method)

        if view.action == 'me':
            return request.user.is_authenticated

        return True

    def has_object_permission(self, request, view, obj):
        is_safe_method = request.method in SAFE_METHODS

        if not is_safe_method:
            raise MethodNotAllowed(method=request.method)

        if view.action == 'me':
            return obj == request.user

        return True
