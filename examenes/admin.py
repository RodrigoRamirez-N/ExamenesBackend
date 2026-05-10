from django.contrib import admin

from examenes.models import (
    Arquetipo,
    Examen,
    ExamenPresentado,
    ExamenPresentadoRespuesta,
    JungResultado,
    Pregunta,
    Respuesta,
    VarkResultado,
)


admin.site.register(Examen)
admin.site.register(Pregunta)
admin.site.register(Respuesta)
admin.site.register(ExamenPresentado)
admin.site.register(ExamenPresentadoRespuesta)
admin.site.register(VarkResultado)
admin.site.register(JungResultado)
admin.site.register(Arquetipo)
