from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from usuarios.forms import UsuarioCambioFormulario, UsuarioCreacionFormulario
from usuarios.models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    add_form = UsuarioCreacionFormulario
    form = UsuarioCambioFormulario
    model = Usuario
    list_display = ("usuario_id", "email", "nombre", "rol", "grupo", "is_active")
    list_filter = ("rol", "grupo", "is_active")
    search_fields = ("email", "nombre")
    ordering = ("email",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Informacion personal", {"fields": ("nombre", "grupo", "rol")}),
        (
            "Permisos",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Fechas", {"fields": ("last_login",)}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "nombre", "grupo", "rol", "contrasena1", "contrasena2"),
            },
        ),
    )
