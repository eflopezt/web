"""Django settings for ProClean Servid Innova project."""

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# --- Security ---
SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "django-insecure-dev-only-replace-me-in-prod-please-do-it",
)
DEBUG = os.environ.get("DEBUG", "1") == "1"
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
CSRF_TRUSTED_ORIGINS = [
    o.strip()
    for o in os.environ.get(
        "CSRF_TRUSTED_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000"
    ).split(",")
    if o.strip()
]

# --- Subpath deploy (e.g. harmoni.pe/proclean) ---
FORCE_SCRIPT_NAME = os.environ.get("FORCE_SCRIPT_NAME", "") or None
USE_X_FORWARDED_HOST = os.environ.get("USE_X_FORWARDED_HOST", "0") == "1"
_BEHIND_HTTPS_PROXY = os.environ.get("SECURE_PROXY_SSL_HEADER", "0") == "1"
if _BEHIND_HTTPS_PROXY:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    # Cookies Secure: el browser solo las envía sobre HTTPS, las protege ante MITM
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
# SameSite "Lax" permite que el browser mande la cookie en top-level navigation
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"

# Cookie names únicos para evitar colisión con otras apps del mismo dominio
# (ej. harmoni.pe tiene Harmoni en / y ProClean en /proclean/ — ambas usaban
# `sessionid`/`csrftoken` por default y el browser sobrescribía la una con la otra).
# Path=/ (no /proclean) para que el browser maneje las cookies de forma estándar.
SESSION_COOKIE_NAME = "proclean_sessionid"
CSRF_COOKIE_NAME = "proclean_csrftoken"

# Domain/protocolo del sitio (para sitemap.xml y JSON-LD)
SITE_DOMAIN = os.environ.get("SITE_DOMAIN", "proclean.pe")
SITE_PROTOCOL = os.environ.get("SITE_PROTOCOL", "https")

# --- Apps ---
INSTALLED_APPS = [
    # Unfold (admin moderno) ANTES de django.contrib.admin
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "unfold.contrib.inlines",
    "unfold.contrib.import_export",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "django.contrib.sitemaps",
    "apps.core",
    "apps.catalogo",
    "apps.clientes",
    "apps.cotizaciones",
    "apps.pedidos",
    "apps.facturacion",
    "apps.intranet",
    "apps.portal",
    "apps.cms",
]

# Login/logout redirects (Django prepende FORCE_SCRIPT_NAME automáticamente al usar reverse(),
# pero para rutas absolutas en settings necesitamos hacerlo manual)
_SCRIPT_NAME = (FORCE_SCRIPT_NAME or "").rstrip("/")
LOGIN_URL = f"{_SCRIPT_NAME}/accounts/login/"
LOGIN_REDIRECT_URL = f"{_SCRIPT_NAME}/post-login/"
LOGOUT_REDIRECT_URL = f"{_SCRIPT_NAME}/"

# Datos del emisor para PDFs (modificables vía env)
import os as _os
EMISOR_RAZON_SOCIAL = _os.environ.get("EMISOR_RAZON_SOCIAL", "LimpiaPro S.A.C. (DEMO)")
EMISOR_RUC = _os.environ.get("EMISOR_RUC", "20612345678")
EMISOR_DIRECCION = _os.environ.get("EMISOR_DIRECCION", "Av. Industrial 123, Ate, Lima")
EMISOR_EMAIL = _os.environ.get("EMISOR_EMAIL", "ventas@limpiapro.pe")
EMISOR_TELEFONO = _os.environ.get("EMISOR_TELEFONO", "+51 999 999 999")

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "apps.cotizaciones.middleware.CarritoContadorMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.core.context_processors.site_info",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# --- Database ---
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# --- Auth ---
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- i18n ---
LANGUAGE_CODE = "es-pe"
TIME_ZONE = "America/Lima"
USE_I18N = True
USE_TZ = True

# --- Static + media (con soporte de subpath) ---
_STATIC_PREFIX = f"{_SCRIPT_NAME}/static/" if _SCRIPT_NAME else "/static/"
_MEDIA_PREFIX = f"{_SCRIPT_NAME}/media/" if _SCRIPT_NAME else "/media/"
STATIC_URL = os.environ.get("STATIC_URL", _STATIC_PREFIX)
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = os.environ.get("MEDIA_URL", _MEDIA_PREFIX)
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Email ---
EMAIL_BACKEND = os.environ.get(
    "EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"
)
EMAIL_HOST = os.environ.get("EMAIL_HOST", "")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "1") == "1"
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "ventas@proclean.pe")
VENTAS_EMAIL = os.environ.get("VENTAS_EMAIL", "ventas@proclean.pe")

# --- Site ---
SITE_NAME = "ProClean"
SITE_BRAND = "ProClean Servid Innova"
SITE_TAGLINE = "Productos de limpieza profesional para tu hogar o negocio"
SITE_WHATSAPP = os.environ.get("SITE_WHATSAPP", "51918570814")
SITE_WHATSAPP_DISPLAY = os.environ.get("SITE_WHATSAPP_DISPLAY", "+51 918 570 814")
SITE_PHONE = os.environ.get("SITE_PHONE", "+51 918 570 814")
SITE_EMAIL = os.environ.get("SITE_EMAIL", "ventas@proclean.pe")
SITE_ADDRESS = os.environ.get("SITE_ADDRESS", "Lima y Callao, Perú")
SITE_DELIVERY_AREA = "Envío gratis en Lima y Callao"


# ============================================================================
# UNFOLD ADMIN — tema moderno tipo WooCommerce/Odoo con paleta ProClean
# ============================================================================
from django.templatetags.static import static as _static
from django.urls import reverse_lazy as _rl

UNFOLD = {
    "SITE_TITLE": "ProClean Admin",
    "SITE_HEADER": "ProClean Servid Innova",
    "SITE_SUBHEADER": "Backoffice",
    "SITE_DROPDOWN": [],
    "SITE_URL": "/",
    "SITE_SYMBOL": "store",
    # Logo PNG real (transparente) — variantes light/dark
    "SITE_LOGO": {
        "light": lambda request: _static("img/logo-real.png"),
        "dark":  lambda request: _static("img/logo-white-real.png"),
    },
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "ENVIRONMENT": None,
    "BORDER_RADIUS": "10px",
    "COLORS": {
        "base": {
            "50":  "240 249 255",
            "100": "224 242 254",
            "200": "186 230 253",
            "300": "125 211 252",
            "400": "56 189 248",
            "500": "27 117 188",
            "600": "26 79 139",
            "700": "20 63 115",
            "800": "12 46 85",
            "900": "8 33 60",
            "950": "5 22 40",
        },
        "primary": {
            "50":  "240 253 244",
            "100": "220 252 231",
            "200": "187 247 208",
            "300": "134 229 72",
            "400": "107 203 58",
            "500": "63 174 42",
            "600": "46 139 31",
            "700": "35 105 20",
            "800": "27 80 15",
            "900": "20 60 11",
            "950": "10 35 5",
        },
        "font": {
            "subtle-light":  "var(--color-base-500)",
            "subtle-dark":   "var(--color-base-400)",
            "default-light": "var(--color-base-600)",
            "default-dark":  "var(--color-base-300)",
            "important-light": "var(--color-base-900)",
            "important-dark":  "var(--color-base-100)",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,
        "navigation": [
            {
                "title": "Panel principal",
                "separator": False,
                "items": [
                    {
                        "title": "Dashboard",
                        "icon": "dashboard",
                        "link": _rl("admin:index"),
                    },
                ],
            },
            {
                "title": "Contenido web (CMS)",
                "separator": True,
                "items": [
                    {"title": "✏️ Editar páginas",  "icon": "edit_note",  "link": _rl("admin:cms_pagina_changelist")},
                    {"title": "📝 Todos los bloques", "icon": "view_quilt", "link": _rl("admin:cms_bloque_changelist")},
                ],
            },
            {
                "title": "Catálogo",
                "separator": True,
                "items": [
                    {"title": "Productos",   "icon": "inventory_2",  "link": _rl("admin:catalogo_producto_changelist")},
                    {"title": "Categorías",  "icon": "category",     "link": _rl("admin:catalogo_categoria_changelist")},
                    {"title": "Marcas",      "icon": "branding_watermark", "link": _rl("admin:catalogo_marca_changelist")},
                    {"title": "Imágenes",    "icon": "photo_library", "link": _rl("admin:catalogo_imagenproducto_changelist")},
                ],
            },
            {
                "title": "Comercial",
                "separator": True,
                "items": [
                    {"title": "Clientes",     "icon": "people",        "link": _rl("admin:clientes_cliente_changelist")},
                    {"title": "Cotizaciones", "icon": "request_quote", "link": _rl("admin:cotizaciones_cotizacion_changelist")},
                    {"title": "Pedidos",      "icon": "shopping_cart", "link": _rl("admin:pedidos_pedido_changelist")},
                    {"title": "Facturas",     "icon": "receipt_long",  "link": _rl("admin:facturacion_factura_changelist")},
                ],
            },
            {
                "title": "Sistema",
                "separator": True,
                "items": [
                    {"title": "Usuarios",  "icon": "person", "link": _rl("admin:auth_user_changelist")},
                    {"title": "Grupos",    "icon": "groups", "link": _rl("admin:auth_group_changelist")},
                ],
            },
        ],
    },
    "TABS": [],
    "STYLES": [
        lambda request: _static("admin/css/proclean_unfold.css"),
    ],
}
