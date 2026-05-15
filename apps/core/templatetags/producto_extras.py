"""Helpers de plantilla: emoji por producto + WhatsApp links."""

import re
from urllib.parse import quote

from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

register = template.Library()


# Regex para extraer peso/volumen de una presentación (Galón 4L, Bolsa 25kg, etc.)
_PESO_RE = re.compile(
    r"(\d+(?:[\.,]\d+)?)\s*"
    r"(kg|g|gr|mg|t|l|lt|ltr|litro|litros|ml|cc|oz|lb)\b",
    re.IGNORECASE,
)

# Unidades schema.org QuantitativeValue (UN/CEFACT Common Code)
_UNIT_CODE_MAP = {
    "kg": "KGM",
    "g": "GRM", "gr": "GRM",
    "mg": "MGM",
    "t": "TNE",
    "l": "LTR", "lt": "LTR", "ltr": "LTR", "litro": "LTR", "litros": "LTR",
    "ml": "MLT", "cc": "MLT",
    "oz": "ONZ",
    "lb": "LBR",
}

# Si la unidad es de peso o volumen para distinguir schema (weight vs volume)
_VOLUME_UNITS = {"l", "lt", "ltr", "litro", "litros", "ml", "cc"}


CATEGORIA_EMOJI = {
    "detergentes": "🧴",
    "desinfectantes": "💧",
    "bano": "🚿",
    "pisos": "🧹",
    "papel": "🧻",
    "dispensadores": "📦",
    "lavanderia": "👕",
    "equipos": "🔧",
}

KEYWORDS = [
    (("detergente", "desengrasante"), "🧴"),
    (("desinfect", "amonio", "alcohol", "peroxido", "hipoclorito", "lejia", "lejía"), "💧"),
    (("baño", "bano", "sarro", "urinario", "inodoro"), "🚿"),
    (("piso", "cera", "decapante", "trapeador", "escoba"), "🧹"),
    (("papel", "toalla", "servilleta", "higienic", "rollo"), "🧻"),
    (("guante",), "🧤"),
    (("dispensador", "carro", "bolsa"), "📦"),
    (("lavander", "suavizante", "blanqueador"), "👕"),
    (("aspiradora", "hidrolavadora", "maquina", "equipo"), "🔧"),
]


@register.simple_tag
def producto_emoji(producto):
    """Devuelve un emoji apropiado según nombre/categoría del producto."""
    nombre = (producto.nombre or "").lower()
    cat = (producto.categoria.nombre if producto.categoria else "").lower()
    full = nombre + " " + cat
    for keys, emoji in KEYWORDS:
        if any(k in full for k in keys):
            return emoji
    return "🧴"


# Mapeo categoría -> SVG ilustración. El orden importa: primero los más específicos.
ILUSTRACION_MAPPING = [
    ("detergente", "detergentes.svg"),
    ("desengrasante", "detergentes.svg"),
    ("desinfect", "desinfectantes.svg"),
    ("sanitiz", "desinfectantes.svg"),
    ("baño", "bano.svg"),
    ("bano", "bano.svg"),
    ("inodoro", "bano.svg"),
    ("piso", "pisos.svg"),
    ("superficie", "pisos.svg"),
    ("papel", "papel.svg"),
    ("descartab", "papel.svg"),
    ("dispens", "dispensadores.svg"),
    ("accesorio", "dispensadores.svg"),
    ("lavander", "lavanderia.svg"),
    ("ropa", "lavanderia.svg"),
    ("equipo", "equipos.svg"),
    ("maquinaria", "equipos.svg"),
    ("aspiradora", "equipos.svg"),
    ("hidrolavadora", "equipos.svg"),
    ("protecci", "epp.svg"),
    ("epp", "epp.svg"),
    ("guante", "epp.svg"),
    ("mascarilla", "epp.svg"),
    ("bioseg", "bioseguridad.svg"),
    ("antibact", "bioseguridad.svg"),
    ("gel", "bioseguridad.svg"),
    ("paño", "panos.svg"),
    ("pano", "panos.svg"),
    ("trapo", "panos.svg"),
    ("microfibra", "panos.svg"),
    ("abrasivo", "panos.svg"),
    ("esponja", "panos.svg"),
]


@register.simple_tag
def producto_ilustracion(producto):
    """Devuelve el path al SVG de ilustración según la categoría del producto.

    Se usa como placeholder visual cuando el producto no tiene `imagen`.
    Cae a `detergentes.svg` si la categoría no matchea ninguna keyword.

    Uso en template:
        {% producto_ilustracion producto as ilus %}
        <img src="{% static ilus %}" ... />
    """
    nombre = (producto.nombre or "").lower()
    cat = (producto.categoria.nombre if producto.categoria else "").lower()
    full = cat + " " + nombre  # categoría tiene prioridad
    for key, file in ILUSTRACION_MAPPING:
        if key in full:
            return f"img/categorias/{file}"
    return "img/categorias/detergentes.svg"  # fallback genérico


@register.simple_tag
def producto_ilustracion_categoria(categoria):
    """Versión para `Categoria` directamente (no necesita producto)."""
    if not categoria:
        return "img/categorias/detergentes.svg"
    cat = (categoria.nombre or "").lower()
    for key, file in ILUSTRACION_MAPPING:
        if key in cat:
            return f"img/categorias/{file}"
    return "img/categorias/detergentes.svg"


@register.simple_tag
def whatsapp_url(mensaje=""):
    """Genera link wa.me con mensaje pre-rellenado.

    Uso: {% whatsapp_url "Hola, me interesa el producto X" %}
    """
    numero = getattr(settings, "SITE_WHATSAPP", "51918570814")
    if not mensaje:
        nombre = getattr(settings, "SITE_NAME", "ProClean")
        mensaje = f"Hola {nombre}, quisiera información sobre sus productos de limpieza."
    return f"https://wa.me/{numero}?text={quote(mensaje)}"


@register.simple_tag
def whatsapp_producto(producto):
    """Link de WhatsApp para cotizar un producto específico."""
    nombre = getattr(settings, "SITE_NAME", "ProClean")
    codigo = getattr(producto, "codigo", "") or ""
    marca = getattr(producto, "marca", None)
    marca_str = f" {marca.nombre}" if marca else ""
    presentacion = getattr(producto, "presentacion", "") or ""
    pres_str = f" — {presentacion}" if presentacion else ""
    cod_str = f" (cód. {codigo})" if codigo else ""
    msg = f"Hola {nombre}, me interesa cotizar:{marca_str} {producto.nombre}{pres_str}{cod_str}"
    return whatsapp_url(msg)


@register.simple_tag
def whatsapp_categoria(categoria):
    """Link de WhatsApp para cotizar productos de una categoría."""
    nombre = getattr(settings, "SITE_NAME", "ProClean")
    msg = f"Hola {nombre}, me interesan productos de {categoria.nombre}."
    return whatsapp_url(msg)
