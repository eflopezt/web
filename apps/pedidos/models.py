from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.catalogo.models import Producto
from apps.clientes.models import Cliente
from apps.cotizaciones.models import Cotizacion, IGV_PCT


class Pedido(models.Model):
    ESTADO_CHOICES = [
        ("confirmado", "Confirmado"),
        ("preparando", "En preparación"),
        ("enviado", "Enviado"),
        ("entregado", "Entregado"),
        ("cancelado", "Cancelado"),
    ]

    codigo = models.CharField(max_length=20, unique=True, blank=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name="pedidos")
    cotizacion = models.ForeignKey(
        Cotizacion, on_delete=models.SET_NULL, null=True, blank=True, related_name="pedidos"
    )

    fecha = models.DateField(default=timezone.localdate)
    direccion_envio = models.CharField(max_length=300, blank=True)
    fecha_entrega_estimada = models.DateField(null=True, blank=True)
    fecha_entrega_real = models.DateField(null=True, blank=True)

    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    igv = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="confirmado")
    observaciones = models.TextField(blank=True)

    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-creado"]

    def __str__(self):
        return f"{self.codigo} — {self.cliente.razon_social}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.codigo:
            year = self.fecha.year
            self.codigo = f"PED-{year}-{self.pk:05d}"
            super().save(update_fields=["codigo"])

    def recalcular_totales(self):
        sub_t = Decimal("0")
        for li in self.lineas.all():
            li.calcular_subtotal()
            li.save(update_fields=["subtotal"])
            sub_t += li.subtotal
        base = (sub_t / (Decimal("1") + IGV_PCT / Decimal("100"))).quantize(Decimal("0.01"))
        self.igv = (sub_t - base).quantize(Decimal("0.01"))
        self.subtotal = base
        self.total = sub_t.quantize(Decimal("0.01"))
        self.save(update_fields=["subtotal", "igv", "total"])

    @property
    def color_estado(self):
        return {
            "confirmado": "info",
            "preparando": "warning",
            "enviado": "primary",
            "entregado": "success",
            "cancelado": "error",
        }.get(self.estado, "neutral")


class LineaPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="lineas")
    producto = models.ForeignKey(
        Producto, on_delete=models.PROTECT, related_name="lineas_pedido", null=True, blank=True
    )
    descripcion = models.CharField(max_length=300)
    sku = models.CharField(max_length=60, blank=True)
    unidad = models.CharField(max_length=20, default="UND")
    cantidad = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    descuento_pct = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["orden", "pk"]

    def calcular_subtotal(self):
        bruto = self.cantidad * self.precio_unitario
        dscto = bruto * (self.descuento_pct / Decimal("100"))
        self.subtotal = (bruto - dscto).quantize(Decimal("0.01"))
        return self.subtotal
