from rest_framework.permissions import BasePermission
from rest_framework.permissions import DjangoModelPermissions as BaseDjangoPermissions
from rest_framework.permissions import SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)


class DjangoModelPermissions(BaseDjangoPermissions):
    """Add GET to djangoAdmin Permissions"""

    perms_map = {
        "GET": ["%(app_label)s.view_%(model_name)s"],
    }
