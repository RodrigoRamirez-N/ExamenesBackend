import re
from pathlib import Path

from django.core.management.base import BaseCommand

from examenes.models import Examen, Pregunta, Respuesta, TipoExamen


class Command(BaseCommand):
    help = "Importa preguntas y respuestas desde GuiadeTests_VARK_Personalidad.md"

    def add_arguments(self, parser):
        parser.add_argument(
            "--ruta",
            default="GuiadeTests_VARK_Personalidad.md",
            help="Ruta del archivo GuiadeTests_VARK_Personalidad.md",
        )
        parser.add_argument(
            "--forzar",
            action="store_true",
            help="Elimina preguntas y respuestas previas del examen",
        )

    def handle(self, *args, **options):
        ruta = Path(options["ruta"])
        if not ruta.exists():
            self.stderr.write("No se encontro el archivo de guia")
            return
        texto = ruta.read_text(encoding="utf-8")
        vark_preguntas = self._extraer_preguntas(
            texto,
            inicio="## PARTE 2:",
            fin="## PARTE 3:",
            opciones_regex=r"^[a-d]\)\s*(.+?)\s*\*\*\((.)\)\*\*",
        )
        jung_preguntas = self._extraer_preguntas(
            texto,
            inicio="## PARTE 3:",
            fin="## PARTE 4:",
            opciones_regex=r"^[ab]\)\s*(.+?)\s*\*\*\((.)\)\*\*",
        )
        self._cargar_examen(
            tipo=TipoExamen.VARK,
            nombre="Test VARK",
            descripcion="Estilos de aprendizaje VARK",
            preguntas=vark_preguntas,
            forzar=options["forzar"],
        )
        self._cargar_examen(
            tipo=TipoExamen.JUNG,
            nombre="Test de Personalidad Jung-Myers Briggs",
            descripcion="Personalidad Jung-Myers Briggs",
            preguntas=jung_preguntas,
            forzar=options["forzar"],
        )
        self.stdout.write("Importacion completada")

    def _extraer_preguntas(self, texto: str, inicio: str, fin: str, opciones_regex: str):
        lineas = texto.splitlines()
        en_seccion = False
        preguntas = []
        actual = None
        esperando_texto = False
        patron_pregunta = re.compile(r"^\*\*Pregunta\s+(\d+):\*\*")
        patron_opcion = re.compile(opciones_regex)
        for linea in lineas:
            linea = linea.strip()
            if not linea:
                continue
            if inicio in linea:
                en_seccion = True
                continue
            if fin in linea:
                break
            if not en_seccion:
                continue
            match_pregunta = patron_pregunta.match(linea)
            if match_pregunta:
                if actual:
                    preguntas.append(actual)
                actual = {"numero": int(match_pregunta.group(1)), "texto": "", "respuestas": []}
                esperando_texto = True
                continue
            if actual and esperando_texto:
                actual["texto"] = linea
                esperando_texto = False
                continue
            if actual:
                match_opcion = patron_opcion.match(linea)
                if match_opcion:
                    actual["respuestas"].append(
                        {"texto": match_opcion.group(1).strip(), "codigo": match_opcion.group(2).strip()}
                    )
        if actual:
            preguntas.append(actual)
        return preguntas

    def _cargar_examen(self, tipo, nombre, descripcion, preguntas, forzar: bool):
        examen, creado = Examen.objects.get_or_create(
            tipo=tipo,
            defaults={"nombre": nombre, "descripcion": descripcion},
        )
        if not creado:
            examen.nombre = nombre
            examen.descripcion = descripcion
            examen.save(update_fields=["nombre", "descripcion"])
            if not forzar and Pregunta.objects.filter(examen=examen).exists():
                self.stdout.write(
                    f"El examen {tipo} ya tiene preguntas. Usa --forzar para reemplazar."
                )
                return
        if forzar:
            Pregunta.objects.filter(examen=examen).delete()
        for pregunta_data in preguntas:
            pregunta = Pregunta.objects.create(examen=examen, texto=pregunta_data["texto"])
            respuestas = [
                Respuesta(
                    pregunta=pregunta,
                    texto=respuesta["texto"],
                    codigo=respuesta["codigo"],
                    valor=1,
                )
                for respuesta in pregunta_data["respuestas"]
            ]
            Respuesta.objects.bulk_create(respuestas)
