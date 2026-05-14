"""Sitemaps para ProClean Servid Innova.

Implementa sitemaps sin requerir django.contrib.sites: cada Sitemap retorna
URLs absolutas usando SITE_DOMAIN + SITE_PROTOCOL definidos en settings.
"""
from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from apps.catalogo.models import Categoria, Producto


class _BaseSitemap(Sitemap):
    """Sitemap base que evita django.contrib.sites usando SITE_DOMAIN."""

    @property
    def protocol(self):  # type: ignore[override]
        return getattr(settings, "SITE_PROTOCOL", "https")

    def get_domain(self, site=None):  # type: ignore[override]
        # Reemplaza la dependencia de django.contrib.sites
        return getattr(settings, "SITE_DOMAIN", "proclean.pe")


class StaticViewSitemap(_BaseSitemap):
    """Páginas estáticas del sitio público."""
    priority = 0.8
    changefreq = "weekly"

    def items(self):
        return [
            "core:home",
            "core:nosotros",
            "core:contacto",
            "core:faq",
            "core:recursos",
            "core:terminos",
            "core:privacidad",
            "catalogo:lista",
        ]

    def location(self, item):
        return reverse(item)

    def priority(self, item):  # type: ignore[override]
        return 1.0 if item == "core:home" else 0.7

    def changefreq(self, item):  # type: ignore[override]
        return "daily" if item == "core:home" else "monthly"


class SolucionesSitemap(_BaseSitemap):
    """Páginas de soluciones por industria."""
    priority = 0.7
    changefreq = "monthly"

    def items(self):
        # Slugs definidos en apps.core.views.SOLUCIONES
        return ["hoteles", "clinicas", "industria", "oficinas", "retail"]

    def location(self, slug):
        return reverse("core:solucion", args=[slug])


class CategoriaSitemap(_BaseSitemap):
    """Categorías activas del catálogo."""
    priority = 0.6
    changefreq = "weekly"

    def items(self):
        return Categoria.objects.filter(activa=True).order_by("orden", "nombre")

    def location(self, obj):
        return obj.get_absolute_url()


class ProductoSitemap(_BaseSitemap):
    """Productos activos del catálogo."""
    priority = 0.5
    changefreq = "weekly"

    def items(self):
        return Producto.objects.filter(activo=True).only(
            "slug", "actualizado", "nombre"
        )

    def lastmod(self, obj):
        return obj.actualizado

    def location(self, obj):
        return obj.get_absolute_url()


SITEMAPS = {
    "static": StaticViewSitemap,
    "soluciones": SolucionesSitemap,
    "categorias": CategoriaSitemap,
    "productos": ProductoSitemap,
}
