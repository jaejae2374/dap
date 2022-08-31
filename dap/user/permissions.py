from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Only object's owner can touch object.
    """

    message = 'Not allowed.'

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return obj.id == request.user.id

class IsAdminUser(permissions.BasePermission):
    """
    Only admin user can touch object.
    """

    message = 'Not allowed.'

    def has_permission(self, request, view):
        user = request.user
        return user and user.is_authenticated and user.is_superuser


class IsMentor(permissions.BasePermission):
    """
    Only mentor user can touch object.
    """

    message = 'Not allowed.'

    def has_permission(self, request, view):
        print("ohyeah")
        user = request.user
        return user and user.is_authenticated and user.mentor


class IsMentee(permissions.BasePermission):
    """
    Only mentee user can touch object.
    """

    message = 'Not allowed.'

    def has_permission(self, request, view):
        user = request.user
        return user and user.is_authenticated and user.mentee

    
