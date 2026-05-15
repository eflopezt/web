from django.conf import settings
from django.db.models import Q
from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.urls import reverse

from apps.catalogo.models import Categoria, Producto


PASOS = [
    {"icon": "🔍", "titulo": "Explora el catálogo",
     "descripcion": "Más de 500 productos organizados por línea e industria."},
    {"icon": "📨", "titulo": "Solicita tu cotización",
     "descripcion": "Arma tu lista, completa tus datos y envíanos la solicitud."},
    {"icon": "📄", "titulo": "Recibe tu propuesta",
     "descripcion": "Te enviamos la cotización con precios y plazos en menos de 24 h hábiles."},
    {"icon": "📦", "titulo": "Despachamos a tu local",
     "descripcion": "Aceptas, generamos pedido y entregamos en 24 a 72 horas."},
]


FAQS = [
    {"q": "¿Por qué no hay precios en la web?",
     "a": "Atendemos B2B y los precios dependen del volumen, frecuencia, ubicación de despacho y plazo de pago de cada cliente. Solicita tu cotización y la enviamos en menos de 24 horas hábiles."},
    {"q": "¿Cuál es el monto mínimo de compra?",
     "a": "No tenemos monto mínimo, pero el flete tiene costo según destino. Para Lima Metropolitana las compras desde S/ 500 incluyen despacho gratuito."},
    {"q": "¿Cómo es el plazo de entrega?",
     "a": "Lima Metropolitana: 24 a 48 horas hábiles. Lima provincias: 48 a 72 horas. Provincias del Perú: 3 a 7 días hábiles según ubicación."},
    {"q": "¿Aceptan crédito a 15 días?",
     "a": "Sí, ofrecemos crédito a 15 días para clientes recurrentes (sujeto a evaluación). La primera compra suele ser al contado y luego se otorga línea de crédito."},
    {"q": "¿Emiten factura electrónica SUNAT?",
     "a": "Sí, 100% de nuestras ventas se facturan electrónicamente a través del PSE/OSE autorizado. Recibes el XML y PDF en menos de 1 hora hábil después de confirmado el pedido."},
    {"q": "¿Tienen línea de productos ecológicos?",
     "a": "Sí. Tenemos productos biodegradables sin fosfatos, peróxido de hidrógeno (oxígeno activo) y blanqueadores sin cloro, ideales para empresas con certificación ESG."},
    {"q": "¿Capacitan a mi personal en el uso de los productos?",
     "a": "Sí, ofrecemos capacitación gratuita en sitio para clientes recurrentes. Incluye dilución correcta, fichas técnicas, hojas MSDS y EPP recomendado."},
    {"q": "¿Cómo manejan los reclamos o devoluciones?",
     "a": "Tienes 7 días para reportar defectos de fábrica o errores en el despacho. Cambiamos el producto sin costo. Para productos abiertos, la garantía se evalúa caso a caso."},
    {"q": "¿Atienden licitaciones públicas o privadas?",
     "a": "Sí, contamos con experiencia en licitaciones. Podemos entregar ficha técnica, MSDS, certificados de calidad y carta de garantía con anticipación."},
    {"q": "¿Tienen contratos de suministro recurrente?",
     "a": "Sí. Ofrecemos contratos mensuales, trimestrales o anuales con precios fijos y stock asegurado. Ideal para hoteles, clínicas y operadores multi-local."},
]


SOLUCIONES = {
    "hoteles": {
        "slug": "hoteles",
        "titulo": "Hoteles y Restaurantes",
        "emoji": "🏨",
        "tagline": "Limpieza diaria, cocina industrial, baños públicos y lavandería en un solo proveedor.",
        "descripcion": "Sabemos lo que significa cumplir con estándares de servicio. Trabajamos con cadenas hoteleras, hostales boutique, restaurantes y operadores gastronómicos para asegurar consistencia de marca, eficiencia operativa y cumplimiento sanitario.",
        "puntos": [
            ("✨", "Estándar 5 estrellas", "Limpieza de habitaciones, áreas comunes y SPA con productos de alto rendimiento."),
            ("🍳", "Cocina industrial", "Desengrasantes, desinfectantes alimentarios y certificaciones DIGESA."),
            ("🛏️", "Lavandería integrada", "Detergentes, blanqueadores, suavizantes y neutralizantes para máquinas 25-100 kg."),
            ("📊", "Consumo controlado", "Reporte mensual de consumo por área y ahorro vs. mes anterior."),
        ],
        "keywords": ["amonio", "detergente líquido", "papel higiénico", "aromatizador", "limpiador", "blanqueador"],
        "cta": "Cotizar para mi hotel/restaurante",
    },
    "clinicas": {
        "slug": "clinicas",
        "titulo": "Clínicas y Centros de Salud",
        "emoji": "🏥",
        "tagline": "Desinfección hospitalaria certificada, sanitización de áreas críticas y descartables médicos.",
        "descripcion": "Trabajamos con clínicas privadas, consultorios, dentales y veterinarias. Cumplimos protocolos de bioseguridad y proveemos certificados DIGESA cuando aplica.",
        "puntos": [
            ("🦠", "Desinfección hospitalaria", "Amonios cuaternarios de 5ta generación + peróxido de hidrógeno."),
            ("📋", "Cumplimiento normativo", "Fichas técnicas, MSDS y certificados DIGESA al día."),
            ("🧤", "EPP y descartables", "Guantes, mascarillas, papel toalla y bolsas rojas."),
            ("🔬", "Áreas críticas", "Protocolos diferenciados para quirófano, UCI, consulta y laboratorio."),
        ],
        "keywords": ["amonio", "alcohol", "guantes", "peróxido", "hipoclorito"],
        "cta": "Cotizar para mi clínica",
    },
    "industria": {
        "slug": "industria",
        "titulo": "Industria y Manufactura",
        "emoji": "🏭",
        "tagline": "Desengrasantes de uso pesado, equipos industriales y mantención de planta.",
        "descripcion": "Trabajamos con plantas de producción, manufactura, almacenes logísticos y empresas de servicios técnicos. Productos de alta concentración para rendimiento óptimo en grandes superficies.",
        "puntos": [
            ("🛢️", "Desengrasantes pesados", "Para cocinas industriales, planta y mantenimiento mecánico."),
            ("⚙️", "Equipos profesionales", "Aspiradoras, hidrolavadoras, restregadoras y barredoras."),
            ("📦", "Compras a granel", "Bidones 20L y 200L con precio por volumen."),
            ("🛡️", "Seguridad industrial", "Fichas MSDS, etiquetado SGA y capacitación de uso."),
        ],
        "keywords": ["desengrasante", "hidrolavadora", "aspiradora", "hipoclorito"],
        "cta": "Cotizar para mi planta",
    },
    "oficinas": {
        "slug": "oficinas",
        "titulo": "Oficinas Corporativas",
        "emoji": "🏢",
        "tagline": "Mantención diaria, dispensadores higiénicos y experiencia premium para empleados y visitantes.",
        "descripcion": "Trabajamos con corporativos, coworkings, edificios de oficinas y servicios de gerencia. Foco en eficiencia, dispensadores instalados y reabastecimiento programado.",
        "puntos": [
            ("☕", "Espacios premium", "Productos con aroma suave para áreas compartidas."),
            ("🚰", "Dispensadores y consumibles", "Instalación de dispensadores + reabasto recurrente."),
            ("📅", "Despachos programados", "Suscripción mensual o quincenal con factura única."),
            ("🌱", "Productos eco-friendly", "Línea biodegradable para empresas con certificación ESG."),
        ],
        "keywords": ["papel", "dispensador", "limpiador", "aromatizador", "alcohol"],
        "cta": "Cotizar para mi oficina",
    },
    "retail": {
        "slug": "retail",
        "titulo": "Retail y Cadenas Multi-Local",
        "emoji": "🛒",
        "tagline": "Una sola cuenta, múltiples puntos de entrega y consolidación de compras corporativas.",
        "descripcion": "Atendemos supermercados, farmacias, tiendas por departamento, gasolineras y franquicias con presencia nacional. Centralización de compras + facturación consolidada.",
        "puntos": [
            ("🗺️", "Multi-local", "Despachos a múltiples puntos con orden única."),
            ("🧾", "Facturación corporativa", "Consolidación quincenal o mensual, sin sorpresas."),
            ("🚀", "Reabasto automático", "Configura niveles mínimos por local y deja el resto en nuestras manos."),
            ("👥", "Ejecutivo dedicado", "Un solo punto de contacto para toda la cadena."),
        ],
        "keywords": ["limpiador", "detergente", "papel", "alcohol", "aromatizador"],
        "cta": "Cotizar para mi cadena",
    },
}


INDUSTRIAS_HOME = [
    ("hoteles", "🏨", "Hoteles & Restaurantes", "Limpieza diaria + cocina + lavandería"),
    ("clinicas", "🏥", "Clínicas & Salud", "Desinfección hospitalaria + DIGESA"),
    ("industria", "🏭", "Industria", "Desengrasantes + equipos"),
    ("oficinas", "🏢", "Oficinas", "Mantención corporativa"),
    ("retail", "🛒", "Retail & Cadenas", "Multi-local + recurrente"),
]


PASOS_COMPRA = [
    ("1", "search", "Explora el catálogo",
     "Más de 160 productos por categoría. Busca por nombre, marca o SKU sin necesidad de registrarte."),
    ("2", "message-circle", "Cotiza por WhatsApp",
     "Click en 'Cotizar por WhatsApp' y te respondemos con precio y plazos en menos de 24 h hábiles."),
    ("3", "truck", "Recibe tu pedido",
     "Despacho en 24-48 h a Lima y Callao, gratis. Factura SUNAT al correo al confirmar."),
]


def home(request):
    productos_destacados = (
        Producto.objects.filter(activo=True, destacado=True)
        .select_related("categoria", "marca")[:8]
    )
    categorias = Categoria.objects.filter(activa=True).order_by("orden", "nombre")[:12]
    return render(
        request,
        "core/home.html",
        {
            "productos_destacados": productos_destacados,
            "categorias": categorias,
            "pasos": PASOS,
            "pasos_compra": PASOS_COMPRA,
            "faqs": FAQS[:5],
            "industrias_home": INDUSTRIAS_HOME,
        },
    )


def home_v2(request):
    """Versión sales-first: productos arriba, hero compacto, secundarias al final."""
    qs = Producto.objects.filter(activo=True).select_related("categoria", "marca")
    productos_destacados = list(
        qs.filter(destacado=True, disponibilidad="en_stock")
        .order_by("-id")[:24]
    )
    if len(productos_destacados) < 24:
        # Completar con productos en_stock no destacados
        ids_existentes = [p.id for p in productos_destacados]
        relleno = list(
            qs.filter(disponibilidad="en_stock")
            .exclude(id__in=ids_existentes)
            .order_by("-id")[: 24 - len(productos_destacados)]
        )
        productos_destacados.extend(relleno)

    categorias = Categoria.objects.filter(activa=True).order_by("orden", "nombre")
    # Productos por categoría top (3-4 productos por categoría visible)
    productos_por_categoria = []
    for cat in categorias[:6]:
        productos_cat = list(
            qs.filter(categoria=cat).order_by("-destacado", "-id")[:4]
        )
        if productos_cat:
            productos_por_categoria.append({"categoria": cat, "productos": productos_cat})

    return render(
        request,
        "core/home_v2.html",
        {
            "productos_destacados": productos_destacados,
            "productos_por_categoria": productos_por_categoria,
            "categorias": categorias[:12],
            "industrias_home": INDUSTRIAS_HOME,
        },
    )


def nosotros(request):
    return render(request, "core/nosotros.html")


def contacto(request):
    return render(request, "core/contacto.html")


def terminos(request):
    return render(request, "core/terminos.html")


def privacidad(request):
    return render(request, "core/privacidad.html")


def faq(request):
    return render(request, "core/faq.html", {"faqs": FAQS})


GUIAS = [
    {
        "slug": "dispensadores-bano",
        "titulo": "Guía de dispensadores para baños corporativos",
        "categoria": "Equipamiento",
        "lectura": "8 min",
        "icon": "package",
        "resumen": "Cómo elegir dispensadores de jabón, papel toalla y papel jumbo según el flujo diario de tu local. Incluye cálculo de capacidad por usuario.",
        "body": (
            "Tener el dispensador correcto reduce hasta 30% el consumo de insumos. "
            "Esta guía cubre: capacidad por número de usuarios diarios, tipos de "
            "dispensador (manual, sensor, palanca), materiales (ABS plástico vs. "
            "acero inoxidable) y cálculo del retorno de inversión. Para un baño "
            "corporativo con 50 personas/día recomendamos dispensador de papel "
            "jumbo 300m y dispensador de jabón líquido 1L con recarga a granel."
        ),
    },
    {
        "slug": "desinfeccion-hospitalaria",
        "titulo": "Protocolo de desinfección para áreas críticas hospitalarias",
        "categoria": "Salud",
        "lectura": "12 min",
        "icon": "shield-check",
        "resumen": "Concentraciones correctas de amonio cuaternario, hipoclorito y peróxido para quirófano, UCI, consulta y laboratorio. Cumple DIGESA.",
        "body": (
            "DIGESA exige protocolos diferenciados por área. Amonio cuaternario 5ta "
            "generación al 1:200 para superficies de contacto, hipoclorito 0.5% "
            "para áreas no críticas, peróxido al 7% nebulizado para quirófanos "
            "post-procedimiento. Esta guía incluye tablas de dilución, tiempo de "
            "contacto, EPP recomendado y registro obligatorio de aplicaciones."
        ),
    },
    {
        "slug": "ahorro-lavanderia-hotelera",
        "titulo": "Reducir costo de lavandería hotelera sin perder calidad",
        "categoria": "Hotelería",
        "lectura": "6 min",
        "icon": "trending-down",
        "resumen": "5 ajustes operativos (temperatura, dilución, ciclo) que bajan el costo por kg de ropa procesada hasta un 22%.",
        "body": (
            "El 70% del costo en lavandería hotelera es químico mal dosificado. "
            "Pasos para optimizar: 1) medir consumo actual por kg, 2) calibrar "
            "dosificadores automáticos, 3) ajustar temperatura a 60°C (no más), "
            "4) usar detergente líquido alta concentración, 5) neutralizar pH al "
            "cierre con suavizante. Resultado típico: -22% costo en 60 días."
        ),
    },
    {
        "slug": "calculadora-roi-suministros",
        "titulo": "Calculadora de ROI: cambiar de proveedor de suministros",
        "categoria": "Finanzas",
        "lectura": "4 min",
        "icon": "calculator",
        "resumen": "Plantilla simple para evaluar si conviene migrar de proveedor: precio, plazo de pago, costos ocultos de entrega y disponibilidad.",
        "body": (
            "Cambiar de proveedor B2B parece costoso pero suele pagar en 90 días. "
            "Calcula: ahorro en precio unitario × volumen mensual − tiempo de "
            "implementación. Variables ocultas: plazo de pago (crédito vs contado), "
            "costo de quiebre de stock, calidad consistente (descarte por mal "
            "producto). Solicita una propuesta paralela 30 días sin compromiso."
        ),
    },
]


def recursos(request):
    return render(request, "core/recursos.html", {"guias": GUIAS})


def guia(request, slug):
    g = next((x for x in GUIAS if x["slug"] == slug), None)
    if not g:
        raise Http404("Guía no encontrada")
    otras = [x for x in GUIAS if x["slug"] != slug][:3]
    return render(request, "core/guia.html", {"guia": g, "otras": otras})


def solucion(request, slug):
    data = SOLUCIONES.get(slug)
    if not data:
        raise Http404("Solución no encontrada")

    # Productos sugeridos por keywords del nombre o categoría
    q = Q()
    for kw in data["keywords"]:
        q |= Q(nombre__icontains=kw) | Q(categoria__nombre__icontains=kw)
    productos = (
        Producto.objects.filter(activo=True)
        .filter(q)
        .select_related("categoria", "marca")
        .distinct()[:8]
    )

    return render(request, "core/solucion.html", {
        "data": data,
        "productos": productos,
        "soluciones": SOLUCIONES,
    })


def newsletter_subscribe(request):
    """Captura simple de email para newsletter. Almacena en sesión y agradece."""
    if request.method == "POST":
        email = (request.POST.get("email") or "").strip().lower()
        if email and "@" in email:
            request.session.setdefault("newsletter_emails", []).append(email)
            request.session.modified = True
            from django.contrib import messages
            messages.success(request, f"Gracias, te enviaremos novedades a {email}.")
    from django.shortcuts import redirect
    return redirect(request.META.get("HTTP_REFERER", "core:home"))


# ============ SEO ============

def robots_txt(request):
    """Devuelve robots.txt con referencia al sitemap.xml absoluto."""
    domain = getattr(settings, "SITE_DOMAIN", "proclean.pe")
    protocol = getattr(settings, "SITE_PROTOCOL", "https")
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin/",
        "Disallow: /intranet/",
        "Disallow: /portal/",
        "Disallow: /accounts/",
        "Disallow: /post-login/",
        "Disallow: /registro/",
        "Disallow: /cotizacion/",
        "",
        f"Sitemap: {protocol}://{domain}/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def sitemap_html(request):
    """Mapa del sitio en HTML (humanos + SEO secundario)."""
    categorias = Categoria.objects.filter(activa=True).order_by("orden", "nombre")
    productos = (
        Producto.objects.filter(activo=True)
        .select_related("categoria")
        .order_by("categoria__nombre", "nombre")
    )
    soluciones = [
        {"slug": s, "titulo": data["titulo"]}
        for s, data in SOLUCIONES.items()
    ]
    paginas = [
        {"url": reverse("core:home"), "titulo": "Inicio"},
        {"url": reverse("core:nosotros"), "titulo": "Nosotros"},
        {"url": reverse("catalogo:lista"), "titulo": "Catálogo"},
        {"url": reverse("core:contacto"), "titulo": "Contacto"},
        {"url": reverse("core:faq"), "titulo": "Preguntas frecuentes"},
        {"url": reverse("core:recursos"), "titulo": "Recursos y guías"},
        {"url": reverse("core:terminos"), "titulo": "Términos y condiciones"},
        {"url": reverse("core:privacidad"), "titulo": "Política de privacidad"},
    ]
    guias = [{"url": reverse("core:guia", args=[g["slug"]]), "titulo": g["titulo"]} for g in GUIAS]
    return render(
        request,
        "core/sitemap.html",
        {
            "paginas": paginas,
            "soluciones": soluciones,
            "categorias": categorias,
            "productos": productos,
            "guias": guias,
        },
    )


