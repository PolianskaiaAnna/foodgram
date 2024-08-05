from rest_framework import permissions


# class IsOwnerOrReadOnly(permissions.BasePermission):
#     """
#     Разрешение, дающее доступ к редактированию только
#     автору контента или админу
#     """
#     def has_permission(self, request, view):
#         return (
#             request.method in permissions.SAFE_METHODS
#             or request.user.is_authenticated
#             and request.user.is_admin
#         )

    # def has_object_permission(self, request, view, obj):
    #     return (
    #         request.method in permissions.SAFE_METHODS
    #         or request.user.is_authenticated
    #         and request.user.is_admin
    #     )
    

class IsAuthorOrAdmin(permissions.BasePermission):
    """
    Пермишен, который разрешает доступ на просмотр всем пользователям,
    но разрешает изменение только авторам и администраторам.
    """

    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (
            obj.author == request.user            
            or request.user.is_staff
        )