from pathlib import Path

from django.core.management.base import BaseCommand

from examenes.models import Arquetipo


class Command(BaseCommand):
    help = "Importa arquetipos desde arquetipos.md"

    def add_arguments(self, parser):
        parser.add_argument(
            "--ruta",
            default="arquetipos.md",
            help="Ruta del archivo arquetipos.md",
        )
        parser.add_argument(
            "--forzar",
            action="store_true",
            help="Elimina todos los arquetipos antes de importar",
        )

    def handle(self, *args, **options):
        ruta = Path(options["ruta"])
        if not ruta.exists():
            self.stderr.write("No se encontro el archivo de arquetipos")
            return
        if options["forzar"]:
            Arquetipo.objects.all().delete()
        texto = ruta.read_text(encoding="utf-8")
        secciones = self._separar_secciones(texto)
        total = 0
        for filas in secciones.values():
            for codigo, nombre, descripcion in self._parsear_tabla(filas):
                Arquetipo.objects.update_or_create(
                    codigo=codigo,
                    defaults={"nombre": nombre, "descripcion": descripcion},
                )
                total += 1
        self.stdout.write(f"Arquetipos importados: {total}")

    def _separar_secciones(self, texto: str):
        secciones = {"jung": [], "vark": []}
        seccion_actual = None
        for linea in texto.splitlines():
            linea = linea.strip()
            if linea.startswith("# "):
                if "personalidad" in linea.lower():
                    seccion_actual = "jung"
                elif "aprendizaje" in linea.lower() or "vark" in linea.lower():
                    seccion_actual = "vark"
                else:
                    seccion_actual = None
                continue
            if seccion_actual:
                secciones[seccion_actual].append(linea)
        return secciones

    def _parsear_tabla(self, lineas):
        for linea in lineas:
            linea = linea.strip()
            if not linea.startswith("|"):
                continue
            if set(linea.replace("|", "").strip()) <= {"-", ":", " "}:
                continue
            partes = [parte.strip() for parte in linea.strip("|").split("|")]
            if len(partes) < 3:
                continue
            codigo, nombre, descripcion = partes[0], partes[1], partes[2]
            if codigo.lower() == "codigo":
                continue
            yield codigo, nombre, descripcion
