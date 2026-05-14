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

MARCAS = ["LimpiaPro", "CleanMaster", "EcoBrill", "Sanitex", "InduClean"]

PRODUCTOS = [
    # (nombre, categoria, marca, presentacion, disponibilidad, destacado, descripcion_corta)
    ("Detergente líquido multiuso concentrado", "Detergentes y desengrasantes", "LimpiaPro", "Galón 4L", "en_stock", True,
     "Detergente neutro de alta espuma para limpieza general. Biodegradable, pH 7."),
    ("Desengrasante alcalino industrial", "Detergentes y desengrasantes", "InduClean", "Bidón 20L", "en_stock", False,
     "Desengrasante de uso pesado para cocinas industriales y planta de producción."),
    ("Limpiador desinfectante multisuperficie", "Detergentes y desengrasantes", "Sanitex", "Galón 4L", "en_stock", True,
     "Limpia y desinfecta en un solo paso. Aroma lavanda. DIGESA aprobado."),

    ("Amonio cuaternario 5ta generación", "Desinfectantes y sanitizantes", "Sanitex", "Galón 4L", "en_stock", True,
     "Desinfectante hospitalario de amplio espectro. Concentración 1:200."),
    ("Hipoclorito de sodio 7.5%", "Desinfectantes y sanitizantes", "InduClean", "Bidón 20L", "en_stock", False,
     "Lejía industrial estabilizada para desinfección de superficies y aguas."),
    ("Alcohol etílico 70° desnaturalizado", "Desinfectantes y sanitizantes", "CleanMaster", "Galón 4L", "en_stock", False,
     "Sanitizante de manos y superficies. Listo para usar."),
    ("Peróxido de hidrógeno estabilizado", "Desinfectantes y sanitizantes", "EcoBrill", "Bidón 5L", "bajo_pedido", False,
     "Desinfectante ecológico de descomposición rápida, ideal para áreas alimentarias."),

    ("Limpiador removedor de sarro", "Productos para baño", "LimpiaPro", "Botella 1L", "en_stock", False,
     "Removedor ácido fosfórico para sarro, óxido e incrustaciones en sanitarios."),
    ("Aromatizador desinfectante para inodoros", "Productos para baño", "EcoBrill", "Galón 4L", "en_stock", False,
     "Doble acción: aromatiza y desinfecta. Disponible en pino, lavanda y cítrico."),
    ("Limpiador urinario concentrado", "Productos para baño", "Sanitex", "Galón 4L", "en_stock", False,
     "Elimina manchas y olores de urinarios. Fórmula tensoactiva concentrada."),

    ("Cera líquida abrillantadora", "Pisos y superficies", "CleanMaster", "Galón 4L", "en_stock", True,
     "Acabado mate-brillante para pisos vinílicos y cerámicos. Alto rendimiento."),
    ("Decapante para pisos", "Pisos y superficies", "InduClean", "Galón 4L", "en_stock", False,
     "Remueve ceras viejas y residuos antes de aplicar acabado nuevo."),
    ("Limpia pisos perfumado", "Pisos y superficies", "LimpiaPro", "Galón 4L", "en_stock", False,
     "Aroma duradero, espuma controlada. Compatible con máquina restregadora."),

    ("Papel higiénico jumbo doble hoja", "Papel y descartables", "LimpiaPro", "Caja 12 rollos x 250m", "en_stock", True,
     "Doble hoja blanco premium para dispensador jumbo industrial."),
    ("Toalla de manos en Z doble hoja", "Papel y descartables", "CleanMaster", "Caja 20 paquetes x 200u", "en_stock", False,
     "Para dispensador Z, alta absorción, ideal para baños corporativos."),
    ("Guantes de nitrilo descartables", "Papel y descartables", "Sanitex", "Caja 100u talla M", "en_stock", False,
     "Sin polvo, ambidiestros, alta sensibilidad táctil. Disponibles S/M/L/XL."),

    ("Dispensador de papel jumbo plástico", "Dispensadores y accesorios", "LimpiaPro", "Unidad", "en_stock", True,
     "Capacidad rollo 300m, llave de seguridad, color blanco ABS."),
    ("Dispensador de jabón líquido 1L", "Dispensadores y accesorios", "CleanMaster", "Unidad", "en_stock", False,
     "Recargable con bidón a granel, válvula antigoteo, pulsador suave."),
    ("Carro de limpieza profesional 2 baldes", "Dispensadores y accesorios", "InduClean", "Unidad", "bajo_pedido", False,
     "Estructura metálica + 2 baldes 25L con prensa de rodillos."),

    ("Detergente lavandería líquido alta concentración", "Lavandería industrial", "InduClean", "Bidón 20L", "en_stock", True,
     "Para máquinas industriales 25-100kg. Excelente remoción de manchas."),
    ("Suavizante neutralizante lavandería", "Lavandería industrial", "LimpiaPro", "Bidón 20L", "en_stock", False,
     "Suaviza fibras y neutraliza pH alcalino residual del lavado."),
    ("Blanqueador oxigenado sin cloro", "Lavandería industrial", "EcoBrill", "Bidón 20L", "en_stock", False,
     "Alternativa ecológica al cloro para prendas blancas y de color."),

    ("Aspiradora industrial polvo-líquido 30L", "Equipos y maquinaria", "InduClean", "Unidad 1400W", "en_stock", True,
     "Tanque 30L acero inoxidable, succión 2200mm H₂O, ideal para hoteles e industria."),
    ("Hidrolavadora profesional 150 bar", "Equipos y maquinaria", "CleanMaster", "Unidad 2300W", "bajo_pedido", False,
     "Motor inducción, lanza profesional, ideal para flotas y exteriores."),
]


class Command(BaseCommand):
    help = "Carga datos demo idempotentes para LimpiaPro."

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

        created = 0
        for nombre, cat_nombre, marca_nombre, presentacion, disp, destacado, desc in PRODUCTOS:
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
                },
            )
            if was_created:
                created += 1
        self.stdout.write(self.style.SUCCESS(f"[OK] {created} productos creados ({len(PRODUCTOS) - created} ya existian)"))

        self.stdout.write(self.style.SUCCESS("\nSeed completo. Ingresa al admin para personalizar."))

    @staticmethod
    def _build_sku(nombre, marca):
        from django.utils.text import slugify
        slug = slugify(nombre)[:20].upper().replace("-", "")
        return f"{marca[:3].upper()}-{slug[:18]}"
