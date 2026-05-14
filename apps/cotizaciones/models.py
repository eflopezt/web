from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.catalogo.models import Producto
from apps.clientes.models import Cliente


IGV_PCT = Decimal("18.00")


# ---------------------------------------------------------------------------
# Solicitud pública (lead que llega desde el sitio sin login)
# ---------------------------------------------------------------------------

class SolicitudCotizacion(models.Model):
    ESTADO_CHOICES = [
        ("pendiente", "Pendiente"),
        ("en_revision", "En revisión"),
        ("cotizada", "Cotización emitida"),
        ("cerrada", "Cerrada"),
        ("descartada", "Descartada"),
    ]
    TIPO_CLIENTE = [
        ("persona", "Persona natural"),
        ("empresa", "Empresa"),
    ]

    codigo = models.CharField(max_length=20, unique=True, blank=True)
    tipo_cliente = models.CharField(max_length=10, choices=TIPO_CLIENTE, default="empresa")
    razon_social = models.CharField(max_length=200, blank=True)
    ruc = models.CharField(max_length=11, blank=True)
    nombre_contacto = models.CharField(max_length=150)
    email = models.EmailField()
    telefono = models.CharField(max_length=30)
    departamento = models.CharField(max_length=80, blank=True)
    ciudad = models.CharField(max_length=80, blank=True)
    direccion = models.CharField(max_length=200, blank=True)
    mensaje = models.TextField(blank=True)

    cliente = models.ForeignKey(
        Cliente, on_delete=models.SET_NULL, null=True, blank=True, related_name="solicitudes"
    )
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="pendiente")
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
            self.codigo = f"SOL-{self.pk:06d}"
            super().save(update_fields=["codigo"])

    @property
    def total_items(self):
        return sum(i.cantidad for i in self.items.all())

    @property
    def color_estado(self):
        return {
            "pendiente": "warning",
            "en_revision": "info",
            "cotizada": "success",
            "cerrada": "neutral",
            "descartada": "error",
        }.get(self.estado, "neutral")


class ItemSolicitud(models.Model):
    solicitud = models.ForeignKey(
        SolicitudCotizacion, on_delete=models.CASCADE, related_name="items"
    )
    producto = models.ForeignKey(
        Producto, on_delete=models.PROTECT, related_name="items_solicitud"
    )
    nombre_snapshot = models.CharField(max_length=200)
    sku_snapshot = models.CharField(max_length=60)
    cantidad = models.PositiveIntegerField(default=1)
    nota = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["pk"]

    def __str__(self):
        return f"{self.cantidad} x {self.nombre_snapshot}"


# ---------------------------------------------------------------------------
# Cotización formal: la respuesta del vendedor con precios
# ---------------------------------------------------------------------------

class Cotizacion(models.Model):
    ESTADO_CHOICES = [
        ("borrador", "Borrador"),
        ("enviada", "Enviada al cliente"),
        ("aceptada", "Aceptada"),
        ("rechazada", "Rechazada"),
        ("vencida", "Vencida"),
    ]

    codigo = models.CharField(max_length=20, unique=True, blank=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name="cotizaciones")
    solicitud = models.ForeignKey(
        SolicitudCotizacion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cotizaciones",
    )

    fecha_emision = models.DateField(default=timezone.localdate)
    validez_dias = models.PositiveIntegerField(default=15)
    fecha_vencimiento = models.DateField(null=True, blank=True)

    moneda = models.CharField(max_length=3, default="PEN")
    incluye_igv = models.BooleanField(default=True, help_text="Si TRUE, los precios mostrados YA incluyen IGV.")
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    igv = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    observaciones = models.TextField(blank=True)
    condiciones = models.TextField(
        blank=True,
        default=(
            "1. Precios expresados en Soles peruanos (PEN) e incluyen IGV.\n"
            "2. Forma de pago: contado o crédito 15 días sujeto a evaluación.\n"
            "3. Tiempo de entrega: 2 a 5 días hábiles tras confirmación.\n"
            "4. La cotización pierde validez al vencimiento indicado."
        ),
    )

    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="borrador")
    creada_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    enviada_en = models.DateTimeField(null=True, blank=True)
    respondida_en = models.DateTimeField(null=True, blank=True)
    motivo_rechazo = models.TextField(blank=True)

    creada = models.DateTimeField(auto_now_add=True)
    actualizada = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-creada"]
        verbose_name = "Cotización"
        verbose_name_plural = "Cotizaciones"

    def __str__(self):
        return f"{self.codigo or 'sin-código'} — {self.cliente.razon_social}"

    def save(self, *args, **kwargs):
        if self.fecha_emision and self.validez_dias:
            self.fecha_vencimiento = self.fecha_emision + timedelta(days=self.validez_dias)
        super().save(*args, **kwargs)
        if not self.codigo:
            year = self.fecha_emision.year
            self.codigo = f"COT-{year}-{self.pk:05d}"
            super().save(update_fields=["codigo"])

    def recalcular_totales(self):
        sub_t = Decimal("0")
        for li in self.lineas.all():
            li.calcular_subtotal()
            li.save(update_fields=["subtotal"])
            sub_t += li.subtotal
        if self.incluye_igv:
            base = (sub_t / (Decimal("1") + IGV_PCT / Decimal("100"))).quantize(Decimal("0.01"))
            self.igv = (sub_t - base).quantize(Decimal("0.01"))
            self.subtotal = base
            self.total = sub_t.quantize(Decimal("0.01"))
        else:
            self.subtotal = sub_t.quantize(Decimal("0.01"))
            self.igv = (sub_t * IGV_PCT / Decimal("100")).quantize(Decimal("0.01"))
            self.total = (self.subtotal + self.igv).quantize(Decimal("0.01"))
        self.save(update_fields=["subtotal", "igv", "total"])

    @property
    def vencida(self):
        return self.fecha_vencimiento and self.fecha_vencimiento < timezone.localdate()

    @property
    def color_estado(self):
        return {
            "borrador": "neutral",
            "enviada": "info",
            "aceptada": "success",
            "rechazada": "error",
            "vencida": "warning",
        }.get(self.estado, "neutral")


class LineaCotizacion(models.Model):
    cotizacion = models.ForeignKey(Cotizacion, on_delete=models.CASCADE, related_name="lineas")
    producto = models.ForeignKey(
        Producto, on_delete=models.PROTECT, related_name="lineas_cotizacion", null=True, blank=True
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

    def __str__(self):
        return f"{self.cantidad} {self.unidad} × {self.descripcion}"

    def calcular_subtotal(self):
        bruto = (self.cantidad * self.precio_unitario)
        dscto = bruto * (self.descuento_pct / Decimal("100"))
        self.subtotal = (bruto - dscto).quantize(Decimal("0.01"))
        return self.subtotal
