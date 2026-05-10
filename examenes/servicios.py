from collections import Counter

from examenes.models import Arquetipo, ExamenPresentado, ExamenPresentadoRespuesta, JungResultado, TipoExamen, VarkResultado


def _obtener_arquetipo(codigo: str | None) -> Arquetipo | None:
    if not codigo:
        return None
    return Arquetipo.objects.filter(codigo=codigo).first()


def _codigo_vark(contadores: dict[str, int]) -> str | None:
    if not contadores:
        return None
    ordenados = sorted(contadores.items(), key=lambda item: item[1], reverse=True)
    if len(ordenados) > 1 and (ordenados[0][1] - ordenados[1][1]) <= 2:
        return f"{ordenados[0][0]}-{ordenados[1][0]}"
    return ordenados[0][0]


def calcular_resultado_vark(examen_presentado: ExamenPresentado) -> VarkResultado:
    respuestas = ExamenPresentadoRespuesta.objects.filter(
        examen_presentado=examen_presentado
    ).select_related("respuesta")
    contadores = Counter({"V": 0, "A": 0, "R": 0, "K": 0})
    for item in respuestas:
        codigo = item.respuesta.codigo
        if codigo in contadores:
            contadores[codigo] += item.valor
    codigo_arquetipo = _codigo_vark(contadores)
    arquetipo = _obtener_arquetipo(codigo_arquetipo)
    resultado, _ = VarkResultado.objects.update_or_create(
        examen_presentado=examen_presentado,
        defaults={
            "v": contadores["V"],
            "a": contadores["A"],
            "r": contadores["R"],
            "k": contadores["K"],
            "arquetipo": arquetipo,
        },
    )
    return resultado


def calcular_resultado_jung(examen_presentado: ExamenPresentado) -> JungResultado:
    respuestas = ExamenPresentadoRespuesta.objects.filter(
        examen_presentado=examen_presentado
    ).select_related("respuesta")
    contadores = Counter({"E": 0, "I": 0, "S": 0, "N": 0, "T": 0, "F": 0, "J": 0, "P": 0})
    for item in respuestas:
        codigo = item.respuesta.codigo
        if codigo in contadores:
            contadores[codigo] += item.valor
    tipo_personalidad = "".join(
        [
            "E" if contadores["E"] >= contadores["I"] else "I",
            "S" if contadores["S"] >= contadores["N"] else "N",
            "T" if contadores["T"] >= contadores["F"] else "F",
            "J" if contadores["J"] >= contadores["P"] else "P",
        ]
    )
    arquetipo = _obtener_arquetipo(tipo_personalidad)
    resultado, _ = JungResultado.objects.update_or_create(
        examen_presentado=examen_presentado,
        defaults={
            "i_count": contadores["I"],
            "e_count": contadores["E"],
            "n_count": contadores["N"],
            "s_count": contadores["S"],
            "t_count": contadores["T"],
            "f_count": contadores["F"],
            "j_count": contadores["J"],
            "p_count": contadores["P"],
            "tipo_personalidad": tipo_personalidad,
            "arquetipo": arquetipo,
        },
    )
    return resultado


def calcular_resultado(examen_presentado: ExamenPresentado):
    if examen_presentado.examen.tipo == TipoExamen.VARK:
        return calcular_resultado_vark(examen_presentado)
    return calcular_resultado_jung(examen_presentado)
