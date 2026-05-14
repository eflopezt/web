from django.contrib import admin

from .models import ItemCotizacion, SolicitudCotizacion


class ItemInline(admin.TabularInline):
    model = ItemCotizacion
    extra = 0
    readonly_fields = ("nombre_snapshot", "sku_snapshot")
    autocomplete_fields = ("producto",)


@admin.register(SolicitudCotizacion)
class SolicitudCotizacionAdmin(admin.ModelAdmin):
    list_display = (
        "codigo",
        "razon_social",
        "nombre_contacto",
        "email",
        "telefono",
        "estado",
        "creado",
    )
    list_filter = ("estado", "tipo_cliente", "creado")
    search_fields = (
        "codigo",
        "razon_social",
        "ruc",
        "nombre_contacto",
        "email",
        "telefono",
    )
    readonly_fields = ("codigo", "creado", "actualizado")
    inlines = [ItemInline]
    list_editable = ("estado",)
    date_hierarchy = "creado"
