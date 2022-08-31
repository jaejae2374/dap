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
            return obj.mentor.filter(id=request.user.id).exists()
