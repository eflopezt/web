from django.shortcuts import render
from apps.catalogo.models import Categoria, Producto


def home(request):
    productos_destacados = (
        Producto.objects.filter(activo=True, destacado=True)
        .select_related("categoria", "marca")[:8]
    )
    categorias = Categoria.objects.filter(activa=True).order_by("orden", "nombre")[:8]
    return render(
        request,
        "core/home.html",
        {
            "productos_destacados": productos_destacados,
            "categorias": categorias,
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
