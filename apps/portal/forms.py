from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from apps.clientes.models import Cliente

User = get_user_model()


class RegistroClienteForm(UserCreationForm):
    razon_social = forms.CharField(label="Razón social / Nombre", max_length=200)
    documento = forms.CharField(label="RUC o DNI", required=False, max_length=20)
    tipo = forms.ChoiceField(choices=Cliente.TIPO_CHOICES, initial="empresa")
    telefono = forms.CharField(required=False, max_length=30)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Ya existe un usuario con este email.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            cliente, _ = Cliente.objects.get_or_create(
                email__iexact=user.email,
                defaults={
                    "tipo": self.cleaned_data["tipo"],
                    "razon_social": self.cleaned_data["razon_social"],
                    "documento": self.cleaned_data["documento"],
                    "email": user.email,
                    "telefono": self.cleaned_data.get("telefono", ""),
                },
            )
            if not cliente.usuario_id:
                cliente.usuario = user
                cliente.save(update_fields=["usuario"])
        return user


class PerfilForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = (
            "razon_social",
            "nombre_comercial",
            "documento",
            "telefono",
            "direccion",
            "departamento",
            "ciudad",
        )
