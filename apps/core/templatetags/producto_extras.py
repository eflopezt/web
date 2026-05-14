"""Helpers de plantilla: placeholder de producto."""

from django import template

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

# Mapping por palabra clave en el nombre o categoría
KEYWORDS = [
    (("detergente", "desengrasante"), "🧴"),
    (("desinfect", "amonio", "alcohol", "peroxido", "hipoclorito"), "💧"),
    (("baño", "bano", "sarro", "urinario", "inodoro"), "🚿"),
    (("piso", "cera", "decapante"), "🧹"),
    (("papel", "toalla", "servilleta", "higienic"), "🧻"),
    (("guante",), "🧤"),
    (("dispensador", "carro"), "📦"),
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
