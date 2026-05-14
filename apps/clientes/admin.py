from django.contrib import admin

from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("razon_social", "tipo", "documento", "email", "telefono", "ciudad", "activo")
    list_filter = ("tipo", "activo", "departamento")
    search_fields = ("razon_social", "nombre_comercial", "documento", "email", "telefono")
    autocomplete_fields = ("usuario",)
