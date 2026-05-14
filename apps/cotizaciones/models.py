from django.db import models

from apps.catalogo.models import Producto


class SolicitudCotizacion(models.Model):
    ESTADO_CHOICES = [
        ("pendiente", "Pendiente"),
        ("en_revision", "En revisión"),
        ("enviada", "Cotización enviada"),
        ("cerrada", "Cerrada"),
        ("descartada", "Descartada"),
    ]
    TIPO_CLIENTE = [
        ("persona", "Persona natural"),
        ("empresa", "Empresa"),
    ]

    codigo = models.CharField(max_length=20, unique=True, blank=True)
    tipo_cliente = models.CharField(
        max_length=10, choices=TIPO_CLIENTE, default="empresa"
    )
    razon_social = models.CharField(max_length=200, blank=True)
    ruc = models.CharField(max_length=11, blank=True)
    nombre_contacto = models.CharField(max_length=150)
    email = models.EmailField()
    telefono = models.CharField(max_length=30)
    departamento = models.CharField(max_length=80, blank=True)
    ciudad = models.CharField(max_length=80, blank=True)
    direccion = models.CharField(max_length=200, blank=True)
    mensaje = models.TextField(blank=True)

    estado = models.CharField(
        max_length=20, choices=ESTADO_CHOICES, default="pendiente"
    )
    nota_interna = models.TextField(blank=True)

    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-creado"]
        verbose_name = "Solicitud de cotización"
        verbose_name_plural = "Solicitudes de cotización"

    def __str__(self):
        return f"{self.codigo or self.pk} — {self.razon_social or self.nombre_contacto}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.codigo:
            self.codigo = f"COT-{self.pk:06d}"
            super().save(update_fields=["codigo"])

    @property
    def total_items(self):
        return sum(i.cantidad for i in self.items.all())


class ItemCotizacion(models.Model):
    solicitud = models.ForeignKey(
        SolicitudCotizacion, on_delete=models.CASCADE, related_name="items"
    )
    producto = models.ForeignKey(
        Producto, on_delete=models.PROTECT, related_name="items_cotizacion"
    )
    nombre_snapshot = models.CharField(max_length=200)
    sku_snapshot = models.CharField(max_length=60)
    cantidad = models.PositiveIntegerField(default=1)
    nota = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["pk"]

    def __str__(self):
        return f"{self.cantidad} x {self.nombre_snapshot}"
