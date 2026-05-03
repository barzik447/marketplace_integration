from rest_framework.permissions import BasePermission


class AdminCreatorPermision(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user:
            user = request.user
            if user.is_superuser or user == obj.creator:
                return True
        return False
