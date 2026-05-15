"""Admin estilo WooCommerce para el catálogo de ProClean."""
import csv
import io

from django import forms
from django.contrib import admin, messages
from django.db.models import Count, Q
from django.http import HttpResponse
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import Categoria, ImagenProducto, Marca, Producto


# ============================================================================
# INLINES
# ============================================================================
class ImagenInline(admin.TabularInline):
    model = ImagenProducto
    extra = 1
    fields = ("preview", "imagen", "alt", "orden")
    readonly_fields = ("preview",)
    ordering = ("orden",)

    def preview(self, obj):
        if obj and obj.imagen:
            return format_html(
                '<img src="{}" style="width:80px;height:80px;object-fit:cover;border-radius:6px;border:1px solid #ddd"/>',
                obj.imagen.url,
            )
        return format_html('<span style="color:#999">—</span>')

    preview.short_description = "Vista previa"


# ============================================================================
# CATEGORÍA
# ============================================================================
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nombre_link", "icono_chip", "productos_count", "orden", "activa_chip")
    list_editable = ("orden",)
    list_filter = ("activa",)
    search_fields = ("nombre", "descripcion")
    prepopulated_fields = {"slug": ("nombre",)}
    ordering = ("orden", "nombre")
    actions = ["activar", "desactivar"]
    fieldsets = (
        ("Identificación", {"fields": ("nombre", "slug", "icono")}),
        ("Contenido", {"fields": ("descripcion",)}),
        ("Visibilidad", {"fields": ("activa", "orden")}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            _productos_count=Count("producto", filter=Q(producto__activo=True))
        )

    def nombre_link(self, obj):
        return format_html(
            '<strong style="color:#1B75BC">{}</strong><br><small style="color:#999">/{}</small>',
            obj.nombre, obj.slug,
        )
    nombre_link.short_description = "Categoría"
    nombre_link.admin_order_field = "nombre"

    def icono_chip(self, obj):
        if obj.icono:
            return format_html(
                '<code style="background:#E6F3FB;color:#1A4F8B;padding:3px 8px;border-radius:4px;font-size:11px">{}</code>',
                obj.icono,
            )
        return "—"
    icono_chip.short_description = "Icono"

    def productos_count(self, obj):
        n = obj._productos_count
        url = reverse("admin:catalogo_producto_changelist") + f"?categoria__id__exact={obj.id}"
        color = "#3FAE2A" if n > 0 else "#999"
        return format_html(
            '<a href="{}" style="color:{};font-weight:600">{} productos</a>',
            url, color, n,
        )
    productos_count.short_description = "Productos activos"

    def activa_chip(self, obj):
        if obj.activa:
            return format_html('<span style="background:#DCFCE7;color:#14532D;padding:3px 10px;border-radius:12px;font-size:11px;font-weight:600">● Activa</span>')
        return format_html('<span style="background:#FEE2E2;color:#7F1D1D;padding:3px 10px;border-radius:12px;font-size:11px;font-weight:600">○ Inactiva</span>')
    activa_chip.short_description = "Estado"
    activa_chip.admin_order_field = "activa"

    @admin.action(description="Activar seleccionadas")
    def activar(self, request, queryset):
        n = queryset.update(activa=True)
        self.message_user(request, f"{n} categorías activadas.", messages.SUCCESS)

    @admin.action(description="Desactivar seleccionadas")
    def desactivar(self, request, queryset):
        n = queryset.update(activa=False)
        self.message_user(request, f"{n} categorías desactivadas.", messages.WARNING)


# ============================================================================
# MARCA
# ============================================================================
@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "productos_count", "activa_chip")
    list_filter = ("activa",)
    search_fields = ("nombre",)
    prepopulated_fields = {"slug": ("nombre",)}
    ordering = ("nombre",)
    actions = ["activar", "desactivar"]

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            _productos_count=Count("producto", filter=Q(producto__activo=True))
        )

    def productos_count(self, obj):
        n = obj._productos_count
        url = reverse("admin:catalogo_producto_changelist") + f"?marca__id__exact={obj.id}"
        color = "#3FAE2A" if n > 0 else "#999"
        return format_html(
            '<a href="{}" style="color:{};font-weight:600">{}</a>', url, color, n,
        )
    productos_count.short_description = "Productos"

    def activa_chip(self, obj):
        if obj.activa:
            return format_html('<span style="background:#DCFCE7;color:#14532D;padding:3px 10px;border-radius:12px;font-size:11px;font-weight:600">● Activa</span>')
        return format_html('<span style="background:#FEE2E2;color:#7F1D1D;padding:3px 10px;border-radius:12px;font-size:11px;font-weight:600">○ Inactiva</span>')
    activa_chip.short_description = "Estado"

    @admin.action(description="Activar seleccionadas")
    def activar(self, request, queryset):
        n = queryset.update(activa=True)
        self.message_user(request, f"{n} marcas activadas.", messages.SUCCESS)

    @admin.action(description="Desactivar seleccionadas")
    def desactivar(self, request, queryset):
        n = queryset.update(activa=False)
        self.message_user(request, f"{n} marcas desactivadas.", messages.WARNING)


# ============================================================================
# PRODUCTO — vista WooCommerce-style
# ============================================================================
class ProductoForm(forms.ModelForm):
    """Form con widgets más cómodos."""
    class Meta:
        model = Producto
        fields = "__all__"
        widgets = {
            "descripcion_corta": forms.Textarea(attrs={"rows": 2, "cols": 80}),
            "descripcion": forms.Textarea(attrs={"rows": 6, "cols": 80}),
        }


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    form = ProductoForm
    list_display = (
        "thumb",
        "nombre_link",
        "sku_chip",
        "marca",
        "categoria",
        "presentacion",
        "precio_format",
        "disponibilidad_chip",
        "destacado_chip",
        "activo_chip",
    )
    list_display_links = ("thumb", "nombre_link")
    list_editable = ()  # editamos vía acciones masivas para evitar conflictos
    list_filter = (
        ("categoria", admin.RelatedOnlyFieldListFilter),
        ("marca", admin.RelatedOnlyFieldListFilter),
        "disponibilidad",
        "destacado",
        "activo",
    )
    search_fields = ("nombre", "sku", "descripcion_corta", "descripcion", "presentacion")
    prepopulated_fields = {"slug": ("nombre",)}
    inlines = [ImagenInline]
    autocomplete_fields = ("categoria", "marca")
    save_on_top = True
    list_per_page = 30
    list_max_show_all = 500
    date_hierarchy = "creado"
    show_full_result_count = True
    actions = [
        "activar", "desactivar",
        "marcar_destacado", "quitar_destacado",
        "marcar_en_stock", "marcar_bajo_pedido", "marcar_agotado",
        "exportar_csv",
    ]
    fieldsets = (
        ("Identificación", {
            "fields": ("nombre", "slug", "sku", "categoria", "marca"),
        }),
        ("Presentación y disponibilidad", {
            "fields": ("presentacion", "disponibilidad", "destacado", "activo"),
        }),
        ("Descripciones", {
            "fields": ("descripcion_corta", "descripcion"),
        }),
        ("Imagen principal", {
            "fields": ("imagen",),
            "description": "Sube fotos secundarias abajo en la sección 'Imágenes producto'.",
        }),
        ("Comercial (uso interno)", {
            "fields": ("precio_referencia",),
            "classes": ("collapse",),
            "description": "El precio no se muestra en el sitio público; se usa en cotizaciones internas.",
        }),
    )
    readonly_fields = ()

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("categoria", "marca")

    # ---------- Columnas custom ----------
    def thumb(self, obj):
        if obj.imagen:
            return format_html(
                '<img src="{}" style="width:54px;height:54px;object-fit:cover;border-radius:6px;border:1px solid #ddd"/>',
                obj.imagen.url,
            )
        return format_html(
            '<div style="width:54px;height:54px;background:linear-gradient(135deg,#E6F3FB,#DCFCE7);border-radius:6px;border:1px solid #ddd;display:flex;align-items:center;justify-content:center;color:#1B75BC;font-weight:700;font-size:18px">PC</div>'
        )
    thumb.short_description = "📷"

    def nombre_link(self, obj):
        return format_html(
            '<strong style="color:#1A4F8B">{}</strong>',
            obj.nombre,
        )
    nombre_link.short_description = "Producto"
    nombre_link.admin_order_field = "nombre"

    def sku_chip(self, obj):
        return format_html(
            '<code style="background:#F1F5F9;color:#475569;padding:2px 8px;border-radius:4px;font-size:11px;font-family:monospace">{}</code>',
            obj.sku,
        )
    sku_chip.short_description = "SKU"
    sku_chip.admin_order_field = "sku"

    def precio_format(self, obj):
        if obj.precio_referencia:
            return format_html(
                '<span style="font-weight:600;color:#0F172A">S/ {}</span>',
                f"{obj.precio_referencia:.2f}",
            )
        return format_html('<span style="color:#999;font-style:italic">a cotizar</span>')
    precio_format.short_description = "Precio ref."
    precio_format.admin_order_field = "precio_referencia"

    def disponibilidad_chip(self, obj):
        colors = {
            "en_stock": ("#DCFCE7", "#14532D", "● En stock"),
            "bajo_pedido": ("#FEF3C7", "#78350F", "◐ Bajo pedido"),
            "agotado": ("#FEE2E2", "#7F1D1D", "○ Agotado"),
        }
        bg, fg, label = colors.get(obj.disponibilidad, ("#F1F5F9", "#475569", obj.disponibilidad))
        return format_html(
            '<span style="background:{};color:{};padding:3px 10px;border-radius:12px;font-size:11px;font-weight:600;white-space:nowrap">{}</span>',
            bg, fg, label,
        )
    disponibilidad_chip.short_description = "Stock"
    disponibilidad_chip.admin_order_field = "disponibilidad"

    def destacado_chip(self, obj):
        if obj.destacado:
            return format_html('<span style="color:#F59E0B;font-size:16px" title="Destacado">★</span>')
        return format_html('<span style="color:#CBD5E1;font-size:16px" title="No destacado">☆</span>')
    destacado_chip.short_description = "★"
    destacado_chip.admin_order_field = "destacado"

    def activo_chip(self, obj):
        if obj.activo:
            return format_html('<span style="color:#3FAE2A;font-size:16px" title="Activo">✓</span>')
        return format_html('<span style="color:#DC2626;font-size:16px" title="Inactivo">✗</span>')
    activo_chip.short_description = "✓"
    activo_chip.admin_order_field = "activo"

    # ---------- Acciones masivas ----------
    @admin.action(description="✓ Activar seleccionados")
    def activar(self, request, queryset):
        n = queryset.update(activo=True)
        self.message_user(request, f"{n} productos activados.", messages.SUCCESS)

    @admin.action(description="✗ Desactivar seleccionados (quitar del sitio)")
    def desactivar(self, request, queryset):
        n = queryset.update(activo=False)
        self.message_user(request, f"{n} productos desactivados.", messages.WARNING)

    @admin.action(description="★ Marcar como destacados")
    def marcar_destacado(self, request, queryset):
        n = queryset.update(destacado=True)
        self.message_user(request, f"{n} productos marcados como destacados.", messages.SUCCESS)

    @admin.action(description="☆ Quitar destacado")
    def quitar_destacado(self, request, queryset):
        n = queryset.update(destacado=False)
        self.message_user(request, f"{n} productos quitados de destacados.", messages.INFO)

    @admin.action(description="● Marcar disponibilidad: En stock")
    def marcar_en_stock(self, request, queryset):
        n = queryset.update(disponibilidad="en_stock")
        self.message_user(request, f"{n} productos marcados En stock.", messages.SUCCESS)

    @admin.action(description="◐ Marcar disponibilidad: Bajo pedido")
    def marcar_bajo_pedido(self, request, queryset):
        n = queryset.update(disponibilidad="bajo_pedido")
        self.message_user(request, f"{n} productos marcados Bajo pedido.", messages.WARNING)

    @admin.action(description="○ Marcar disponibilidad: Agotado")
    def marcar_agotado(self, request, queryset):
        n = queryset.update(disponibilidad="agotado")
        self.message_user(request, f"{n} productos marcados como Agotados.", messages.ERROR)

    @admin.action(description="📥 Exportar seleccionados a CSV")
    def exportar_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv; charset=utf-8-sig")
        response["Content-Disposition"] = 'attachment; filename="productos.csv"'
        writer = csv.writer(response, delimiter=";")
        writer.writerow([
            "SKU", "Nombre", "Marca", "Categoría", "Presentación",
            "Precio ref.", "Disponibilidad", "Destacado", "Activo",
            "Descripción corta",
        ])
        for p in queryset.select_related("categoria", "marca"):
            writer.writerow([
                p.sku, p.nombre,
                p.marca.nombre if p.marca else "",
                p.categoria.nombre if p.categoria else "",
                p.presentacion or "",
                f"{p.precio_referencia:.2f}" if p.precio_referencia else "",
                p.get_disponibilidad_display(),
                "Sí" if p.destacado else "No",
                "Sí" if p.activo else "No",
                p.descripcion_corta or "",
            ])
        self.message_user(request, f"{queryset.count()} productos exportados.", messages.SUCCESS)
        return response


# ============================================================================
# IMAGEN PRODUCTO (también accesible directamente)
# ============================================================================
@admin.register(ImagenProducto)
class ImagenProductoAdmin(admin.ModelAdmin):
    list_display = ("preview", "producto", "alt", "orden")
    list_filter = ("producto__categoria",)
    search_fields = ("producto__nombre", "alt")
    autocomplete_fields = ("producto",)
    list_per_page = 50

    def preview(self, obj):
        if obj.imagen:
            return format_html(
                '<img src="{}" style="width:60px;height:60px;object-fit:cover;border-radius:6px;border:1px solid #ddd"/>',
                obj.imagen.url,
            )
        return "—"
    preview.short_description = "📷"
