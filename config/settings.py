"""Django settings for LimpiaPro project."""

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

# --- Apps ---
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "apps.core",
    "apps.catalogo",
    "apps.clientes",
    "apps.cotizaciones",
    "apps.pedidos",
    "apps.facturacion",
    "apps.intranet",
    "apps.portal",
]

# Login/logout redirects
LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/post-login/"
LOGOUT_REDIRECT_URL = "/"

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

# --- Static + media ---
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
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
