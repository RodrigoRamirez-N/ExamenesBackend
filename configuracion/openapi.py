from drf_spectacular.extensions import OpenApiAuthenticationExtension


class TokenAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = "rest_framework.authentication.TokenAuthentication"
    name = "TokenAuth"

    def get_security_definition(self, auto_schema):
        return {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "Token de acceso. Formato: Token <token>",
        }
