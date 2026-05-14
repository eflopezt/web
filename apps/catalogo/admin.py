from django.contrib import admin

from .models import Categoria, ImagenProducto, Marca, Producto


class ImagenInline(admin.TabularInline):
    model = ImagenProducto
    extra = 1


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "orden", "activa", "creado")
    list_editable = ("orden", "activa")
    search_fields = ("nombre",)
    prepopulated_fields = {"slug": ("nombre",)}


@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "activa")
    list_editable = ("activa",)
    search_fields = ("nombre",)
    prepopulated_fields = {"slug": ("nombre",)}


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "sku",
        "categoria",
        "marca",
        "disponibilidad",
        "destacado",
        "activo",
    )
    list_editable = ("disponibilidad", "destacado", "activo")
    list_filter = ("categoria", "marca", "disponibilidad", "activo", "destacado")
    search_fields = ("nombre", "sku", "descripcion")
    prepopulated_fields = {"slug": ("nombre",)}
    inlines = [ImagenInline]
    autocomplete_fields = ("categoria", "marca")
