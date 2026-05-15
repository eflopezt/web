"""Generador de catálogo PDF profesional para ProClean.

- Portada con branding y datos de contacto
- Índice por categoría
- Productos en grid 3 por página con QR único que abre WhatsApp
  pre-rellenado para cotizar ese producto específico
- Header y footer en todas las páginas internas
- Listo para enviar al cliente sin revisión adicional
"""
from __future__ import annotations

import io
from pathlib import Path
from urllib.parse import quote

import qrcode
from django.conf import settings
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


# Paleta ProClean
BLUE_DARK = colors.HexColor("#1A4F8B")
BLUE = colors.HexColor("#1B75BC")
BLUE_LIGHT = colors.HexColor("#2BA0E0")
GREEN_DARK = colors.HexColor("#2E8B1F")
GREEN = colors.HexColor("#3FAE2A")
GREEN_LIGHT = colors.HexColor("#6BCB3A")
ACCENT = colors.HexColor("#143F73")
SOFT_BG = colors.HexColor("#F0F9FF")
SOFT_BG_GREEN = colors.HexColor("#F0FDF4")
TEXT = colors.HexColor("#0F172A")
MUTED = colors.HexColor("#64748B")
WHATSAPP = colors.HexColor("#25D366")

PAGE_W, PAGE_H = A4
MARGIN_X = 1.8 * cm
MARGIN_Y = 2.0 * cm


def _qr_image(data: str, box_size: int = 8) -> ImageReader:
    """Genera un QR PNG en memoria con esquinas amigables, listo para reportlab."""
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=box_size,
        border=2,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0F172A", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return ImageReader(buf)


def _whatsapp_url(producto) -> str:
    """Link de cotización por WhatsApp pre-rellenado para un producto."""
    numero = getattr(settings, "SITE_WHATSAPP", "51918570814")
    marca = producto.marca.nombre if producto.marca else ""
    cod = f" (cód. {producto.sku})" if producto.sku else ""
    pres = f" — {producto.presentacion}" if producto.presentacion else ""
    msg = f"Hola ProClean, quisiera cotizar {producto.nombre}{pres}{cod} {marca}".strip()
    return f"https://wa.me/{numero}?text={quote(msg)}"


def _get_static_path(rel: str) -> Path | None:
    """Resuelve un archivo estático en disco (no via STATIC_URL)."""
    candidates = [
        Path(settings.BASE_DIR) / "static" / rel,
        Path(settings.BASE_DIR) / "staticfiles" / rel,
    ]
    for p in candidates:
        if p.exists():
            return p
    return None


def _categoria_svg_filename(cat_nombre: str) -> str:
    """Mapea nombre de categoría a SVG. Espejo simple de producto_extras."""
    n = (cat_nombre or "").lower()
    mapping = [
        ("detergente", "detergentes.png"),
        ("desengrasante", "detergentes.png"),
        ("desinfectante", "desinfectantes.png"),
        ("sanitiz", "desinfectantes.png"),
        ("bioseguridad", "bioseguridad.png"),
        ("baño", "bano.png"),
        ("bano", "bano.png"),
        ("piso", "pisos.png"),
        ("papel", "papel.png"),
        ("descartab", "papel.png"),
        ("dispensador", "dispensadores.png"),
        ("lavander", "lavanderia.png"),
        ("equipo", "equipos.png"),
        ("maquinaria", "equipos.png"),
        ("epp", "epp.png"),
        ("protecci", "epp.png"),
        ("paño", "panos.png"),
        ("escoba", "papel.png"),
        ("recoged", "papel.png"),
        ("tacho", "papel.png"),
    ]
    for key, file in mapping:
        if key in n:
            return file
    return "detergentes.png"


def _draw_dot_pattern(c: canvas.Canvas, x: float, y: float, w: float, h: float, color, opacity: float = 0.5):
    """Dibuja un patrón de puntos sutil como background decorativo."""
    c.saveState()
    c.setFillColor(color)
    step = 12
    rx, ry = x, y
    while ry < y + h:
        cx = rx
        while cx < x + w:
            c.circle(cx, ry, 0.6, stroke=0, fill=1)
            cx += step
        ry += step
    c.restoreState()


def _draw_header(c: canvas.Canvas, num_pag: int, total_pags: int):
    """Header en cada página interna: logo mini + título sección + paginación."""
    c.saveState()
    # Banda superior
    c.setFillColor(SOFT_BG)
    c.rect(0, PAGE_H - 1.6 * cm, PAGE_W, 1.6 * cm, stroke=0, fill=1)
    # Línea gradient simulada con dos rectángulos
    c.setFillColor(BLUE)
    c.rect(0, PAGE_H - 1.62 * cm, PAGE_W / 2, 2, stroke=0, fill=1)
    c.setFillColor(GREEN)
    c.rect(PAGE_W / 2, PAGE_H - 1.62 * cm, PAGE_W / 2, 2, stroke=0, fill=1)

    # Texto izquierdo
    c.setFillColor(BLUE_DARK)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(MARGIN_X, PAGE_H - 1.05 * cm, "ProClean Servid Innova")
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 8.5)
    c.drawString(MARGIN_X, PAGE_H - 1.4 * cm, "Catálogo de productos · Lima y Callao")

    # Paginación derecha
    c.setFillColor(BLUE_DARK)
    c.setFont("Helvetica-Bold", 9)
    c.drawRightString(PAGE_W - MARGIN_X, PAGE_H - 1.05 * cm, f"Página {num_pag} / {total_pags}")
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 8)
    c.drawRightString(PAGE_W - MARGIN_X, PAGE_H - 1.4 * cm, "harmoni.pe/proclean")
    c.restoreState()


def _draw_footer(c: canvas.Canvas):
    """Footer con CTA WhatsApp + email en cada página."""
    c.saveState()
    # Banda inferior
    c.setFillColor(BLUE_DARK)
    c.rect(0, 0, PAGE_W, 1.8 * cm, stroke=0, fill=1)

    # Punto pulsante decorativo
    c.setFillColor(GREEN_LIGHT)
    c.circle(MARGIN_X + 4, 0.95 * cm + 2, 3, stroke=0, fill=1)

    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(MARGIN_X + 15, 1.1 * cm, "Cotiza ahora por WhatsApp")
    c.setFont("Helvetica", 8.5)
    c.drawString(MARGIN_X + 15, 0.7 * cm, "+51 918 570 814 · ventas@proclean.pe")

    # CTA centro/derecha
    c.setFillColor(WHATSAPP)
    c.roundRect(PAGE_W - MARGIN_X - 5.5 * cm, 0.55 * cm, 5.5 * cm, 0.75 * cm, 0.375 * cm, stroke=0, fill=1)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 9.5)
    c.drawCentredString(PAGE_W - MARGIN_X - 5.5 * cm / 2, 0.85 * cm, "Escanea el QR de tu producto")
    c.restoreState()


def _draw_cover(c: canvas.Canvas, n_productos: int, n_categorias: int, n_marcas: int):
    """Portada profesional con branding ProClean."""
    # Fondo gradient simulado con bandas
    bands = [
        (0, PAGE_H / 3, ACCENT),
        (PAGE_H / 3, PAGE_H * 2 / 3, BLUE),
        (PAGE_H * 2 / 3, PAGE_H, GREEN),
    ]
    for y_start, y_end, color in bands:
        c.setFillColor(color)
        c.rect(0, y_start, PAGE_W, y_end - y_start, stroke=0, fill=1)

    # Patrón decorativo
    _draw_dot_pattern(c, 0, 0, PAGE_W, PAGE_H, colors.HexColor("#ffffff"), opacity=0.18)

    # Logo (PNG real si existe)
    logo_path = _get_static_path("img/logo-white-real.png")
    if logo_path:
        try:
            img = ImageReader(str(logo_path))
            iw, ih = img.getSize()
            target_w = 10 * cm
            target_h = ih * (target_w / iw)
            c.drawImage(
                img,
                (PAGE_W - target_w) / 2,
                PAGE_H - 8 * cm,
                width=target_w,
                height=target_h,
                mask="auto",
            )
        except Exception:
            pass

    # Title
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 42)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 11 * cm, "CATÁLOGO")
    c.setFont("Helvetica-Bold", 26)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 12.4 * cm, "DE PRODUCTOS")

    # Línea decorativa
    c.setStrokeColor(GREEN_LIGHT)
    c.setLineWidth(2)
    c.line(PAGE_W / 2 - 2 * cm, PAGE_H - 13.5 * cm, PAGE_W / 2 + 2 * cm, PAGE_H - 13.5 * cm)

    # Subtitle
    c.setFont("Helvetica", 14)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 14.5 * cm, "Productos de limpieza profesional")
    c.setFont("Helvetica", 12)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 15.2 * cm, "Lima · Callao · Perú")

    # Card con stats
    card_x = (PAGE_W - 12 * cm) / 2
    card_y = 7 * cm
    c.setFillColor(colors.white)
    c.setStrokeColor(colors.white)
    c.roundRect(card_x, card_y, 12 * cm, 4 * cm, 0.4 * cm, stroke=0, fill=1)

    stats = [
        (str(n_productos), "Productos"),
        (str(n_marcas), "Marcas"),
        (str(n_categorias), "Categorías"),
    ]
    cell_w = 12 * cm / 3
    for i, (val, label) in enumerate(stats):
        cx = card_x + cell_w * i + cell_w / 2
        # Number gradient simulada
        c.setFillColor(BLUE_DARK)
        c.setFont("Helvetica-Bold", 28)
        c.drawCentredString(cx, card_y + 2.4 * cm, val)
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 9.5)
        c.drawCentredString(cx, card_y + 1.5 * cm, label.upper())

    # Bottom info
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(PAGE_W / 2, 4.8 * cm, "Envío gratis en Lima y Callao")

    # WhatsApp CTA
    c.setFillColor(WHATSAPP)
    cta_w = 8.5 * cm
    c.roundRect((PAGE_W - cta_w) / 2, 3 * cm, cta_w, 1 * cm, 0.5 * cm, stroke=0, fill=1)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(PAGE_W / 2, 3.35 * cm, "Cotiza por WhatsApp · +51 918 570 814")

    c.setFont("Helvetica", 9)
    c.drawCentredString(PAGE_W / 2, 1.8 * cm, "Distribuidor autorizado: Elite Professional · Kimberly-Clark · Sapolio · 3M · Wypall")
    c.setFont("Helvetica", 8)
    c.drawCentredString(PAGE_W / 2, 1.3 * cm, "harmoni.pe/proclean · ventas@proclean.pe")


def _draw_indice(c: canvas.Canvas, categorias_con_paginas: list[tuple[str, int, int]]):
    """Página de índice con categoría → número de página y contador."""
    _draw_header(c, 2, 0)  # total se actualiza al final, OK aproximado
    _draw_footer(c)

    y = PAGE_H - 3.5 * cm
    c.setFillColor(BLUE_DARK)
    c.setFont("Helvetica-Bold", 28)
    c.drawString(MARGIN_X, y, "Índice")
    c.setFillColor(GREEN)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(MARGIN_X, y - 0.7 * cm, "12 CATEGORÍAS · TODOS LOS PRODUCTOS")

    y -= 2.5 * cm

    for cat_nombre, n_productos, pagina in categorias_con_paginas:
        # Línea con dots
        c.setFillColor(BLUE_DARK)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(MARGIN_X, y, cat_nombre)

        c.setFillColor(MUTED)
        c.setFont("Helvetica", 9)
        c.drawString(MARGIN_X, y - 0.4 * cm, f"{n_productos} productos")

        # Dots
        c.setStrokeColor(colors.HexColor("#CBD5E1"))
        c.setLineWidth(0.5)
        dot_y = y + 0.1 * cm
        dots_x = MARGIN_X + 7.5 * cm
        while dots_x < PAGE_W - MARGIN_X - 1.5 * cm:
            c.circle(dots_x, dot_y, 0.5, stroke=1, fill=0)
            dots_x += 0.25 * cm

        # Número de página
        c.setFillColor(BLUE)
        c.setFont("Helvetica-Bold", 14)
        c.drawRightString(PAGE_W - MARGIN_X, y, str(pagina))

        y -= 1.3 * cm
        if y < 4 * cm:
            break


def _draw_categoria_header(c: canvas.Canvas, cat, descripcion: str | None = None):
    """Header decorativo de inicio de cada categoría (1/3 superior de la página)."""
    # Banner
    c.setFillColor(SOFT_BG)
    c.rect(0, PAGE_H - 8.5 * cm, PAGE_W, 7 * cm, stroke=0, fill=1)
    _draw_dot_pattern(c, 0, PAGE_H - 8.5 * cm, PAGE_W, 7 * cm, BLUE_LIGHT, opacity=0.3)

    # Eyebrow
    c.setFillColor(GREEN)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(MARGIN_X, PAGE_H - 3.5 * cm, "CATEGORÍA")

    # Nombre grande
    c.setFillColor(BLUE_DARK)
    c.setFont("Helvetica-Bold", 30)
    c.drawString(MARGIN_X, PAGE_H - 4.8 * cm, cat.nombre)

    # Descripción
    if descripcion or getattr(cat, "descripcion", None):
        desc = descripcion or cat.descripcion
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 10)
        # Wrap manual simple
        max_w = PAGE_W - 2 * MARGIN_X - 5 * cm
        words = desc.split()
        line = ""
        y_desc = PAGE_H - 5.7 * cm
        for w in words:
            test = (line + " " + w).strip()
            if c.stringWidth(test, "Helvetica", 10) <= max_w:
                line = test
            else:
                c.drawString(MARGIN_X, y_desc, line)
                y_desc -= 0.5 * cm
                line = w
                if y_desc < PAGE_H - 7 * cm:
                    break
        if line:
            c.drawString(MARGIN_X, y_desc, line)

    # Icono SVG/PNG de la categoría a la derecha
    ico_file = _categoria_svg_filename(cat.nombre)
    ico_path = _get_static_path(f"img/categorias/{ico_file}")
    if not ico_path:
        # Buscar SVG si no hay PNG
        ico_path = _get_static_path(f"img/categorias/{ico_file.replace('.png', '.svg')}")
    if ico_path and ico_path.suffix.lower() == ".png":
        try:
            img = ImageReader(str(ico_path))
            c.drawImage(img, PAGE_W - MARGIN_X - 4 * cm, PAGE_H - 8 * cm,
                        width=4 * cm, height=4 * cm, mask="auto")
        except Exception:
            pass


def _draw_producto_card(c: canvas.Canvas, x: float, y: float, w: float, h: float, producto):
    """Dibuja una card de producto: imagen + datos + QR."""
    # Card background
    c.setFillColor(colors.white)
    c.setStrokeColor(colors.HexColor("#E2E8F0"))
    c.setLineWidth(0.5)
    c.roundRect(x, y, w, h, 0.35 * cm, stroke=1, fill=1)

    # Header de la card (banda superior decorativa)
    header_h = 0.5 * cm
    c.setFillColor(BLUE)
    c.roundRect(x, y + h - header_h, w, header_h, 0.35 * cm, stroke=0, fill=1)
    # Tapa cuadrada para evitar redondeo superior
    c.rect(x, y + h - header_h, w, header_h / 2, stroke=0, fill=1)
    # Línea verde sutil
    c.setFillColor(GREEN)
    c.rect(x, y + h - header_h, w / 3, header_h / 2, stroke=0, fill=1)

    inner_pad = 0.4 * cm

    # ============ COLUMNA IZQUIERDA: Info producto ============
    info_x = x + inner_pad
    info_w = w * 0.62
    text_y = y + h - header_h - 0.7 * cm

    # Marca
    if producto.marca:
        c.setFillColor(BLUE)
        c.setFont("Helvetica-Bold", 8.5)
        c.drawString(info_x, text_y, producto.marca.nombre.upper())
        text_y -= 0.5 * cm

    # Nombre del producto (wrap)
    c.setFillColor(TEXT)
    c.setFont("Helvetica-Bold", 11)
    nombre = producto.nombre
    max_w = info_w - 0.2 * cm
    words = nombre.split()
    line = ""
    lines_drawn = 0
    for word in words:
        test = (line + " " + word).strip()
        if c.stringWidth(test, "Helvetica-Bold", 11) <= max_w:
            line = test
        else:
            if lines_drawn < 2:
                c.drawString(info_x, text_y, line)
                text_y -= 0.45 * cm
                lines_drawn += 1
                line = word
            else:
                line = line + "..."
                break
    if line and lines_drawn < 3:
        c.drawString(info_x, text_y, line)
        text_y -= 0.45 * cm

    # SKU + presentación
    if producto.sku:
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 7.5)
        c.drawString(info_x, text_y, f"SKU {producto.sku}")
        text_y -= 0.35 * cm
    if producto.presentacion:
        c.setFillColor(BLUE_DARK)
        c.setFont("Helvetica-Bold", 9)
        # Wrap presentación
        max_w_pres = info_w - 0.2 * cm
        words = producto.presentacion.split()
        line = ""
        for word in words:
            test = (line + " " + word).strip()
            if c.stringWidth(test, "Helvetica-Bold", 9) <= max_w_pres:
                line = test
            else:
                c.drawString(info_x, text_y, line)
                text_y -= 0.4 * cm
                line = word
                break
        if line:
            c.drawString(info_x, text_y, line)
            text_y -= 0.4 * cm

    # Badge de disponibilidad
    disp_label = producto.get_disponibilidad_display()
    disp_color = {
        "en_stock": (colors.HexColor("#DCFCE7"), GREEN_DARK),
        "bajo_pedido": (colors.HexColor("#FEF3C7"), colors.HexColor("#78350F")),
        "agotado": (colors.HexColor("#FEE2E2"), colors.HexColor("#7F1D1D")),
    }.get(producto.disponibilidad, (SOFT_BG, BLUE_DARK))
    badge_w = c.stringWidth(disp_label, "Helvetica-Bold", 7.5) + 0.6 * cm
    c.setFillColor(disp_color[0])
    c.roundRect(info_x, text_y - 0.1 * cm, badge_w, 0.55 * cm, 0.2 * cm, stroke=0, fill=1)
    c.setFillColor(disp_color[1])
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(info_x + 0.3 * cm, text_y + 0.05 * cm, disp_label)

    # Descripción corta (si cabe)
    if producto.descripcion_corta and text_y > y + 3 * cm:
        text_y -= 0.7 * cm
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 7.5)
        max_w_desc = info_w - 0.2 * cm
        words = producto.descripcion_corta.split()
        line = ""
        lines_drawn = 0
        for word in words:
            test = (line + " " + word).strip()
            if c.stringWidth(test, "Helvetica", 7.5) <= max_w_desc:
                line = test
            else:
                if lines_drawn < 3 and text_y > y + 1.5 * cm:
                    c.drawString(info_x, text_y, line)
                    text_y -= 0.32 * cm
                    lines_drawn += 1
                    line = word
                else:
                    break
        if line and lines_drawn < 4 and text_y > y + 1.5 * cm:
            c.drawString(info_x, text_y, line)

    # ============ COLUMNA DERECHA: QR ============
    qr_size = 2.6 * cm
    qr_x = x + w - qr_size - inner_pad
    qr_y = y + (h - qr_size) / 2 - 0.4 * cm
    try:
        qr_img = _qr_image(_whatsapp_url(producto), box_size=6)
        c.drawImage(qr_img, qr_x, qr_y, width=qr_size, height=qr_size, mask="auto")
    except Exception:
        pass

    # Texto bajo el QR
    c.setFillColor(WHATSAPP)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawCentredString(qr_x + qr_size / 2, qr_y - 0.3 * cm, "ESCANEA Y COTIZA")
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 6.5)
    c.drawCentredString(qr_x + qr_size / 2, qr_y - 0.6 * cm, "WhatsApp directo")


def generar_pdf_catalogo(productos_qs) -> io.BytesIO:
    """Genera el PDF y devuelve el BytesIO listo para servir como response.

    `productos_qs` puede ser cualquier iterable de Producto. Se agrupa por
    categoría (orden, nombre).
    """
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    c.setTitle("Catálogo ProClean — Productos de limpieza profesional")
    c.setAuthor("ProClean Servid Innova")
    c.setSubject("Catálogo de productos")
    c.setCreator("ProClean Backoffice")

    # Agrupar productos por categoría preservando orden
    from collections import OrderedDict
    grupos: "OrderedDict[int, dict]" = OrderedDict()
    # Materializar la lista (puede venir como queryset sliced o lista). Ordenamos en Python
    # para no fallar con QuerySets que ya tienen LIMIT.
    raw = list(productos_qs)
    productos = sorted(
        raw,
        key=lambda p: (
            (p.categoria.orden if p.categoria else 999),
            (p.categoria.nombre.lower() if p.categoria else ""),
            0 if p.destacado else 1,
            p.nombre.lower(),
        ),
    )
    for p in productos:
        if not p.categoria:
            continue
        cat_id = p.categoria.id
        if cat_id not in grupos:
            grupos[cat_id] = {"categoria": p.categoria, "productos": []}
        grupos[cat_id]["productos"].append(p)

    n_productos = len(productos)
    n_categorias = len(grupos)
    marcas_unicas = {p.marca_id for p in productos if p.marca_id}
    n_marcas = len(marcas_unicas)

    # ============ PORTADA ============
    _draw_cover(c, n_productos, n_categorias, n_marcas)
    c.showPage()

    # ============ ÍNDICE (placeholder, se llena al final) ============
    # Reservamos número de página 2 para el índice
    indice_page_num = 2
    # Dibujamos primero los contenidos para calcular páginas reales
    contenido_pages = []  # list of (categoria, productos_list, start_page)

    # Calculamos primero las páginas de contenido sin pintarlas
    productos_por_pagina = 3
    pagina_actual = 3  # después de portada (1) e índice (2)
    for grupo in grupos.values():
        cat = grupo["categoria"]
        prods = grupo["productos"]
        contenido_pages.append((cat, prods, pagina_actual))
        # Cada categoría: 1 página con header + N páginas con productos
        # Header consume el tercio superior, luego 2 productos en el resto
        # Pero para simplificar: 1 header + ceil(prods / 3) páginas de cards
        productos_primera_pag = 2  # menos productos en página con header
        n_restantes = max(0, len(prods) - productos_primera_pag)
        n_paginas_grupo = 1 + (n_restantes + productos_por_pagina - 1) // productos_por_pagina
        pagina_actual += n_paginas_grupo

    total_pags = pagina_actual - 1

    # Dibuja el índice ahora (en la página actual del canvas, que es página 2)
    _draw_indice(c, [(cat.nombre, len(prods), pg) for (cat, prods, pg) in contenido_pages])
    c.showPage()

    # ============ CONTENIDO DE CATEGORÍAS ============
    pag_num = 3
    card_h = 5.2 * cm

    for cat, prods, _ in contenido_pages:
        # Primera página de la categoría: header + 2 cards
        _draw_header(c, pag_num, total_pags)
        _draw_footer(c)
        _draw_categoria_header(c, cat)

        # Cards debajo del header
        cards_y_start = PAGE_H - 9 * cm  # debajo del banner de categoría
        card_w = PAGE_W - 2 * MARGIN_X
        idx = 0
        cards_in_page = 0
        max_cards_first = 2
        max_cards_normal = 3

        # Cards en primera página (debajo del header)
        for i in range(min(max_cards_first, len(prods))):
            y_card = cards_y_start - (cards_in_page + 1) * (card_h + 0.3 * cm) + card_h
            _draw_producto_card(c, MARGIN_X, y_card, card_w, card_h, prods[idx])
            idx += 1
            cards_in_page += 1

        c.showPage()
        pag_num += 1

        # Resto de páginas: 3 cards por página
        while idx < len(prods):
            _draw_header(c, pag_num, total_pags)
            _draw_footer(c)
            cards_y_start_normal = PAGE_H - 2.5 * cm
            for i in range(max_cards_normal):
                if idx >= len(prods):
                    break
                y_card = cards_y_start_normal - (i + 1) * (card_h + 0.4 * cm) + card_h
                _draw_producto_card(c, MARGIN_X, y_card, card_w, card_h, prods[idx])
                idx += 1
            c.showPage()
            pag_num += 1

    c.save()
    buf.seek(0)
    return buf
