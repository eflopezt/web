from django.contrib import messages
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.core.decorators import cliente_required
from apps.core.pdf import build_pdf
from apps.cotizaciones.models import Cotizacion, SolicitudCotizacion
from apps.facturacion.models import Factura
from apps.pedidos.models import Pedido

from .forms import PerfilForm


def _cliente(request):
    return request.user.cliente


@cliente_required
def dashboard(request):
    c = _cliente(request)
    solicitudes = c.solicitudes.all()
    cotizaciones = c.cotizaciones.all()
    pedidos = c.pedidos.all()
    facturas = c.facturas.all()
    saldo_pendiente = sum(
        (f.saldo for f in facturas.exclude(estado="anulada") if f.saldo > 0), 0
    )
    return render(request, "portal/dashboard.html", {
        "solicitudes_count": solicitudes.count(),
        "solicitudes_pendientes": solicitudes.filter(estado__in=["pendiente", "en_revision"]).count(),
        "cotizaciones_count": cotizaciones.count(),
        "cotizaciones_por_revisar": cotizaciones.filter(estado="enviada").count(),
        "pedidos_count": pedidos.count(),
        "pedidos_en_camino": pedidos.filter(estado__in=["preparando", "enviado"]).count(),
        "facturas_count": facturas.count(),
        "saldo_pendiente": saldo_pendiente,
        "ultimas_cotizaciones": cotizaciones.select_related().order_by("-creada")[:5],
        "ultimos_pedidos": pedidos.order_by("-creado")[:5],
        "ultimas_facturas": facturas.order_by("-fecha_emision")[:5],
    })


@cliente_required
def solicitudes(request):
    c = _cliente(request)
    qs = c.solicitudes.all().order_by("-creado")
    return render(request, "portal/solicitudes.html", {"solicitudes": qs})


@cliente_required
def solicitud_detalle(request, codigo):
    c = _cliente(request)
    s = get_object_or_404(SolicitudCotizacion, codigo=codigo, cliente=c)
    return render(request, "portal/solicitud_detalle.html", {"solicitud": s})


@cliente_required
def cotizaciones(request):
    c = _cliente(request)
    qs = c.cotizaciones.select_related().order_by("-creada")
    return render(request, "portal/cotizaciones.html", {"cotizaciones": qs})


@cliente_required
def cotizacion_detalle(request, codigo):
    c = _cliente(request)
    cot = get_object_or_404(
        Cotizacion.objects.prefetch_related("lineas"), codigo=codigo, cliente=c
    )
    return render(request, "portal/cotizacion_detalle.html", {"cotizacion": cot})


@cliente_required
@require_POST
def cotizacion_aceptar(request, codigo):
    c = _cliente(request)
    cot = get_object_or_404(Cotizacion, codigo=codigo, cliente=c)
    if cot.estado != "enviada":
        messages.warning(request, "Esta cotización ya no puede aceptarse.")
        return redirect("portal:cotizacion_detalle", codigo=cot.codigo)
    cot.estado = "aceptada"
    cot.respondida_en = timezone.now()
    cot.save(update_fields=["estado", "respondida_en"])

    # Auto-generar pedido confirmado
    from apps.pedidos.models import LineaPedido, Pedido

    pedido = Pedido.objects.create(
        cliente=cot.cliente,
        cotizacion=cot,
        direccion_envio=cot.cliente.direccion,
        estado="confirmado",
    )
    for l in cot.lineas.all():
        LineaPedido.objects.create(
            pedido=pedido,
            producto=l.producto,
            descripcion=l.descripcion,
            sku=l.sku,
            unidad=l.unidad,
            cantidad=l.cantidad,
            precio_unitario=l.precio_unitario,
            descuento_pct=l.descuento_pct,
            orden=l.orden,
        )
    pedido.recalcular_totales()

    messages.success(request, f"Cotización aceptada. Pedido {pedido.codigo} generado.")
    return redirect("portal:pedido_detalle", codigo=pedido.codigo)


@cliente_required
@require_POST
def cotizacion_rechazar(request, codigo):
    c = _cliente(request)
    cot = get_object_or_404(Cotizacion, codigo=codigo, cliente=c)
    if cot.estado != "enviada":
        messages.warning(request, "Esta cotización ya no puede rechazarse.")
        return redirect("portal:cotizacion_detalle", codigo=cot.codigo)
    motivo = request.POST.get("motivo", "").strip()
    cot.estado = "rechazada"
    cot.respondida_en = timezone.now()
    cot.motivo_rechazo = motivo
    cot.save(update_fields=["estado", "respondida_en", "motivo_rechazo"])
    messages.info(request, "Registramos tu respuesta. Gracias.")
    return redirect("portal:cotizacion_detalle", codigo=cot.codigo)


@cliente_required
def cotizacion_pdf(request, codigo):
    c = _cliente(request)
    cot = get_object_or_404(
        Cotizacion.objects.prefetch_related("lineas"), codigo=codigo, cliente=c
    )
    pdf = build_pdf(
        titulo="COTIZACIÓN",
        codigo=cot.codigo,
        fecha_emision=cot.fecha_emision.strftime("%d/%m/%Y"),
        venc_label="Válida hasta",
        venc_value=cot.fecha_vencimiento.strftime("%d/%m/%Y") if cot.fecha_vencimiento else "—",
        est_label="Estado",
        est_value=cot.get_estado_display(),
        cliente=cot.cliente,
        lineas=list(cot.lineas.all()),
        subtotal=cot.subtotal,
        igv=cot.igv,
        total=cot.total,
        moneda=cot.moneda,
        observaciones=cot.observaciones,
        condiciones=cot.condiciones,
    )
    resp = HttpResponse(pdf, content_type="application/pdf")
    resp["Content-Disposition"] = f'inline; filename="cotizacion_{cot.codigo}.pdf"'
    return resp


@cliente_required
def pedidos(request):
    c = _cliente(request)
    qs = c.pedidos.order_by("-creado")
    return render(request, "portal/pedidos.html", {"pedidos": qs})


@cliente_required
def pedido_detalle(request, codigo):
    c = _cliente(request)
    p = get_object_or_404(
        Pedido.objects.prefetch_related("lineas", "facturas"), codigo=codigo, cliente=c
    )
    return render(request, "portal/pedido_detalle.html", {"pedido": p})


@cliente_required
def facturas(request):
    c = _cliente(request)
    qs = c.facturas.order_by("-fecha_emision")
    return render(request, "portal/facturas.html", {"facturas": qs})


@cliente_required
def factura_detalle(request, pk):
    c = _cliente(request)
    f = get_object_or_404(
        Factura.objects.prefetch_related("lineas", "pagos"), pk=pk, cliente=c
    )
    return render(request, "portal/factura_detalle.html", {"factura": f})


@cliente_required
def factura_pdf(request, pk):
    c = _cliente(request)
    f = get_object_or_404(Factura.objects.prefetch_related("lineas"), pk=pk, cliente=c)
    pdf = build_pdf(
        titulo=f.get_tipo_display().upper(),
        codigo=f.numero,
        fecha_emision=f.fecha_emision.strftime("%d/%m/%Y"),
        venc_label="Vencimiento",
        venc_value=f.fecha_vencimiento.strftime("%d/%m/%Y") if f.fecha_vencimiento else "—",
        est_label="Estado",
        est_value=f.get_estado_display(),
        cliente=f.cliente,
        lineas=list(f.lineas.all()),
        subtotal=f.subtotal,
        igv=f.igv,
        total=f.total,
        moneda=f.moneda,
        observaciones=f.observaciones,
    )
    resp = HttpResponse(pdf, content_type="application/pdf")
    resp["Content-Disposition"] = f'inline; filename="{f.numero}.pdf"'
    return resp


@cliente_required
def perfil(request):
    c = _cliente(request)
    if request.method == "POST":
        form = PerfilForm(request.POST, instance=c)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil actualizado.")
            return redirect("portal:perfil")
    else:
        form = PerfilForm(instance=c)
    return render(request, "portal/perfil.html", {"form": form, "cliente": c})
