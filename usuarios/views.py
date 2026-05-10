from rest_framework import serializers, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
    inline_serializer,
)

from usuarios.models import RolUsuario, Usuario
from usuarios.permissions import EsAdmin
from usuarios.serializers import (
    LoginSerializer,
    UsuarioAdminSerializer,
    UsuarioLecturaSerializer,
    UsuarioPerfilSerializer,
    UsuarioRegistroSerializer,
)


LoginRespuestaSerializer = inline_serializer(
    name="LoginRespuesta",
    fields={
        "token": serializers.CharField(),
        "usuario": UsuarioLecturaSerializer(),
    },
)
ErrorCredencialesSerializer = inline_serializer(
    name="ErrorCredenciales",
    fields={
        "non_field_errors": serializers.ListField(child=serializers.CharField()),
    },
)
ErrorDetalleSerializer = inline_serializer(
    name="ErrorDetalle",
    fields={
        "detail": serializers.CharField(),
    },
)


class LoginAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        request=LoginSerializer,
        responses={
            200: OpenApiResponse(
                response=LoginRespuestaSerializer,
                examples=[
                    OpenApiExample(
                        "Login exitoso",
                        value={
                            "token": "0f1a...",
                            "usuario": {
                                "usuario_id": 1,
                                "nombre": "Juan Perez",
                                "email": "usuario@correo.com",
                                "grupo": "LICENCIATURA",
                                "rol": "USUARIO",
                            },
                        },
                    )
                ],
            ),
            400: OpenApiResponse(
                response=ErrorCredencialesSerializer,
                examples=[
                    OpenApiExample(
                        "Credenciales invalidas",
                        value={"non_field_errors": ["Credenciales invalidas"]},
                    )
                ],
            ),
        },
        examples=[
            OpenApiExample(
                "Login request",
                value={"email": "usuario@correo.com", "contrasena": "mi_password"},
                request_only=True,
            )
        ],
        auth=[],
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        usuario = serializer.validated_data["usuario"]
        token, _ = Token.objects.get_or_create(user=usuario)
        return Response(
            {
                "token": token.key,
                "usuario": UsuarioLecturaSerializer(usuario).data,
            }
        )


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            204: OpenApiResponse(description="Logout exitoso"),
            401: OpenApiResponse(
                response=ErrorDetalleSerializer,
                examples=[
                    OpenApiExample(
                        "Sin credenciales",
                        value={"detail": "Authentication credentials were not provided."},
                    )
                ],
            ),
        }
    )
    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema_view(
    list=extend_schema(
        responses={
            200: OpenApiResponse(
                response=UsuarioLecturaSerializer(many=True),
                examples=[
                    OpenApiExample(
                        "Lista usuarios",
                        value=[
                            {
                                "usuario_id": 1,
                                "nombre": "Juan Perez",
                                "email": "usuario@correo.com",
                                "grupo": "LICENCIATURA",
                                "rol": "USUARIO",
                            }
                        ],
                    )
                ],
            ),
            401: OpenApiResponse(
                response=ErrorDetalleSerializer,
                examples=[
                    OpenApiExample(
                        "Sin credenciales",
                        value={"detail": "Authentication credentials were not provided."},
                    )
                ],
            ),
            403: OpenApiResponse(
                response=ErrorDetalleSerializer,
                examples=[
                    OpenApiExample(
                        "Sin permisos",
                        value={"detail": "You do not have permission to perform this action."},
                    )
                ],
            ),
        }
    ),
    retrieve=extend_schema(
        responses={
            200: OpenApiResponse(
                response=UsuarioLecturaSerializer,
                examples=[
                    OpenApiExample(
                        "Detalle usuario",
                        value={
                            "usuario_id": 3,
                            "nombre": "Pedro Ruiz",
                            "email": "pedro@correo.com",
                            "grupo": "PREPA",
                            "rol": "USUARIO",
                        },
                    )
                ],
            ),
            401: OpenApiResponse(
                response=ErrorDetalleSerializer,
                examples=[
                    OpenApiExample(
                        "Sin credenciales",
                        value={"detail": "Authentication credentials were not provided."},
                    )
                ],
            ),
            403: OpenApiResponse(
                response=ErrorDetalleSerializer,
                examples=[
                    OpenApiExample(
                        "Sin permisos",
                        value={"detail": "You do not have permission to perform this action."},
                    )
                ],
            ),
            404: OpenApiResponse(
                response=ErrorDetalleSerializer,
                examples=[
                    OpenApiExample(
                        "No encontrado",
                        value={"detail": "Not found."},
                    )
                ],
            ),
        }
    ),
    create=extend_schema(
        request=UsuarioRegistroSerializer,
        responses={
            201: OpenApiResponse(
                response=UsuarioAdminSerializer,
                examples=[
                    OpenApiExample(
                        "Registro publico",
                        value={
                            "usuario_id": 2,
                            "nombre": "Ana Lopez",
                            "email": "ana@correo.com",
                            "grupo": "LICENCIATURA",
                            "rol": "USUARIO",
                        },
                    ),
                    OpenApiExample(
                        "Creacion admin",
                        value={
                            "usuario_id": 4,
                            "nombre": "Admin Uno",
                            "email": "admin@correo.com",
                            "grupo": "MAESTRIA",
                            "rol": "ADMIN",
                            "is_active": True,
                        },
                    ),
                ],
            ),
            400: OpenApiResponse(
                response=inline_serializer(
                    name="ErrorRegistro",
                    fields={"email": serializers.ListField(child=serializers.CharField())},
                ),
                examples=[
                    OpenApiExample(
                        "Email duplicado",
                        value={"email": ["usuario con este email ya existe."]},
                    )
                ],
            ),
        },
        examples=[
            OpenApiExample(
                "Registro request",
                value={
                    "nombre": "Ana Lopez",
                    "email": "ana@correo.com",
                    "contrasena": "miclave123",
                    "grupo": "LICENCIATURA",
                },
                request_only=True,
            )
        ],
        auth=[],
    ),
    update=extend_schema(
        request=UsuarioAdminSerializer,
        responses={
            200: OpenApiResponse(
                response=UsuarioAdminSerializer,
                examples=[
                    OpenApiExample(
                        "Actualizacion admin",
                        value={
                            "usuario_id": 3,
                            "nombre": "Pedro Ruiz",
                            "email": "pedro@correo.com",
                            "grupo": "DOCTORADO",
                            "rol": "ADMIN",
                            "is_active": True,
                        },
                    )
                ],
            ),
            400: OpenApiResponse(
                response=inline_serializer(
                    name="ErrorValidacionUsuario",
                    fields={"email": serializers.ListField(child=serializers.CharField())},
                ),
                examples=[
                    OpenApiExample(
                        "Error validacion",
                        value={"email": ["Formato de email invalido"]},
                    )
                ],
            ),
            401: OpenApiResponse(
                response=ErrorDetalleSerializer,
                examples=[
                    OpenApiExample(
                        "Sin credenciales",
                        value={"detail": "Authentication credentials were not provided."},
                    )
                ],
            ),
            403: OpenApiResponse(
                response=ErrorDetalleSerializer,
                examples=[
                    OpenApiExample(
                        "Sin permisos",
                        value={"detail": "You do not have permission to perform this action."},
                    )
                ],
            ),
            404: OpenApiResponse(
                response=ErrorDetalleSerializer,
                examples=[
                    OpenApiExample(
                        "No encontrado",
                        value={"detail": "Not found."},
                    )
                ],
            ),
        }
    ),
    partial_update=extend_schema(
        request=UsuarioAdminSerializer,
        responses={
            200: OpenApiResponse(
                response=UsuarioAdminSerializer,
                examples=[
                    OpenApiExample(
                        "Actualizacion parcial",
                        value={
                            "usuario_id": 3,
                            "nombre": "Pedro Ruiz",
                            "email": "pedro@correo.com",
                            "grupo": "DOCTORADO",
                            "rol": "ADMIN",
                            "is_active": True,
                        },
                    )
                ],
            ),
            400: OpenApiResponse(
                response=inline_serializer(
                    name="ErrorValidacionUsuarioParcial",
                    fields={"email": serializers.ListField(child=serializers.CharField())},
                ),
                examples=[
                    OpenApiExample(
                        "Error validacion",
                        value={"email": ["Formato de email invalido"]},
                    )
                ],
            ),
            401: OpenApiResponse(
                response=ErrorDetalleSerializer,
                examples=[
                    OpenApiExample(
                        "Sin credenciales",
                        value={"detail": "Authentication credentials were not provided."},
                    )
                ],
            ),
            403: OpenApiResponse(
                response=ErrorDetalleSerializer,
                examples=[
                    OpenApiExample(
                        "Sin permisos",
                        value={"detail": "You do not have permission to perform this action."},
                    )
                ],
            ),
            404: OpenApiResponse(
                response=ErrorDetalleSerializer,
                examples=[
                    OpenApiExample(
                        "No encontrado",
                        value={"detail": "Not found."},
                    )
                ],
            ),
        }
    ),
    destroy=extend_schema(
        responses={
            204: OpenApiResponse(description="Usuario eliminado"),
            401: OpenApiResponse(
                response=ErrorDetalleSerializer,
                examples=[
                    OpenApiExample(
                        "Sin credenciales",
                        value={"detail": "Authentication credentials were not provided."},
                    )
                ],
            ),
            403: OpenApiResponse(
                response=ErrorDetalleSerializer,
                examples=[
                    OpenApiExample(
                        "Sin permisos",
                        value={"detail": "You do not have permission to perform this action."},
                    )
                ],
            ),
            404: OpenApiResponse(
                response=ErrorDetalleSerializer,
                examples=[
                    OpenApiExample(
                        "No encontrado",
                        value={"detail": "Not found."},
                    )
                ],
            ),
        }
    ),
)
class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all().order_by("usuario_id")

    def get_permissions(self):
        if self.action == "create":
            return [AllowAny()]
        if self.action == "mi_perfil":
            return [IsAuthenticated()]
        return [EsAdmin()]

    def get_serializer_class(self):
        if self.action == "create":
            if self.request.user.is_authenticated and self.request.user.rol == RolUsuario.ADMIN:
                return UsuarioAdminSerializer
            return UsuarioRegistroSerializer
        if self.action in {"update", "partial_update"}:
            return UsuarioAdminSerializer
        if self.action == "mi_perfil":
            return UsuarioPerfilSerializer
        return UsuarioLecturaSerializer

    @extend_schema(
        request=UsuarioPerfilSerializer,
        responses={
            200: OpenApiResponse(
                response=UsuarioLecturaSerializer,
                examples=[
                    OpenApiExample(
                        "Perfil",
                        value={
                            "usuario_id": 2,
                            "nombre": "Ana Lopez",
                            "email": "ana@correo.com",
                            "grupo": "LICENCIATURA",
                            "rol": "USUARIO",
                        },
                    )
                ],
            ),
            204: OpenApiResponse(description="Cuenta eliminada"),
            400: OpenApiResponse(
                response=inline_serializer(
                    name="ErrorPerfil",
                    fields={"email": serializers.ListField(child=serializers.CharField())},
                ),
                examples=[
                    OpenApiExample(
                        "Error validacion",
                        value={"email": ["Formato de email invalido"]},
                    )
                ],
            ),
            401: OpenApiResponse(
                response=ErrorDetalleSerializer,
                examples=[
                    OpenApiExample(
                        "Sin credenciales",
                        value={"detail": "Authentication credentials were not provided."},
                    )
                ],
            ),
        },
        examples=[
            OpenApiExample(
                "Actualizar perfil",
                value={"nombre": "Ana Lopez Garcia", "contrasena": "nuevaClave123"},
                request_only=True,
            )
        ],
    )
    @action(detail=False, methods=["get", "patch", "delete"], url_path="mi-perfil")
    def mi_perfil(self, request):
        usuario = request.user
        if request.method == "GET":
            return Response(UsuarioLecturaSerializer(usuario).data)
        if request.method == "PATCH":
            serializer = UsuarioPerfilSerializer(usuario, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(UsuarioLecturaSerializer(usuario).data)
        usuario.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
