from rest_framework import permissions


class IsAuthorOrAdmin(permissions.BasePermission):
    """
    Пермишен, который разрешает доступ на просмотр всем пользователям,
    но разрешает изменение только авторам и администраторам.
    """

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.is_staff
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Разрешение, дающее доступ к редактированию только
    админу
    """
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_staff
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_staff
        )


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Разрешение, дающее доступ к редактированию только
    админу
    """
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_staff
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_staff
        )
