from django.db import models

from usuarios.models import Usuario


class TipoExamen(models.TextChoices):
    VARK = "VARK", "VARK"
    JUNG = "JUNG", "JUNG"


class EstadoExamenPresentado(models.TextChoices):
    EN_PROCESO = "EN_PROCESO", "EN_PROCESO"
    FINALIZADO = "FINALIZADO", "FINALIZADO"
    ANULADO = "ANULADO", "ANULADO"


class Examen(models.Model):
    examen_id = models.BigAutoField(primary_key=True, db_column="examen_id")
    tipo = models.CharField(max_length=10, choices=TipoExamen.choices)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)

    class Meta:
        db_table = "examen"
        verbose_name = "Examen"
        verbose_name_plural = "Examenes"

    def __str__(self) -> str:
        return f"{self.nombre} ({self.tipo})"


class Pregunta(models.Model):
    pregunta_id = models.BigAutoField(primary_key=True, db_column="pregunta_id")
    examen = models.ForeignKey(Examen, on_delete=models.CASCADE, related_name="preguntas")
    texto = models.TextField()

    class Meta:
        db_table = "pregunta"
        verbose_name = "Pregunta"
        verbose_name_plural = "Preguntas"

    def __str__(self) -> str:
        return self.texto[:60]


class Respuesta(models.Model):
    respuesta_id = models.BigAutoField(primary_key=True, db_column="respuesta_id")
    pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE, related_name="respuestas")
    texto = models.TextField()
    valor = models.IntegerField(default=1)
    codigo = models.CharField(max_length=2)

    class Meta:
        db_table = "respuesta"
        verbose_name = "Respuesta"
        verbose_name_plural = "Respuestas"

    def __str__(self) -> str:
        return self.texto[:60]


class Arquetipo(models.Model):
    arquetipo_id = models.BigAutoField(primary_key=True, db_column="arquetipo_id")
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)

    class Meta:
        db_table = "arquetipo"
        verbose_name = "Arquetipo"
        verbose_name_plural = "Arquetipos"

    def __str__(self) -> str:
        return self.codigo


class ExamenPresentado(models.Model):
    examen_presentado_id = models.BigAutoField(
        primary_key=True, db_column="examen_presentado_id"
    )
    examen = models.ForeignKey(Examen, on_delete=models.PROTECT, related_name="examenes_presentados")
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="examenes_presentados",
    )
    grupo = models.CharField(max_length=20, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(
        max_length=20, choices=EstadoExamenPresentado.choices, default=EstadoExamenPresentado.EN_PROCESO
    )

    class Meta:
        db_table = "examen_presentado"
        verbose_name = "Examen presentado"
        verbose_name_plural = "Examenes presentados"
        indexes = [
            models.Index(fields=["examen"]),
            models.Index(fields=["usuario"]),
            models.Index(fields=["grupo"]),
            models.Index(fields=["estado"]),
            models.Index(fields=["fecha_creacion"]),
        ]

    def __str__(self) -> str:
        return f"{self.examen_id} - {self.examen_presentado_id}"


class ExamenPresentadoRespuesta(models.Model):
    examen_presentado_respuesta_id = models.BigAutoField(
        primary_key=True, db_column="examen_presentado_respuesta_id"
    )
    examen_presentado = models.ForeignKey(
        ExamenPresentado,
        on_delete=models.CASCADE,
        related_name="respuestas",
    )
    pregunta = models.ForeignKey(Pregunta, on_delete=models.PROTECT)
    respuesta = models.ForeignKey(Respuesta, on_delete=models.PROTECT)
    valor = models.IntegerField()

    class Meta:
        db_table = "examen_presentado_respuesta"
        verbose_name = "Examen presentado respuesta"
        verbose_name_plural = "Examenes presentados respuestas"
        constraints = [
            models.UniqueConstraint(
                fields=["examen_presentado", "pregunta"],
                name="uq_examen_presentado_pregunta",
            )
        ]

    def __str__(self) -> str:
        return f"{self.examen_presentado_id} - {self.pregunta_id}"


class VarkResultado(models.Model):
    examen_presentado = models.OneToOneField(
        ExamenPresentado,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="resultado_vark",
        db_column="examen_presentado_id",
    )
    v = models.IntegerField(default=0)
    a = models.IntegerField(default=0)
    r = models.IntegerField(default=0)
    k = models.IntegerField(default=0)
    arquetipo = models.ForeignKey(Arquetipo, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = "vark_resultado"
        verbose_name = "VARK resultado"
        verbose_name_plural = "VARK resultados"


class JungResultado(models.Model):
    examen_presentado = models.OneToOneField(
        ExamenPresentado,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="resultado_jung",
        db_column="examen_presentado_id",
    )
    i_count = models.IntegerField(default=0)
    e_count = models.IntegerField(default=0)
    n_count = models.IntegerField(default=0)
    s_count = models.IntegerField(default=0)
    t_count = models.IntegerField(default=0)
    f_count = models.IntegerField(default=0)
    j_count = models.IntegerField(default=0)
    p_count = models.IntegerField(default=0)
    tipo_personalidad = models.CharField(max_length=4)
    arquetipo = models.ForeignKey(Arquetipo, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = "jung_resultado"
        verbose_name = "Jung resultado"
        verbose_name_plural = "Jung resultados"
