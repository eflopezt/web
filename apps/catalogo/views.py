from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from .models import Categoria, Marca, Producto


def catalogo(request, categoria_slug=None):
    productos = (
        Producto.objects.filter(activo=True)
        .select_related("categoria", "marca")
    )

    categoria = None
    if categoria_slug:
        categoria = get_object_or_404(Categoria, slug=categoria_slug, activa=True)
        productos = productos.filter(categoria=categoria)

    q = request.GET.get("q", "").strip()
    if q:
        productos = productos.filter(
            Q(nombre__icontains=q)
            | Q(sku__icontains=q)
            | Q(descripcion_corta__icontains=q)
            | Q(marca__nombre__icontains=q)
        )

    marca_slug = request.GET.get("marca", "").strip()
    if marca_slug:
        productos = productos.filter(marca__slug=marca_slug)

    disp = request.GET.get("disp", "").strip()
    if disp:
        productos = productos.filter(disponibilidad=disp)

    paginator = Paginator(productos, 12)
    page = paginator.get_page(request.GET.get("page"))

    contexto = {
        "categoria_actual": categoria,
        "categorias": Categoria.objects.filter(activa=True),
        "marcas": Marca.objects.filter(activa=True),
        "productos": page.object_list,
        "page_obj": page,
        "q": q,
        "marca_slug": marca_slug,
        "disp_actual": disp,
    }
    template = (
        "catalogo/_lista_productos.html"
        if request.headers.get("HX-Request")
        else "catalogo/lista.html"
    )
    return render(request, template, contexto)


def detalle(request, slug):
    producto = get_object_or_404(
        Producto.objects.select_related("categoria", "marca").prefetch_related(
            "imagenes"
        ),
        slug=slug,
        activo=True,
    )
    relacionados = (
        Producto.objects.filter(categoria=producto.categoria, activo=True)
        .exclude(pk=producto.pk)
        .select_related("marca")[:4]
    )
    return render(
        request,
        "catalogo/detalle.html",
        {"producto": producto, "relacionados": relacionados},
    )
