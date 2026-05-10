from datetime import datetime

from django.db import transaction
from django.db.models import Count, Q
from rest_framework import serializers, status, viewsets
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

from examenes.models import (
    EstadoExamenPresentado,
    Examen,
    ExamenPresentado,
    ExamenPresentadoRespuesta,
    Respuesta,
    TipoExamen,
)
from examenes.serializers import (
    ExamenLecturaSerializer,
    ExamenPresentadoDetalleSerializer,
    ExamenPresentadoEnvioSerializer,
    ExamenPresentadoResumenSerializer,
    JungResultadoSerializer,
    VarkResultadoSerializer,
)
from examenes.servicios import calcular_resultado_jung, calcular_resultado_vark
from usuarios.permissions import EsAdmin
from usuarios.models import RolUsuario


ErrorDetalleSerializer = inline_serializer(
    name="ErrorDetalle",
    fields={"detail": serializers.CharField()},
)
ErrorDetallePersonalizadoSerializer = inline_serializer(
    name="ErrorDetallePersonalizado",
    fields={"detalle": serializers.CharField()},
)
ErrorEnvioSerializer = inline_serializer(
    name="ErrorEnvio",
    fields={
        "detalle": serializers.CharField(required=False),
        "respuestas": serializers.ListField(child=serializers.CharField(), required=False),
    },
)


@extend_schema_view(
    list=extend_schema(
        auth=[],
        responses={
            200: OpenApiResponse(
                response=ExamenLecturaSerializer(many=True),
                examples=[
                    OpenApiExample(
                        "Listado examenes",
                        value=[
                            {
                                "examen_id": 1,
                                "tipo": "VARK",
                                "nombre": "Test VARK",
                                "descripcion": "Estilos de aprendizaje VARK",
                                "preguntas": [
                                    {
                                        "pregunta_id": 1,
                                        "texto": "Estas ayudando a alguien a llegar...",
                                        "respuestas": [
                                            {"respuesta_id": 1, "texto": "Le dibuja un mapa..."}
                                        ],
                                    }
                                ],
                            }
                        ],
                    )
                ],
            )
        }
    ),
    retrieve=extend_schema(
        auth=[],
        responses={
            200: OpenApiResponse(
                response=ExamenLecturaSerializer,
                examples=[
                    OpenApiExample(
                        "Detalle examen",
                        value={
                            "examen_id": 1,
                            "tipo": "VARK",
                            "nombre": "Test VARK",
                            "descripcion": "Estilos de aprendizaje VARK",
                            "preguntas": [],
                        },
                    )
                ],
            ),
            404: OpenApiResponse(
                response=ErrorDetalleSerializer,
                examples=[
                    OpenApiExample("No encontrado", value={"detail": "Not found."})
                ],
            ),
        }
    ),
)
class ExamenViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Examen.objects.all()
    serializer_class = ExamenLecturaSerializer
    permission_classes = [AllowAny]

    @action(detail=True, methods=["post"], permission_classes=[AllowAny])
    @extend_schema(
        request=None,
        responses={
            201: OpenApiResponse(
                response=inline_serializer(
                    name="ExamenIniciado",
                    fields={
                        "examen_presentado": ExamenPresentadoResumenSerializer(),
                        "examen": ExamenLecturaSerializer(),
                    },
                ),
                examples=[
                    OpenApiExample(
                        "Examen iniciado",
                        value={
                            "examen_presentado": {
                                "examen_presentado_id": 10,
                                "examen_id": 1,
                                "usuario_id": 2,
                                "grupo": "LICENCIATURA",
                                "fecha_creacion": "2026-05-09T12:00:00Z",
                                "estado": "EN_PROCESO",
                            },
                            "examen": {
                                "examen_id": 1,
                                "tipo": "VARK",
                                "nombre": "Test VARK",
                                "descripcion": "Estilos de aprendizaje VARK",
                                "preguntas": [
                                    {
                                        "pregunta_id": 1,
                                        "texto": "Estas ayudando a alguien a llegar...",
                                        "respuestas": [
                                            {"respuesta_id": 1, "texto": "Le dibuja un mapa..."}
                                        ],
                                    }
                                ],
                            },
                        },
                    )
                ],
            ),
            404: OpenApiResponse(
                response=ErrorDetalleSerializer,
                examples=[
                    OpenApiExample("No encontrado", value={"detail": "Not found."})
                ],
            ),
        },
        auth=[],
    )
    def iniciar(self, request, pk=None):
        examen = self.get_object()
        usuario = request.user if request.user.is_authenticated else None
        grupo = usuario.grupo if usuario else None
        examen_presentado = ExamenPresentado.objects.create(
            examen=examen,
            usuario=usuario,
            grupo=grupo,
            estado=EstadoExamenPresentado.EN_PROCESO,
        )
        return Response(
            {
                "examen_presentado": ExamenPresentadoResumenSerializer(examen_presentado).data,
                "examen": ExamenLecturaSerializer(examen).data,
            },
            status=status.HTTP_201_CREATED,
        )


@extend_schema_view(
    list=extend_schema(
        responses={
            200: OpenApiResponse(
                response=ExamenPresentadoDetalleSerializer(many=True),
                examples=[
                    OpenApiExample(
                        "Listado examenes presentados",
                        value=[
                            {
                                "examen_presentado_id": 10,
                                "examen": {
                                    "examen_id": 1,
                                    "tipo": "VARK",
                                    "nombre": "Test VARK",
                                    "descripcion": "Estilos de aprendizaje VARK",
                                },
                                "usuario_id": 2,
                                "grupo": "LICENCIATURA",
                                "fecha_creacion": "2026-05-09T12:00:00Z",
                                "estado": "FINALIZADO",
                                "resultado_vark": {
                                    "v": 4,
                                    "a": 6,
                                    "r": 2,
                                    "k": 4,
                                    "arquetipo": {
                                        "arquetipo_id": 1,
                                        "codigo": "A",
                                        "nombre": "Aural / Auditivo",
                                        "descripcion": "Aprende mejor escuchando...",
                                    },
                                },
                                "resultado_jung": None,
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
                response=ExamenPresentadoDetalleSerializer,
                examples=[
                    OpenApiExample(
                        "Detalle examen presentado",
                        value={
                            "examen_presentado_id": 10,
                            "examen": {
                                "examen_id": 1,
                                "tipo": "VARK",
                                "nombre": "Test VARK",
                                "descripcion": "Estilos de aprendizaje VARK",
                            },
                            "usuario_id": 2,
                            "grupo": "LICENCIATURA",
                            "fecha_creacion": "2026-05-09T12:00:00Z",
                            "estado": "FINALIZADO",
                            "resultado_vark": {
                                "v": 4,
                                "a": 6,
                                "r": 2,
                                "k": 4,
                                "arquetipo": {
                                    "arquetipo_id": 1,
                                    "codigo": "A",
                                    "nombre": "Aural / Auditivo",
                                    "descripcion": "Aprende mejor escuchando...",
                                },
                            },
                            "resultado_jung": None,
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
                    OpenApiExample("No encontrado", value={"detail": "Not found."})
                ],
            ),
        }
    ),
)
class ExamenPresentadoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ExamenPresentado.objects.select_related("examen", "usuario")
    serializer_class = ExamenPresentadoDetalleSerializer

    def get_permissions(self):
        if self.action == "enviar":
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset()
        usuario = self.request.user
        if usuario.is_authenticated and usuario.rol == RolUsuario.ADMIN:
            return queryset
        if usuario.is_authenticated:
            return queryset.filter(usuario=usuario)
        return queryset.none()

    @action(detail=True, methods=["post"], permission_classes=[AllowAny])
    @extend_schema(
        request=ExamenPresentadoEnvioSerializer,
        responses={
            200: OpenApiResponse(
                response=inline_serializer(
                    name="ExamenEnviado",
                    fields={
                        "examen_presentado": ExamenPresentadoResumenSerializer(),
                        "resultado": serializers.JSONField(),
                    },
                ),
                examples=[
                    OpenApiExample(
                        "Resultado VARK",
                        value={
                            "examen_presentado": {
                                "examen_presentado_id": 10,
                                "examen_id": 1,
                                "usuario_id": 2,
                                "grupo": "LICENCIATURA",
                                "fecha_creacion": "2026-05-09T12:00:00Z",
                                "estado": "FINALIZADO",
                            },
                            "resultado": {
                                "v": 4,
                                "a": 6,
                                "r": 2,
                                "k": 4,
                                "arquetipo": {
                                    "arquetipo_id": 1,
                                    "codigo": "A",
                                    "nombre": "Aural / Auditivo",
                                    "descripcion": "Aprende mejor escuchando...",
                                },
                            },
                        },
                    ),
                    OpenApiExample(
                        "Resultado JUNG",
                        value={
                            "examen_presentado": {
                                "examen_presentado_id": 20,
                                "examen_id": 2,
                                "usuario_id": None,
                                "grupo": None,
                                "fecha_creacion": "2026-05-09T12:00:00Z",
                                "estado": "FINALIZADO",
                            },
                            "resultado": {
                                "i_count": 3,
                                "e_count": 5,
                                "n_count": 6,
                                "s_count": 2,
                                "t_count": 4,
                                "f_count": 4,
                                "j_count": 5,
                                "p_count": 3,
                                "tipo_personalidad": "ENFJ",
                                "arquetipo": {
                                    "arquetipo_id": 5,
                                    "codigo": "ENFJ",
                                    "nombre": "El Profesor",
                                    "descripcion": "Carismatico, atento...",
                                },
                            },
                        },
                    ),
                ],
            ),
            400: OpenApiResponse(
                response=ErrorEnvioSerializer,
                examples=[
                    OpenApiExample(
                        "Estado no valido",
                        value={"detalle": "El examen no esta en estado EN_PROCESO"},
                    ),
                    OpenApiExample(
                        "Respuesta no corresponde",
                        value={"detalle": "Respuesta no corresponde al examen"},
                    ),
                    OpenApiExample(
                        "Preguntas duplicadas",
                        value={"respuestas": ["Hay preguntas duplicadas en el envio"]},
                    ),
                ],
            ),
            403: OpenApiResponse(
                response=ErrorDetallePersonalizadoSerializer,
                examples=[
                    OpenApiExample(
                        "Sin permiso",
                        value={"detalle": "No tienes permiso para enviar este examen"},
                    )
                ],
            ),
            404: OpenApiResponse(
                response=ErrorDetallePersonalizadoSerializer,
                examples=[
                    OpenApiExample(
                        "No encontrado",
                        value={"detalle": "Examen presentado no encontrado"},
                    )
                ],
            ),
        },
        examples=[
            OpenApiExample(
                "Envio de respuestas",
                value={
                    "respuestas": [
                        {"pregunta_id": 1, "respuesta_id": 2},
                        {"pregunta_id": 2, "respuesta_id": 8},
                    ]
                },
                request_only=True,
            )
        ],
        auth=[],
    )
    def enviar(self, request, pk=None):
        try:
            examen_presentado = ExamenPresentado.objects.select_related("examen", "usuario").get(
                examen_presentado_id=pk
            )
        except ExamenPresentado.DoesNotExist:
            return Response(
                {"detalle": "Examen presentado no encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )
        if examen_presentado.estado != EstadoExamenPresentado.EN_PROCESO:
            return Response(
                {"detalle": "El examen no esta en estado EN_PROCESO"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if examen_presentado.usuario_id:
            if not request.user.is_authenticated or request.user != examen_presentado.usuario:
                return Response(
                    {"detalle": "No tienes permiso para enviar este examen"},
                    status=status.HTTP_403_FORBIDDEN,
                )
        serializer = ExamenPresentadoEnvioSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        respuestas_data = serializer.validated_data["respuestas"]
        respuesta_ids = [item["respuesta_id"] for item in respuestas_data]
        respuestas = Respuesta.objects.filter(respuesta_id__in=respuesta_ids).select_related("pregunta")
        if respuestas.count() != len(respuesta_ids):
            return Response(
                {"detalle": "Hay respuestas que no existen"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        respuestas_por_id = {respuesta.respuesta_id: respuesta for respuesta in respuestas}
        registros = []
        for item in respuestas_data:
            respuesta = respuestas_por_id[item["respuesta_id"]]
            if respuesta.pregunta_id != item["pregunta_id"]:
                return Response(
                    {"detalle": "Respuesta no corresponde a la pregunta"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if respuesta.pregunta.examen_id != examen_presentado.examen_id:
                return Response(
                    {"detalle": "Respuesta no corresponde al examen"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            registros.append(
                ExamenPresentadoRespuesta(
                    examen_presentado=examen_presentado,
                    pregunta_id=item["pregunta_id"],
                    respuesta=respuesta,
                    valor=respuesta.valor,
                )
            )
        with transaction.atomic():
            ExamenPresentadoRespuesta.objects.filter(examen_presentado=examen_presentado).delete()
            ExamenPresentadoRespuesta.objects.bulk_create(registros)
            if examen_presentado.examen.tipo == TipoExamen.VARK:
                resultado = calcular_resultado_vark(examen_presentado)
                resultado_serializado = VarkResultadoSerializer(resultado).data
            else:
                resultado = calcular_resultado_jung(examen_presentado)
                resultado_serializado = JungResultadoSerializer(resultado).data
            examen_presentado.estado = EstadoExamenPresentado.FINALIZADO
            examen_presentado.save(update_fields=["estado"])
        return Response(
            {
                "examen_presentado": ExamenPresentadoResumenSerializer(examen_presentado).data,
                "resultado": resultado_serializado,
            }
        )


class ResumenAnaliticaAPIView(APIView):
    permission_classes = [EsAdmin]

    @extend_schema(
        responses={
            200: OpenApiResponse(
                response=inline_serializer(
                    name="ResumenAnalitica",
                    fields={
                        "total": serializers.IntegerField(),
                        "por_estado": serializers.JSONField(),
                        "por_grupo": serializers.JSONField(),
                        "por_tipo": serializers.JSONField(),
                        "por_rol": serializers.JSONField(),
                        "arquetipos_vark": serializers.JSONField(),
                        "arquetipos_jung": serializers.JSONField(),
                    },
                ),
                examples=[
                    OpenApiExample(
                        "Resumen",
                        value={
                            "total": 10,
                            "por_estado": [{"estado": "FINALIZADO", "total": 7}],
                            "por_grupo": [{"grupo": "LICENCIATURA", "total": 5}],
                            "por_tipo": [{"examen__tipo": "VARK", "total": 6}],
                            "por_rol": [{"usuario__rol": "USUARIO", "total": 8}],
                            "arquetipos_vark": [
                                {"resultado_vark__arquetipo__codigo": "A", "total": 3}
                            ],
                            "arquetipos_jung": [
                                {"resultado_jung__arquetipo__codigo": "INTJ", "total": 2}
                            ],
                        },
                    )
                ],
            ),
            400: OpenApiResponse(
                response=ErrorDetallePersonalizadoSerializer,
                examples=[
                    OpenApiExample(
                        "Fecha invalida",
                        value={"detalle": "fecha_inicio debe ser YYYY-MM-DD"},
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
    )
    def get(self, request):
        filtros = self._aplicar_filtros(request)
        if isinstance(filtros, Response):
            return filtros
        queryset = filtros
        total = queryset.count()
        por_estado = list(
            queryset.values("estado").annotate(total=Count("examen_presentado_id")).order_by("estado")
        )
        por_grupo = list(
            queryset.values("grupo").annotate(total=Count("examen_presentado_id")).order_by("grupo")
        )
        por_tipo = list(
            queryset.values("examen__tipo").annotate(total=Count("examen_presentado_id")).order_by("examen__tipo")
        )
        por_rol = list(
            queryset.values("usuario__rol").annotate(total=Count("examen_presentado_id")).order_by("usuario__rol")
        )
        arquetipos_vark = list(
            queryset.filter(examen__tipo=TipoExamen.VARK)
            .values("resultado_vark__arquetipo__codigo")
            .annotate(total=Count("examen_presentado_id"))
            .order_by("resultado_vark__arquetipo__codigo")
        )
        arquetipos_jung = list(
            queryset.filter(examen__tipo=TipoExamen.JUNG)
            .values("resultado_jung__arquetipo__codigo")
            .annotate(total=Count("examen_presentado_id"))
            .order_by("resultado_jung__arquetipo__codigo")
        )
        return Response(
            {
                "total": total,
                "por_estado": por_estado,
                "por_grupo": por_grupo,
                "por_tipo": por_tipo,
                "por_rol": por_rol,
                "arquetipos_vark": arquetipos_vark,
                "arquetipos_jung": arquetipos_jung,
            }
        )

    def _aplicar_filtros(self, request):
        queryset = ExamenPresentado.objects.select_related("examen", "usuario")
        exam_id = request.query_params.get("examen_id")
        usuario_id = request.query_params.get("usuario_id")
        grupo = request.query_params.get("grupo")
        tipo = request.query_params.get("tipo")
        rol = request.query_params.get("rol")
        estado = request.query_params.get("estado")
        arquetipo = request.query_params.get("arquetipo")
        fecha_inicio = request.query_params.get("fecha_inicio")
        fecha_fin = request.query_params.get("fecha_fin")

        if exam_id:
            queryset = queryset.filter(examen_id=exam_id)
        if usuario_id:
            queryset = queryset.filter(usuario_id=usuario_id)
        if grupo:
            queryset = queryset.filter(grupo=grupo)
        if tipo:
            queryset = queryset.filter(examen__tipo=tipo)
        if rol:
            queryset = queryset.filter(usuario__rol=rol)
        if estado:
            queryset = queryset.filter(estado=estado)
        if arquetipo:
            queryset = queryset.filter(
                Q(resultado_vark__arquetipo__codigo=arquetipo)
                | Q(resultado_jung__arquetipo__codigo=arquetipo)
            )
        if fecha_inicio:
            try:
                fecha_inicio_dt = datetime.strptime(fecha_inicio, "%Y-%m-%d")
            except ValueError:
                return Response(
                    {"detalle": "fecha_inicio debe ser YYYY-MM-DD"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            queryset = queryset.filter(fecha_creacion__date__gte=fecha_inicio_dt.date())
        if fecha_fin:
            try:
                fecha_fin_dt = datetime.strptime(fecha_fin, "%Y-%m-%d")
            except ValueError:
                return Response(
                    {"detalle": "fecha_fin debe ser YYYY-MM-DD"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            queryset = queryset.filter(fecha_creacion__date__lte=fecha_fin_dt.date())
        return queryset
