from django.contrib.auth import authenticate
from rest_framework import serializers

from usuarios.models import RolUsuario, Usuario


class UsuarioLecturaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ("usuario_id", "nombre", "email", "grupo", "rol")
        read_only_fields = fields


class UsuarioRegistroSerializer(serializers.ModelSerializer):
    contrasena = serializers.CharField(write_only=True, min_length=8)
    rol = serializers.ChoiceField(choices=RolUsuario.choices, required=False)

    class Meta:
        model = Usuario
        fields = ("usuario_id", "nombre", "email", "contrasena", "grupo", "rol")
        read_only_fields = ("usuario_id",)

    def validate_rol(self, value: str) -> str:
        if value and value != RolUsuario.USUARIO:
            raise serializers.ValidationError("No es posible asignar rol ADMIN en registro publico")
        return value

    def create(self, validated_data):
        contrasena = validated_data.pop("contrasena")
        usuario = Usuario(**validated_data)
        usuario.set_password(contrasena)
        usuario.save()
        return usuario


class UsuarioAdminSerializer(serializers.ModelSerializer):
    contrasena = serializers.CharField(write_only=True, required=False, min_length=8)

    class Meta:
        model = Usuario
        fields = ("usuario_id", "nombre", "email", "contrasena", "grupo", "rol", "is_active")
        read_only_fields = ("usuario_id",)

    def create(self, validated_data):
        contrasena = validated_data.pop("contrasena", None)
        usuario = Usuario(**validated_data)
        if contrasena:
            usuario.set_password(contrasena)
        else:
            usuario.set_unusable_password()
        usuario.save()
        return usuario

    def update(self, instance, validated_data):
        contrasena = validated_data.pop("contrasena", None)
        for atributo, valor in validated_data.items():
            setattr(instance, atributo, valor)
        if contrasena:
            instance.set_password(contrasena)
        instance.save()
        return instance


class UsuarioPerfilSerializer(serializers.ModelSerializer):
    contrasena = serializers.CharField(write_only=True, required=False, min_length=8)

    class Meta:
        model = Usuario
        fields = ("usuario_id", "nombre", "email", "contrasena", "grupo", "rol")
        read_only_fields = ("usuario_id", "rol")

    def update(self, instance, validated_data):
        contrasena = validated_data.pop("contrasena", None)
        for atributo, valor in validated_data.items():
            setattr(instance, atributo, valor)
        if contrasena:
            instance.set_password(contrasena)
        instance.save()
        return instance


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    contrasena = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get("email")
        contrasena = attrs.get("contrasena")
        usuario = authenticate(username=email, password=contrasena)
        if not usuario:
            raise serializers.ValidationError("Credenciales invalidas")
        attrs["usuario"] = usuario
        return attrs
