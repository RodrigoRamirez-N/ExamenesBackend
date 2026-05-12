from rest_framework import serializers

from examenes.models import (
    Arquetipo,
    Examen,
    ExamenPresentado,
    JungResultado,
    Pregunta,
    Respuesta,
    VarkResultado,
)


class RespuestaLecturaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Respuesta
        fields = ("respuesta_id", "texto")
        read_only_fields = fields


class PreguntaLecturaSerializer(serializers.ModelSerializer):
    respuestas = RespuestaLecturaSerializer(many=True, read_only=True)

    class Meta:
        model = Pregunta
        fields = ("pregunta_id", "texto", "respuestas")
        read_only_fields = fields


class ExamenLecturaSerializer(serializers.ModelSerializer):
    preguntas = PreguntaLecturaSerializer(many=True, read_only=True)

    class Meta:
        model = Examen
        fields = ("examen_id", "tipo", "nombre", "descripcion", "preguntas")
        read_only_fields = fields


class ExamenLecturaResumenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Examen
        fields = ("examen_id", "tipo", "nombre", "descripcion")
        read_only_fields = fields


class ExamenPresentadoResumenSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamenPresentado
        fields = (
            "examen_presentado_id",
            "examen_id",
            "usuario_id",
            "grupo",
            "fecha_creacion",
            "estado",
        )
        read_only_fields = fields


class RespuestaEnvioSerializer(serializers.Serializer):
    pregunta_id = serializers.IntegerField()
    respuesta_id = serializers.IntegerField()


class ExamenPresentadoEnvioSerializer(serializers.Serializer):
    examen_id = serializers.IntegerField()
    tipo = serializers.CharField(required=False)
    nombre = serializers.CharField(required=False)
    descripcion = serializers.CharField(required=False, allow_blank=True)
    preguntas = RespuestaEnvioSerializer(many=True)

    def validate_preguntas(self, value):
        ids_pregunta = [item["pregunta_id"] for item in value]
        if len(ids_pregunta) != len(set(ids_pregunta)):
            raise serializers.ValidationError("Hay preguntas duplicadas en el envio")
        return value


class ArquetipoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Arquetipo
        fields = ("arquetipo_id", "codigo", "nombre", "descripcion")
        read_only_fields = fields


class VarkResultadoSerializer(serializers.ModelSerializer):
    arquetipo = ArquetipoSerializer(read_only=True, allow_null=True)

    class Meta:
        model = VarkResultado
        fields = ("v", "a", "r", "k", "arquetipo")
        read_only_fields = fields


class JungResultadoSerializer(serializers.ModelSerializer):
    arquetipo = ArquetipoSerializer(read_only=True, allow_null=True)

    class Meta:
        model = JungResultado
        fields = (
            "i_count",
            "e_count",
            "n_count",
            "s_count",
            "t_count",
            "f_count",
            "j_count",
            "p_count",
            "tipo_personalidad",
            "arquetipo",
        )
        read_only_fields = fields


class ExamenPresentadoDetalleSerializer(serializers.ModelSerializer):
    examen = ExamenLecturaResumenSerializer(read_only=True)
    resultado_vark = VarkResultadoSerializer(read_only=True)
    resultado_jung = JungResultadoSerializer(read_only=True)

    class Meta:
        model = ExamenPresentado
        fields = (
            "examen_presentado_id",
            "examen",
            "usuario_id",
            "grupo",
            "fecha_creacion",
            "estado",
            "resultado_vark",
            "resultado_jung",
        )
        read_only_fields = fields
