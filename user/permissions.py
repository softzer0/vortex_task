from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsGuest(BasePermission):
    """
    Allows access only to guests.
    """
    message = "This action is not allowed for logged in users."

    def has_permission(self, request, view):
        return bool(not request.user or request.user.is_anonymous)


class IsOwnerOrReadOnly(BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in SAFE_METHODS:
            return True

        return obj == request.user

