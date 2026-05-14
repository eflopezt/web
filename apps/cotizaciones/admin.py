from django.contrib import admin

from .models import Cotizacion, ItemSolicitud, LineaCotizacion, SolicitudCotizacion


class ItemSolicitudInline(admin.TabularInline):
    model = ItemSolicitud
    extra = 0
    readonly_fields = ("nombre_snapshot", "sku_snapshot")
    autocomplete_fields = ("producto",)


@admin.register(SolicitudCotizacion)
class SolicitudCotizacionAdmin(admin.ModelAdmin):
    list_display = ("codigo", "razon_social", "nombre_contacto", "email", "telefono", "estado", "creado")
    list_filter = ("estado", "tipo_cliente", "creado")
    search_fields = ("codigo", "razon_social", "ruc", "nombre_contacto", "email", "telefono")
    readonly_fields = ("codigo", "creado", "actualizado")
    inlines = [ItemSolicitudInline]
    list_editable = ("estado",)
    date_hierarchy = "creado"
    autocomplete_fields = ("cliente",)


class LineaCotizacionInline(admin.TabularInline):
    model = LineaCotizacion
    extra = 0
    readonly_fields = ("subtotal",)
    autocomplete_fields = ("producto",)


@admin.register(Cotizacion)
class CotizacionAdmin(admin.ModelAdmin):
    list_display = ("codigo", "cliente", "fecha_emision", "fecha_vencimiento", "total", "estado")
    list_filter = ("estado", "fecha_emision", "moneda")
    search_fields = ("codigo", "cliente__razon_social", "cliente__documento")
    readonly_fields = ("codigo", "subtotal", "igv", "total", "creada", "actualizada", "fecha_vencimiento")
    inlines = [LineaCotizacionInline]
    autocomplete_fields = ("cliente", "solicitud")
    date_hierarchy = "fecha_emision"

    actions = ["recalcular_totales"]

    @admin.action(description="Recalcular totales")
    def recalcular_totales(self, request, queryset):
        for cot in queryset:
            cot.recalcular_totales()
        self.message_user(request, f"Recalculadas {queryset.count()} cotizaciones.")
