from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.contrib.sitemaps.views import sitemap
from django.shortcuts import redirect
from django.urls import include, path
from django.utils.http import url_has_allowed_host_and_scheme

from apps.core.sitemaps import SITEMAPS
from apps.core.views import robots_txt


# Branding del Django admin (visible en /admin/)
admin.site.site_header = "ProClean Servid Innova — Admin"
admin.site.site_title = "ProClean Admin"
admin.site.index_title = "Panel de control"


def post_login_redirect(request):
    """Redirige según grupo + respeta ?next= si es URL segura.

    Prioridad:
      1. ?next= si es seguro (permite venir del admin / portal con un destino claro)
      2. Superuser → /admin/
      3. Staff → /intranet/
      4. Cliente → /portal/
    """
    u = request.user
    if not u.is_authenticated:
        return redirect("login")

    next_url = request.GET.get("next") or request.POST.get("next")
    if next_url and url_has_allowed_host_and_scheme(
        next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return redirect(next_url)

    if u.is_superuser:
        return redirect("admin:index")
    if u.is_staff or u.groups.filter(name="Staff Intranet").exists():
        return redirect("intranet:dashboard")
    return redirect("portal:dashboard")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("post-login/", login_required(post_login_redirect), name="post_login"),
    path("registro/", include("apps.portal.urls_registro")),
    path("portal/", include("apps.portal.urls")),
    path("intranet/", include("apps.intranet.urls")),
    # SEO: sitemap.xml + robots.txt
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": SITEMAPS},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path("robots.txt", robots_txt, name="robots_txt"),
    path("", include("apps.core.urls")),
    path("productos/", include("apps.catalogo.urls")),
    path("cotizacion/", include("apps.cotizaciones.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.BASE_DIR / "static")
