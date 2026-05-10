from rest_framework.views import exception_handler

_TRADUCCIONES = {
    "Authentication credentials were not provided.": "No se proporcionaron credenciales de autenticacion.",
    "You do not have permission to perform this action.": "No tienes permiso para realizar esta accion.",
    "Not found.": "No encontrado.",
    "Invalid token.": "Token invalido.",
}


def manejar_excepcion(exc, context):
    respuesta = exception_handler(exc, context)
    if respuesta and isinstance(respuesta.data, dict):
        detalle = respuesta.data.get("detail")
        if isinstance(detalle, str) and detalle in _TRADUCCIONES:
            respuesta.data["detail"] = _TRADUCCIONES[detalle]
    return respuesta
