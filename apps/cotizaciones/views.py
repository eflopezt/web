from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.decorators.http import require_POST

from apps.catalogo.models import Producto

from . import carrito as carrito_lib
from .forms import SolicitudCotizacionForm
from .models import ItemSolicitud, SolicitudCotizacion


def _render_carrito_drawer(request):
    return render(
        request,
        "cotizaciones/_drawer.html",
        {
            "items": carrito_lib.items(request.session),
            "total_unidades": carrito_lib.total_unidades(request.session),
        },
    )


def _render_carrito_badge(request):
    return render(
        request,
        "cotizaciones/_badge.html",
        {"total_unidades": carrito_lib.total_unidades(request.session)},
    )


@require_POST
def agregar(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id, activo=True)
    cantidad = max(1, int(request.POST.get("cantidad", 1) or 1))
    carrito_lib.agregar(request.session, producto.pk, cantidad)

    if request.headers.get("HX-Request"):
        response = _render_carrito_badge(request)
        response["HX-Trigger"] = "carrito-actualizado"
        return response
    messages.success(request, f"Se agregó {producto.nombre} a la cotización.")
    return redirect(request.META.get("HTTP_REFERER", reverse("cotizaciones:carrito")))


@require_POST
def actualizar(request, producto_id):
    cantidad = int(request.POST.get("cantidad", 1) or 0)
    carrito_lib.actualizar(request.session, producto_id, cantidad)
    if request.headers.get("HX-Request"):
        return _render_carrito_drawer(request)
    return redirect("cotizaciones:carrito")


@require_POST
def quitar(request, producto_id):
    carrito_lib.quitar(request.session, producto_id)
    if request.headers.get("HX-Request"):
        return _render_carrito_drawer(request)
    return redirect("cotizaciones:carrito")


def ver_carrito(request):
    return render(
        request,
        "cotizaciones/carrito.html",
        {
            "items": carrito_lib.items(request.session),
            "total_unidades": carrito_lib.total_unidades(request.session),
        },
    )


def drawer(request):
    return _render_carrito_drawer(request)


def checkout(request):
    items = carrito_lib.items(request.session)
    if not items and request.method == "GET":
        messages.info(request, "Tu carrito está vacío. Agrega productos para cotizar.")
        return redirect("catalogo:lista")

    if request.method == "POST":
        form = SolicitudCotizacionForm(request.POST)
        if form.is_valid() and items:
            solicitud = form.save()
            # Asociar cliente existente por email (case-insensitive) si lo hay
            from apps.clientes.models import Cliente

            cliente = Cliente.objects.filter(email__iexact=solicitud.email).first()
            if not cliente:
                cliente = Cliente.objects.create(
                    tipo=solicitud.tipo_cliente,
                    razon_social=solicitud.razon_social or solicitud.nombre_contacto,
                    documento=solicitud.ruc,
                    email=solicitud.email,
                    telefono=solicitud.telefono,
                    direccion=solicitud.direccion,
                    departamento=solicitud.departamento,
                    ciudad=solicitud.ciudad,
                )
            solicitud.cliente = cliente
            solicitud.save(update_fields=["cliente"])

            for item in items:
                ItemSolicitud.objects.create(
                    solicitud=solicitud,
                    producto=item["producto"],
                    nombre_snapshot=item["producto"].nombre,
                    sku_snapshot=item["producto"].sku,
                    cantidad=item["cantidad"],
                )
            _enviar_emails(solicitud)
            carrito_lib.vaciar(request.session)
            return redirect("cotizaciones:exito", codigo=solicitud.codigo)
    else:
        form = SolicitudCotizacionForm()

    return render(
        request,
        "cotizaciones/checkout.html",
        {"form": form, "items": items},
    )


def exito(request, codigo):
    solicitud = get_object_or_404(SolicitudCotizacion, codigo=codigo)
    return render(request, "cotizaciones/exito.html", {"solicitud": solicitud})


def _enviar_emails(solicitud):
    ctx = {"solicitud": solicitud, "items": solicitud.items.all()}
    try:
        html_cliente = render_to_string("cotizaciones/email_cliente.html", ctx)
        msg = EmailMultiAlternatives(
            subject=f"Recibimos tu solicitud {solicitud.codigo} — {settings.SITE_NAME}",
            body=f"Hola {solicitud.nombre_contacto}, recibimos tu solicitud {solicitud.codigo}.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[solicitud.email],
        )
        msg.attach_alternative(html_cliente, "text/html")
        msg.send(fail_silently=True)

        html_ventas = render_to_string("cotizaciones/email_ventas.html", ctx)
        msg2 = EmailMultiAlternatives(
            subject=f"[Nueva cotización] {solicitud.codigo} — {solicitud.razon_social or solicitud.nombre_contacto}",
            body=f"Nueva solicitud {solicitud.codigo} de {solicitud.nombre_contacto}.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[settings.VENTAS_EMAIL],
        )
        msg2.attach_alternative(html_ventas, "text/html")
        msg2.send(fail_silently=True)
    except Exception:
        pass
