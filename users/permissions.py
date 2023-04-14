from rest_framework.permissions import BasePermission

from users.models import CustomUser


class AdminAccessPermission(BasePermission):
    def has_permission(self, request, view):
        (user, created) = CustomUser.objects.get_or_create(user_id=request.user.id)
        return user.is_admin