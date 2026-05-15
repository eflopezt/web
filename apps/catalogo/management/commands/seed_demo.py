"""Carga datos demo: catálogo basado en productos reales del mercado PE B2B.

Fuente factual: catálogo CATALOGO-DE-LIMPIEZA.pdf compartido por el cliente.
Las descripciones son originales redactadas para ProClean Servid Innova.
NO se copia texto literal de terceros: las cards usan ilustraciones SVG por categoría.
"""

import re

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from apps.catalogo.models import Categoria, Marca, Producto


def make_sku(nombre: str, marca: str) -> str:
    """Genera SKU corto y único: PRE-XXXX desde marca + slug del nombre."""
    marca_pref = re.sub(r"[^A-Z]", "", marca.upper())[:3] or "PRO"
    slug = slugify(nombre).upper().replace("-", "")[:8]
    return f"{marca_pref}-{slug}"


CATEGORIAS = [
    ("Detergentes y desengrasantes", "sparkles", "Detergentes industriales en polvo y líquido, desengrasantes alcalinos y ácidos para cocina, planta y mantenimiento.", 1),
    ("Desinfectantes y sanitizantes", "shield", "Hipoclorito industrial, amonios cuaternarios, ácido peracético y alcohol para sanitización de áreas críticas.", 2),
    ("Productos para baño", "droplet", "Limpiadores de inodoros, sarro, urinarios, vidrios y desinfección sanitaria.", 3),
    ("Pisos y superficies", "broom", "Ceras, abrillantadores, decapantes y limpiapisos para vinílico, porcelanato y cemento.", 4),
    ("Papel y descartables", "scroll", "Papel higiénico jumbo, papel toalla interfoliada, servilletas y guantes desechables.", 5),
    ("Dispensadores y accesorios", "package", "Dispensadores Elite/Kimberly de papel, jabón y alcohol, escobillones, recogedores y pedilúvios.", 6),
    ("Lavandería industrial", "shirt", "Detergentes, suavizantes, blanqueadores y neutralizantes para lavandería profesional.", 7),
    ("Equipos y maquinaria", "wrench", "Aspiradoras industriales, restregadoras, hidrolavadoras y pulidoras.", 8),
    ("Equipos de protección personal", "hard-hat", "EPP industrial: mascarillas, respiradores, guantes, lentes de seguridad, cascos y mandiles.", 9),
    ("Bioseguridad y sanitización", "shield-check", "Jabones y alcohol gel antibacterial Kimberly-Clark / Esral, ácido peracético, dispensadores con sensor.", 10),
    ("Paños industriales y abrasivos", "layers", "Paños Wypall / Wype Master, esponjas Scotch Brite, paños de microfibra y estropajos.", 11),
    ("Escobas, recogedores y tachos", "trash-2", "Escobas FBK, escobillones, recogedores flip, jaladores de agua, tachos KeyPlast/Bess y bolsas de basura.", 12),
]

MARCAS = [
    # Papel
    "Elite", "Kimberly-Clark", "Suprema", "Sumaq", "Cana", "Suave", "Scott", "Paracas", "Sumac", "Rendipel",
    # Limpieza institucional
    "Sapolio", "Poett", "Marsella", "Dkasa", "Brisol", "Daryza", "Kaz", "Nea Detar", "PFS",
    # Bioseguridad
    "Esral", "Bafagón", "Calorimo", "Alkofarma", "Tianq",
    # Paños y esponjas
    "Wypall", "Wype Master", "Scotch Brite", "Klane",
    # Herramientas y plásticos
    "FBK", "Prolimpio", "Neco", "KeyPlast", "Bess",
    # Otros
    "Clorox", "Lysol", "3M", "Nova",
]


PRODUCTOS = [
    # =====================================================================
    # PAPEL Y DESCARTABLES
    # =====================================================================
    # Papel higiénico jumbo
    ("Papel higiénico jumbo doble hoja Elite 300m", "Papel y descartables", "Elite", "Caja 6 rollos x 300m", "en_stock", True,
     "Rollo industrial doble hoja blanco premium para dispensador jumbo, alta absorción y resistencia.", 165.00),
    ("Papel higiénico jumbo doble hoja Elite 500m", "Papel y descartables", "Elite", "Caja 6 rollos x 500m", "en_stock", True,
     "Versión extendida para baños de alto tráfico, reduce frecuencia de recarga.", 245.00),
    ("Papel higiénico jumbo Kimberly-Clark 300m", "Papel y descartables", "Kimberly-Clark", "Caja 6 rollos x 300m", "en_stock", False,
     "Rollo institucional Kimberly con tecnología absorbente, ideal para oficinas corporativas.", 175.00),
    ("Papel higiénico jumbo Kimberly-Clark 500m", "Papel y descartables", "Kimberly-Clark", "Caja 6 rollos x 500m", "en_stock", True,
     "Mayor metraje, optimizado para hoteles, restaurantes y áreas de alto consumo.", 255.00),
    ("Papel higiénico jumbo Suprema 300m", "Papel y descartables", "Suprema", "Caja 6 rollos x 300m", "en_stock", False,
     "Doble hoja resistente, opción económica para uso institucional intensivo.", 135.00),
    ("Papel higiénico jumbo Sumaq 300m", "Papel y descartables", "Sumaq", "Caja 6 rollos x 300m", "en_stock", False,
     "Fabricado en Perú, doble hoja con buena absorción para uso comercial.", 128.00),
    ("Papel higiénico jumbo Sumaq 500m", "Papel y descartables", "Sumaq", "Caja 6 rollos x 500m", "en_stock", False,
     "Rendimiento extendido para clientes con alta rotación.", 195.00),
    ("Papel higiénico jumbo Cana 500m", "Papel y descartables", "Cana", "Caja 6 rollos x 500m", "en_stock", False,
     "Rollo institucional resistente, gran metraje para reducir recargas.", 188.00),
    ("Papel higiénico doméstico Suave Resiste Max", "Papel y descartables", "Suave", "Pack 4 rollos x 40m", "en_stock", False,
     "Doble hoja resistente para uso residencial y oficina.", 12.80),
    ("Papel higiénico premium Sumac Gofrado", "Papel y descartables", "Sumac", "Pack 6 rollos x 500m", "en_stock", True,
     "Pulpa virgen 100%, textura gofrada premium para baños corporativos.", 22.00),
    ("Papel higiénico Paracas Doble Hoja", "Papel y descartables", "Paracas", "Pack 4 rollos x 40m", "en_stock", False,
     "Producto peruano con textura suave punta a punta.", 11.00),

    # Papel toalla interfoliada y de mano
    ("Papel toalla interfoliada Elite 200m", "Papel y descartables", "Elite", "Caja 20 paquetes x 200u", "en_stock", True,
     "Toalla en Z doble hoja, compatible con dispensador automático, alta absorción.", 145.00),
    ("Papel toalla interfoliada Elite 300m", "Papel y descartables", "Elite", "Caja 12 paquetes x 300u", "en_stock", False,
     "Versión rendidora para áreas con tráfico medio-alto.", 175.00),
    ("Papel toalla interfoliada Kimberly-Clark 200m", "Papel y descartables", "Kimberly-Clark", "Caja 20 paquetes x 200u", "en_stock", False,
     "Toalla institucional para dispensador, doble hoja resistente en húmedo.", 155.00),
    ("Papel toalla interfoliada Sumaq 200m", "Papel y descartables", "Sumaq", "Caja 20 paquetes x 200u", "en_stock", False,
     "Toalla en Z económica, compatible con dispensadores estándar.", 125.00),
    ("Papel toalla interfoliada Cana 200m", "Papel y descartables", "Cana", "Caja 20 paquetes x 200u", "en_stock", False,
     "Hoja sencilla resistente, opción para alto consumo institucional.", 118.00),
    ("Rollo multiuso Elite Excellence 6639", "Papel y descartables", "Elite", "Caja 6 rollos x 200 paños", "en_stock", True,
     "Doble hoja absorbente, ideal para cocina industrial y limpieza intensiva.", 165.00),
    ("Rollo papel toalla Rendipel PRO 100m", "Papel y descartables", "Rendipel", "Caja 6 rollos x 100m", "en_stock", False,
     "500 hojas más gruesas, mayor absorción para áreas de alto consumo.", 138.00),
    ("Servilleta cocktail Elite blanca", "Papel y descartables", "Elite", "Paquete 100 unidades", "en_stock", False,
     "Doble hoja para restaurantes, hoteles y eventos corporativos.", 9.50),
    ("Servilleta institucional Scott", "Papel y descartables", "Scott", "Caja 24 paquetes x 250u", "en_stock", False,
     "Para dispensador de mesa, doble hoja, alta resistencia.", 195.00),

    # Guantes y bolsas (descartables)
    ("Guantes nitrilo sin polvo talla M", "Papel y descartables", "Nova", "Caja 100 unidades", "en_stock", True,
     "Ambidiestros, alta sensibilidad táctil, libres de látex. También en S/L/XL.", 65.00),
    ("Guantes nitrilo sin polvo talla L", "Papel y descartables", "Nova", "Caja 100 unidades", "en_stock", False,
     "Espesor 4 mil, resistencia a químicos diluidos y manipulación de alimentos.", 65.00),
    ("Guantes látex con polvo talla M", "Papel y descartables", "Nova", "Caja 100 unidades", "en_stock", False,
     "Para uso general, limpieza ligera y manipulación rápida.", 42.00),

    # =====================================================================
    # DESINFECTANTES Y SANITIZANTES
    # =====================================================================
    # Cloro industrial / hipoclorito (Sapolio, Daryza, Nea Detar)
    ("Lejía industrial Sapolio hipoclorito 4kg", "Desinfectantes y sanitizantes", "Sapolio", "Bidón 4kg", "en_stock", True,
     "Hipoclorito de sodio al 5.25% para desinfección de superficies y tratamiento de aguas.", 28.00),
    ("Lejía industrial Sapolio hipoclorito 10kg", "Desinfectantes y sanitizantes", "Sapolio", "Bidón 10kg", "en_stock", True,
     "Concentración estable, ideal para sanitización institucional diaria.", 58.00),
    ("Lejía industrial Sapolio hipoclorito 20kg", "Desinfectantes y sanitizantes", "Sapolio", "Bidón 20kg", "en_stock", False,
     "Presentación de volumen para clientes con alto consumo.", 105.00),
    ("Lejía industrial Daryza hipoclorito 16kg", "Desinfectantes y sanitizantes", "Daryza", "Bidón 16kg", "en_stock", False,
     "Hipoclorito estabilizado para procesos de limpieza profunda.", 88.00),
    ("Lejía industrial Daryza hipoclorito 5kg", "Desinfectantes y sanitizantes", "Daryza", "Bidón 5kg", "en_stock", False,
     "Presentación intermedia para PYMES y restaurantes.", 35.00),
    ("Lejía industrial Nea Detar hipoclorito 20kg", "Desinfectantes y sanitizantes", "Nea Detar", "Bidón 20kg", "en_stock", False,
     "Cloro institucional para sanitización en industria alimentaria.", 98.00),
    ("Lejía industrial Nea Detar hipoclorito 45kg", "Desinfectantes y sanitizantes", "Nea Detar", "Bidón 45kg", "bajo_pedido", False,
     "Presentación XXL para plantas y operadores logísticos multi-local.", 195.00),
    ("Lejía perfumada Sapolio Lavanda", "Desinfectantes y sanitizantes", "Sapolio", "Bidón 5L", "en_stock", False,
     "Hipoclorito perfumado para uso doméstico e institucional ligero.", 38.00),
    ("Lejía Clorox Original 3.78L", "Desinfectantes y sanitizantes", "Clorox", "Botella 3.78L", "en_stock", True,
     "Concentración estándar Clorox 5%, marca de confianza para uso institucional.", 35.00),

    # Amonio cuaternario (Bafagón)
    ("Amonio cuaternario Bafagón 5ta gen 250mL", "Desinfectantes y sanitizantes", "Bafagón", "Botella 250mL", "en_stock", True,
     "Concentrado al 10%, rinde 50L de solución desinfectante de amplio espectro. Apto sector salud.", 18.00),
    ("Amonio cuaternario Bafagón 5ta gen 1L", "Desinfectantes y sanitizantes", "Bafagón", "Botella 1L", "en_stock", True,
     "Rinde hasta 200L de solución desinfectante de uso hospitalario y áreas de alimentos.", 65.00),
    ("Amonio cuaternario Bafagón 5ta gen 5L", "Desinfectantes y sanitizantes", "Bafagón", "Bidón 5L", "en_stock", False,
     "Presentación granel para clientes con alto consumo institucional.", 285.00),

    # Ácido peracético
    ("Ácido peracético sanitizante 15% Bafagón", "Desinfectantes y sanitizantes", "Bafagón", "Bidón 2.5L", "en_stock", False,
     "Desinfectante oxidante de última generación al 15%, elimina virus, bacterias y hongos en superficies.", 145.00),
    ("Peróxido de hidrógeno estabilizado 7%", "Desinfectantes y sanitizantes", "Daryza", "Bidón 5L", "bajo_pedido", False,
     "Desinfectante de descomposición ecológica, apto industria alimentaria.", 95.00),

    # Limpiatodo desinfectante
    ("Limpiatodo Poett Lavanda 5L", "Desinfectantes y sanitizantes", "Poett", "Bidón 5L", "en_stock", True,
     "Antibacterial con fragancia floral prolongada, alta cobertura.", 58.00),
    ("Limpiatodo Poett Bouquet 5L", "Desinfectantes y sanitizantes", "Poett", "Bidón 5L", "en_stock", False,
     "Aroma floral suave con acción antibacterial certificada.", 58.00),
    ("Limpiatodo Dkasa Floral antibacterial", "Desinfectantes y sanitizantes", "Dkasa", "Bidón 4L", "en_stock", False,
     "Producto institucional con triple acción limpiadora.", 52.00),
    ("Limpiatodo Lysol multisuperficie 4L", "Desinfectantes y sanitizantes", "Lysol", "Galón 4L", "en_stock", False,
     "Marca premium con eficacia comprobada contra virus y bacterias.", 78.00),

    # =====================================================================
    # BIOSEGURIDAD Y SANITIZACIÓN
    # =====================================================================
    # Jabón antibacterial (Kimberly-Clark, Esral, Nea Detar)
    ("Jabón antibacterial Kimberly-Clark espuma 1L", "Bioseguridad y sanitización", "Kimberly-Clark", "Botella 1L", "en_stock", True,
     "Espuma instantánea, suave con la piel, ideal para dispensadores institucionales.", 45.00),
    ("Jabón antibacterial Kimberly-Clark espuma 2.5L", "Bioseguridad y sanitización", "Kimberly-Clark", "Bidón 2.5L", "en_stock", True,
     "Recarga de volumen para clientes con alto tráfico de personal.", 95.00),
    ("Jabón antibacterial Kimberly-Clark líquido 20L", "Bioseguridad y sanitización", "Kimberly-Clark", "Bidón 20L", "en_stock", False,
     "Granel institucional para recarga continua de dispensadores.", 425.00),
    ("Jabón antibacterial Esral espuma 1L", "Bioseguridad y sanitización", "Esral", "Botella 1L", "en_stock", False,
     "Fórmula espumante con triclosán, suave al lavado frecuente.", 38.00),
    ("Jabón antibacterial Esral líquido 2.5L", "Bioseguridad y sanitización", "Esral", "Bidón 2.5L", "en_stock", False,
     "Versión líquida para dispensador tradicional, fragancia suave.", 78.00),
    ("Jabón antibacterial Esral granel 20L", "Bioseguridad y sanitización", "Esral", "Bidón 20L", "en_stock", False,
     "Granel económico para empresas con muchos puntos de lavado.", 385.00),
    ("Jabón antibacterial Nea Detar 100mL", "Bioseguridad y sanitización", "Nea Detar", "Botella 100mL", "en_stock", False,
     "Presentación pocket para visitas y eventos.", 8.50),
    ("Jabón antibacterial Nea Detar 1L", "Bioseguridad y sanitización", "Nea Detar", "Botella 1L", "en_stock", False,
     "Líquido institucional, dosificación controlada.", 32.00),

    # Alcohol gel
    ("Alcohol gel antibacterial Kimberly-Clark 1L", "Bioseguridad y sanitización", "Kimberly-Clark", "Botella 1L con válvula", "en_stock", True,
     "Hidroalcohólico 70° con glicerina humectante, secado rápido sin pegajosidad.", 35.00),
    ("Alcohol gel antibacterial Kimberly-Clark 2.5L", "Bioseguridad y sanitización", "Kimberly-Clark", "Bidón 2.5L", "en_stock", False,
     "Recarga para dispensadores institucionales.", 78.00),
    ("Alcohol gel antibacterial Esral 1L", "Bioseguridad y sanitización", "Esral", "Botella 1L", "en_stock", False,
     "Gel 70° con humectante, ideal para control de accesos.", 28.00),
    ("Alcohol gel antibacterial Esral 2.5L", "Bioseguridad y sanitización", "Esral", "Bidón 2.5L", "en_stock", True,
     "Granel económico para puntos de sanitización fijos.", 65.00),
    ("Alcohol gel antibacterial Esral 20L", "Bioseguridad y sanitización", "Esral", "Bidón 20L", "en_stock", False,
     "Volumen para recarga continua, costo unitario reducido.", 385.00),

    # Alcohol líquido (Calorimo, Alkofarma, Tianq)
    ("Alcohol etílico 70° Calorimo 1L", "Bioseguridad y sanitización", "Calorimo", "Botella 1L", "en_stock", True,
     "Alcohol desnaturalizado 70° listo para usar en superficies y manos.", 22.00),
    ("Alcohol etílico 96° Alkofarma 1L", "Bioseguridad y sanitización", "Alkofarma", "Botella 1L", "en_stock", False,
     "Alcohol farmacéutico 96° para preparaciones técnicas y desinfección concentrada.", 28.00),
    ("Alcohol etílico 70° Tianq 3.5L", "Bioseguridad y sanitización", "Tianq", "Botella 3.5L", "en_stock", False,
     "Presentación intermedia para clínicas y oficinas medianas.", 75.00),
    ("Alcohol etílico 70° granel 20L", "Bioseguridad y sanitización", "Dkasa", "Bidón 20L", "en_stock", True,
     "Alcohol desnaturalizado granel para recarga de dispensadores y atomizadores.", 165.00),
    ("Termómetro digital infrarrojo sin contacto", "Bioseguridad y sanitización", "3M", "Unidad", "en_stock", False,
     "Lectura en 1 segundo, rango 32-43°C, ideal para control de accesos.", 95.00),
    ("Atomizador industrial 1L con gatillo", "Bioseguridad y sanitización", "Dkasa", "Unidad transparente", "en_stock", False,
     "Para preparación de soluciones desinfectantes diluidas.", 14.00),

    # =====================================================================
    # DETERGENTES Y DESENGRASANTES
    # =====================================================================
    # Detergente industrial (Sapolio, Daryza, Nea Detar)
    ("Detergente industrial Sapolio polvo 15kg", "Detergentes y desengrasantes", "Sapolio", "Saco 15kg", "en_stock", True,
     "Polvo concentrado para lavado manual y máquina, alto rendimiento institucional.", 185.00),
    ("Detergente industrial Daryza polvo 15kg", "Detergentes y desengrasantes", "Daryza", "Saco 15kg", "en_stock", False,
     "Detergente granulado con tensoactivos biodegradables, baja espuma.", 175.00),
    ("Detergente industrial Nea Detar líquido 20L", "Detergentes y desengrasantes", "Nea Detar", "Bidón 20L", "en_stock", False,
     "Líquido concentrado para máquinas industriales 25-100 kg.", 215.00),
    ("Detergente Sapolio Máximo Poder Limón", "Detergentes y desengrasantes", "Sapolio", "Bolsa 13.5kg", "en_stock", True,
     "Detergente premium con aroma limón duradero, alto rendimiento.", 165.00),
    ("Detergente Marsella Profesional", "Detergentes y desengrasantes", "Marsella", "Bolsa 13.5kg", "en_stock", False,
     "Polvo tradicional para uso doméstico e institucional ligero.", 125.00),

    # Limpiavidrios / lavavajillas / pinesol
    ("Lavavajillas líquido Sapolio Limón", "Detergentes y desengrasantes", "Sapolio", "Galón 4L", "en_stock", True,
     "Detergente neutro para vajilla manual, corta grasa y respeta las manos.", 36.50),
    ("Lavavajillas en pasta PFS 1kg", "Detergentes y desengrasantes", "PFS", "Pote 1kg", "en_stock", False,
     "Pasta concentrada de larga duración, fragancia neutra.", 18.50),
    ("Limpiavidrios Brisol amoniacal", "Detergentes y desengrasantes", "Brisol", "Galón 4L", "en_stock", False,
     "Sin residuos ni manchas, secado rápido para vidrios, espejos y mamparas.", 42.00),
    ("Limpiavidrios Sapolio 500mL", "Detergentes y desengrasantes", "Sapolio", "Atomizador 500mL", "en_stock", False,
     "Listo para usar con gatillo, fórmula sin amoníaco.", 14.50),
    ("Desengrasante alcalino industrial", "Detergentes y desengrasantes", "Marsella", "Bidón 20L", "en_stock", False,
     "Para grasa pesada en planchas, freidoras y motores. Diluible 1:10.", 89.50),
    ("Detergente líquido multiuso concentrado", "Detergentes y desengrasantes", "Sapolio", "Galón 4L", "en_stock", False,
     "Limpiador neutro de uso general para superficies lavables, espuma controlada.", 48.90),
    ("Jabón en barra azul institucional", "Detergentes y desengrasantes", "Marsella", "Caja 36 barras x 200g", "en_stock", False,
     "Jabón tradicional multiuso para prelavado de ropa, baño y cocina.", 95.00),

    # =====================================================================
    # PRODUCTOS PARA BAÑO
    # =====================================================================
    ("Pinesol institucional Sapolio Galón", "Productos para baño", "Sapolio", "Galón 4L", "en_stock", True,
     "Limpiador desinfectante aroma pino para baños y áreas húmedas.", 48.00),
    ("Pinesol Lavanda 5L", "Productos para baño", "Sapolio", "Bidón 5L", "en_stock", False,
     "Variante floral del clásico pino, mismo poder desinfectante.", 55.00),
    ("Removedor de sarro y óxido Sapolio", "Productos para baño", "Sapolio", "Botella 1L", "en_stock", False,
     "Fórmula ácida para incrustaciones de calcio, sarro y óxido en sanitarios.", 18.50),
    ("Aromatizador desinfectante para inodoros Brisol", "Productos para baño", "Brisol", "Galón 4L", "en_stock", True,
     "Doble acción aromatizante y desinfectante para sanitarios institucionales.", 52.00),
    ("Limpiador para urinarios concentrado Poett", "Productos para baño", "Poett", "Galón 4L", "en_stock", False,
     "Elimina sales urinarias y olores en una sola aplicación.", 49.00),
    ("Pastilla aromatizante para inodoro Brisol", "Productos para baño", "Brisol", "Caja 24 unidades", "en_stock", False,
     "Libera fragancia con cada descarga, durabilidad ~30 días por unidad.", 65.00),

    # =====================================================================
    # PISOS Y SUPERFICIES
    # =====================================================================
    ("Cera líquida abrillantadora Dkasa", "Pisos y superficies", "Dkasa", "Galón 4L", "en_stock", True,
     "Acabado satinado para pisos vinílicos y cerámicos de alto tráfico.", 72.00),
    ("Decapante para pisos vinílicos Marsella", "Pisos y superficies", "Marsella", "Galón 4L", "en_stock", False,
     "Remueve ceras antiguas y residuos polimerizados antes de aplicar nuevo acabado.", 68.00),
    ("Limpiapisos perfumado floral Poett", "Pisos y superficies", "Poett", "Galón 4L", "en_stock", True,
     "Aroma duradero, baja espuma para uso con máquina restregadora o trapeador.", 38.00),
    ("Limpiapisos antibacterial Kaz Limón", "Pisos y superficies", "Kaz", "Bidón 16L", "en_stock", False,
     "Acción germicida con fragancia limón, ideal para industria alimentaria.", 110.00),
    ("Sellador acrílico para pisos Dkasa", "Pisos y superficies", "Dkasa", "Galón 4L", "bajo_pedido", False,
     "Capa protectora antes de aplicar cera, prolonga la vida del acabado.", 95.00),

    # =====================================================================
    # PAÑOS INDUSTRIALES Y ABRASIVOS (Wypall, Wype Master, Scotch Brite, Klane)
    # =====================================================================
    ("Paño industrial Wypall X70 caja x60", "Paños industriales y abrasivos", "Wypall", "Caja 60 paños 30x42cm", "en_stock", True,
     "Paño hidroentrelazado reutilizable, alta resistencia para mantenimiento.", 145.00),
    ("Paño industrial Wypall X80 caja x90", "Paños industriales y abrasivos", "Wypall", "Caja 90 paños 31x32cm", "en_stock", True,
     "Versión XL del paño técnico, soporta solventes y aceites.", 195.00),
    ("Paño industrial Wypall L40 caja x70", "Paños industriales y abrasivos", "Wypall", "Caja 70 paños 38x35cm", "en_stock", False,
     "Paño desechable de pulpa, alta absorción para derrames ligeros.", 135.00),
    ("Paño Wype Master x60", "Paños industriales y abrasivos", "Wype Master", "Caja 60 paños 30x40cm", "en_stock", False,
     "Alternativa económica al Wypall, similar performance para mantenimiento.", 85.00),
    ("Paño microfibra azul 40x40cm", "Paños industriales y abrasivos", "Wypall", "Paquete 10 unidades", "en_stock", True,
     "Microfibra 80/20 lavable, alta captura de polvo y partículas.", 38.00),
    ("Paño microfibra perro 60x80cm", "Paños industriales y abrasivos", "Wypall", "Unidad 60x80cm", "en_stock", False,
     "Microfibra premium para secado de superficies grandes sin rayar.", 18.00),
    ("Paño de secado microfibra 45x70cm", "Paños industriales y abrasivos", "Wype Master", "Paquete 4 unidades", "en_stock", False,
     "Modelo intermedio multipropósito, colores surtidos.", 25.00),

    # Esponjas
    ("Esponja verde Scotch Brite 21x14cm", "Paños industriales y abrasivos", "Scotch Brite", "Pack 10 unidades", "en_stock", True,
     "Doble cara amarilla con fibra verde, para vajilla y superficies resistentes.", 22.00),
    ("Esponja industrial Scotch Brite 21x40cm", "Paños industriales y abrasivos", "Scotch Brite", "Caja 20 unidades", "en_stock", False,
     "Tamaño industrial para limpieza intensiva de pisos y áreas grandes.", 145.00),
    ("Esponja Klane antibacterial", "Paños industriales y abrasivos", "Klane", "Pack 10 unidades", "en_stock", False,
     "Esponja con triclosán, evita formación de bacterias entre usos.", 35.00),
    ("Estropajo acero inoxidable", "Paños industriales y abrasivos", "Sapolio", "Pack 6 unidades", "en_stock", False,
     "Para residuos quemados en planchas y ollas industriales.", 14.00),

    # =====================================================================
    # DISPENSADORES Y ACCESORIOS (Elite, Kimberly-Clark)
    # =====================================================================
    ("Dispensador papel jumbo Elite ABS", "Dispensadores y accesorios", "Elite", "Unidad blanco 300m", "en_stock", True,
     "Capacidad rollo 300m, llave de seguridad anti-vandalismo, ABS resistente.", 89.00),
    ("Dispensador papel jumbo Elite 500m", "Dispensadores y accesorios", "Elite", "Unidad blanco 500m", "en_stock", False,
     "Versión para rollo extendido, reduce frecuencia de recarga.", 115.00),
    ("Dispensador papel jumbo Kimberly-Clark", "Dispensadores y accesorios", "Kimberly-Clark", "Unidad blanco", "en_stock", False,
     "Línea premium con apertura superior, candado anti-pérdida.", 135.00),
    ("Dispensador papel toalla automático Elite", "Dispensadores y accesorios", "Elite", "Unidad sin contacto", "en_stock", True,
     "Sensor infrarrojo, ideal para áreas de alto flujo y bioseguridad.", 285.00),
    ("Dispensador papel toalla Z Elite", "Dispensadores y accesorios", "Elite", "Unidad recarga frontal", "en_stock", False,
     "Para paquetes interfoliados Z, recarga frontal, ABS blanco.", 95.00),
    ("Dispensador papel toalla Z Kimberly-Clark", "Dispensadores y accesorios", "Kimberly-Clark", "Unidad institucional", "en_stock", False,
     "Diseño profesional con visor de nivel, capacidad para 400 paños.", 145.00),
    ("Dispensador jabón clásico Kimberly-Clark 1L", "Dispensadores y accesorios", "Kimberly-Clark", "Unidad recargable", "en_stock", True,
     "Recargable a granel, válvula antigoteo, palanca ergonómica.", 72.00),
    ("Dispensador jabón espuma Esral", "Dispensadores y accesorios", "Esral", "Unidad 1L", "en_stock", False,
     "Para jabón en espuma, control de dosis ajustable.", 85.00),
    ("Dispensador automático sin contacto", "Dispensadores y accesorios", "Esral", "Unidad 1L sensor", "bajo_pedido", True,
     "Sensor IR de proximidad, batería 4xAA, ideal post-COVID.", 195.00),
    ("Carro de limpieza profesional 2 baldes", "Dispensadores y accesorios", "Marsella", "Unidad metálica", "bajo_pedido", False,
     "Estructura metálica con 2 baldes 25L y prensa de rodillos.", 580.00),
    ("Mopa microfibra con mango telescópico", "Dispensadores y accesorios", "Dkasa", "Unidad aluminio", "en_stock", False,
     "Mopa lavable múltiples usos, mango extensible hasta 1.5m.", 48.00),

    # =====================================================================
    # ESCOBAS, RECOGEDORES Y TACHOS
    # =====================================================================
    # Cepillos y escobas FBK (línea profesional)
    ("Escoba recta FBK cerdas suaves", "Escobas, recogedores y tachos", "FBK", "Unidad 30cm", "en_stock", True,
     "Escoba profesional polipropileno con cerdas suaves para uso interior.", 38.00),
    ("Escoba recta FBK cerdas duras", "Escobas, recogedores y tachos", "FBK", "Unidad 30cm", "en_stock", False,
     "Para barrido exterior y residuos pesados, polipropileno reforzado.", 42.00),
    ("Escoba para lavado FBK", "Escobas, recogedores y tachos", "FBK", "Unidad 30cm", "en_stock", False,
     "Cerdas medias para lavado de pisos con detergente, no se deforma.", 45.00),
    ("Escobillón industrial FBK 50cm", "Escobas, recogedores y tachos", "FBK", "Unidad 50cm cerdas duras", "en_stock", True,
     "Para grandes áreas comerciales e industriales, peso 380g.", 65.00),
    ("Escobillón industrial FBK 80cm", "Escobas, recogedores y tachos", "FBK", "Unidad 80cm cerdas mixtas", "en_stock", False,
     "Versión XL para almacenes, planta y exteriores grandes.", 95.00),
    ("Cepillo multiusos con mango FBK", "Escobas, recogedores y tachos", "FBK", "Unidad colores surtidos", "en_stock", False,
     "Cepillo manual con cerdas duras, ergonómico, código de colores HACCP.", 18.00),
    ("Cepillo de mano sin mango FBK", "Escobas, recogedores y tachos", "FBK", "Unidad cerdas variadas", "en_stock", False,
     "Para limpieza puntual de superficies, agarre antideslizante.", 14.00),
    ("Cepillo cabezal cerdas duras FBK", "Escobas, recogedores y tachos", "FBK", "Unidad", "en_stock", False,
     "Cabezal de repuesto compatible con mangos FBK estándar.", 12.00),
    ("Cepillo con cable de acero FBK", "Escobas, recogedores y tachos", "FBK", "Unidad", "en_stock", False,
     "Para limpieza de cañerías, desagües y superficies metálicas oxidadas.", 22.00),
    ("Mango ergonómico polipropileno FBK", "Escobas, recogedores y tachos", "FBK", "Unidad 130cm colores", "en_stock", False,
     "Mango profesional intercambiable con cepillos FBK, 10 colores.", 18.00),
    ("Lavatodo FBK con mango", "Escobas, recogedores y tachos", "FBK", "Unidad", "en_stock", False,
     "Cepillo multiuso para pisos y paredes, cerdas semiduras.", 32.00),

    # Recogedores
    ("Recogedor super resistente con mango", "Escobas, recogedores y tachos", "FBK", "Unidad mango PVC", "en_stock", True,
     "PVC reforzado con mango lance, facilita recojo de basura sin agacharse.", 28.00),
    ("Recogedor flip plegable ahorra espacio", "Escobas, recogedores y tachos", "FBK", "Unidad plegable", "en_stock", False,
     "Diseño plegable para almacenes con espacio limitado.", 35.00),
    ("Escobillón + recogedor kit institucional", "Escobas, recogedores y tachos", "FBK", "Kit 2 piezas", "en_stock", False,
     "Combinación práctica para limpieza diaria de oficinas y locales.", 68.00),

    # Jaladores de agua
    ("Jalador de agua FBK 44cm", "Escobas, recogedores y tachos", "FBK", "Unidad 44cm", "en_stock", True,
     "Goma neopreno doble labio, ideal para drenaje rápido de pisos.", 42.00),
    ("Jalador de agua FBK 55cm", "Escobas, recogedores y tachos", "FBK", "Unidad 55cm", "en_stock", False,
     "Versión XL para áreas comerciales y industriales grandes.", 55.00),
    ("Jalador Prolimpio con repuesto goma", "Escobas, recogedores y tachos", "Prolimpio", "Unidad con repuestos", "en_stock", False,
     "Estructura plástica con goma reemplazable, mejor relación precio/duración.", 38.00),
    ("Jalador Neco con repuesto goma", "Escobas, recogedores y tachos", "Neco", "Unidad con repuestos", "en_stock", False,
     "Material plástico reforzado, gomas reemplazables individuales.", 32.00),

    # Trapeadores
    ("Trapeador Perico 250g algodón", "Escobas, recogedores y tachos", "FBK", "Unidad 250g", "en_stock", True,
     "Trapeador clásico de algodón institucional, alta absorción.", 18.00),
    ("Set Tray trapeador con balde", "Escobas, recogedores y tachos", "FBK", "Kit trapeador + balde", "en_stock", False,
     "Sistema completo de limpieza húmeda con escurridor incorporado.", 145.00),
    ("Limpia vidrios industrial 2 rodillos", "Escobas, recogedores y tachos", "FBK", "Unidad con mango", "en_stock", False,
     "Dos rodillos: uno absorbente, uno limpiador, ideal para mamparas grandes.", 95.00),
    ("Escobaltín microfibra 80cm", "Escobas, recogedores y tachos", "FBK", "Unidad 80cm microfibra", "en_stock", False,
     "Microfibra y rayón para limpieza profunda sin químicos, alta absorción.", 65.00),

    # Pedilúvios
    ("Pedilúvio sanitizante NORDII 40x40cm", "Escobas, recogedores y tachos", "FBK", "Unidad 40x40cm", "en_stock", False,
     "Estructura plástica con reservorio para solución sanitizante en accesos.", 85.00),
    ("Tapete pedilúvio caucho pesado 50x40cm", "Escobas, recogedores y tachos", "FBK", "Unidad 50x40cm", "en_stock", False,
     "Caucho antideslizante para zona de transición de calzado en industria alimentaria.", 65.00),

    # Tachos de basura (KeyPlast, Bess)
    ("Tacho basura Cosmos KeyPlast 80L pedal", "Escobas, recogedores y tachos", "KeyPlast", "Unidad 80L sistema pedal", "en_stock", True,
     "Tacho institucional con pedal, polietileno de alta densidad, código colores HACCP.", 185.00),
    ("Tacho basura Bodeguita Bess pedal", "Escobas, recogedores y tachos", "Bess", "Unidad sistema pedal", "en_stock", False,
     "Tacho compacto polietileno con pedal, ideal para áreas pequeñas.", 95.00),
    ("Tacho basura Gorilla Bess 120L", "Escobas, recogedores y tachos", "Bess", "Unidad 120L con tapa y ruedas", "en_stock", True,
     "Contenedor industrial con tapa abatible y ruedas, polietileno HD.", 285.00),
    ("Tacho basura Gorilla Bess 240L", "Escobas, recogedores y tachos", "Bess", "Unidad 240L con tapa y ruedas", "en_stock", False,
     "Versión XL para condominios, edificios y operadores logísticos.", 425.00),
    ("Tacho de basura Gorila pedal Bess", "Escobas, recogedores y tachos", "Bess", "Unidad pedal grande", "en_stock", False,
     "Tacho rectangular con pedal silencioso, capacidad mediana.", 145.00),

    # Bolsas de basura (varias presentaciones)
    ("Bolsa basura negra calibre 2 30x40", "Escobas, recogedores y tachos", "Nova", "Paquete 100 unidades 30x40\"", "en_stock", True,
     "Polietileno calibre 2 para residuos hasta 30 kg, color negro institucional.", 58.00),
    ("Bolsa basura roja bioseguridad 30x40", "Escobas, recogedores y tachos", "Nova", "Paquete 100 unidades 30x40\"", "en_stock", False,
     "Polietileno rojo para residuos biocontaminados (uso hospitalario y clínicas).", 75.00),
    ("Bolsa basura amarilla residuos hospitalarios", "Escobas, recogedores y tachos", "Nova", "Paquete 100 unidades 30x40\"", "en_stock", False,
     "Para residuos peligrosos no biocontaminados, polietileno grueso.", 72.00),
    ("Bolsa basura 25L nacional", "Escobas, recogedores y tachos", "Nova", "Paquete 100 unidades 25L", "en_stock", False,
     "Polietileno calibre 1 para residuos domésticos y de oficina.", 28.00),
    ("Bolsa basura 50L nacional", "Escobas, recogedores y tachos", "Nova", "Paquete 100 unidades 50L", "en_stock", False,
     "Tamaño medio para áreas comunes y oficinas.", 38.00),
    ("Bolsa basura 70L nacional", "Escobas, recogedores y tachos", "Nova", "Paquete 100 unidades 70L", "en_stock", False,
     "Para tachos institucionales medianos, polietileno reforzado.", 48.00),
    ("Bolsa basura 100L nacional", "Escobas, recogedores y tachos", "Nova", "Paquete 100 unidades 100L", "en_stock", False,
     "Para contenedores Gorila 120L, calibre 2 resistencia industrial.", 65.00),
    ("Bolsa basura 120L nacional", "Escobas, recogedores y tachos", "Nova", "Paquete 100 unidades 120L", "en_stock", False,
     "Tamaño estándar para condominios, compatible Gorilla 120L.", 85.00),
    ("Bolsa basura 140L nacional", "Escobas, recogedores y tachos", "Nova", "Paquete 100 unidades 140L", "bajo_pedido", False,
     "Volumen XL para operadores logísticos y planta industrial.", 105.00),
    ("Bolsa basura 250L industrial", "Escobas, recogedores y tachos", "Nova", "Paquete 50 unidades 250L", "bajo_pedido", False,
     "Polietileno calibre 3, para contenedores Gorilla 240L.", 145.00),
    ("Bolsa con fuelle 60L", "Escobas, recogedores y tachos", "Nova", "Paquete 100 unidades 60L", "en_stock", False,
     "Con fuelle lateral para mayor capacidad real, polietileno virgen.", 55.00),

    # =====================================================================
    # LAVANDERÍA INDUSTRIAL
    # =====================================================================
    ("Detergente lavandería líquido alta concentración", "Lavandería industrial", "Marsella", "Bidón 20L", "en_stock", True,
     "Para máquinas industriales 25-100 kg, alta remoción de manchas profundas.", 215.00),
    ("Suavizante neutralizante Sapolio", "Lavandería industrial", "Sapolio", "Bidón 20L", "en_stock", False,
     "Neutraliza pH residual del lavado y suaviza fibras textiles.", 168.00),
    ("Blanqueador oxigenado sin cloro Daryza", "Lavandería industrial", "Daryza", "Bidón 20L", "en_stock", False,
     "Alternativa segura al cloro para prendas blancas y de color delicado.", 195.00),
    ("Quitamanchas concentrado prelavado", "Lavandería industrial", "Marsella", "Bidón 5L", "en_stock", False,
     "Para manchas de grasa, sangre y café antes del ciclo principal.", 105.00),

    # =====================================================================
    # EQUIPOS Y MAQUINARIA
    # =====================================================================
    ("Aspiradora industrial polvo-líquido 30L", "Equipos y maquinaria", "Nova", "Unidad 1400W", "en_stock", True,
     "Tanque 30L acero inoxidable, succión 2200mm H₂O para hoteles e industria.", 1450.00),
    ("Aspiradora industrial 60L doble motor", "Equipos y maquinaria", "Nova", "Unidad 2400W doble motor", "bajo_pedido", False,
     "Para uso intensivo, doble turbina, autonomía de operación extendida.", 2850.00),
    ("Hidrolavadora profesional 150 bar", "Equipos y maquinaria", "Nova", "Unidad 2300W", "bajo_pedido", False,
     "Motor de inducción para uso continuo, ideal para flotas y exteriores.", 1890.00),
    ("Máquina restregadora monodisco 17\"", "Equipos y maquinaria", "Nova", "Unidad 17 pulgadas", "bajo_pedido", False,
     "Restregadora monodisco para encerado, abrillantado y limpieza profunda.", 2950.00),
    ("Pulidora orbital eléctrica 1100W", "Equipos y maquinaria", "Nova", "Unidad orbital", "bajo_pedido", False,
     "Para pisos vinílicos y porcelanato, velocidad variable.", 1650.00),

    # =====================================================================
    # EQUIPOS DE PROTECCIÓN PERSONAL
    # =====================================================================
    ("Mascarilla KN95 5 capas 3M", "Equipos de protección personal", "3M", "Caja 50 unidades", "en_stock", True,
     "Filtración ≥95% partículas, ajuste ergonómico nasal y elásticos reforzados.", 95.00),
    ("Mascarilla quirúrgica triple capa", "Equipos de protección personal", "Nova", "Caja 50 unidades", "en_stock", True,
     "Tres capas con tira nasal moldeable, uso institucional certificado.", 28.00),
    ("Respirador media cara con filtro 3M", "Equipos de protección personal", "3M", "Unidad + 2 filtros P2", "en_stock", False,
     "Filtros P2 reemplazables para áreas con polvo o vapores químicos ligeros.", 195.00),
    ("Guantes industrial nitrilo recubierto", "Equipos de protección personal", "Nova", "Par talla L", "en_stock", False,
     "Recubrimiento nitrilo para manejo de químicos diluidos y materiales abrasivos.", 18.50),
    ("Lentes de seguridad transparentes 3M", "Equipos de protección personal", "3M", "Unidad", "en_stock", False,
     "Protección antiimpacto y antirayado, patillas ergonómicas norma ANSI Z87.", 22.00),
    ("Lentes de seguridad oscuros 3M", "Equipos de protección personal", "3M", "Unidad", "en_stock", False,
     "Protección UV adicional para trabajo exterior.", 25.00),
    ("Casco de seguridad industrial ABS", "Equipos de protección personal", "Nova", "Unidad amarillo norma ANSI", "en_stock", False,
     "Norma ANSI clase E, ajuste con perilla giratoria.", 38.00),
    ("Mandil PVC industrial 1.2m", "Equipos de protección personal", "Nova", "Unidad amarillo 1.2m", "en_stock", False,
     "Resistente a químicos y humedad para cocina industrial y lavandería.", 32.00),
    ("Botas seguridad PVC antideslizantes talla 42", "Equipos de protección personal", "Nova", "Par talla 42", "en_stock", False,
     "Caña alta para limpieza con químicos, suela antideslizante.", 65.00),
    ("Tapones auditivos espuma desechables", "Equipos de protección personal", "3M", "Caja 200 pares", "en_stock", False,
     "NRR 32dB, para trabajos en áreas con ruido continuo >85dB.", 85.00),
]


class Command(BaseCommand):
    help = "Carga datos demo idempotentes para ProClean (catálogo basado en PDF cliente)."

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true", help="Borra productos demo y re-siembra.")

    @transaction.atomic
    def handle(self, *args, **opts):
        if opts["reset"]:
            self.stdout.write("Borrando productos demo (preservando los con FK)...")
            # Borrado seguro: solo productos sin FK desde Cotizacion/Pedido/Factura
            from django.db import IntegrityError
            sid = transaction.savepoint()
            try:
                Producto.objects.all().delete()
                transaction.savepoint_commit(sid)
            except IntegrityError:
                transaction.savepoint_rollback(sid)
                self.stdout.write(self.style.WARNING("[WARN] Algunos productos tienen FK desde transaccionales, se actualizan en lugar de borrar"))

        cats = {}
        for nombre, icono, desc, orden in CATEGORIAS:
            cat, _ = Categoria.objects.get_or_create(
                nombre=nombre,
                defaults={"icono": icono, "descripcion": desc, "orden": orden},
            )
            # Actualizar descripcion si cambió
            if cat.descripcion != desc:
                cat.descripcion = desc
                cat.save(update_fields=["descripcion"])
            cats[nombre] = cat
        self.stdout.write(self.style.SUCCESS(f"[OK] {len(cats)} categorias"))

        marcas = {}
        for nombre in MARCAS:
            marca, _ = Marca.objects.get_or_create(nombre=nombre)
            marcas[nombre] = marca
        self.stdout.write(self.style.SUCCESS(f"[OK] {len(marcas)} marcas"))

        creados = 0
        actualizados = 0
        skus_vistos = set()
        for nombre, cat_nombre, marca_nombre, presentacion, disp, destacado, desc_corta, precio in PRODUCTOS:
            sku = make_sku(nombre, marca_nombre)
            # Resolver colisiones agregando sufijo numérico
            base_sku = sku
            i = 2
            while sku in skus_vistos:
                sku = f"{base_sku}{i}"
                i += 1
            skus_vistos.add(sku)

            defaults = {
                "nombre": nombre,
                "categoria": cats[cat_nombre],
                "marca": marcas[marca_nombre],
                "presentacion": presentacion,
                "disponibilidad": disp,
                "destacado": destacado,
                "descripcion_corta": desc_corta,
                "precio_referencia": precio,
                "activo": True,
            }
            producto, created = Producto.objects.update_or_create(sku=sku, defaults=defaults)
            if created:
                creados += 1
            else:
                actualizados += 1

        # Desactivar productos que no están en la lista nueva (para limpiar viejos del catálogo)
        desactivados = Producto.objects.exclude(sku__in=skus_vistos).update(activo=False)

        total = Producto.objects.filter(activo=True).count()
        self.stdout.write(self.style.SUCCESS(
            f"[OK] {creados} creados, {actualizados} actualizados, {desactivados} desactivados — Total activos: {total}"
        ))
