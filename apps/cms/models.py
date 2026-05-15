"""CMS sencillo tipo Wix: bloques de contenido editables por clave.

Filosofía:
- El admin NO crea ni borra bloques — solo los EDITA. Las claves las define el dev
  desde el código (via `seed_cms`) y el cliente cambia el contenido por el admin
  sin tocar la web.
- Cada bloque tiene tipo (texto/html/imagen/lista) y un valor según tipo.
- Cache en memoria de 5 min para no consultar la DB en cada render.
"""
from django.core.cache import cache
from django.db import models
from django.utils.safestring import mark_safe


CACHE_PREFIX = "cms_bloque_v1:"
CACHE_TTL = 300  # 5 min


class Pagina(models.Model):
    """Agrupador visual en el admin (Home, Nosotros, Contacto…)."""
    slug = models.SlugField(max_length=60, unique=True, help_text="Identificador interno (no se muestra al público).")
    titulo = models.CharField(max_length=120, help_text="Nombre amigable para el admin (ej. 'Página de inicio').")
    descripcion = models.CharField(max_length=240, blank=True, help_text="Pequeña ayuda para el editor.")
    icono = models.CharField(max_length=40, blank=True, default="article", help_text="Material icon name (Unfold).")
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["orden", "titulo"]
        verbose_name = "Página"
        verbose_name_plural = "Páginas del sitio"

    def __str__(self):
        return self.titulo


class Bloque(models.Model):
    """Un bloque de contenido editable.

    La `clave` la usan los templates con `{% bloque "clave" %}`. NO debe cambiar
    porque rompería el render del template — el admin oculta este campo.
    """
    TIPO_CHOICES = [
        ("texto",  "Texto corto"),
        ("textarea", "Texto largo (párrafo)"),
        ("html",   "HTML enriquecido"),
        ("imagen", "Imagen"),
        ("numero", "Número"),
        ("url",    "Enlace (URL)"),
    ]

    pagina = models.ForeignKey(
        Pagina, on_delete=models.PROTECT, related_name="bloques",
        help_text="Sección del sitio a la que pertenece este bloque.",
    )
    clave = models.SlugField(
        max_length=80, unique=True,
        help_text="Identificador interno usado por la web. NO editar.",
    )
    etiqueta = models.CharField(
        max_length=160,
        help_text="Nombre amigable mostrado al editor (ej. 'Título principal del hero').",
    )
    ayuda = models.CharField(
        max_length=300, blank=True,
        help_text="Pista contextual que aparece bajo el campo en el admin.",
    )
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default="texto")

    # Valores según tipo
    valor_texto = models.CharField(max_length=500, blank=True)
    valor_textarea = models.TextField(blank=True)
    valor_html = models.TextField(
        blank=True,
        help_text="Permite HTML: usa <strong>, <em>, <br> y enlaces &lt;a href='...'&gt;.",
    )
    valor_imagen = models.ImageField(upload_to="cms/", blank=True, null=True)
    valor_numero = models.CharField(max_length=20, blank=True, help_text="Acepta texto: '+160', '24h', '100%', etc.")
    valor_url = models.URLField(blank=True)

    orden = models.PositiveIntegerField(default=0)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["pagina__orden", "pagina__titulo", "orden", "etiqueta"]
        verbose_name = "Bloque de contenido"
        verbose_name_plural = "Bloques de contenido"

    def __str__(self):
        return f"{self.etiqueta} ({self.clave})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache.delete(f"{CACHE_PREFIX}{self.clave}")

    def delete(self, *args, **kwargs):
        cache.delete(f"{CACHE_PREFIX}{self.clave}")
        return super().delete(*args, **kwargs)

    @property
    def valor(self):
        """Devuelve el valor activo del bloque según su tipo."""
        if self.tipo == "texto":
            return self.valor_texto
        if self.tipo == "textarea":
            return self.valor_textarea
        if self.tipo == "html":
            return mark_safe(self.valor_html)
        if self.tipo == "imagen":
            return self.valor_imagen.url if self.valor_imagen else ""
        if self.tipo == "numero":
            return self.valor_numero
        if self.tipo == "url":
            return self.valor_url
        return ""


def obtener_bloque(clave: str, default: str = "") -> str:
    """API pública usada por el template tag `{% bloque %}`.

    Devuelve el valor cacheado (5 min) del bloque o `default` si no existe.
    """
    cache_key = f"{CACHE_PREFIX}{clave}"
    cached = cache.get(cache_key)
    if cached is not None:
        # cached puede ser "" — válido. Solo None marca miss.
        return cached
    try:
        b = Bloque.objects.only(
            "tipo", "valor_texto", "valor_textarea", "valor_html",
            "valor_imagen", "valor_numero", "valor_url",
        ).get(clave=clave)
        valor = b.valor
    except Bloque.DoesNotExist:
        valor = default
    cache.set(cache_key, valor, CACHE_TTL)
    return valor
