from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import BasePermission, IsAuthenticated, \
    SAFE_METHODS


class IsOwnerOrReadOnly(BasePermission):
    """
    Разрешает доступ к эндпоинту /users/me только авторизованному пользователю.
    """

    def has_permission(self, request, view):
        if view.action == 'me':
            return request.user.is_authenticated
        elif request.method in SAFE_METHODS:
            return True
        raise MethodNotAllowed(method=request.method)


    def has_object_permission(self, request, view, obj):
        if view.action == 'me':
            return obj == request.user
        elif request.method in SAFE_METHODS:
            return True
        raise MethodNotAllowed(method=request.method)
