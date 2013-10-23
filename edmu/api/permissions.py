from rest_framework import permissions


class IsCompanyActive(permissions.BasePermission):
    """
    Permission to check verify if a company is active
    """
    def has_permission(self, request, view):
        return request.user.company.is_active


class IsStaff(permissions.BasePermission):
    """
    Object-level permission, only users that are set as staff members.
    """
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Instance must have an attribute named `owner`.
        return obj.owner == request.user


class IsOwner(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to view or
    edit it. Assumes the model instance has an `owner` attribute.
    """
    def has_object_permission(self, request, view, obj):
        # Instance must have an attribute named `owner`.
        return obj.owner == request.user


class HasRole(permissions.BasePermission):
    """
    Object-level permission only to allow users that has a certain
    role access to a resource.
    """
    def has_permission(self, request, view):
        # `View` must have an attribute named `_role`
        return view.role in request.user.roles