from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.contrib.sitemaps.views import sitemap
from django.shortcuts import redirect
from django.urls import include, path

from apps.core.sitemaps import SITEMAPS
from apps.core.views import robots_txt


def post_login_redirect(request):
    """Redirige según grupo: staff intranet → /intranet/, cliente → /portal/."""
    u = request.user
    if not u.is_authenticated:
        return redirect("login")
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
