"""Generador de PDF base usando reportlab. Sin dependencias externas."""

import io

from django.conf import settings
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


PRIMARY = colors.HexColor("#1E40AF")  # indigo-700, corporativo
SECONDARY = colors.HexColor("#0F766E")  # teal-700
DARK = colors.HexColor("#0F172A")  # slate-900
MUTED = colors.HexColor("#64748B")  # slate-500
LIGHT = colors.HexColor("#F8FAFC")  # slate-50
BORDER = colors.HexColor("#E2E8F0")  # slate-200


def _styles():
    s = getSampleStyleSheet()
    s.add(ParagraphStyle(name="H1Brand", parent=s["Heading1"], fontSize=20, textColor=PRIMARY, spaceAfter=4))
    s.add(ParagraphStyle(name="Sub", parent=s["Normal"], fontSize=9, textColor=MUTED))
    s.add(ParagraphStyle(name="Lbl", parent=s["Normal"], fontSize=8, textColor=MUTED, leading=10))
    s.add(ParagraphStyle(name="Val", parent=s["Normal"], fontSize=10, textColor=DARK, leading=12))
    s.add(ParagraphStyle(name="Cell", parent=s["Normal"], fontSize=8.5, textColor=DARK, leading=11))
    s.add(ParagraphStyle(name="CellRight", parent=s["Normal"], fontSize=8.5, textColor=DARK, alignment=2, leading=11))
    s.add(ParagraphStyle(name="CellCenter", parent=s["Normal"], fontSize=8.5, textColor=DARK, alignment=1, leading=11))
    s.add(ParagraphStyle(name="Foot", parent=s["Normal"], fontSize=7.5, textColor=MUTED))
    return s


def _header_table(titulo, codigo, fecha_emision, vencimiento_label, vencimiento_value, est_label, est_value):
    s = _styles()
    left = [
        Paragraph(f"<b>{settings.EMISOR_RAZON_SOCIAL}</b>", s["Val"]),
        Paragraph(f"RUC {settings.EMISOR_RUC}", s["Sub"]),
        Paragraph(settings.EMISOR_DIRECCION, s["Sub"]),
        Paragraph(f"{settings.EMISOR_EMAIL} · {settings.EMISOR_TELEFONO}", s["Sub"]),
    ]
    right_box = Table(
        [
            [Paragraph(f"<b>{titulo}</b>", s["H1Brand"])],
            [Paragraph(f"N° <b>{codigo}</b>", s["Val"])],
            [Paragraph(f"Fecha emisión: {fecha_emision}", s["Sub"])],
            [Paragraph(f"{vencimiento_label}: <b>{vencimiento_value}</b>", s["Sub"])],
            [Paragraph(f"{est_label}: <b>{est_value}</b>", s["Sub"])],
        ],
        colWidths=[80 * mm],
    )
    right_box.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), LIGHT),
                ("BOX", (0, 0), (-1, -1), 0.5, PRIMARY),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )

    tabla = Table([[left, right_box]], colWidths=[95 * mm, 85 * mm])
    tabla.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    return tabla


def _cliente_table(cliente):
    s = _styles()
    lineas = [
        ("Cliente", cliente.razon_social),
        ("Documento", cliente.documento or "—"),
        ("Email", cliente.email or "—"),
        ("Teléfono", cliente.telefono or "—"),
        (
            "Dirección",
            ", ".join(filter(None, [cliente.direccion, cliente.ciudad, cliente.departamento])) or "—",
        ),
    ]
    rows = [[Paragraph(f"<b>{k}</b>", s["Lbl"]), Paragraph(v, s["Val"])] for k, v in lineas]
    t = Table(rows, colWidths=[25 * mm, 140 * mm])
    t.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 0.4, MUTED),
                ("INNERGRID", (0, 0), (-1, -1), 0.2, LIGHT),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    return t


def _items_table(lineas, moneda="PEN"):
    s = _styles()
    head = [
        Paragraph("<b>Cant.</b>", s["CellCenter"]),
        Paragraph("<b>Unidad</b>", s["CellCenter"]),
        Paragraph("<b>Descripción</b>", s["Cell"]),
        Paragraph("<b>P. Unit.</b>", s["CellRight"]),
        Paragraph("<b>Dscto %</b>", s["CellRight"]),
        Paragraph(f"<b>Subtotal ({moneda})</b>", s["CellRight"]),
    ]
    data = [head]
    for li in lineas:
        data.append(
            [
                Paragraph(f"{li.cantidad:g}", s["CellCenter"]),
                Paragraph(li.unidad, s["CellCenter"]),
                Paragraph(
                    f"<b>{li.descripcion}</b>{' · SKU ' + li.sku if li.sku else ''}", s["Cell"]
                ),
                Paragraph(f"{li.precio_unitario:.2f}", s["CellRight"]),
                Paragraph(f"{li.descuento_pct:.1f}", s["CellRight"]),
                Paragraph(f"{li.subtotal:.2f}", s["CellRight"]),
            ]
        )
    t = Table(data, colWidths=[15 * mm, 18 * mm, 70 * mm, 22 * mm, 18 * mm, 32 * mm], repeatRows=1)
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
                ("BOX", (0, 0), (-1, -1), 0.4, MUTED),
                ("INNERGRID", (0, 0), (-1, -1), 0.2, MUTED),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return t


def _totales_table(subtotal, igv, total, moneda="PEN"):
    s = _styles()
    data = [
        [Paragraph("Subtotal", s["Lbl"]), Paragraph(f"{moneda} {subtotal:,.2f}", s["CellRight"])],
        [Paragraph("IGV (18%)", s["Lbl"]), Paragraph(f"{moneda} {igv:,.2f}", s["CellRight"])],
        [Paragraph("<b>TOTAL</b>", s["Val"]), Paragraph(f"<b>{moneda} {total:,.2f}</b>", s["CellRight"])],
    ]
    t = Table(data, colWidths=[50 * mm, 50 * mm])
    t.setStyle(
        TableStyle(
            [
                ("LINEABOVE", (0, -1), (-1, -1), 1, PRIMARY),
                ("BACKGROUND", (0, -1), (-1, -1), LIGHT),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    return t


def build_pdf(titulo, codigo, fecha_emision, venc_label, venc_value, est_label, est_value,
              cliente, lineas, subtotal, igv, total, moneda, observaciones="", condiciones="",
              pie="Documento generado por LimpiaPro · DEMO"):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=15 * mm, rightMargin=15 * mm,
        topMargin=15 * mm, bottomMargin=15 * mm,
        title=f"{titulo} {codigo}",
    )
    s = _styles()
    story = []
    story.append(_header_table(titulo, codigo, fecha_emision, venc_label, venc_value, est_label, est_value))
    story.append(Spacer(1, 6 * mm))
    story.append(_cliente_table(cliente))
    story.append(Spacer(1, 4 * mm))
    story.append(_items_table(lineas, moneda))
    story.append(Spacer(1, 3 * mm))
    story.append(Table([["", _totales_table(subtotal, igv, total, moneda)]], colWidths=[80 * mm, 100 * mm]))
    if observaciones:
        story.append(Spacer(1, 4 * mm))
        story.append(Paragraph("<b>Observaciones</b>", s["Lbl"]))
        story.append(Paragraph(observaciones.replace("\n", "<br/>"), s["Cell"]))
    if condiciones:
        story.append(Spacer(1, 4 * mm))
        story.append(Paragraph("<b>Condiciones</b>", s["Lbl"]))
        story.append(Paragraph(condiciones.replace("\n", "<br/>"), s["Cell"]))
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph(pie, s["Foot"]))

    doc.build(story)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf
