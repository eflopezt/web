"""Admin Unfold del CMS — interfaz tipo Wix para editar el contenido del sitio.

Decisiones de diseño:
- El admin **no permite crear ni eliminar bloques**: los crea el dev con `seed_cms`.
  Así el cliente no puede romper la web cambiando una clave o borrando un texto
  que el template espera encontrar.
- Cada bloque muestra SOLO el campo de valor que corresponde a su tipo, no todos.
- Vista previa de imágenes y de texto.
- Filtros por página para que el editor encuentre rápido la sección que quiere
  cambiar ("Home", "Nosotros", "Contacto"…).
"""
from django.contrib import admin, messages
from django.utils.html import format_html, escape
from unfold.admin import ModelAdmin as UnfoldModelAdmin, TabularInline as UnfoldTabularInline

from .models import Bloque, Pagina


class BloqueInline(UnfoldTabularInline):
    model = Bloque
    extra = 0
    can_delete = False
    show_change_link = True
    fields = ("etiqueta_chip", "tipo", "valor_preview", "actualizado")
    readonly_fields = ("etiqueta_chip", "tipo", "valor_preview", "actualizado")
    ordering = ("orden", "etiqueta")

    def has_add_permission(self, request, obj=None):
        return False

    def etiqueta_chip(self, obj):
        return format_html(
            '<strong style="color:#1A4F8B">{}</strong><br>'
            '<code style="font-size:10px;color:#94A3B8">{}</code>',
            obj.etiqueta, obj.clave,
        )
    etiqueta_chip.short_description = "Campo"

    def valor_preview(self, obj):
        return _valor_preview(obj)
    valor_preview.short_description = "Valor actual"


@admin.register(Pagina)
class PaginaAdmin(UnfoldModelAdmin):
    list_display = ("titulo_chip", "bloques_count", "orden_chip")
    search_fields = ("titulo", "slug", "descripcion")
    ordering = ("orden", "titulo")
    inlines = [BloqueInline]
    fieldsets = (
        ("Identificación", {
            "fields": ("titulo", "slug", "descripcion", "icono", "orden"),
            "description": (
                "Las páginas las crea el desarrollador. Tú normalmente solo "
                "editas el contenido de los bloques que aparecen abajo."
            ),
        }),
    )

    def has_delete_permission(self, request, obj=None):
        return False

    def titulo_chip(self, obj):
        return format_html(
            '<span style="font-size:18px;margin-right:8px">📄</span>'
            '<strong style="color:#1A4F8B;font-size:14px">{}</strong>'
            '<br><small style="color:#94A3B8">/{}</small>',
            obj.titulo, obj.slug,
        )
    titulo_chip.short_description = "Página"
    titulo_chip.admin_order_field = "titulo"

    def bloques_count(self, obj):
        n = obj.bloques.count()
        color = "#3FAE2A" if n > 0 else "#94A3B8"
        return format_html(
            '<span style="background:#DCFCE7;color:{};padding:4px 12px;'
            'border-radius:12px;font-weight:700;font-size:12px">{} bloques editables</span>',
            color, n,
        )
    bloques_count.short_description = "Contenido"

    def orden_chip(self, obj):
        return format_html(
            '<code style="background:#F1F5F9;color:#475569;padding:3px 8px;'
            'border-radius:6px;font-weight:600">#{}</code>',
            obj.orden,
        )
    orden_chip.short_description = "Orden"


@admin.register(Bloque)
class BloqueAdmin(UnfoldModelAdmin):
    list_display = ("etiqueta_link", "pagina_chip", "tipo_chip", "valor_preview", "actualizado_chip")
    list_filter = (("pagina", admin.RelatedOnlyFieldListFilter), "tipo")
    search_fields = ("etiqueta", "clave", "valor_texto", "valor_textarea", "valor_html", "ayuda")
    ordering = ("pagina__orden", "orden", "etiqueta")
    list_per_page = 50

    # Bloqueamos crear y eliminar — esto es la clave del enfoque "Wix-like":
    # el cliente solo edita lo que el dev preparó.
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    # Campos según tipo — usamos JS sencillo + clases de Unfold
    def get_fieldsets(self, request, obj=None):
        if not obj:
            return ((None, {"fields": ()}),)
        # Campo valor según tipo
        if obj.tipo == "texto":
            valor_field = "valor_texto"
        elif obj.tipo == "textarea":
            valor_field = "valor_textarea"
        elif obj.tipo == "html":
            valor_field = "valor_html"
        elif obj.tipo == "imagen":
            valor_field = "valor_imagen"
        elif obj.tipo == "numero":
            valor_field = "valor_numero"
        elif obj.tipo == "url":
            valor_field = "valor_url"
        else:
            valor_field = "valor_texto"

        return (
            ("Contenido", {
                "fields": (valor_field,),
                "description": obj.ayuda or "Edita el contenido de este bloque y guarda los cambios.",
            }),
            ("Referencia (sólo lectura)", {
                "fields": ("pagina", "clave", "etiqueta", "tipo"),
                "classes": ("collapse",),
                "description": "Estos campos los gestiona el desarrollador. No los modifiques salvo que sepas lo que haces.",
            }),
        )

    def get_readonly_fields(self, request, obj=None):
        # Para no-superusuarios: TODOS los campos de identificación son readonly.
        # Para superusuarios: se pueden tocar.
        if obj and not request.user.is_superuser:
            return ("pagina", "clave", "etiqueta", "tipo")
        return ()

    # ---------- Columnas ----------
    def etiqueta_link(self, obj):
        tipo_emoji = {
            "texto": "📝", "textarea": "📄", "html": "🎨",
            "imagen": "🖼️", "numero": "🔢", "url": "🔗",
        }.get(obj.tipo, "📌")
        return format_html(
            '<span style="font-size:16px;margin-right:6px">{}</span>'
            '<strong style="color:#0F172A;font-size:13px">{}</strong>'
            '<br><code style="font-size:10px;color:#94A3B8;font-family:monospace">{}</code>',
            tipo_emoji, obj.etiqueta, obj.clave,
        )
    etiqueta_link.short_description = "Bloque"
    etiqueta_link.admin_order_field = "etiqueta"

    def pagina_chip(self, obj):
        return format_html(
            '<span style="background:#E0F2FE;color:#0369A1;padding:4px 10px;'
            'border-radius:10px;font-size:11px;font-weight:600">📄 {}</span>',
            obj.pagina.titulo,
        )
    pagina_chip.short_description = "Página"
    pagina_chip.admin_order_field = "pagina__titulo"

    def tipo_chip(self, obj):
        colors = {
            "texto":    ("#DCFCE7", "#14532D"),
            "textarea": ("#DBEAFE", "#1E3A8A"),
            "html":     ("#FEF3C7", "#78350F"),
            "imagen":   ("#FCE7F3", "#831843"),
            "numero":   ("#E0E7FF", "#3730A3"),
            "url":      ("#F1F5F9", "#475569"),
        }
        bg, fg = colors.get(obj.tipo, ("#F1F5F9", "#475569"))
        return format_html(
            '<span style="background:{};color:{};padding:3px 10px;'
            'border-radius:10px;font-size:11px;font-weight:600">{}</span>',
            bg, fg, obj.get_tipo_display(),
        )
    tipo_chip.short_description = "Tipo"
    tipo_chip.admin_order_field = "tipo"

    def valor_preview(self, obj):
        return _valor_preview(obj)
    valor_preview.short_description = "Valor actual"

    def actualizado_chip(self, obj):
        return format_html(
            '<small style="color:#94A3B8">{}</small>',
            obj.actualizado.strftime("%d/%m/%Y %H:%M"),
        )
    actualizado_chip.short_description = "Última edición"
    actualizado_chip.admin_order_field = "actualizado"

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        messages.success(
            request,
            f"✓ Bloque '{obj.etiqueta}' actualizado. Los cambios se reflejarán en el sitio en máximo 5 minutos (o vacía el caché).",
        )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _valor_preview(bloque):
    """Devuelve un preview corto del valor según tipo."""
    if bloque.tipo == "imagen":
        if bloque.valor_imagen:
            return format_html(
                '<img src="{}" style="width:80px;height:60px;'
                'object-fit:cover;border-radius:6px;border:1px solid #ddd"/>',
                bloque.valor_imagen.url,
            )
        return format_html('<span style="color:#CBD5E1">— sin imagen —</span>')

    val = bloque.valor or ""
    if bloque.tipo == "html":
        # Mostrar texto sin tags
        import re
        plain = re.sub(r"<[^>]+>", "", str(val))
        if len(plain) > 80:
            plain = plain[:80] + "…"
        return format_html(
            '<span style="color:#475569;font-style:italic">{}</span>',
            plain or "—",
        )

    val_str = str(val)
    if len(val_str) > 100:
        val_str = val_str[:100] + "…"
    if not val_str:
        return format_html('<span style="color:#CBD5E1">— vacío —</span>')
    return format_html(
        '<span style="color:#0F172A">{}</span>',
        val_str,
    )
