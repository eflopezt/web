"""Carga datos demo idempotentes: 11 categorías + 19 marcas + ~65 productos.

Las descripciones son originales redactadas para ProClean Servid Innova.
NO se copian textos ni imágenes de terceros: las cards usan emoji fallback.
"""

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
    ("Equipos de protección personal", "hard-hat", "EPP industrial: mascarillas, respiradores, guantes, lentes de seguridad, cascos y mandiles.", 9),
    ("Bioseguridad y sanitización", "shield-check", "Geles antibacteriales, alcohol institucional, tapetes sanitizantes, termómetros y atomizadores.", 10),
    ("Paños industriales y abrasivos", "layers", "Paños de microfibra, paños técnicos absorbentes, esponjas verdes y estropajos institucionales.", 11),
]

MARCAS = [
    "Sapolio", "Poett", "Marsella", "Elite", "Dkasa", "Suave", "Scott",
    "Paracas", "Daryza", "Kaz", "Rendipel", "Sumac", "Brisol",
    "Wypall", "Moldex", "Clorox", "Lysol", "3M", "Nova",
]

PRODUCTOS = [
    # (nombre, categoria, marca, presentacion, disponibilidad, destacado, descripcion_corta, precio_referencia)

    # ============ Detergentes y desengrasantes ============
    ("Detergente líquido multiuso concentrado", "Detergentes y desengrasantes", "Sapolio", "Galón 4L", "en_stock", True,
     "Limpiador neutro de uso general para superficies lavables. Espuma controlada, biodegradable.", 48.90),
    ("Desengrasante alcalino industrial", "Detergentes y desengrasantes", "Marsella", "Bidón 20L", "en_stock", False,
     "Para grasa pesada en planchas, freidoras, motores y áreas de planta. Diluible 1:10.", 89.50),
    ("Detergente en polvo multiuso", "Detergentes y desengrasantes", "Marsella", "Bolsa 13.5 kg", "en_stock", True,
     "Polvo concentrado para limpieza general manual o en máquina, alto rendimiento.", 78.00),
    ("Limpiador desinfectante multisuperficie", "Detergentes y desengrasantes", "Poett", "Galón 4L", "en_stock", True,
     "Limpia y aromatiza en un solo paso, formulado para áreas de alto tráfico.", 55.00),
    ("Lavavajillas líquido concentrado", "Detergentes y desengrasantes", "Sapolio", "Galón 4L", "en_stock", False,
     "Detergente para vajilla manual, corta grasa y respeta las manos.", 36.50),
    ("Jabón en barra azul institucional", "Detergentes y desengrasantes", "Marsella", "Caja 36 barras x 200g", "en_stock", False,
     "Jabón tradicional multiuso para prelavado de ropa, baño y cocina.", 95.00),
    ("Desengrasante cítrico ecológico", "Detergentes y desengrasantes", "Daryza", "Bidón 5L", "en_stock", False,
     "Limpiador biodegradable a base de aceites cítricos, sin solventes derivados de petróleo.", 88.00),

    # ============ Desinfectantes y sanitizantes ============
    ("Amonio cuaternario 5ta generación", "Desinfectantes y sanitizantes", "Lysol", "Galón 4L", "en_stock", True,
     "Desinfectante de amplio espectro para superficies de contacto. Dilución 1:200 para uso institucional.", 65.00),
    ("Hipoclorito de sodio 7.5%", "Desinfectantes y sanitizantes", "Clorox", "Bidón 20L", "en_stock", False,
     "Lejía estabilizada para tratamiento de aguas, sanitización de superficies y blanqueo.", 78.00),
    ("Alcohol etílico 70° desnaturalizado", "Desinfectantes y sanitizantes", "Dkasa", "Galón 4L", "en_stock", True,
     "Listo para usar en superficies y manos. Evaporación rápida, sin residuos.", 42.00),
    ("Peróxido de hidrógeno estabilizado 7%", "Desinfectantes y sanitizantes", "Daryza", "Bidón 5L", "bajo_pedido", False,
     "Desinfectante oxidante, descomposición ecológica, apto para áreas de manipulación alimentaria.", 95.00),
    ("Lejía perfumada lavanda", "Desinfectantes y sanitizantes", "Sapolio", "Bidón 5L", "en_stock", False,
     "Hipoclorito perfumado para uso doméstico e institucional ligero.", 38.00),
    ("Limpiatodo desinfectante antibacterial", "Desinfectantes y sanitizantes", "Poett", "Galón 4L", "en_stock", True,
     "Multisuperficies con fragancia floral prolongada, acción antibacterial.", 58.00),

    # ============ Productos para baño ============
    ("Removedor de sarro y óxido", "Productos para baño", "Sapolio", "Botella 1L", "en_stock", False,
     "Fórmula ácida para incrustaciones de calcio, sarro y óxido en sanitarios.", 18.50),
    ("Aromatizador desinfectante para inodoros", "Productos para baño", "Brisol", "Galón 4L", "en_stock", True,
     "Doble acción aromatizante y desinfectante. Variantes pino, lavanda y bouquet floral.", 52.00),
    ("Limpiador para urinarios concentrado", "Productos para baño", "Poett", "Galón 4L", "en_stock", False,
     "Elimina sales urinarias y olores en una sola aplicación.", 49.00),
    ("Pastilla aromatizante para inodoro", "Productos para baño", "Brisol", "Caja 24 unidades", "en_stock", False,
     "Aroma durable, libera fragancia con cada descarga.", 65.00),
    ("Limpia vidrios y espejos", "Productos para baño", "Sapolio", "Atomizador 500ml", "en_stock", False,
     "Sin residuos ni manchas, secado rápido para espejos y mamparas.", 14.50),

    # ============ Pisos y superficies ============
    ("Cera líquida abrillantadora premium", "Pisos y superficies", "Dkasa", "Galón 4L", "en_stock", True,
     "Acabado satinado para pisos vinílicos y cerámicos, alto tráfico.", 72.00),
    ("Decapante para pisos vinílicos", "Pisos y superficies", "Marsella", "Galón 4L", "en_stock", False,
     "Remueve ceras antiguas y residuos polimerizados, preparando el piso para nuevo acabado.", 68.00),
    ("Limpiapisos perfumado floral", "Pisos y superficies", "Poett", "Galón 4L", "en_stock", True,
     "Aroma duradero, baja espuma para uso con máquina restregadora o trapeador.", 38.00),
    ("Limpiapisos antibacterial kazlim", "Pisos y superficies", "Kaz", "Bidón 16L", "en_stock", False,
     "Acción germicida con fragancia limón, ideal para pisos en industria alimentaria.", 110.00),
    ("Sellador acrílico para pisos", "Pisos y superficies", "Dkasa", "Galón 4L", "bajo_pedido", False,
     "Capa protectora antes de aplicar cera, prolonga la vida del acabado.", 95.00),

    # ============ Papel y descartables ============
    ("Papel higiénico jumbo doble hoja", "Papel y descartables", "Elite", "Caja 12 rollos x 250m", "en_stock", True,
     "Premium doble hoja blanco, compatible con dispensador jumbo industrial.", 180.00),
    ("Papel higiénico doméstico 4 rollos", "Papel y descartables", "Suave", "Pack 4 rollos x 40m", "en_stock", False,
     "Doble hoja resistente para uso residencial e institucional.", 12.50),
    ("Papel higiénico premium gofrado", "Papel y descartables", "Sumac", "Pack 6 rollos x 500m", "en_stock", True,
     "Pulpa virgen 100%, doble hoja gofrada para baños corporativos premium.", 22.00),
    ("Papel higiénico Paracas doble hoja", "Papel y descartables", "Paracas", "Pack 4 rollos x 40m", "en_stock", False,
     "Hecho en Perú, doble hoja con textura suave punta a punta.", 11.00),
    ("Toalla de manos en Z doble hoja", "Papel y descartables", "Elite", "Caja 20 paquetes x 200u", "en_stock", True,
     "Para dispensador Z, alta absorción, baño corporativo o industrial.", 145.00),
    ("Rollo multiuso Excellence 200 paños", "Papel y descartables", "Elite", "Caja 6 rollos x 200 paños", "en_stock", True,
     "Doble hoja absorbente, ideal para cocina industrial y limpieza intensiva.", 165.00),
    ("Rollo papel toalla institucional Rendipel PRO", "Papel y descartables", "Rendipel", "Caja 6 rollos x 100m", "en_stock", False,
     "500 hojas más gruesas, mayor absorción para áreas de alto consumo.", 138.00),
    ("Servilleta cocktail blanca", "Papel y descartables", "Elite", "Paquete 100 unidades", "en_stock", False,
     "Servilleta doble hoja para restaurantes, hoteles y eventos.", 9.50),
    ("Servilleta tipo dispensador", "Papel y descartables", "Scott", "Caja 24 paquetes x 250u", "en_stock", False,
     "Para dispensador de mesa, doble hoja, alta resistencia.", 195.00),
    ("Guantes de nitrilo descartables", "Papel y descartables", "Nova", "Caja 100u talla M", "en_stock", True,
     "Sin polvo, ambidiestros, alta sensibilidad táctil. Tallas S/M/L/XL.", 65.00),
    ("Guantes de látex con polvo", "Papel y descartables", "Nova", "Caja 100u talla L", "en_stock", False,
     "Para uso general, limpieza y manipulación liviana.", 42.00),
    ("Bolsa de basura industrial roja", "Papel y descartables", "Nova", "Paquete 100 unidades 30\"x40\"", "en_stock", False,
     "Polietileno grueso para residuos biocontaminados (uso hospitalario).", 75.00),
    ("Bolsa de basura negra resistente", "Papel y descartables", "Nova", "Paquete 100 unidades 30\"x40\"", "en_stock", True,
     "Calibre 2, soporta cargas pesadas hasta 30 kg.", 58.00),

    # ============ Dispensadores y accesorios ============
    ("Dispensador de papel jumbo ABS", "Dispensadores y accesorios", "Elite", "Unidad", "en_stock", True,
     "Capacidad rollo 300m, llave de seguridad anti-vandalismo, color blanco.", 89.00),
    ("Dispensador papel toalla Z", "Dispensadores y accesorios", "Elite", "Unidad", "en_stock", False,
     "Para paquetes Z, recarga frontal, ABS resistente.", 75.00),
    ("Dispensador de jabón líquido 1L", "Dispensadores y accesorios", "Dkasa", "Unidad", "en_stock", False,
     "Recargable a granel, válvula antigoteo, palanca ergonómica.", 72.00),
    ("Dispensador gel automático sin contacto", "Dispensadores y accesorios", "Dkasa", "Unidad 1000ml", "bajo_pedido", True,
     "Sensor infrarrojo, ideal para áreas de alto flujo y bioseguridad.", 285.00),
    ("Carro de limpieza profesional 2 baldes", "Dispensadores y accesorios", "Marsella", "Unidad", "bajo_pedido", False,
     "Estructura metálica con 2 baldes 25L y prensa de rodillos.", 580.00),
    ("Mopa de microfibra con mango", "Dispensadores y accesorios", "Dkasa", "Unidad", "en_stock", False,
     "Mopa lavable múltiples usos, mango telescópico aluminio.", 48.00),
    ("Escoba industrial cerdas duras", "Dispensadores y accesorios", "Sapolio", "Unidad", "en_stock", False,
     "Cabeza ancha 40 cm con mango de madera reforzado para barrido pesado.", 28.00),

    # ============ Lavandería industrial ============
    ("Detergente lavandería líquido alta concentración", "Lavandería industrial", "Marsella", "Bidón 20L", "en_stock", True,
     "Para máquinas industriales 25-100 kg, alta remoción de manchas profundas.", 215.00),
    ("Suavizante neutralizante", "Lavandería industrial", "Sapolio", "Bidón 20L", "en_stock", False,
     "Neutraliza pH residual del lavado y suaviza fibras textiles.", 168.00),
    ("Blanqueador oxigenado sin cloro", "Lavandería industrial", "Daryza", "Bidón 20L", "en_stock", False,
     "Alternativa segura al cloro para prendas blancas y de color delicado.", 195.00),
    ("Quitamanchas concentrado prelavado", "Lavandería industrial", "Marsella", "Bidón 5L", "en_stock", False,
     "Para manchas de grasa, sangre y café antes del ciclo principal.", 105.00),

    # ============ Equipos y maquinaria ============
    ("Aspiradora industrial polvo-líquido 30L", "Equipos y maquinaria", "Nova", "Unidad 1400W", "en_stock", True,
     "Tanque 30L acero inoxidable, succión 2200mm H₂O para hoteles e industria.", 1450.00),
    ("Hidrolavadora profesional 150 bar", "Equipos y maquinaria", "Nova", "Unidad 2300W", "bajo_pedido", False,
     "Motor de inducción para uso continuo, ideal para flotas y exteriores.", 1890.00),
    ("Máquina restregadora de pisos", "Equipos y maquinaria", "Nova", "Unidad 17 pulgadas", "bajo_pedido", False,
     "Restregadora monodisco para encerado, abrillantado y limpieza profunda.", 2950.00),
    ("Pulidora orbital eléctrica", "Equipos y maquinaria", "Nova", "Unidad 1100W", "bajo_pedido", False,
     "Para pisos vinílicos y porcelanato, regulación de velocidad variable.", 1650.00),

    # ============ Equipos de protección personal ============
    ("Mascarilla KN95 5 capas", "Equipos de protección personal", "3M", "Caja 50 unidades", "en_stock", True,
     "Filtración ≥95% partículas, ajuste ergonómico nasal y elásticos reforzados.", 95.00),
    ("Mascarilla quirúrgica triple capa", "Equipos de protección personal", "Moldex", "Caja 50 unidades", "en_stock", True,
     "Tres capas con tira nasal moldeable, uso institucional.", 28.00),
    ("Respirador media cara con filtro", "Equipos de protección personal", "3M", "Unidad + 2 filtros", "en_stock", False,
     "Filtros P2 reemplazables para áreas con polvo o vapores químicos ligeros.", 195.00),
    ("Guantes de seguridad industrial nitrilo", "Equipos de protección personal", "Moldex", "Par talla L", "en_stock", False,
     "Recubrimiento nitrilo para manejo de químicos diluidos y materiales abrasivos.", 18.50),
    ("Lentes de seguridad transparentes", "Equipos de protección personal", "3M", "Unidad", "en_stock", False,
     "Protección antiimpacto y antirayado, patillas ergonómicas.", 22.00),
    ("Casco de seguridad industrial ABS", "Equipos de protección personal", "Moldex", "Unidad color amarillo", "en_stock", False,
     "Norma ANSI clase E, ajuste con perilla giratoria.", 38.00),
    ("Mandil PVC industrial", "Equipos de protección personal", "Moldex", "Unidad amarillo 1.2m", "en_stock", False,
     "Resistente a químicos y humedad para cocina industrial y lavandería.", 32.00),
    ("Botas de seguridad PVC antideslizantes", "Equipos de protección personal", "Moldex", "Par talla 42", "en_stock", False,
     "Caña alta para limpieza con químicos, suela antideslizante.", 65.00),

    # ============ Bioseguridad y sanitización ============
    ("Gel antibacterial 70° con dispensador", "Bioseguridad y sanitización", "Dkasa", "Botella 1L con válvula", "en_stock", True,
     "Hidroalcohólico con glicerina humectante, secado rápido sin residuo pegajoso.", 22.00),
    ("Alcohol institucional 70° granel", "Bioseguridad y sanitización", "Dkasa", "Bidón 20L", "en_stock", True,
     "Alcohol desnaturalizado para recarga de dispensadores y atomizadores.", 165.00),
    ("Termómetro digital infrarrojo sin contacto", "Bioseguridad y sanitización", "3M", "Unidad", "en_stock", False,
     "Lectura en 1 segundo, rango 32-43°C, ideal para control de accesos.", 95.00),
    ("Atomizador industrial 1L con gatillo", "Bioseguridad y sanitización", "Dkasa", "Unidad transparente", "en_stock", False,
     "Para preparación de soluciones desinfectantes y sanitizantes diluidas.", 14.00),
    ("Tapete sanitizante para ingreso", "Bioseguridad y sanitización", "Moldex", "Unidad 60x80cm", "en_stock", False,
     "Estructura plástica con reservorio para solución sanitizante de calzado.", 85.00),

    # ============ Paños industriales y abrasivos ============
    ("Paño microfibra azul institucional", "Paños industriales y abrasivos", "Wypall", "Paquete 10 unidades 40x40cm", "en_stock", True,
     "Microfibra 80/20, lavable, alta capacidad de captura de polvo y partículas.", 38.00),
    ("Paño absorbente industrial Wypall L40", "Paños industriales y abrasivos", "Wypall", "Caja 200 paños 38x35cm", "en_stock", True,
     "Paño desechable de pulpa, alta absorción para mantenimiento y derrames ligeros.", 195.00),
    ("Paño técnico Wypall X80 alto rendimiento", "Paños industriales y abrasivos", "Wypall", "Caja 150 paños 31x32cm", "en_stock", False,
     "Paño hidroentrelazado reutilizable, resistente a solventes y aceites.", 245.00),
    ("Trapo industrial blanco granel", "Paños industriales y abrasivos", "Nova", "Saco 10 kg", "en_stock", False,
     "Trapo de algodón reciclado, ideal para limpieza de aceites y grasas en taller.", 88.00),
    ("Esponja verde abrasiva doble cara", "Paños industriales y abrasivos", "Sapolio", "Pack 10 unidades", "en_stock", False,
     "Esponja amarilla con fibra verde, para vajilla y superficies resistentes.", 18.00),
    ("Estropajo de acero inoxidable", "Paños industriales y abrasivos", "Sapolio", "Pack 6 unidades", "en_stock", False,
     "Para remoción de residuos quemados en planchas y ollas industriales.", 14.00),
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
