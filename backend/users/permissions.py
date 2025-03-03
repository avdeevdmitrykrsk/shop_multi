from rest_framework.permissions import BasePermission


class AllBlock(BasePermission):

    def has_permission(self, request, view):
        return False

    def has_object_permission(self, request, view, obj):
        return False


class IsSuperuser(BasePermission):

    def has_permission(self, request, view):
        return bool(
            request.user.is_authenticated and request.user.is_superuser
        )
