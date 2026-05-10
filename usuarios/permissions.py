from rest_framework import permissions

from usuarios.models import RolUsuario


class EsAdmin(permissions.BasePermission):
    def has_permission(self, request, view) -> bool:
        return bool(request.user and request.user.is_authenticated and request.user.rol == RolUsuario.ADMIN)
