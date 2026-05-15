"""Seed idempotente del CMS: define páginas y bloques editables.

Cada bloque tiene una `clave` única que el template usa con `{% bloque "clave" %}`.
Si el bloque ya existe, **NO sobrescribe el contenido** (respeta lo que el
cliente haya editado desde el admin). Solo crea los que no existan.

Para forzar reset de contenido al texto por defecto:

    python manage.py seed_cms --reset

Para resetear UNA sola clave:

    python manage.py seed_cms --reset-clave home_hero_titulo
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.cms.models import Bloque, Pagina


# ---------------------------------------------------------------------------
# Definición de páginas y bloques (orden y valor inicial).
# Los valores ya reflejan las observaciones del cliente del PDF.
# ---------------------------------------------------------------------------

PAGINAS = [
    {"slug": "home", "titulo": "Página de inicio", "icono": "home", "orden": 1,
     "descripcion": "El home es lo primero que ve un visitante. Cuida los títulos y la propuesta."},
    {"slug": "global", "titulo": "Contenido global del sitio", "icono": "public", "orden": 10,
     "descripcion": "Información que aparece en todas las páginas (footer, navbar, etc)."},
]


# Bloques: (pagina_slug, clave, etiqueta, ayuda, tipo, valor_inicial, orden)
BLOQUES = [
    # ----- HOME · Hero -----
    ("home", "home_hero_badge",
     "Badge superior del hero",
     "Banner pequeño sobre el título. Mantén corto (máx 80 caracteres).",
     "texto",
     "Delivery gratis desde S/150 en Lima y Callao • Atención rápida por WhatsApp",
     10),

    ("home", "home_hero_titulo",
     "Título principal del hero",
     "El título más importante de la web. Debe captar la atención en 1-2 líneas.",
     "texto",
     "Todo en productos de limpieza al mejor precio",
     20),

    ("home", "home_hero_subtitulo",
     "Subtítulo / descripción del hero",
     "Párrafo corto debajo del título principal. Explica el valor de la marca.",
     "textarea",
     "Productos de limpieza de calidad con entrega rápida y atención personalizada. "
     "Todo lo que necesitas para mantener tus espacios limpios, con precios "
     "especiales y atención directa para una compra fácil y sin complicaciones.",
     30),

    # ----- HOME · 4 stats del hero -----
    ("home", "home_hero_stat1_numero", "Stat #1 — número",
     "Número grande visible en la primera tarjeta del hero (ej. '+160').",
     "numero", "+160", 40),
    ("home", "home_hero_stat1_label", "Stat #1 — etiqueta",
     "Texto pequeño bajo el número de la primera tarjeta.",
     "texto", "productos en catálogo", 41),

    ("home", "home_hero_stat2_numero", "Stat #2 — número",
     "Número de la segunda tarjeta (ej. '37').",
     "numero", "37", 50),
    ("home", "home_hero_stat2_label", "Stat #2 — etiqueta",
     "Texto pequeño bajo el número de la segunda tarjeta.",
     "texto", "marcas líderes", 51),

    ("home", "home_hero_stat3_numero", "Stat #3 — número",
     "Número/icono de la tercera tarjeta. Ej. 'Atención rápida' o '24h'.",
     "texto", "Atención", 60),
    ("home", "home_hero_stat3_label", "Stat #3 — etiqueta",
     "Texto pequeño bajo el número de la tercera tarjeta.",
     "texto", "rápida y personalizada", 61),

    ("home", "home_hero_stat4_numero", "Stat #4 — número",
     "Número/texto de la cuarta tarjeta. Ej. 'Productos' o '100%'.",
     "texto", "Productos", 70),
    ("home", "home_hero_stat4_label", "Stat #4 — etiqueta",
     "Texto pequeño bajo el número de la cuarta tarjeta.",
     "texto", "originales y oficiales", 71),

    # ----- HOME · Trust bar (4 ventajas) -----
    ("home", "home_trust1_titulo", "Ventaja #1 — título", "Primera ventaja después del hero.",
     "texto", "Calidad garantizada", 80),
    ("home", "home_trust1_subtitulo", "Ventaja #1 — descripción", "Frase corta complementaria.",
     "texto", "Marcas oficiales", 81),

    ("home", "home_trust2_titulo", "Ventaja #2 — título", "Segunda ventaja.",
     "texto", "Envío gratis", 90),
    ("home", "home_trust2_subtitulo", "Ventaja #2 — descripción", "Frase corta complementaria.",
     "texto", "Lima y Callao", 91),

    ("home", "home_trust3_titulo", "Ventaja #3 — título",
     "Tercera ventaja. Por petición del cliente: 'Precios por mayor y menor'.",
     "texto", "Precios por mayor y menor", 100),
    ("home", "home_trust3_subtitulo", "Ventaja #3 — descripción", "Frase corta complementaria.",
     "texto", "Para empresas y hogares", 101),

    ("home", "home_trust4_titulo", "Ventaja #4 — título",
     "Cuarta ventaja. Por petición del cliente: 'Atención personalizada'.",
     "texto", "Atención personalizada", 110),
    ("home", "home_trust4_subtitulo", "Ventaja #4 — descripción", "Frase corta complementaria.",
     "texto", "WhatsApp directo con ventas", 111),

    # ----- HOME · Marquee marcas -----
    ("home", "home_marcas_titulo", "Texto introductorio de las marcas",
     "Texto pequeño que aparece encima del carrusel de marcas.",
     "texto", "Distribuimos las marcas más solicitadas", 120),

    # ----- HOME · Sección catálogo -----
    ("home", "home_catalogo_eyebrow", "Etiqueta superior de la sección Catálogo",
     "Texto pequeño en mayúsculas que va arriba del título (ej. 'CATÁLOGO').",
     "texto", "Catálogo", 130),
    ("home", "home_catalogo_titulo", "Título de la sección Catálogo",
     "Título grande de la sección de categorías.",
     "texto", "Todo en productos de limpieza al mejor precio", 131),
    ("home", "home_catalogo_subtitulo", "Subtítulo de la sección Catálogo",
     "Texto descriptivo de la sección de categorías.",
     "textarea",
     "Encuentra papeles, lejía, desinfectantes y más con precios especiales y "
     "entrega rápida. Delivery gratis en Lima y Callao y envíos a nivel nacional.",
     132),

    # ----- HOME · Números que respaldan -----
    ("home", "home_numeros_eyebrow", "Etiqueta de la sección 'Números'", "Texto pequeño superior.",
     "texto", "Números que respaldan", 140),
    ("home", "home_numeros_titulo", "Título de la sección 'Números'",
     "Título grande.",
     "texto", "Por qué nos eligen las empresas peruanas", 141),

    ("home", "home_num1_numero", "Número grande #1", "Ej. '+160'.",
     "numero", "+160", 142),
    ("home", "home_num1_label", "Etiqueta #1", "Texto bajo el número.",
     "texto", "productos auténticos", 143),
    ("home", "home_num2_numero", "Número grande #2", "Ej. '37'.",
     "numero", "37", 144),
    ("home", "home_num2_label", "Etiqueta #2", "Texto bajo el número.",
     "texto", "marcas líderes", 145),
    ("home", "home_num3_numero", "Número grande #3", "Ej. '24h'.",
     "numero", "24h", 146),
    ("home", "home_num3_label", "Etiqueta #3", "Texto bajo el número.",
     "texto", "cotización máxima", 147),
    ("home", "home_num4_numero", "Número grande #4", "Ej. '48h'.",
     "numero", "48h", 148),
    ("home", "home_num4_label", "Etiqueta #4", "Texto bajo el número.",
     "texto", "entrega Lima/Callao", 149),

    # ----- HOME · Productos destacados -----
    ("home", "home_destacados_eyebrow", "Etiqueta de 'Destacados'", "Texto pequeño superior.",
     "texto", "Bestsellers", 150),
    ("home", "home_destacados_titulo", "Título de 'Destacados'", "Título grande de la sección.",
     "texto", "Productos destacados", 151),
    ("home", "home_destacados_subtitulo", "Subtítulo de 'Destacados'", "Frase descriptiva.",
     "texto", "Los más cotizados por nuestros clientes B2B en Lima.", 152),

    # ----- HOME · Soluciones por sector -----
    ("home", "home_sectores_eyebrow", "Etiqueta de 'Soluciones'", "Texto pequeño.",
     "texto", "Soluciones", 160),
    ("home", "home_sectores_titulo", "Título de 'Soluciones'", "Título grande.",
     "texto", "A la medida de tu sector", 161),
    ("home", "home_sectores_subtitulo", "Subtítulo de 'Soluciones'", "Frase descriptiva.",
     "textarea",
     "Cada industria tiene exigencias distintas. Te asesoramos con los productos "
     "correctos y volúmenes óptimos.", 162),

    # ----- HOME · Franja WhatsApp -----
    ("home", "home_wa_eyebrow", "Texto pequeño franja WhatsApp", "Encima del título de la franja verde.",
     "texto", "¿Compra recurrente o cantidad especial?", 170),
    ("home", "home_wa_titulo", "Título franja WhatsApp", "Título grande de la franja verde.",
     "texto", "Pide tu cotización ahora", 171),
    ("home", "home_wa_descripcion", "Descripción franja WhatsApp", "Frase pequeña descriptiva.",
     "textarea", "Te respondemos en menos de 24 h hábiles con tu precio personalizado.", 172),

    # ----- HOME · CTA Final -----
    ("home", "home_cta_titulo", "Título del CTA final", "Título grande al final del home.",
     "texto", "¿Listo para cotizar?", 180),
    ("home", "home_cta_descripcion", "Descripción del CTA final", "Frase debajo del título.",
     "textarea",
     "Atención inmediata por WhatsApp. Envío gratis en Lima y Callao. Factura SUNAT incluida.", 181),

    # ----- GLOBAL -----
    ("global", "global_footer_about",
     "Texto del footer (sobre la empresa)",
     "Pequeño párrafo descriptivo en el footer.",
     "textarea",
     "ProClean Servid Innova es proveedor de productos de limpieza profesional para "
     "hogares, negocios e industria en Lima y Callao.", 10),
]


class Command(BaseCommand):
    help = "Seed inicial del CMS: páginas y bloques editables del sitio público."

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true",
                            help="Sobreescribe TODOS los valores con el default (peligroso).")
        parser.add_argument("--reset-clave", default="",
                            help="Sobreescribe el valor de una sola clave al default.")

    @transaction.atomic
    def handle(self, *args, **opts):
        reset_all = opts["reset"]
        reset_clave = opts["reset_clave"]

        # 1. Páginas
        pagina_map = {}
        for p in PAGINAS:
            obj, created = Pagina.objects.update_or_create(
                slug=p["slug"],
                defaults={
                    "titulo": p["titulo"],
                    "descripcion": p.get("descripcion", ""),
                    "icono": p.get("icono", ""),
                    "orden": p["orden"],
                },
            )
            pagina_map[p["slug"]] = obj
            self.stdout.write(("  [+] Pagina creada: " if created else "  [=] Pagina actualizada: ") + obj.titulo)

        # 2. Bloques
        creados = 0
        actualizados = 0
        respetados = 0
        for row in BLOQUES:
            # Soporte para tuplas mal-formadas defensivo
            if len(row) != 7:
                continue
            pagina_slug, clave, etiqueta, ayuda, tipo, valor, orden = row

            pagina = pagina_map[pagina_slug]
            valor_field = {
                "texto": "valor_texto",
                "textarea": "valor_textarea",
                "html": "valor_html",
                "numero": "valor_numero",
                "url": "valor_url",
            }.get(tipo)

            existing = Bloque.objects.filter(clave=clave).first()
            if existing:
                # Si --reset o si la clave coincide con --reset-clave, sobrescribe.
                # Si no, preserva el valor que el cliente haya editado.
                force = reset_all or (reset_clave and reset_clave == clave)
                # Sí actualizamos siempre los metadatos (etiqueta, ayuda, orden, tipo).
                existing.etiqueta = etiqueta
                existing.ayuda = ayuda
                existing.orden = orden
                existing.tipo = tipo
                existing.pagina = pagina
                if force and valor_field:
                    setattr(existing, valor_field, valor)
                existing.save()
                if force:
                    actualizados += 1
                else:
                    respetados += 1
            else:
                kwargs = {
                    "pagina": pagina, "clave": clave, "etiqueta": etiqueta,
                    "ayuda": ayuda, "tipo": tipo, "orden": orden,
                }
                if valor_field:
                    kwargs[valor_field] = valor
                Bloque.objects.create(**kwargs)
                creados += 1

        self.stdout.write(self.style.SUCCESS(
            f"\n[OK] CMS seed listo: {creados} bloques creados, "
            f"{actualizados} reseteados, {respetados} preservados."
        ))
        if not reset_all and respetados > 0:
            self.stdout.write(self.style.WARNING(
                "  (los bloques 'preservados' tenían valores editados por el cliente; "
                "se mantuvo su contenido. Usa --reset para forzar default.)"
            ))
