"""Template tags del CMS.

Uso en templates:

    {% load cms_tags %}

    {% bloque "home_hero_titulo" %}
    {% bloque "home_hero_titulo" "Texto por defecto si el bloque no existe" %}
    {% bloque_imagen "home_hero_imagen" %}
"""
from django import template
from django.utils.safestring import mark_safe

from apps.cms.models import obtener_bloque

register = template.Library()


@register.simple_tag
def bloque(clave, default=""):
    """Devuelve el valor del bloque con esa clave.

    Para tipo `html` retorna SafeString (no se escapa). Para `texto`, `textarea`,
    `numero` y `url` retorna un string normal (se escapa por defecto en Django).
    Para `imagen` retorna la URL del archivo (string).
    """
    val = obtener_bloque(clave, default)
    return val


@register.simple_tag
def bloque_imagen(clave, default=""):
    """Atajo legible para imágenes — equivale a `{% bloque clave %}` pero hace
    explícito en el template que se espera una URL de imagen."""
    return obtener_bloque(clave, default)


@register.simple_tag
def bloque_html(clave, default=""):
    """Renderiza HTML crudo. Útil si el bloque guarda HTML pero está marcado
    como `texto` por error — fuerza el mark_safe."""
    val = obtener_bloque(clave, default)
    return mark_safe(val) if val else ""
