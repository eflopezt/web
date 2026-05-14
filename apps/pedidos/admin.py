from django.contrib import admin

from .models import LineaPedido, Pedido


class LineaPedidoInline(admin.TabularInline):
    model = LineaPedido
    extra = 0
    readonly_fields = ("subtotal",)
    autocomplete_fields = ("producto",)


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ("codigo", "cliente", "fecha", "estado", "total")
    list_filter = ("estado", "fecha")
    search_fields = ("codigo", "cliente__razon_social")
    autocomplete_fields = ("cliente", "cotizacion")
    readonly_fields = ("codigo", "subtotal", "igv", "total", "creado", "actualizado")
    inlines = [LineaPedidoInline]
    date_hierarchy = "fecha"
