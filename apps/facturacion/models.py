from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.catalogo.models import Producto
from apps.clientes.models import Cliente
from apps.cotizaciones.models import IGV_PCT
from apps.pedidos.models import Pedido


class Factura(models.Model):
    TIPO_CHOICES = [
        ("factura", "Factura"),
        ("boleta", "Boleta"),
    ]
    ESTADO_CHOICES = [
        ("emitida", "Emitida"),
        ("pagada", "Pagada"),
        ("parcial", "Pago parcial"),
        ("anulada", "Anulada"),
    ]
    ESTADO_SUNAT_CHOICES = [
        ("pendiente", "Pendiente envío"),
        ("aceptada", "Aceptada por SUNAT"),
        ("rechazada", "Rechazada"),
        ("anulada", "Anulada (CDR)"),
    ]

    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default="factura")
    serie = models.CharField(max_length=4, default="F001")
    correlativo = models.PositiveIntegerField()
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name="facturas")
    pedido = models.ForeignKey(
        Pedido, on_delete=models.SET_NULL, null=True, blank=True, related_name="facturas"
    )

    fecha_emision = models.DateField(default=timezone.localdate)
    fecha_vencimiento = models.DateField(null=True, blank=True)

    moneda = models.CharField(max_length=3, default="PEN")
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    igv = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default="emitida")
    estado_sunat = models.CharField(
        max_length=12, choices=ESTADO_SUNAT_CHOICES, default="pendiente"
    )
    hash_sunat = models.CharField(max_length=80, blank=True, help_text="Hash simulado para demo.")

    observaciones = models.TextField(blank=True)

    creada_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    creada = models.DateTimeField(auto_now_add=True)
    actualizada = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-fecha_emision", "-correlativo"]
        unique_together = [("serie", "correlativo")]
        verbose_name = "Factura / Boleta"
        verbose_name_plural = "Facturas y Boletas"

    def __str__(self):
        return self.numero

    @property
    def numero(self):
        return f"{self.serie}-{self.correlativo:08d}"

    @property
    def saldo(self):
        pagado = sum((p.monto for p in self.pagos.all()), Decimal("0"))
        return (self.total - pagado).quantize(Decimal("0.01"))

    @property
    def color_estado(self):
        return {
            "emitida": "info",
            "pagada": "success",
            "parcial": "warning",
            "anulada": "error",
        }.get(self.estado, "neutral")

    def save(self, *args, **kwargs):
        if not self.correlativo:
            last = (
                Factura.objects.filter(serie=self.serie)
                .order_by("-correlativo")
                .values_list("correlativo", flat=True)
                .first()
            )
            self.correlativo = (last or 0) + 1
        super().save(*args, **kwargs)

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

    def actualizar_estado_pago(self):
        if self.estado == "anulada":
            return
        saldo = self.saldo
        if saldo <= 0:
            self.estado = "pagada"
        elif saldo < self.total:
            self.estado = "parcial"
        else:
            self.estado = "emitida"
        self.save(update_fields=["estado"])


class LineaFactura(models.Model):
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE, related_name="lineas")
    producto = models.ForeignKey(
        Producto, on_delete=models.PROTECT, related_name="lineas_factura", null=True, blank=True
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


class Pago(models.Model):
    METODO_CHOICES = [
        ("transferencia", "Transferencia bancaria"),
        ("deposito", "Depósito en cuenta"),
        ("yape", "Yape / Plin"),
        ("efectivo", "Efectivo"),
        ("tarjeta", "Tarjeta"),
        ("credito", "Letra / Crédito"),
    ]
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE, related_name="pagos")
    fecha = models.DateField(default=timezone.localdate)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    metodo = models.CharField(max_length=15, choices=METODO_CHOICES, default="transferencia")
    referencia = models.CharField(max_length=120, blank=True)
    nota = models.CharField(max_length=200, blank=True)
    registrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha", "-creado"]

    def __str__(self):
        return f"{self.factura.numero} — S/ {self.monto} ({self.get_metodo_display()})"
