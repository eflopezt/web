"""Carga datos demo idempotentes: 8 categorías + 5 marcas + 24 productos."""

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.catalogo.models import Categoria, Marca, Producto


CATEGORIAS = [
    ("Detergentes y desengrasantes", "sparkles", "Limpiadores multiusos, desengrasantes alcalinos y ácidos para cocina, planta y mantenimiento.", 1),
    ("Desinfectantes y sanitizantes", "shield", "Amonios cuaternarios, hipoclorito, peróxidos y alcoholes para áreas críticas.", 2),
    ("Productos para baño", "droplet", "Limpiadores de inodoros, sarro, urinarios y desinfección sanitaria.", 3),
    ("Pisos y superficies", "broom", "Ceras, abrillantadores, decapantes y limpiadores para pisos vinílicos, porcelanato y cemento.", 4),
    ("Papel y descartables", "scroll", "Papel higiénico jumbo, toalla z, servilletas y guantes desechables.", 5),
    ("Dispensadores y accesorios", "package", "Dispensadores de jabón, papel, dosificadores y carros de limpieza.", 6),
    ("Lavandería industrial", "shirt", "Detergentes, suavizantes, blanqueadores y neutralizantes para lavandería profesional.", 7),
    ("Equipos y maquinaria", "wrench", "Aspiradoras industriales, máquinas restregadoras, hidrolavadoras y pulidoras.", 8),
]

MARCAS = ["Sapolio", "Poett", "Marsella", "Elite", "Dkasa", "Suave", "Scott", "Paracas", "Daryza", "Kaz", "Rendipel"]

PRODUCTOS = [
    # (nombre, categoria, marca, presentacion, disponibilidad, destacado, descripcion_corta, precio_referencia)
    ("Detergente líquido multiuso concentrado", "Detergentes y desengrasantes", "Sapolio", "Galón 4L", "en_stock", True,
     "Detergente neutro de alta espuma para limpieza general. Biodegradable, pH 7.", 48.90),
    ("Desengrasante alcalino industrial", "Detergentes y desengrasantes", "InduClean", "Bidón 20L", "en_stock", False,
     "Desengrasante de uso pesado para cocinas industriales y planta de producción.", 89.50),
    ("Limpiador desinfectante multisuperficie", "Detergentes y desengrasantes", "Sanitex", "Galón 4L", "en_stock", True,
     "Limpia y desinfecta en un solo paso. Aroma lavanda. DIGESA aprobado.", 55.00),

    ("Amonio cuaternario 5ta generación", "Desinfectantes y sanitizantes", "Sanitex", "Galón 4L", "en_stock", True,
     "Desinfectante hospitalario de amplio espectro. Concentración 1:200.", 65.00),
    ("Hipoclorito de sodio 7.5%", "Desinfectantes y sanitizantes", "InduClean", "Bidón 20L", "en_stock", False,
     "Lejía industrial estabilizada para desinfección de superficies y aguas.", 78.00),
    ("Alcohol etílico 70° desnaturalizado", "Desinfectantes y sanitizantes", "CleanMaster", "Galón 4L", "en_stock", False,
     "Sanitizante de manos y superficies. Listo para usar.", 42.00),
    ("Peróxido de hidrógeno estabilizado", "Desinfectantes y sanitizantes", "EcoBrill", "Bidón 5L", "bajo_pedido", False,
     "Desinfectante ecológico de descomposición rápida, ideal para áreas alimentarias.", 95.00),

    ("Limpiador removedor de sarro", "Productos para baño", "Sapolio", "Botella 1L", "en_stock", False,
     "Removedor ácido fosfórico para sarro, óxido e incrustaciones en sanitarios.", 18.50),
    ("Aromatizador desinfectante para inodoros", "Productos para baño", "EcoBrill", "Galón 4L", "en_stock", False,
     "Doble acción: aromatiza y desinfecta. Disponible en pino, lavanda y cítrico.", 52.00),
    ("Limpiador urinario concentrado", "Productos para baño", "Sanitex", "Galón 4L", "en_stock", False,
     "Elimina manchas y olores de urinarios. Fórmula tensoactiva concentrada.", 49.00),

    ("Cera líquida abrillantadora", "Pisos y superficies", "CleanMaster", "Galón 4L", "en_stock", True,
     "Acabado mate-brillante para pisos vinílicos y cerámicos. Alto rendimiento.", 72.00),
    ("Decapante para pisos", "Pisos y superficies", "InduClean", "Galón 4L", "en_stock", False,
     "Remueve ceras viejas y residuos antes de aplicar acabado nuevo.", 68.00),
    ("Limpia pisos perfumado", "Pisos y superficies", "Sapolio", "Galón 4L", "en_stock", False,
     "Aroma duradero, espuma controlada. Compatible con máquina restregadora.", 38.00),

    ("Papel higiénico jumbo doble hoja", "Papel y descartables", "Sapolio", "Caja 12 rollos x 250m", "en_stock", True,
     "Doble hoja blanco premium para dispensador jumbo industrial.", 180.00),
    ("Toalla de manos en Z doble hoja", "Papel y descartables", "CleanMaster", "Caja 20 paquetes x 200u", "en_stock", False,
     "Para dispensador Z, alta absorción, ideal para baños corporativos.", 145.00),
    ("Guantes de nitrilo descartables", "Papel y descartables", "Sanitex", "Caja 100u talla M", "en_stock", False,
     "Sin polvo, ambidiestros, alta sensibilidad táctil. Disponibles S/M/L/XL.", 65.00),

    ("Dispensador de papel jumbo plástico", "Dispensadores y accesorios", "Sapolio", "Unidad", "en_stock", True,
     "Capacidad rollo 300m, llave de seguridad, color blanco ABS.", 89.00),
    ("Dispensador de jabón líquido 1L", "Dispensadores y accesorios", "CleanMaster", "Unidad", "en_stock", False,
     "Recargable con bidón a granel, válvula antigoteo, pulsador suave.", 72.00),
    ("Carro de limpieza profesional 2 baldes", "Dispensadores y accesorios", "InduClean", "Unidad", "bajo_pedido", False,
     "Estructura metálica + 2 baldes 25L con prensa de rodillos.", 580.00),

    ("Detergente lavandería líquido alta concentración", "Lavandería industrial", "InduClean", "Bidón 20L", "en_stock", True,
     "Para máquinas industriales 25-100kg. Excelente remoción de manchas.", 215.00),
    ("Suavizante neutralizante lavandería", "Lavandería industrial", "Sapolio", "Bidón 20L", "en_stock", False,
     "Suaviza fibras y neutraliza pH alcalino residual del lavado.", 168.00),
    ("Blanqueador oxigenado sin cloro", "Lavandería industrial", "EcoBrill", "Bidón 20L", "en_stock", False,
     "Alternativa ecológica al cloro para prendas blancas y de color.", 195.00),

    ("Aspiradora industrial polvo-líquido 30L", "Equipos y maquinaria", "InduClean", "Unidad 1400W", "en_stock", True,
     "Tanque 30L acero inoxidable, succión 2200mm H₂O, ideal para hoteles e industria.", 1450.00),
    ("Hidrolavadora profesional 150 bar", "Equipos y maquinaria", "CleanMaster", "Unidad 2300W", "bajo_pedido", False,
     "Motor inducción, lanza profesional, ideal para flotas y exteriores.", 1890.00),
]


class Command(BaseCommand):
    help = "Carga datos demo idempotentes para ProClean."

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true", help="Borra productos demo y re-siembra.")

    @transaction.atomic
    def handle(self, *args, **opts):
        if opts["reset"]:
            self.stdout.write("Borrando productos demo...")
            Producto.objects.all().delete()

        cats = {}
        for nombre, icono, desc, orden in CATEGORIAS:
            cat, _ = Categoria.objects.get_or_create(
                nombre=nombre,
                defaults={"icono": icono, "descripcion": desc, "orden": orden},
            )
            cats[nombre] = cat
        self.stdout.write(self.style.SUCCESS(f"[OK] {len(cats)} categorias"))

        marcas = {}
        for nombre in MARCAS:
            m, _ = Marca.objects.get_or_create(nombre=nombre)
            marcas[nombre] = m
        self.stdout.write(self.style.SUCCESS(f"[OK] {len(marcas)} marcas"))

        from decimal import Decimal

        created = 0
        updated = 0
        for nombre, cat_nombre, marca_nombre, presentacion, disp, destacado, desc, precio in PRODUCTOS:
            sku = self._build_sku(nombre, marca_nombre)
            obj, was_created = Producto.objects.get_or_create(
                sku=sku,
                defaults={
                    "nombre": nombre,
                    "categoria": cats[cat_nombre],
                    "marca": marcas[marca_nombre],
                    "presentacion": presentacion,
                    "disponibilidad": disp,
                    "destacado": destacado,
                    "descripcion_corta": desc,
                    "precio_referencia": Decimal(str(precio)),
                    "descuento_volumen": "Desde 10 unid: 5% · Desde 50: 10% · Desde 100: 15%",
                },
            )
            if was_created:
                created += 1
            else:
                # Actualizar precio si quedó en 0
                if obj.precio_referencia == 0:
                    obj.precio_referencia = Decimal(str(precio))
                    obj.descuento_volumen = "Desde 10 unid: 5% · Desde 50: 10% · Desde 100: 15%"
                    obj.save(update_fields=["precio_referencia", "descuento_volumen"])
                    updated += 1
        self.stdout.write(self.style.SUCCESS(
            f"[OK] {created} productos creados, {updated} actualizados con precios "
            f"({len(PRODUCTOS) - created - updated} sin cambios)"
        ))

        self.stdout.write(self.style.SUCCESS("\nSeed completo. Ingresa al admin para personalizar."))

    @staticmethod
    def _build_sku(nombre, marca):
        from django.utils.text import slugify
        slug = slugify(nombre)[:20].upper().replace("-", "")
        return f"{marca[:3].upper()}-{slug[:18]}"
