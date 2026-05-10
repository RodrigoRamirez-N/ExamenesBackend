from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class GrupoUsuario(models.TextChoices):
    PRIMARIA = "PRIMARIA", "PRIMARIA"
    SECUNDARIA = "SECUNDARIA", "SECUNDARIA"
    PREPA = "PREPA", "PREPA"
    LICENCIATURA = "LICENCIATURA", "LICENCIATURA"
    MAESTRIA = "MAESTRIA", "MAESTRIA"
    DOCTORADO = "DOCTORADO", "DOCTORADO"


class RolUsuario(models.TextChoices):
    ADMIN = "ADMIN", "ADMIN"
    USUARIO = "USUARIO", "USUARIO"


class UsuarioManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email: str, password: str | None = None, **extra_fields):
        if not email:
            raise ValueError("El email es obligatorio")
        email = self.normalize_email(email)
        usuario = self.model(email=email, **extra_fields)
        if password:
            usuario.set_password(password)
        else:
            usuario.set_unusable_password()
        usuario.save(using=self._db)
        return usuario

    def create_superuser(self, email: str, password: str, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if not extra_fields.get("is_staff"):
            raise ValueError("El superusuario debe tener is_staff=True")
        if not extra_fields.get("is_superuser"):
            raise ValueError("El superusuario debe tener is_superuser=True")
        return self.create_user(email, password, **extra_fields)

    def crear_usuario(self, email: str, contrasena: str | None = None, **extra_fields):
        return self.create_user(email, password=contrasena, **extra_fields)

    def crear_superusuario(self, email: str, contrasena: str, **extra_fields):
        return self.create_superuser(email, password=contrasena, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    usuario_id = models.BigAutoField(primary_key=True, db_column="usuario_id")
    nombre = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    password = models.CharField("contrasena", max_length=128, db_column="contrasena")
    grupo = models.CharField(
        max_length=20,
        choices=GrupoUsuario.choices,
        null=True,
        blank=True,
    )
    rol = models.CharField(
        max_length=10,
        choices=RolUsuario.choices,
        default=RolUsuario.USUARIO,
    )
    is_active = models.BooleanField(default=True, db_column="activo")
    is_staff = models.BooleanField(default=False, db_column="es_staff")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    objects = UsuarioManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nombre"]

    class Meta:
        db_table = "usuario"
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    def __str__(self) -> str:
        return f"{self.nombre} <{self.email}>"
