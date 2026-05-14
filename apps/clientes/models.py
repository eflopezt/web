from django.conf import settings
from django.db import models


class Cliente(models.Model):
    TIPO_CHOICES = [("empresa", "Empresa"), ("persona", "Persona natural")]

    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default="empresa")
    razon_social = models.CharField(
        max_length=200,
        help_text="Razón social o nombre completo de la persona.",
    )
    nombre_comercial = models.CharField(max_length=200, blank=True)
    documento = models.CharField(
        max_length=20, help_text="RUC (11 dig) o DNI (8 dig).", blank=True
    )
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=30, blank=True)
    direccion = models.CharField(max_length=200, blank=True)
    departamento = models.CharField(max_length=80, blank=True)
    ciudad = models.CharField(max_length=80, blank=True)

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cliente",
    )

    notas = models.TextField(blank=True, help_text="Uso interno.")
    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["razon_social"]
        indexes = [
            models.Index(fields=["documento"]),
            models.Index(fields=["email"]),
        ]

    def __str__(self):
        return f"{self.razon_social}{' (' + self.documento + ')' if self.documento else ''}"

    @property
    def display_name(self):
        return self.nombre_comercial or self.razon_social
