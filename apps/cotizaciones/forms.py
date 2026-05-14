from django import forms

from .models import SolicitudCotizacion


class SolicitudCotizacionForm(forms.ModelForm):
    acepta = forms.BooleanField(
        required=True,
        label="Acepto la política de privacidad y el tratamiento de mis datos.",
    )

    class Meta:
        model = SolicitudCotizacion
        fields = [
            "tipo_cliente",
            "razon_social",
            "ruc",
            "nombre_contacto",
            "email",
            "telefono",
            "departamento",
            "ciudad",
            "direccion",
            "mensaje",
        ]
        widgets = {
            "mensaje": forms.Textarea(attrs={"rows": 4}),
        }

    def clean(self):
        cleaned = super().clean()
        tipo = cleaned.get("tipo_cliente")
        ruc = (cleaned.get("ruc") or "").strip()
        razon = (cleaned.get("razon_social") or "").strip()
        if tipo == "empresa":
            if not razon:
                self.add_error("razon_social", "Requerido para empresas.")
            if ruc and (not ruc.isdigit() or len(ruc) != 11):
                self.add_error("ruc", "El RUC debe tener 11 dígitos numéricos.")
        return cleaned
