"""Carga datos demo idempotentes: 11 categorías + ~25 marcas + ~120 productos.

Catálogo redactado con conocimiento factual del mercado B2B peruano de productos
de limpieza, descartables y EPP. Cada descripción es ORIGINAL: redactada desde cero
con criterio técnico (concentración, dilución, pH, materiales, aplicación real).

NO se copian textos ni imágenes de terceros. Marcas y presentaciones son hechos
factuales del rubro (no son objeto de copyright). Los precios son referenciales
para uso interno en cotizaciones (NO se muestran al público).
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
    # Limpieza institucional / consumo masivo PE
    "Sapolio", "Poett", "Marsella", "Dkasa", "Daryza", "Kaz", "Brisol",
    "Clorox", "Lysol", "Ayudín", "Florex",
    # Lavandería / cuidado del hogar
    "Bolívar", "Magia Blanca", "Aval", "Suavitel",
    # Papel y descartables PE
    "Elite", "Suave", "Scott", "Paracas", "Sumac", "Rendipel", "Noble",
    # Paños y abrasivos
    "Wypall",
    # EPP / equipos
    "3M", "Moldex", "Nova", "Steren",
    # Genéricos / accesorios institucionales
    "Drogal", "Genérico",
]

PRODUCTOS = [
    # Tupla: (nombre, categoria, marca, presentacion, disponibilidad, destacado, descripcion_corta, precio_referencia)

    # ============================================================
    # 1) Detergentes y desengrasantes (15)
    # ============================================================
    ("Detergente en Polvo Sapolio Máximo Poder Limón 5kg", "Detergentes y desengrasantes", "Sapolio", "Bolsa 5kg", "en_stock", True,
     "Detergente en polvo de alta espuma con perfume limón. Activos enzimáticos para manchas orgánicas. Apto para lavado manual y máquina semiindustrial.", 38.50),

    ("Detergente en Polvo Marsella Floral 15kg", "Detergentes y desengrasantes", "Marsella", "Bolsa 15kg", "en_stock", True,
     "Formato institucional, espuma controlada y blanqueadores ópticos. Rinde aprox. 100 cargas en lavadora industrial de 8 kg.", 168.00),

    ("Detergente en Polvo Magia Blanca Limón 4kg", "Detergentes y desengrasantes", "Magia Blanca", "Bolsa 4kg", "en_stock", False,
     "Detergente blanqueador con perfume cítrico, dosificación 30 g por kg de ropa. Apto para todo tipo de fibra excepto seda y lana.", 31.00),

    ("Detergente en Polvo Bolívar Floral 4kg", "Detergentes y desengrasantes", "Bolívar", "Bolsa 4kg", "en_stock", False,
     "Polvo tradicional peruano con perfume floral y agentes anti-redepositantes. Conserva el color de prendas oscuras.", 29.50),

    ("Detergente Líquido Sapolio Floral 4L", "Detergentes y desengrasantes", "Sapolio", "Galón 4L", "en_stock", False,
     "Detergente líquido neutro para textiles delicados y máquina. Diluible 1:50 para uso multiuso institucional.", 42.00),

    ("Lavavajilla Sapolio Limón 1.25kg", "Detergentes y desengrasantes", "Sapolio", "Pote 1.25kg", "en_stock", True,
     "Crema lavavajilla con limoneno desengrasante. pH 6.5, no irrita la piel en uso prolongado. Rinde aprox. 800 vajillas.", 18.90),

    ("Lavavajilla Líquido Ayudín Limón Verde 1L", "Detergentes y desengrasantes", "Ayudín", "Botella 1L", "en_stock", False,
     "Lavavajilla líquido concentrado de baja espuma controlada, ideal para vajilla manual. Dilución 1:5 para platos engrasados.", 14.50),

    ("Lavavajilla Industrial Máquina Drogal LM-20", "Detergentes y desengrasantes", "Drogal", "Bidón 20L", "bajo_pedido", False,
     "Líquido alcalino para máquina lavavajilla (Hobart, Winterhalter). Dosificación 1-3 g/L, evita formación de sales en tuberías.", 195.00),

    ("Desengrasante Alcalino para Cocina Industrial", "Detergentes y desengrasantes", "Daryza", "Bidón 20L", "en_stock", True,
     "Solución alcalina pH 12 para grasa carbonizada en planchas, freidoras y campanas. Dilución 1:10 (limpieza profunda) a 1:30 (mantenimiento).", 165.00),

    ("Desengrasante Cítrico Biodegradable Florex", "Detergentes y desengrasantes", "Florex", "Galón 4L", "en_stock", False,
     "Base de d-limoneno cítrico, biodegradable >90% en 28 días. Apto para áreas de manipulación de alimentos según HACCP.", 95.00),

    ("Desengrasante Súper Concentrado Kaz Planta", "Detergentes y desengrasantes", "Kaz", "Bidón 20L", "en_stock", False,
     "Para limpieza de planta industrial: pisos con aceite mineral, motores, talleres mecánicos. Dilución 1:20 en agua tibia.", 148.00),

    ("Limpiador Multiuso Concentrado Sapolio Frescura Total 5L", "Detergentes y desengrasantes", "Sapolio", "Bidón 5L", "en_stock", True,
     "Limpiador neutro multisuperficie. Diluible 1:40, deja fragancia residual hasta 6 horas. Apto para pisos, paredes y superficies lavables.", 52.00),

    ("Limpiador Multiuso Poett Original 5L", "Detergentes y desengrasantes", "Poett", "Bidón 5L", "en_stock", True,
     "Fragancia clásica Poett con tensoactivos no iónicos. Para mopeado de pisos y paños de microfibra en hoteles y oficinas.", 56.00),

    ("Jabón en Barra Bolívar Limón 250g x 24", "Detergentes y desengrasantes", "Bolívar", "Caja 24 barras x 250g", "en_stock", False,
     "Jabón tradicional para prelavado de ropa de trabajo, manchas localizadas y limpieza de utensilios. Caja institucional.", 105.00),

    ("Detergente Multiuso Industrial Daryza 20L", "Detergentes y desengrasantes", "Daryza", "Bidón 20L", "en_stock", False,
     "Detergente líquido concentrado de uso general para lavado manual y restregadoras automáticas. Espuma baja.", 158.00),

    # ============================================================
    # 2) Desinfectantes y sanitizantes (12)
    # ============================================================
    ("Lejía Clorox Original 3.78L", "Desinfectantes y sanitizantes", "Clorox", "Galón 3.78L", "en_stock", True,
     "Hipoclorito de sodio al 5.25% estabilizado. Para desinfección de superficies, blanqueo textil y tratamiento de agua según OMS.", 24.90),

    ("Lejía Sapolio Original 4L", "Desinfectantes y sanitizantes", "Sapolio", "Galón 4L", "en_stock", True,
     "Hipoclorito de sodio 4.5% con perfume floral suave. Apto para limpieza de baños, pisos y desinfección de utensilios.", 18.50),

    ("Lejía Concentrada Brisol Industrial 7.5%", "Desinfectantes y sanitizantes", "Brisol", "Bidón 20L", "en_stock", False,
     "Hipoclorito de sodio 7.5% para uso industrial. Diluible para sanitización de áreas alimentarias (200 ppm) y desinfección de superficies (1000 ppm).", 78.00),

    ("Amonio Cuaternario 5ta Generación Drogal", "Desinfectantes y sanitizantes", "Drogal", "Galón 4L", "en_stock", True,
     "Cloruro de alquil dimetil bencil amonio al 10%. Bactericida, fungicida y virucida. Dilución 1:200 para superficies de contacto.", 85.00),

    ("Amonio Cuaternario Lysol Profesional 5L", "Desinfectantes y sanitizantes", "Lysol", "Bidón 5L", "en_stock", False,
     "Desinfectante de amplio espectro para áreas sanitarias y vestidores. Sin enjuague en superficies no alimentarias.", 145.00),

    ("Alcohol Etílico 70° Desnaturalizado Dkasa", "Desinfectantes y sanitizantes", "Dkasa", "Galón 4L", "en_stock", True,
     "Alcohol etílico desnaturalizado al 70% v/v. Listo para uso en superficies, evaporación rápida sin residuo. Ficha técnica disponible.", 38.00),

    ("Alcohol Isopropílico 99% Drogal", "Desinfectantes y sanitizantes", "Drogal", "Galón 4L", "bajo_pedido", False,
     "Alcohol isopropílico anhidro para limpieza de equipos electrónicos, contactos eléctricos y superficies sensibles a agua.", 92.00),

    ("Peróxido de Hidrógeno Estabilizado 7% Daryza", "Desinfectantes y sanitizantes", "Daryza", "Bidón 5L", "bajo_pedido", False,
     "Oxidante de amplio espectro, descomposición ecológica en agua y oxígeno. Apto para áreas de manipulación de alimentos.", 98.00),

    ("Limpiatodo Poett Floreas 5L", "Desinfectantes y sanitizantes", "Poett", "Bidón 5L", "en_stock", True,
     "Limpiador desinfectante con fragancia Floreas de larga duración. Acción antibacterial sobre superficies lavables.", 58.00),

    ("Limpiatodo Sapolio Florex Lavanda 5L", "Desinfectantes y sanitizantes", "Florex", "Bidón 5L", "en_stock", False,
     "Limpiador aromatizante con notas de lavanda relajante. Apto para baños, oficinas y áreas de descanso.", 49.00),

    ("Limpiatodo Brisol Antibac Eucalipto 4L", "Desinfectantes y sanitizantes", "Brisol", "Galón 4L", "en_stock", False,
     "Limpiador con activos antibacteriales y fragancia eucalipto descongestionante. Para baños y áreas de alto tráfico.", 42.00),

    ("Limpiatodo Kaz Pino 5L", "Desinfectantes y sanitizantes", "Kaz", "Bidón 5L", "en_stock", False,
     "Limpiatodo con aceite de pino real, acción aromatizante y desinfectante. Tradicional para mantenimiento de pisos.", 38.00),

    # ============================================================
    # 3) Productos para baño (10)
    # ============================================================
    ("Removedor de Sarro y Cal Sapolio 1L", "Productos para baño", "Sapolio", "Botella 1L", "en_stock", True,
     "Ácido fosfórico al 10%, ataca incrustaciones de carbonato de calcio en sanitarios, mayólicas y grifería cromada.", 16.50),

    ("Limpiador para Inodoro Poett Bouquet 750ml", "Productos para baño", "Poett", "Botella 750ml", "en_stock", False,
     "Gel adherente con ácido clorhídrico al 9%. Pico anatómico para llegar bajo el borde del inodoro.", 9.80),

    ("Limpiador Ácido para Urinarios Drogal", "Productos para baño", "Drogal", "Galón 4L", "en_stock", False,
     "Ácido clorhídrico amortiguado al 15% para sales urinarias cristalizadas en urinarios y pediluvios.", 52.00),

    ("Aromatizante Desinfectante Brisol Bouquet 4L", "Productos para baño", "Brisol", "Galón 4L", "en_stock", True,
     "Limpiador con doble acción aromatizante (fragancia 12 horas) y desinfectante. Disponible en bouquet, lavanda y pino.", 48.00),

    ("Pastilla Aromatizante para Inodoro Brisol", "Productos para baño", "Brisol", "Caja 24 pastillas 40g", "en_stock", False,
     "Pastilla colgante que libera fragancia con cada descarga. Tinte azul indicador, duración aprox. 30 días.", 58.00),

    ("Pastilla Desodorante para Urinario Brisol", "Productos para baño", "Brisol", "Bolsa 24 pastillas 70g", "en_stock", False,
     "Pastilla de paradiclorobenceno con fragancia, sin colorante. Para urinarios secos y con descarga.", 52.00),

    ("Limpia Vidrios Sapolio Atomizador 650ml", "Productos para baño", "Sapolio", "Atomizador 650ml", "en_stock", False,
     "Solución con amoniaco e isopropanol. Secado rápido sin manchas en mamparas, espejos y vidriería.", 12.50),

    ("Limpia Vidrios Concentrado Drogal 4L", "Productos para baño", "Drogal", "Galón 4L", "en_stock", False,
     "Concentrado diluible 1:10 para limpieza de fachadas, mamparas y oficinas con altura.", 48.00),

    ("Ambientador en Aerosol Glade Lavanda 360ml", "Productos para baño", "Brisol", "Aerosol 360ml", "en_stock", False,
     "Aerosol aromatizante de larga duración. Sin CFC, propelente seguro para uso en interiores.", 14.50),

    ("Difusor Aromático Brisol Cítrico 1L", "Productos para baño", "Brisol", "Botella 1L", "en_stock", False,
     "Aromatizante líquido para dispensadores automáticos, recarga económica para áreas de 50 m².", 32.00),

    # ============================================================
    # 4) Pisos y superficies (10)
    # ============================================================
    ("Cera Acrílica Autobrillante Dkasa Premium", "Pisos y superficies", "Dkasa", "Galón 4L", "en_stock", True,
     "Cera acrílica al 22% de sólidos, acabado de alto brillo. Para pisos vinílicos, porcelanato y losetas. 4-5 capas según tráfico.", 89.00),

    ("Cera Selladora Acrílica Daryza", "Pisos y superficies", "Daryza", "Galón 4L", "en_stock", False,
     "Sellador acrílico base para preparar pisos antes del acabado. Llena porosidades, prolonga vida útil de la cera.", 78.00),

    ("Decapante Removedor de Cera Marsella Industrial", "Pisos y superficies", "Marsella", "Bidón 5L", "en_stock", False,
     "Solución alcalina pH 13 para remover ceras polimerizadas y acabados antiguos. Diluible 1:4 con agua fría.", 95.00),

    ("Limpiapisos Concentrado Poett Original 5L", "Pisos y superficies", "Poett", "Bidón 5L", "en_stock", True,
     "Fragancia clásica Poett, baja espuma para uso con máquina autorestregadora. Dilución 1:50 para mantenimiento diario.", 56.00),

    ("Limpiapisos Florex Bebé Suave 5L", "Pisos y superficies", "Florex", "Bidón 5L", "en_stock", False,
     "Fragancia suave talco-bebé, ideal para áreas pediátricas, jardines de infancia y consultorios.", 52.00),

    ("Limpiador Antigrasa para Pisos Kaz Cocina", "Pisos y superficies", "Kaz", "Bidón 20L", "en_stock", False,
     "Limpiador especial para pisos de cocina industrial, remueve grasa adherida y aceite vegetal.", 125.00),

    ("Abrillantador Spray-Buff Drogal", "Pisos y superficies", "Drogal", "Galón 4L", "bajo_pedido", False,
     "Solución para mantenimiento de cera mediante pulido con disco rojo. Restaura brillo sin re-encerar.", 92.00),

    ("Limpiador Neutro pH7 Drogal Pisos Delicados", "Pisos y superficies", "Drogal", "Galón 4L", "en_stock", False,
     "Limpiador pH neutro para mármol, granito pulido y pisos sensibles a álcalis. No remueve sellador.", 75.00),

    ("Limpiador Ácido para Cemento y Cantería", "Pisos y superficies", "Drogal", "Galón 4L", "bajo_pedido", False,
     "Limpiador a base de ácido fosfórico para remover lechada, eflorescencias y residuos de obra en cemento pulido.", 68.00),

    ("Limpiador Multipropósito Marsella Pisos 4L", "Pisos y superficies", "Marsella", "Galón 4L", "en_stock", False,
     "Limpiador económico de uso diario para pisos cerámicos, mayólica y porcelanato.", 36.00),

    # ============================================================
    # 5) Papel y descartables (18)
    # ============================================================
    ("Papel Higiénico Jumbo Elite Professional Doble Hoja 250m", "Papel y descartables", "Elite", "Caja 12 rollos x 250m", "en_stock", True,
     "Doble hoja blanca, pulpa virgen, gofrado decorativo. Compatible con dispensador jumbo estándar de mandril 60mm.", 185.00),

    ("Papel Higiénico Jumbo Suave Profesional 300m", "Papel y descartables", "Suave", "Caja 8 rollos x 300m", "en_stock", True,
     "Mayor metraje para alto consumo, doble hoja resistente. Reduce frecuencia de recarga en baños públicos.", 168.00),

    ("Papel Higiénico Jumbo Paracas Hoja Sencilla 500m", "Papel y descartables", "Paracas", "Caja 8 rollos x 500m", "en_stock", False,
     "Económico hoja sencilla, alto metraje. Apto para baños de planta industrial y áreas de personal.", 135.00),

    ("Papel Higiénico Jumbo Rendipel Hoja Sencilla 250m", "Papel y descartables", "Rendipel", "Caja 12 rollos x 250m", "en_stock", False,
     "Pulpa reciclada blanqueada sin cloro. Económico para alto consumo en plantas y obras.", 108.00),

    ("Papel Higiénico Doméstico Elite Megarrollo 4 Rollos", "Papel y descartables", "Elite", "Pack 4 rollos x 40m", "en_stock", False,
     "Doble hoja extra suave para uso institucional ligero (oficinas pequeñas, consultorios).", 12.80),

    ("Papel Higiénico Premium Sumac Gofrado 6 Rollos", "Papel y descartables", "Sumac", "Pack 6 rollos x 30m", "en_stock", True,
     "Pulpa virgen 100%, triple hoja gofrada. Para baños corporativos premium y hospedaje 4-5 estrellas.", 22.50),

    ("Papel Higiénico Scott Senda 12 Rollos", "Papel y descartables", "Scott", "Pack 12 rollos x 30m", "en_stock", False,
     "Doble hoja con relieve, formato familiar institucional. Ideal para departamentos corporativos.", 28.50),

    ("Toalla de Manos en Z Elite Professional Doble Hoja", "Papel y descartables", "Elite", "Caja 20 paquetes x 200 hojas", "en_stock", True,
     "Plegado intercalado para dispensador Z. Doble hoja blanca, alta absorción para baños de oficina y consultorios.", 165.00),

    ("Toalla de Manos en Z Suave Hoja Sencilla", "Papel y descartables", "Suave", "Caja 20 paquetes x 200 hojas", "en_stock", False,
     "Hoja sencilla económica para alto rotación. Compatible con dispensadores Z estándar.", 118.00),

    ("Rollo Multiuso Elite Professional Excellence 6639 200 paños", "Papel y descartables", "Elite", "Caja 6 rollos x 200 paños", "en_stock", True,
     "Paño desprendible perforado 24x27cm. Doble hoja absorbente para cocina industrial, talleres y derrames.", 175.00),

    ("Rollo Toalla Industrial Paracas 100m", "Papel y descartables", "Paracas", "Caja 6 rollos x 100m", "en_stock", False,
     "Toalla industrial gofrada hoja sencilla, para limpieza general y secado de manos en planta.", 95.00),

    ("Servilleta Cocktail Elite 100u", "Papel y descartables", "Elite", "Paquete 100 unidades 17x17cm", "en_stock", False,
     "Doble hoja blanca para restaurantes, cafeterías y eventos corporativos.", 8.50),

    ("Servilleta Dispensador Scott 250u", "Papel y descartables", "Scott", "Caja 24 paquetes x 250 hojas", "en_stock", False,
     "Para dispensador de mesa, doble hoja, plegado intercalado de extracción individual.", 195.00),

    ("Guantes Nitrilo Descartables Nova Talla M", "Papel y descartables", "Nova", "Caja 100 unidades", "en_stock", True,
     "Sin polvo, ambidiestros, 4 mil de grosor. Resistentes a aceites y químicos diluidos.", 58.00),

    ("Guantes Látex con Polvo Nova Talla L", "Papel y descartables", "Nova", "Caja 100 unidades", "en_stock", False,
     "Con polvo bioabsorbible, ambidiestros para limpieza general y manipulación liviana.", 38.00),

    ("Guantes Vinilo sin Polvo Nova Talla L", "Papel y descartables", "Nova", "Caja 100 unidades", "en_stock", False,
     "Hipoalergénicos sin látex ni polvo. Para personal con sensibilidad y manipulación de alimentos.", 45.00),

    ("Bolsa de Basura Negra Industrial 30x40", "Papel y descartables", "Noble", "Paquete 100 unidades calibre 2", "en_stock", True,
     "Polietileno calibre 2 (90 micras), capacidad 50 L, soporta hasta 30 kg. Para residuos generales.", 62.00),

    ("Bolsa de Basura Roja Biocontaminada 30x40", "Papel y descartables", "Noble", "Paquete 100 unidades calibre 3", "en_stock", False,
     "Roja con simbología de bioseguridad, calibre 3, normativa MINSA para residuos hospitalarios y biocontaminados.", 85.00),

    ("Bolsa de Basura Transparente 40x60", "Papel y descartables", "Noble", "Paquete 100 unidades calibre 2", "en_stock", False,
     "Polietileno transparente para residuos reciclables (papel, plástico). Permite inspección visual.", 78.00),

    # ============================================================
    # 6) Dispensadores y accesorios (10)
    # ============================================================
    ("Dispensador de Papel Higiénico Jumbo ABS Blanco", "Dispensadores y accesorios", "Elite", "Unidad", "en_stock", True,
     "Para rollo jumbo hasta 300m, mandril 60mm. ABS blanco con cerradura de seguridad anti-vandalismo.", 89.00),

    ("Dispensador de Toalla en Z ABS Blanco", "Dispensadores y accesorios", "Elite", "Unidad", "en_stock", False,
     "Capacidad 400 hojas Z plegadas. Visor frontal para nivel, llave de seguridad lateral.", 78.00),

    ("Dispensador de Jabón Líquido 1L ABS", "Dispensadores y accesorios", "Dkasa", "Unidad", "en_stock", True,
     "Recargable a granel, válvula antigoteo, palanca ergonómica. Para jabón líquido viscosidad media.", 72.00),

    ("Dispensador de Jabón Espuma 1L ABS", "Dispensadores y accesorios", "Dkasa", "Unidad", "en_stock", False,
     "Convierte jabón diluido en espuma. Rendimiento hasta 3x respecto a jabón líquido tradicional.", 85.00),

    ("Dispensador Automático de Gel con Sensor 1L", "Dispensadores y accesorios", "Dkasa", "Unidad 1000ml", "bajo_pedido", True,
     "Sensor infrarrojo, sin contacto. Pilas AAA o adaptador. Dosificación regulable, ideal para bioseguridad.", 285.00),

    ("Carro de Limpieza Profesional 2 Baldes 25L", "Dispensadores y accesorios", "Drogal", "Unidad", "bajo_pedido", False,
     "Estructura metálica plastificada, 2 baldes de 25 L (rojo/azul) y prensa de rodillos para mopeado de doble cubeta.", 580.00),

    ("Mopa Profesional Microfibra con Mango Telescópico", "Dispensadores y accesorios", "Dkasa", "Unidad 40cm", "en_stock", False,
     "Mopa de microfibra 80/20, lavable >500 ciclos. Mango telescópico de aluminio 110-180cm.", 58.00),

    ("Escoba Industrial Cerda Plástica 40cm", "Dispensadores y accesorios", "Sapolio", "Unidad", "en_stock", False,
     "Cabeza ancha 40 cm con cerda plástica rígida y mango de madera reforzada. Para barrido industrial pesado.", 28.00),

    ("Recogedor Industrial Plástico con Mango Largo", "Dispensadores y accesorios", "Sapolio", "Unidad", "en_stock", False,
     "Polipropileno reforzado, borde de goma para sellado al piso. Mango largo de 90 cm.", 22.00),

    ("Balde Industrial Plástico 20L con Asa Metálica", "Dispensadores y accesorios", "Drogal", "Unidad", "en_stock", False,
     "Polietileno de alta densidad con asa metálica y escala graduada interior para dosificación.", 28.00),

    # ============================================================
    # 7) Lavandería industrial (8)
    # ============================================================
    ("Detergente Líquido Lavandería Drogal LL-25", "Lavandería industrial", "Drogal", "Bidón 20L", "en_stock", True,
     "Detergente líquido alta concentración para lavadoras industriales 25-100 kg. Dosificación 5-10 g/kg ropa según suciedad.", 235.00),

    ("Detergente en Polvo Industrial Marsella 25kg", "Lavandería industrial", "Marsella", "Saco 25kg", "en_stock", False,
     "Polvo alcalino industrial con perborato. Dosificación automática vía tolva. Apto para textiles de hotelería y salud.", 285.00),

    ("Suavizante Aval Lavanda 2L", "Lavandería industrial", "Aval", "Botella 2L", "en_stock", False,
     "Suavizante concentrado con fragancia lavanda. Reduce arrugas, electricidad estática y tiempo de planchado.", 22.00),

    ("Suavizante Suavitel Aroma Floral 3L", "Lavandería industrial", "Suavitel", "Galón 3L", "en_stock", False,
     "Suavizante de larga duración (hasta 5 días de fragancia). Apto para máquina automática y lavado manual.", 32.00),

    ("Suavizante Neutralizante Industrial Drogal SN-20", "Lavandería industrial", "Drogal", "Bidón 20L", "en_stock", False,
     "Neutraliza pH alcalino residual del ciclo de lavado. Imprescindible para protección de fibra y piel sensible.", 175.00),

    ("Blanqueador Oxigenado sin Cloro Daryza", "Lavandería industrial", "Daryza", "Bidón 20L", "en_stock", False,
     "Peróxido estabilizado para blanqueo seguro de prendas blancas y de color. Alternativa ecológica al hipoclorito.", 198.00),

    ("Quitamanchas Prelavado Concentrado Marsella", "Lavandería industrial", "Marsella", "Bidón 5L", "en_stock", False,
     "Para manchas localizadas de grasa, sangre, vino y café antes del ciclo principal. Aplicación directa con atomizador.", 108.00),

    ("Detergente Líquido Bolívar 4L", "Lavandería industrial", "Bolívar", "Galón 4L", "en_stock", False,
     "Detergente líquido tradicional para máquinas semiindustriales y lavado manual. Espuma controlada.", 48.00),

    # ============================================================
    # 8) Equipos y maquinaria (6)
    # ============================================================
    ("Aspiradora Industrial Polvo y Líquido 30L", "Equipos y maquinaria", "Nova", "Unidad 1400W", "en_stock", True,
     "Tanque inox 30L, motor 1400W, succión 22 kPa. Manguera 2.5m, accesorios planos y triangular. Filtro HEPA opcional.", 1450.00),

    ("Aspiradora Industrial 60L Doble Motor", "Equipos y maquinaria", "Nova", "Unidad 2400W", "bajo_pedido", False,
     "Para uso continuo en planta, doble motor 2x1200W, autonomía sin sobrecalentamiento. Carrito ruedas industriales.", 2350.00),

    ("Hidrolavadora Profesional 150 Bar Motor Inducción", "Equipos y maquinaria", "Nova", "Unidad 2300W", "bajo_pedido", False,
     "Motor de inducción para uso continuo, presión 150 bar, caudal 540 L/h. Para limpieza de fachadas, vehículos y maquinaria.", 1890.00),

    ("Restregadora de Pisos Monodisco 17 Pulgadas", "Equipos y maquinaria", "Nova", "Unidad", "bajo_pedido", False,
     "Restregadora monodisco 175 RPM, motor 1.5 HP. Para encerado, abrillantado y limpieza profunda. Incluye 2 discos.", 2950.00),

    ("Pulidora Orbital de Pisos 1100W", "Equipos y maquinaria", "Nova", "Unidad", "bajo_pedido", False,
     "Pulidora orbital para acabado fino en porcelanato y mármol. Velocidad variable 800-2000 RPM.", 1650.00),

    ("Sopladora Eléctrica de Hojas 1800W", "Equipos y maquinaria", "Nova", "Unidad", "bajo_pedido", False,
     "Sopladora-aspiradora 1800W, velocidad de aire 270 km/h. Para mantenimiento de áreas externas, estacionamientos y patios.", 485.00),

    # ============================================================
    # 9) Equipos de protección personal (12)
    # ============================================================
    ("Mascarilla KN95 5 Capas 3M Aura", "Equipos de protección personal", "3M", "Caja 50 unidades", "en_stock", True,
     "Filtración ≥95% partículas ≥0.3 micras. Tira nasal moldeable, elásticos elastómero. Certificación GB2626-2019.", 95.00),

    ("Mascarilla Quirúrgica Triple Capa Moldex", "Equipos de protección personal", "Moldex", "Caja 50 unidades", "en_stock", True,
     "Tres capas con barrera bacteriana >98% (BFE). Tira nasal moldeable, elástico para oreja. Uso médico-institucional.", 26.00),

    ("Respirador Media Cara 3M 6200 con Filtros P2", "Equipos de protección personal", "3M", "Kit respirador + 2 filtros 2071", "en_stock", False,
     "Respirador reutilizable elastomérico con doble cartucho. Filtros P2 reemplazables para polvos y aerosoles no aceitosos.", 215.00),

    ("Respirador N95 Moldex 2200", "Equipos de protección personal", "Moldex", "Caja 20 unidades", "en_stock", False,
     "Filtración ≥95% NIOSH N95, sin válvula. Forma de copa con elástico ajustable. Para construcción y manejo de polvos.", 195.00),

    ("Guantes Nitrilo Industrial Reusables Moldex", "Equipos de protección personal", "Moldex", "Par talla L", "en_stock", False,
     "Nitrilo reforzado calibre 15 mil, palma rugosa. Resistente a químicos diluidos y abrasión moderada.", 18.50),

    ("Guantes Cuero Vacuno Soldador Largo 35cm", "Equipos de protección personal", "Moldex", "Par talla única", "en_stock", False,
     "Cuero vacuno flor, manga reforzada 35 cm. Para soldadura, manipulación de calor y bordes filosos.", 32.00),

    ("Lentes de Seguridad 3M Virtua Transparentes", "Equipos de protección personal", "3M", "Unidad", "en_stock", False,
     "Antiimpacto ANSI Z87.1, antirayado, patillas ergonómicas. Lente policarbonato con protección UV.", 22.00),

    ("Casco de Seguridad Industrial 3M H-700 Amarillo", "Equipos de protección personal", "3M", "Unidad color amarillo", "en_stock", False,
     "ABS de alta resistencia, ANSI Z89.1 clase E. Suspensión 4 puntos con perilla giratoria.", 42.00),

    ("Mandil PVC Amarillo Industrial 1.2m", "Equipos de protección personal", "Moldex", "Unidad", "en_stock", False,
     "PVC reforzado calibre 12, resistente a químicos, grasas y agua. Para cocina industrial, lavandería y planta.", 32.00),

    ("Botas de Jebe PVC Caña Alta Antideslizantes", "Equipos de protección personal", "Moldex", "Par talla 42", "en_stock", False,
     "PVC inyectado caña alta 38 cm, suela antideslizante con tacos. Resistente a químicos diluidos.", 65.00),

    ("Tapones Auditivos Espuma 3M 1100 Desechables", "Equipos de protección personal", "3M", "Caja 200 pares", "en_stock", False,
     "Espuma de poliuretano hipoalergénica, NRR 29 dB. Para áreas con ruido continuo de planta y construcción.", 145.00),

    ("Protector Auditivo Tipo Copa 3M Optime 101", "Equipos de protección personal", "3M", "Unidad", "en_stock", False,
     "Orejera tipo copa NRR 27 dB. Vincha ajustable acolchada, almohadillas reemplazables.", 95.00),

    # ============================================================
    # 10) Bioseguridad y sanitización (8)
    # ============================================================
    ("Gel Antibacterial 70° Dkasa Botella 1L con Válvula", "Bioseguridad y sanitización", "Dkasa", "Botella 1L con válvula", "en_stock", True,
     "Hidroalcohólico con glicerina humectante y vitamina E. Secado rápido sin residuo pegajoso. Ficha técnica y registro sanitario.", 22.00),

    ("Gel Antibacterial 70° Dkasa Galón 4L", "Bioseguridad y sanitización", "Dkasa", "Galón 4L", "en_stock", True,
     "Recarga económica para dispensadores. Hidroalcohólico viscosidad estándar, fragancia neutra.", 65.00),

    ("Alcohol Institucional 70° Granel Dkasa", "Bioseguridad y sanitización", "Dkasa", "Bidón 20L", "en_stock", True,
     "Alcohol etílico desnaturalizado al 70% v/v. Para recarga de dispensadores y atomizadores institucionales.", 175.00),

    ("Termómetro Digital Infrarrojo Sin Contacto", "Bioseguridad y sanitización", "Steren", "Unidad", "en_stock", False,
     "Lectura en 1 segundo a 3-5 cm. Rango 32-43°C, precisión ±0.3°C. Para control de accesos y áreas sensibles.", 95.00),

    ("Atomizador Industrial 1L con Gatillo Reforzado", "Bioseguridad y sanitización", "Dkasa", "Unidad transparente 1L", "en_stock", False,
     "Botella PET con gatillo de polipropileno regulable (chorro/spray). Para preparación de soluciones diluidas.", 14.00),

    ("Tapete Sanitizante para Ingreso 60x80cm", "Bioseguridad y sanitización", "Drogal", "Unidad", "en_stock", False,
     "Estructura plástica con reservorio para solución sanitizante de calzado. Borde antiderrame.", 85.00),

    ("Alfombra Absorbente para Tapete Sanitizante", "Bioseguridad y sanitización", "Drogal", "Unidad 60x80cm", "en_stock", False,
     "Alfombra de microfibra para complementar tapete sanitizante. Mejora secado del calzado.", 38.00),

    ("Atomizador Aspersor 5L Mochila Industrial", "Bioseguridad y sanitización", "Drogal", "Unidad 5L", "bajo_pedido", False,
     "Aspersor manual tipo mochila con bomba de palanca. Para sanitización de áreas amplias y aspersión profesional.", 145.00),

    # ============================================================
    # 11) Paños industriales y abrasivos (8)
    # ============================================================
    ("Paño Microfibra Azul Institucional 40x40cm", "Paños industriales y abrasivos", "Drogal", "Paquete 10 unidades", "en_stock", True,
     "Microfibra 80% poliéster / 20% poliamida, 300 g/m². Lavable >500 ciclos. Alta captura de polvo en seco.", 42.00),

    ("Paño Microfibra Sistema 4 Colores", "Paños industriales y abrasivos", "Drogal", "Pack 4 unidades (azul/rojo/verde/amarillo)", "en_stock", False,
     "Set de 4 colores para sistema HACCP de codificación por áreas: baños, cocina, oficina y áreas generales.", 22.00),

    ("Paño Absorbente Industrial Wypall L40", "Paños industriales y abrasivos", "Wypall", "Caja 200 paños 38x35cm", "en_stock", True,
     "Paño desechable de pulpa hidroentrelazada, alta absorción para mantenimiento, derrames y limpieza general.", 215.00),

    ("Paño Técnico Wypall X80 Plus Alto Rendimiento", "Paños industriales y abrasivos", "Wypall", "Caja 150 paños 31x32cm", "en_stock", False,
     "Paño reutilizable de hidroentrelazado, resistente a solventes, aceites y abrasión. Hasta 10 ciclos de uso.", 265.00),

    ("Trapo Industrial Blanco 100% Algodón a Granel", "Paños industriales y abrasivos", "Drogal", "Saco 10 kg", "en_stock", False,
     "Trapo de algodón reciclado clasificado, sin botones ni costuras. Para limpieza de aceites y grasas en taller.", 95.00),

    ("Trapo Industrial de Color Mixto a Granel", "Paños industriales y abrasivos", "Drogal", "Saco 10 kg", "en_stock", False,
     "Trapo de algodón reciclado de color, ideal para limpieza general donde la pelusa no es crítica.", 78.00),

    ("Esponja Verde Doble Cara Sapolio Pack 10", "Paños industriales y abrasivos", "Sapolio", "Pack 10 unidades", "en_stock", False,
     "Esponja amarilla con fibra verde abrasiva. Para vajilla, ollas y superficies resistentes al rayado.", 16.00),

    ("Estropajo de Acero Inoxidable Sapolio", "Paños industriales y abrasivos", "Sapolio", "Pack 6 unidades", "en_stock", False,
     "Lana de acero inoxidable enrollada, para remoción de residuos quemados en planchas y ollas industriales.", 12.50),
]


class Command(BaseCommand):
    help = "Carga datos demo idempotentes para ProClean."

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true", help="Borra productos demo y re-siembra.")

    def handle(self, *args, **opts):
        if opts["reset"]:
            self.stdout.write("Borrando productos demo (omitiendo los referenciados por pedidos/cotizaciones)...")
            from django.db.models import ProtectedError
            borrados, protegidos = 0, 0
            for p in Producto.objects.all():
                try:
                    with transaction.atomic():
                        p.delete()
                    borrados += 1
                except ProtectedError:
                    protegidos += 1
            self.stdout.write(self.style.SUCCESS(
                f"[OK] {borrados} productos borrados, {protegidos} preservados (FK protegida)"
            ))
        self._cargar_catalogo()

    @transaction.atomic
    def _cargar_catalogo(self):
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
        skus_usados = set()
        for idx, (nombre, cat_nombre, marca_nombre, presentacion, disp, destacado, desc, precio) in enumerate(PRODUCTOS, start=1):
            sku = self._build_sku(nombre, marca_nombre, idx, skus_usados)
            skus_usados.add(sku)
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
                # Actualizar contenido si ya existía (idempotencia con mejoras)
                cambios = False
                if obj.precio_referencia == 0 or obj.precio_referencia != Decimal(str(precio)):
                    obj.precio_referencia = Decimal(str(precio))
                    cambios = True
                if obj.descripcion_corta != desc:
                    obj.descripcion_corta = desc
                    cambios = True
                if obj.presentacion != presentacion:
                    obj.presentacion = presentacion
                    cambios = True
                if not obj.descuento_volumen:
                    obj.descuento_volumen = "Desde 10 unid: 5% · Desde 50: 10% · Desde 100: 15%"
                    cambios = True
                if cambios:
                    obj.save(update_fields=["precio_referencia", "descripcion_corta", "presentacion", "descuento_volumen"])
                    updated += 1
        self.stdout.write(self.style.SUCCESS(
            f"[OK] {created} productos creados, {updated} actualizados "
            f"({len(PRODUCTOS) - created - updated} sin cambios) — Total esperado: {len(PRODUCTOS)}"
        ))

        self.stdout.write(self.style.SUCCESS("\nSeed completo. Ingresa al admin para personalizar."))

    @staticmethod
    def _build_sku(nombre, marca, idx, usados):
        """Construye SKU único: PREFIJO_MARCA-SLUG_NOMBRE-IDX. Garantiza unicidad."""
        from django.utils.text import slugify
        slug = slugify(nombre)[:30].upper().replace("-", "")
        prefijo_marca = slugify(marca)[:3].upper()
        sku = f"{prefijo_marca}-{slug[:24]}-{idx:03d}"
        # Garantía extra contra colisiones (poco probable con idx, pero defensivo)
        base = sku
        n = 2
        while sku in usados:
            sku = f"{base}-{n}"
            n += 1
        return sku
