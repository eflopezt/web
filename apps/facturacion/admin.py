from django.contrib import admin

from .models import Factura, LineaFactura, Pago


class LineaInline(admin.TabularInline):
    model = LineaFactura
    extra = 0
    readonly_fields = ("subtotal",)
    autocomplete_fields = ("producto",)


class PagoInline(admin.TabularInline):
    model = Pago
    extra = 0
    autocomplete_fields = ("registrado_por",)


@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display = ("__str__", "tipo", "cliente", "fecha_emision", "total", "estado", "estado_sunat")
    list_filter = ("tipo", "estado", "estado_sunat", "fecha_emision")
    search_fields = ("serie", "correlativo", "cliente__razon_social", "cliente__documento")
    autocomplete_fields = ("cliente", "pedido")
    readonly_fields = ("subtotal", "igv", "total", "creada", "actualizada", "hash_sunat")
    inlines = [LineaInline, PagoInline]
    date_hierarchy = "fecha_emision"


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ("factura", "fecha", "monto", "metodo")
    list_filter = ("metodo", "fecha")
    search_fields = ("factura__serie", "factura__correlativo", "referencia")
