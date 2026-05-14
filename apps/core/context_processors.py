from django.conf import settings
from urllib.parse import quote


def site_info(request):
    whatsapp_raw = settings.SITE_WHATSAPP
    default_text = f"Hola {settings.SITE_NAME}, quisiera información sobre sus productos de limpieza."
    return {
        "SITE_NAME": settings.SITE_NAME,
        "SITE_BRAND": getattr(settings, "SITE_BRAND", settings.SITE_NAME),
        "SITE_TAGLINE": settings.SITE_TAGLINE,
        "SITE_WHATSAPP": whatsapp_raw,
        "SITE_WHATSAPP_DISPLAY": getattr(settings, "SITE_WHATSAPP_DISPLAY", f"+{whatsapp_raw}"),
        "SITE_WHATSAPP_URL": f"https://wa.me/{whatsapp_raw}?text={quote(default_text)}",
        "SITE_PHONE": settings.SITE_PHONE,
        "SITE_EMAIL": settings.SITE_EMAIL,
        "SITE_ADDRESS": settings.SITE_ADDRESS,
        "SITE_DELIVERY_AREA": getattr(settings, "SITE_DELIVERY_AREA", ""),
    }
