"""Helpers de plantilla: emoji por producto + WhatsApp links."""

from urllib.parse import quote

from django import template
from django.conf import settings

register = template.Library()


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
