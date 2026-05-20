from collections import Counter

from django.db.models import Count, Sum

from examenes.models import (
    Arquetipo,
    ExamenPresentado,
    ExamenPresentadoRespuesta,
    JungResultado,
    TipoExamen,
    VarkResultado,
)


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


def resumir_resultado_vark(examenes_presentados):
    resumen = (
        examenes_presentados.filter(
            examen__tipo=TipoExamen.VARK,
            resultado_vark__isnull=False,
        )
        .aggregate(
            total=Count("examen_presentado_id"),
            v=Sum("resultado_vark__v"),
            a=Sum("resultado_vark__a"),
            r=Sum("resultado_vark__r"),
            k=Sum("resultado_vark__k"),
        )
    )
    total = resumen.get("total") or 0
    v = resumen.get("v") or 0
    a = resumen.get("a") or 0
    r = resumen.get("r") or 0
    k = resumen.get("k") or 0
    if total:
        codigo_arquetipo = _codigo_vark({"V": v, "A": a, "R": r, "K": k})
        arquetipo = _obtener_arquetipo(codigo_arquetipo)
    else:
        arquetipo = None
    return {"v": v, "a": a, "r": r, "k": k, "arquetipo": arquetipo}


def resumir_resultado_jung(examenes_presentados):
    resumen = (
        examenes_presentados.filter(
            examen__tipo=TipoExamen.JUNG,
            resultado_jung__isnull=False,
        )
        .aggregate(
            total=Count("examen_presentado_id"),
            i_count=Sum("resultado_jung__i_count"),
            e_count=Sum("resultado_jung__e_count"),
            n_count=Sum("resultado_jung__n_count"),
            s_count=Sum("resultado_jung__s_count"),
            t_count=Sum("resultado_jung__t_count"),
            f_count=Sum("resultado_jung__f_count"),
            j_count=Sum("resultado_jung__j_count"),
            p_count=Sum("resultado_jung__p_count"),
        )
    )
    total = resumen.get("total") or 0
    i_count = resumen.get("i_count") or 0
    e_count = resumen.get("e_count") or 0
    n_count = resumen.get("n_count") or 0
    s_count = resumen.get("s_count") or 0
    t_count = resumen.get("t_count") or 0
    f_count = resumen.get("f_count") or 0
    j_count = resumen.get("j_count") or 0
    p_count = resumen.get("p_count") or 0
    if total:
        tipo_personalidad = "".join(
            [
                "E" if e_count >= i_count else "I",
                "S" if s_count >= n_count else "N",
                "T" if t_count >= f_count else "F",
                "J" if j_count >= p_count else "P",
            ]
        )
        arquetipo = _obtener_arquetipo(tipo_personalidad)
    else:
        tipo_personalidad = None
        arquetipo = None
    return {
        "i_count": i_count,
        "e_count": e_count,
        "n_count": n_count,
        "s_count": s_count,
        "t_count": t_count,
        "f_count": f_count,
        "j_count": j_count,
        "p_count": p_count,
        "tipo_personalidad": tipo_personalidad,
        "arquetipo": arquetipo,
    }
