from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from usuarios.models import Usuario


class UsuarioCreacionFormulario(forms.ModelForm):
    contrasena1 = forms.CharField(label="Contrasena", widget=forms.PasswordInput)
    contrasena2 = forms.CharField(label="Confirmar contrasena", widget=forms.PasswordInput)

    class Meta:
        model = Usuario
        fields = ("email", "nombre", "grupo", "rol")

    def clean_contrasena2(self):
        contrasena1 = self.cleaned_data.get("contrasena1")
        contrasena2 = self.cleaned_data.get("contrasena2")
        if contrasena1 and contrasena2 and contrasena1 != contrasena2:
            raise forms.ValidationError("Las contrasenas no coinciden")
        return contrasena2

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.set_password(self.cleaned_data["contrasena1"])
        if commit:
            usuario.save()
        return usuario


class UsuarioCambioFormulario(forms.ModelForm):
    password = ReadOnlyPasswordHashField(label="Contrasena")

    class Meta:
        model = Usuario
        fields = (
            "email",
            "nombre",
            "password",
            "grupo",
            "rol",
            "is_active",
            "is_staff",
        )

    def clean_password(self):
        return self.initial.get("password")
