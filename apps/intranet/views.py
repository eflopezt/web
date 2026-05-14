import hashlib
import secrets
from decimal import Decimal

from django.contrib import messages
from django.db.models import Count, Q, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.catalogo.models import Categoria, Producto
from apps.clientes.models import Cliente
from apps.core.decorators import staff_intranet_required
from apps.core.pdf import build_pdf
from apps.cotizaciones.models import (
    Cotizacion,
    LineaCotizacion,
    SolicitudCotizacion,
)
from apps.facturacion.models import Factura, LineaFactura, Pago
from apps.pedidos.models import LineaPedido, Pedido

from .forms import (
    ClienteForm,
    CotizacionForm,
    FacturaForm,
    LineaCotizacionForm,
    PagoForm,
    PedidoEstadoForm,
)


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

@staff_intranet_required
def dashboard(request):
    hoy = timezone.localdate()
    inicio_mes = hoy.replace(day=1)

    cot_pendientes = Cotizacion.objects.filter(estado="enviada").count()
    sol_pendientes = SolicitudCotizacion.objects.filter(estado__in=["pendiente", "en_revision"]).count()
    ped_activos = Pedido.objects.filter(estado__in=["confirmado", "preparando", "enviado"]).count()
    fac_pendientes = Factura.objects.exclude(estado__in=["pagada", "anulada"]).count()

    ventas_mes = Factura.objects.filter(
        fecha_emision__gte=inicio_mes, estado__in=["emitida", "parcial", "pagada"]
    ).aggregate(t=Sum("total"))["t"] or Decimal("0")

    cobrado_mes = Pago.objects.filter(fecha__gte=inicio_mes).aggregate(t=Sum("monto"))["t"] or Decimal("0")

    return render(request, "intranet/dashboard.html", {
        "cot_pendientes": cot_pendientes,
        "sol_pendientes": sol_pendientes,
        "ped_activos": ped_activos,
        "fac_pendientes": fac_pendientes,
        "ventas_mes": ventas_mes,
        "cobrado_mes": cobrado_mes,
        "ultimas_solicitudes": SolicitudCotizacion.objects.select_related("cliente").order_by("-creado")[:6],
        "ultimas_cotizaciones": Cotizacion.objects.select_related("cliente").order_by("-creada")[:6],
        "ultimos_pedidos": Pedido.objects.select_related("cliente").order_by("-creado")[:6],
        "ultimas_facturas": Factura.objects.select_related("cliente").order_by("-fecha_emision", "-correlativo")[:6],
    })


# ---------------------------------------------------------------------------
# Solicitudes
# ---------------------------------------------------------------------------

@staff_intranet_required
def solicitudes_lista(request):
    qs = SolicitudCotizacion.objects.select_related("cliente").order_by("-creado")
    estado = request.GET.get("estado")
    q = request.GET.get("q", "").strip()
    if estado:
        qs = qs.filter(estado=estado)
    if q:
        qs = qs.filter(
            Q(codigo__icontains=q)
            | Q(razon_social__icontains=q)
            | Q(nombre_contacto__icontains=q)
            | Q(email__icontains=q)
            | Q(telefono__icontains=q)
        )
    return render(request, "intranet/solicitudes_lista.html", {
        "solicitudes": qs,
        "estado": estado,
        "q": q,
        "estados": SolicitudCotizacion.ESTADO_CHOICES,
    })


@staff_intranet_required
def solicitud_detalle(request, codigo):
    s = get_object_or_404(
        SolicitudCotizacion.objects.prefetch_related("items"), codigo=codigo
    )
    if request.method == "POST" and "estado" in request.POST:
        nuevo = request.POST.get("estado")
        if nuevo in dict(SolicitudCotizacion.ESTADO_CHOICES):
            s.estado = nuevo
            s.nota_interna = request.POST.get("nota_interna", s.nota_interna)
            s.save(update_fields=["estado", "nota_interna"])
            messages.success(request, "Solicitud actualizada.")
            return redirect("intranet:solicitud_detalle", codigo=s.codigo)
    return render(request, "intranet/solicitud_detalle.html", {"solicitud": s})


@staff_intranet_required
def solicitud_cotizar(request, codigo):
    """Crea una cotización a partir de la solicitud, copiando items."""
    s = get_object_or_404(SolicitudCotizacion.objects.prefetch_related("items"), codigo=codigo)

    # Asegurar que tenga cliente
    cliente = s.cliente
    if not cliente:
        cliente, _ = Cliente.objects.get_or_create(
            email__iexact=s.email,
            defaults={
                "tipo": s.tipo_cliente,
                "razon_social": s.razon_social or s.nombre_contacto,
                "documento": s.ruc,
                "email": s.email,
                "telefono": s.telefono,
                "direccion": s.direccion,
                "departamento": s.departamento,
                "ciudad": s.ciudad,
            },
        )
        s.cliente = cliente
        s.save(update_fields=["cliente"])

    cot = Cotizacion.objects.create(
        cliente=cliente,
        solicitud=s,
        creada_por=request.user,
    )
    for it in s.items.all():
        precio = it.producto.precio_referencia if it.producto and it.producto.precio_referencia else Decimal("0.00")
        LineaCotizacion.objects.create(
            cotizacion=cot,
            producto=it.producto,
            descripcion=it.nombre_snapshot or (it.producto.nombre if it.producto else ""),
            sku=it.sku_snapshot or (it.producto.sku if it.producto else ""),
            unidad="UND",
            cantidad=it.cantidad,
            precio_unitario=precio,
            orden=it.pk,
        )
    cot.recalcular_totales()

    s.estado = "en_revision"
    s.save(update_fields=["estado"])

    messages.success(request, f"Cotización {cot.codigo} creada en borrador. Asigna precios y envíala.")
    return redirect("intranet:cotizacion_detalle", codigo=cot.codigo)


# ---------------------------------------------------------------------------
# Cotizaciones
# ---------------------------------------------------------------------------

@staff_intranet_required
def cotizaciones_lista(request):
    qs = Cotizacion.objects.select_related("cliente").order_by("-creada")
    estado = request.GET.get("estado")
    q = request.GET.get("q", "").strip()
    if estado:
        qs = qs.filter(estado=estado)
    if q:
        qs = qs.filter(Q(codigo__icontains=q) | Q(cliente__razon_social__icontains=q))
    return render(request, "intranet/cotizaciones_lista.html", {
        "cotizaciones": qs,
        "estado": estado,
        "q": q,
        "estados": Cotizacion.ESTADO_CHOICES,
    })


@staff_intranet_required
def cotizacion_nueva(request):
    if request.method == "POST":
        form = CotizacionForm(request.POST)
        if form.is_valid():
            cot = form.save(commit=False)
            cot.creada_por = request.user
            cot.save()
            messages.success(request, f"Cotización {cot.codigo} creada. Agrega líneas.")
            return redirect("intranet:cotizacion_detalle", codigo=cot.codigo)
    else:
        form = CotizacionForm()
    return render(request, "intranet/cotizacion_form.html", {"form": form, "modo": "nueva"})


@staff_intranet_required
def cotizacion_detalle(request, codigo):
    cot = get_object_or_404(
        Cotizacion.objects.select_related("cliente").prefetch_related("lineas"), codigo=codigo
    )
    linea_form = LineaCotizacionForm()
    return render(request, "intranet/cotizacion_detalle.html", {
        "cotizacion": cot,
        "linea_form": linea_form,
    })


@staff_intranet_required
def cotizacion_editar(request, codigo):
    cot = get_object_or_404(Cotizacion, codigo=codigo)
    if request.method == "POST":
        form = CotizacionForm(request.POST, instance=cot)
        if form.is_valid():
            form.save()
            messages.success(request, "Cotización actualizada.")
            return redirect("intranet:cotizacion_detalle", codigo=cot.codigo)
    else:
        form = CotizacionForm(instance=cot)
    return render(request, "intranet/cotizacion_form.html", {"form": form, "modo": "editar", "cotizacion": cot})


@staff_intranet_required
@require_POST
def cotizacion_linea_agregar(request, codigo):
    cot = get_object_or_404(Cotizacion, codigo=codigo)
    if cot.estado not in ("borrador",):
        messages.warning(request, "Sólo se pueden modificar líneas de cotizaciones en borrador.")
        return redirect("intranet:cotizacion_detalle", codigo=cot.codigo)
    form = LineaCotizacionForm(request.POST)
    if form.is_valid():
        linea = form.save(commit=False)
        linea.cotizacion = cot
        if linea.producto and not linea.descripcion:
            linea.descripcion = linea.producto.nombre
        if linea.producto and not linea.sku:
            linea.sku = linea.producto.sku
        linea.save()
        cot.recalcular_totales()
        messages.success(request, "Línea agregada.")
    else:
        messages.error(request, "Datos inválidos.")
    return redirect("intranet:cotizacion_detalle", codigo=cot.codigo)


@staff_intranet_required
@require_POST
def cotizacion_linea_eliminar(request, codigo, linea_pk):
    cot = get_object_or_404(Cotizacion, codigo=codigo)
    if cot.estado != "borrador":
        messages.warning(request, "Sólo se pueden eliminar líneas de cotizaciones en borrador.")
        return redirect("intranet:cotizacion_detalle", codigo=cot.codigo)
    LineaCotizacion.objects.filter(pk=linea_pk, cotizacion=cot).delete()
    cot.recalcular_totales()
    return redirect("intranet:cotizacion_detalle", codigo=cot.codigo)


@staff_intranet_required
@require_POST
def cotizacion_enviar(request, codigo):
    cot = get_object_or_404(Cotizacion.objects.prefetch_related("lineas"), codigo=codigo)
    if not cot.lineas.exists():
        messages.error(request, "No puedes enviar una cotización sin líneas.")
        return redirect("intranet:cotizacion_detalle", codigo=cot.codigo)
    cot.recalcular_totales()
    cot.estado = "enviada"
    cot.enviada_en = timezone.now()
    cot.save(update_fields=["estado", "enviada_en"])
    # Marcar solicitud origen
    if cot.solicitud and cot.solicitud.estado != "cotizada":
        cot.solicitud.estado = "cotizada"
        cot.solicitud.save(update_fields=["estado"])
    messages.success(request, "Cotización marcada como enviada.")
    return redirect("intranet:cotizacion_detalle", codigo=cot.codigo)


@staff_intranet_required
@require_POST
def cotizacion_marcar(request, codigo, estado):
    cot = get_object_or_404(Cotizacion, codigo=codigo)
    if estado not in dict(Cotizacion.ESTADO_CHOICES):
        messages.error(request, "Estado inválido.")
    else:
        cot.estado = estado
        cot.save(update_fields=["estado"])
        messages.success(request, f"Cotización marcada como {cot.get_estado_display()}.")
    return redirect("intranet:cotizacion_detalle", codigo=cot.codigo)


@staff_intranet_required
def cotizacion_pdf(request, codigo):
    cot = get_object_or_404(Cotizacion.objects.prefetch_related("lineas"), codigo=codigo)
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


@staff_intranet_required
@require_POST
def cotizacion_duplicar(request, codigo):
    cot = get_object_or_404(Cotizacion.objects.prefetch_related("lineas"), codigo=codigo)
    nueva = Cotizacion.objects.create(
        cliente=cot.cliente,
        solicitud=cot.solicitud,
        creada_por=request.user,
        validez_dias=cot.validez_dias,
        incluye_igv=cot.incluye_igv,
        moneda=cot.moneda,
        observaciones=cot.observaciones,
        condiciones=cot.condiciones,
    )
    for l in cot.lineas.all():
        LineaCotizacion.objects.create(
            cotizacion=nueva,
            producto=l.producto,
            descripcion=l.descripcion,
            sku=l.sku,
            unidad=l.unidad,
            cantidad=l.cantidad,
            precio_unitario=l.precio_unitario,
            descuento_pct=l.descuento_pct,
            orden=l.orden,
        )
    nueva.recalcular_totales()
    messages.success(request, f"Cotización duplicada como {nueva.codigo}.")
    return redirect("intranet:cotizacion_detalle", codigo=nueva.codigo)


@staff_intranet_required
@require_POST
def cotizacion_a_pedido(request, codigo):
    cot = get_object_or_404(Cotizacion.objects.prefetch_related("lineas"), codigo=codigo)
    if cot.estado != "aceptada":
        messages.warning(request, "Sólo se generan pedidos de cotizaciones aceptadas.")
        return redirect("intranet:cotizacion_detalle", codigo=cot.codigo)
    pedido = Pedido.objects.create(
        cliente=cot.cliente,
        cotizacion=cot,
        direccion_envio=cot.cliente.direccion,
        creado_por=request.user,
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
    messages.success(request, f"Pedido {pedido.codigo} creado.")
    return redirect("intranet:pedido_detalle", codigo=pedido.codigo)


# ---------------------------------------------------------------------------
# Pedidos
# ---------------------------------------------------------------------------

@staff_intranet_required
def pedidos_lista(request):
    qs = Pedido.objects.select_related("cliente").order_by("-creado")
    estado = request.GET.get("estado")
    q = request.GET.get("q", "").strip()
    if estado:
        qs = qs.filter(estado=estado)
    if q:
        qs = qs.filter(Q(codigo__icontains=q) | Q(cliente__razon_social__icontains=q))
    return render(request, "intranet/pedidos_lista.html", {
        "pedidos": qs,
        "estado": estado,
        "q": q,
        "estados": Pedido.ESTADO_CHOICES,
    })


@staff_intranet_required
def pedido_detalle(request, codigo):
    p = get_object_or_404(
        Pedido.objects.select_related("cliente").prefetch_related("lineas", "facturas"),
        codigo=codigo,
    )
    if request.method == "POST":
        form = PedidoEstadoForm(request.POST, instance=p)
        if form.is_valid():
            form.save()
            messages.success(request, "Pedido actualizado.")
            return redirect("intranet:pedido_detalle", codigo=p.codigo)
    else:
        form = PedidoEstadoForm(instance=p)
    return render(request, "intranet/pedido_detalle.html", {"pedido": p, "form": form})


@staff_intranet_required
@require_POST
def pedido_cambiar_estado(request, codigo, estado):
    p = get_object_or_404(Pedido, codigo=codigo)
    if estado in dict(Pedido.ESTADO_CHOICES):
        p.estado = estado
        if estado == "entregado" and not p.fecha_entrega_real:
            p.fecha_entrega_real = timezone.localdate()
        p.save()
        messages.success(request, f"Pedido marcado como {p.get_estado_display()}.")
    return redirect("intranet:pedido_detalle", codigo=p.codigo)


@staff_intranet_required
@require_POST
def pedido_facturar(request, codigo):
    p = get_object_or_404(Pedido.objects.prefetch_related("lineas"), codigo=codigo)
    if p.estado == "cancelado":
        messages.error(request, "No se puede facturar un pedido cancelado.")
        return redirect("intranet:pedido_detalle", codigo=p.codigo)

    tipo = request.POST.get("tipo", "factura")
    serie = "F001" if tipo == "factura" else "B001"
    factura = Factura.objects.create(
        tipo=tipo,
        serie=serie,
        cliente=p.cliente,
        pedido=p,
        creada_por=request.user,
    )
    for l in p.lineas.all():
        LineaFactura.objects.create(
            factura=factura,
            producto=l.producto,
            descripcion=l.descripcion,
            sku=l.sku,
            unidad=l.unidad,
            cantidad=l.cantidad,
            precio_unitario=l.precio_unitario,
            descuento_pct=l.descuento_pct,
            orden=l.orden,
        )
    factura.recalcular_totales()
    messages.success(request, f"{factura.get_tipo_display()} {factura.numero} emitida.")
    return redirect("intranet:factura_detalle", pk=factura.pk)


# ---------------------------------------------------------------------------
# Facturas
# ---------------------------------------------------------------------------

@staff_intranet_required
def facturas_lista(request):
    qs = Factura.objects.select_related("cliente").order_by("-fecha_emision", "-correlativo")
    estado = request.GET.get("estado")
    sunat = request.GET.get("sunat")
    q = request.GET.get("q", "").strip()
    if estado:
        qs = qs.filter(estado=estado)
    if sunat:
        qs = qs.filter(estado_sunat=sunat)
    if q:
        qs = qs.filter(
            Q(serie__icontains=q)
            | Q(correlativo__icontains=q)
            | Q(cliente__razon_social__icontains=q)
            | Q(cliente__documento__icontains=q)
        )
    return render(request, "intranet/facturas_lista.html", {
        "facturas": qs,
        "estado": estado,
        "sunat": sunat,
        "q": q,
        "estados": Factura.ESTADO_CHOICES,
        "estados_sunat": Factura.ESTADO_SUNAT_CHOICES,
    })


@staff_intranet_required
def factura_detalle(request, pk):
    f = get_object_or_404(
        Factura.objects.select_related("cliente", "pedido").prefetch_related("lineas", "pagos"),
        pk=pk,
    )
    pago_form = PagoForm()
    return render(request, "intranet/factura_detalle.html", {"factura": f, "pago_form": pago_form})


@staff_intranet_required
@require_POST
def factura_sunat(request, pk):
    f = get_object_or_404(Factura, pk=pk)
    if f.estado_sunat == "aceptada":
        messages.info(request, "Esta factura ya fue aceptada por SUNAT.")
    else:
        token = f"{f.serie}-{f.correlativo}-{secrets.token_hex(4)}"
        f.hash_sunat = hashlib.sha1(token.encode()).hexdigest()[:40]
        f.estado_sunat = "aceptada"
        f.save(update_fields=["hash_sunat", "estado_sunat"])
        messages.success(request, "Factura enviada a SUNAT (simulado). CDR aceptado.")
    return redirect("intranet:factura_detalle", pk=f.pk)


@staff_intranet_required
@require_POST
def factura_anular(request, pk):
    f = get_object_or_404(Factura, pk=pk)
    if f.estado in ("pagada", "parcial"):
        messages.error(request, "No se puede anular una factura con pagos. Genera nota de crédito.")
        return redirect("intranet:factura_detalle", pk=f.pk)
    f.estado = "anulada"
    f.estado_sunat = "anulada"
    f.save(update_fields=["estado", "estado_sunat"])
    messages.warning(request, "Factura anulada.")
    return redirect("intranet:factura_detalle", pk=f.pk)


@staff_intranet_required
@require_POST
def factura_pago_agregar(request, pk):
    f = get_object_or_404(Factura, pk=pk)
    form = PagoForm(request.POST)
    if form.is_valid():
        pago = form.save(commit=False)
        pago.factura = f
        pago.registrado_por = request.user
        pago.save()
        f.actualizar_estado_pago()
        messages.success(request, "Pago registrado.")
    else:
        messages.error(request, "Datos inválidos.")
    return redirect("intranet:factura_detalle", pk=f.pk)


@staff_intranet_required
def factura_pdf(request, pk):
    f = get_object_or_404(Factura.objects.prefetch_related("lineas"), pk=pk)
    pdf = build_pdf(
        titulo=f.get_tipo_display().upper(),
        codigo=f.numero,
        fecha_emision=f.fecha_emision.strftime("%d/%m/%Y"),
        venc_label="Vencimiento",
        venc_value=f.fecha_vencimiento.strftime("%d/%m/%Y") if f.fecha_vencimiento else "—",
        est_label="Estado",
        est_value=f"{f.get_estado_display()} · SUNAT: {f.get_estado_sunat_display()}",
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


# ---------------------------------------------------------------------------
# Clientes
# ---------------------------------------------------------------------------

@staff_intranet_required
def clientes_lista(request):
    qs = Cliente.objects.annotate(
        n_cotizaciones=Count("cotizaciones", distinct=True),
        n_pedidos=Count("pedidos", distinct=True),
        n_facturas=Count("facturas", distinct=True),
    ).order_by("razon_social")
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(
            Q(razon_social__icontains=q)
            | Q(nombre_comercial__icontains=q)
            | Q(documento__icontains=q)
            | Q(email__icontains=q)
        )
    return render(request, "intranet/clientes_lista.html", {"clientes": qs, "q": q})


@staff_intranet_required
def cliente_nuevo(request):
    if request.method == "POST":
        form = ClienteForm(request.POST)
        if form.is_valid():
            c = form.save()
            messages.success(request, f"Cliente {c.razon_social} creado.")
            return redirect("intranet:cliente_detalle", pk=c.pk)
    else:
        form = ClienteForm()
    return render(request, "intranet/cliente_form.html", {"form": form, "modo": "nuevo"})


@staff_intranet_required
def cliente_detalle(request, pk):
    c = get_object_or_404(Cliente, pk=pk)
    return render(request, "intranet/cliente_detalle.html", {
        "cliente": c,
        "cotizaciones": c.cotizaciones.all()[:20],
        "pedidos": c.pedidos.all()[:20],
        "facturas": c.facturas.all()[:20],
        "solicitudes": c.solicitudes.all()[:20],
    })


@staff_intranet_required
def cliente_editar(request, pk):
    c = get_object_or_404(Cliente, pk=pk)
    if request.method == "POST":
        form = ClienteForm(request.POST, instance=c)
        if form.is_valid():
            form.save()
            messages.success(request, "Cliente actualizado.")
            return redirect("intranet:cliente_detalle", pk=c.pk)
    else:
        form = ClienteForm(instance=c)
    return render(request, "intranet/cliente_form.html", {"form": form, "modo": "editar", "cliente": c})


# ---------------------------------------------------------------------------
# Quick actions y exports
# ---------------------------------------------------------------------------

@staff_intranet_required
@require_POST
def solicitud_quick_estado(request, codigo, estado):
    s = get_object_or_404(SolicitudCotizacion, codigo=codigo)
    if estado in dict(SolicitudCotizacion.ESTADO_CHOICES):
        s.estado = estado
        s.save(update_fields=["estado"])
        if request.headers.get("HX-Request"):
            return HttpResponse(
                f'<span class="badge badge-{s.color_estado}">{s.get_estado_display()}</span>'
            )
        messages.success(request, f"Solicitud {s.codigo} → {s.get_estado_display()}")
    return redirect(request.META.get("HTTP_REFERER", reverse("intranet:solicitudes")))


@staff_intranet_required
@require_POST
def pedido_quick_estado(request, codigo, estado):
    p = get_object_or_404(Pedido, codigo=codigo)
    if estado in dict(Pedido.ESTADO_CHOICES):
        p.estado = estado
        if estado == "entregado" and not p.fecha_entrega_real:
            p.fecha_entrega_real = timezone.localdate()
        p.save()
        if request.headers.get("HX-Request"):
            return HttpResponse(
                f'<span class="badge badge-{p.color_estado}">{p.get_estado_display()}</span>'
            )
        messages.success(request, f"Pedido {p.codigo} → {p.get_estado_display()}")
    return redirect(request.META.get("HTTP_REFERER", reverse("intranet:pedidos")))


@staff_intranet_required
def export_csv(request, tipo):
    """Exporta cotizaciones/pedidos/facturas/clientes a CSV (UTF-8 BOM para Excel)."""
    import csv
    from io import StringIO

    buf = StringIO()
    buf.write("﻿")  # BOM para Excel
    w = csv.writer(buf, delimiter=";")

    if tipo == "cotizaciones":
        w.writerow(["Código", "Cliente", "RUC", "Fecha", "Vencimiento", "Subtotal", "IGV", "Total", "Estado"])
        for c in Cotizacion.objects.select_related("cliente").order_by("-creada"):
            w.writerow([c.codigo, c.cliente.razon_social, c.cliente.documento,
                        c.fecha_emision, c.fecha_vencimiento, c.subtotal, c.igv, c.total, c.get_estado_display()])
        filename = "cotizaciones.csv"

    elif tipo == "pedidos":
        w.writerow(["Código", "Cliente", "Fecha", "Entrega est.", "Entrega real", "Subtotal", "IGV", "Total", "Estado"])
        for p in Pedido.objects.select_related("cliente").order_by("-creado"):
            w.writerow([p.codigo, p.cliente.razon_social, p.fecha,
                        p.fecha_entrega_estimada or "", p.fecha_entrega_real or "",
                        p.subtotal, p.igv, p.total, p.get_estado_display()])
        filename = "pedidos.csv"

    elif tipo == "facturas":
        w.writerow(["Número", "Tipo", "Cliente", "RUC", "Fecha", "Vencimiento", "Subtotal", "IGV", "Total", "Saldo", "Estado pago", "Estado SUNAT"])
        for f in Factura.objects.select_related("cliente").order_by("-fecha_emision"):
            w.writerow([f.numero, f.get_tipo_display(), f.cliente.razon_social, f.cliente.documento,
                        f.fecha_emision, f.fecha_vencimiento or "",
                        f.subtotal, f.igv, f.total, f.saldo,
                        f.get_estado_display(), f.get_estado_sunat_display()])
        filename = "facturas.csv"

    elif tipo == "clientes":
        w.writerow(["Razón social", "Tipo", "Documento", "Email", "Teléfono", "Ciudad", "Cotizaciones", "Pedidos", "Facturas", "Total facturado"])
        for c in Cliente.objects.annotate(
            n_cot=Count("cotizaciones", distinct=True),
            n_ped=Count("pedidos", distinct=True),
            n_fac=Count("facturas", distinct=True),
            facturado=Sum("facturas__total", filter=~Q(facturas__estado="anulada")),
        ).order_by("razon_social"):
            w.writerow([c.razon_social, c.get_tipo_display(), c.documento,
                        c.email, c.telefono, c.ciudad,
                        c.n_cot, c.n_ped, c.n_fac, c.facturado or 0])
        filename = "clientes.csv"

    else:
        from django.http import HttpResponseNotFound
        return HttpResponseNotFound("Tipo de export desconocido")

    resp = HttpResponse(buf.getvalue(), content_type="text/csv; charset=utf-8")
    resp["Content-Disposition"] = f'attachment; filename="{filename}"'
    return resp


# ---------------------------------------------------------------------------
# Productos
# ---------------------------------------------------------------------------

@staff_intranet_required
def reportes(request):
    """Reportes simples: top productos vendidos, top clientes, ventas por mes."""
    from django.db.models import F
    from apps.facturacion.models import LineaFactura
    from apps.pedidos.models import LineaPedido

    # Top productos por unidades vendidas (suma de cantidad en líneas de pedido)
    top_productos = (
        LineaPedido.objects.exclude(producto__isnull=True)
        .values("producto__nombre", "producto__sku")
        .annotate(unidades=Sum("cantidad"), monto=Sum("subtotal"))
        .order_by("-unidades")[:10]
    )

    # Top clientes por facturación (suma de total de facturas no anuladas)
    top_clientes = (
        Cliente.objects.exclude(facturas=None)
        .annotate(
            facturado=Sum("facturas__total", filter=~Q(facturas__estado="anulada")),
            n_facturas=Count("facturas", filter=~Q(facturas__estado="anulada")),
        )
        .order_by("-facturado")[:10]
    )

    # Ventas por mes (últimos 6 meses)
    from datetime import date
    from collections import OrderedDict
    hoy = timezone.localdate()
    inicio = hoy.replace(day=1)
    meses = []
    for i in range(5, -1, -1):
        year = inicio.year
        m = inicio.month - i
        while m <= 0:
            m += 12
            year -= 1
        meses.append(date(year, m, 1))
    series = OrderedDict()
    for m_inicio in meses:
        from calendar import monthrange
        last_day = monthrange(m_inicio.year, m_inicio.month)[1]
        m_fin = m_inicio.replace(day=last_day)
        total = Factura.objects.filter(
            fecha_emision__gte=m_inicio, fecha_emision__lte=m_fin
        ).exclude(estado="anulada").aggregate(t=Sum("total"))["t"] or Decimal("0")
        series[m_inicio.strftime("%b %Y")] = total
    max_val = max(series.values()) or Decimal("1")

    return render(request, "intranet/reportes.html", {
        "top_productos": top_productos,
        "top_clientes": top_clientes,
        "ventas_series": series,
        "ventas_max": max_val,
    })


@staff_intranet_required
def productos_lista(request):
    qs = Producto.objects.select_related("categoria", "marca").order_by("nombre")
    q = request.GET.get("q", "").strip()
    cat = request.GET.get("categoria")
    disp = request.GET.get("disp")
    if q:
        qs = qs.filter(Q(nombre__icontains=q) | Q(sku__icontains=q))
    if cat:
        qs = qs.filter(categoria_id=cat)
    if disp:
        qs = qs.filter(disponibilidad=disp)
    return render(request, "intranet/productos_lista.html", {
        "productos": qs[:200],
        "q": q,
        "cat": cat,
        "disp": disp,
        "categorias": Categoria.objects.filter(activa=True),
    })
