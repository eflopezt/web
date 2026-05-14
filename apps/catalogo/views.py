from urllib.parse import urlencode

from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, render

from .models import Categoria, Marca, Producto


PER_PAGE = 24


def _build_query(*, q="", marca_slugs=None, categoria_slugs=None, disp="", orden=""):
    """Return a `?a=b&c=d` query string for the current filter state.

    Empty / default values are omitted so URLs stay clean and shareable.
    """
    params = []
    if q:
        params.append(("q", q))
    if marca_slugs:
        params.append(("marca", ",".join(marca_slugs)))
    if categoria_slugs:
        params.append(("categoria", ",".join(categoria_slugs)))
    if disp:
        params.append(("disp", disp))
    if orden and orden != "destacado":
        params.append(("orden", orden))
    return ("?" + urlencode(params)) if params else "?"


def _split_csv(value):
    """Split a CSV string into a list of cleaned slugs (lowercased, deduped, order-preserved)."""
    if not value:
        return []
    seen = set()
    out = []
    for raw in value.split(","):
        slug = raw.strip().lower()
        if slug and slug not in seen:
            seen.add(slug)
            out.append(slug)
    return out


def _full_text_filter(qs, query):
    """Search nombre + descripcion_corta + presentacion + sku + marca.

    If the query has 2+ words, every word must match somewhere (AND across words,
    OR across fields for each word) — gives "intelligent" multi-word behavior.
    """
    words = [w for w in query.split() if w]
    if not words:
        return qs
    for word in words:
        qs = qs.filter(
            Q(nombre__icontains=word)
            | Q(descripcion_corta__icontains=word)
            | Q(presentacion__icontains=word)
            | Q(sku__icontains=word)
            | Q(marca__nombre__icontains=word)
        )
    return qs


def _apply_ordering(qs, orden):
    if orden == "nombre":
        return qs.order_by("nombre")
    if orden == "recientes":
        return qs.order_by("-creado", "nombre")
    # default: destacado + nombre
    return qs.order_by("-destacado", "nombre")


def catalogo(request, categoria_slug=None):
    # Base queryset — only loaded once.
    base = (
        Producto.objects.filter(activo=True)
        .select_related("categoria", "marca")
        .only(
            "id", "nombre", "slug", "sku", "presentacion",
            "imagen", "disponibilidad", "destacado", "activo",
            "categoria__id", "categoria__nombre", "categoria__slug",
            "marca__id", "marca__nombre", "marca__slug",
        )
    )

    # ---- Read filters from GET ----
    q = request.GET.get("q", "").strip()

    marca_slugs = _split_csv(request.GET.get("marca", ""))

    # If the path provides a categoria, seed it into the query-state.
    categoria_actual = None
    categoria_slugs = _split_csv(request.GET.get("categoria", ""))
    if categoria_slug:
        categoria_actual = get_object_or_404(
            Categoria, slug=categoria_slug, activa=True
        )
        # Only seed if the URL didn't already specify ?categoria= explicitly.
        if not categoria_slugs:
            categoria_slugs = [categoria_slug]

    disp = request.GET.get("disp", "").strip()
    orden = request.GET.get("orden", "").strip() or "destacado"

    # ---- Apply filters ----
    productos = base
    if q:
        productos = _full_text_filter(productos, q)
    if marca_slugs:
        productos = productos.filter(marca__slug__in=marca_slugs)
    if categoria_slugs:
        productos = productos.filter(categoria__slug__in=categoria_slugs)
    if disp:
        productos = productos.filter(disponibilidad=disp)

    productos = _apply_ordering(productos, orden)

    paginator = Paginator(productos, PER_PAGE)
    page = paginator.get_page(request.GET.get("page"))

    # ---- Brand-aware suggestion (intelligent search) ----
    marca_sugerida = None
    if q and not marca_slugs:
        q_lower = q.lower()
        for m in Marca.objects.filter(activa=True):
            m_name = m.nombre.lower()
            if q_lower == m_name or q_lower in m_name or m_name in q_lower:
                marca_sugerida = m
                break

    # ---- Sidebar counts (respect every other filter, so the user can see
    # impact before clicking).
    # For marca counts: don't filter by marca (so all marcas remain visible).
    base_for_counts = base
    if q:
        base_for_counts = _full_text_filter(base_for_counts, q)
    if disp:
        base_for_counts = base_for_counts.filter(disponibilidad=disp)
    if categoria_slugs:
        base_for_counts = base_for_counts.filter(categoria__slug__in=categoria_slugs)

    marca_counts = {
        row["marca__slug"]: row["n"]
        for row in base_for_counts.values("marca__slug").annotate(n=Count("id"))
        if row["marca__slug"]
    }

    # For categoria counts: don't filter by categoria.
    base_for_cat = base
    if q:
        base_for_cat = _full_text_filter(base_for_cat, q)
    if disp:
        base_for_cat = base_for_cat.filter(disponibilidad=disp)
    if marca_slugs:
        base_for_cat = base_for_cat.filter(marca__slug__in=marca_slugs)
    categoria_counts = {
        row["categoria__slug"]: row["n"]
        for row in base_for_cat.values("categoria__slug").annotate(n=Count("id"))
    }

    marcas = list(Marca.objects.filter(activa=True))
    for m in marcas:
        m.count = marca_counts.get(m.slug, 0)
        m.selected = m.slug in marca_slugs

    categorias = list(Categoria.objects.filter(activa=True))
    for c in categorias:
        c.count = categoria_counts.get(c.slug, 0)
        c.selected = c.slug in categoria_slugs

    # ---- Chips (active filters) ----
    # Each chip carries a `remove_url` query string that drops just that filter.
    chips = []

    def _chip(label, **drop):
        # Start from current state, then override with dropped values.
        state = {
            "q": q,
            "marca_slugs": list(marca_slugs),
            "categoria_slugs": list(categoria_slugs),
            "disp": disp,
            "orden": orden,
        }
        state.update(drop)
        chips.append({"label": label, "remove_url": _build_query(**state)})

    if q:
        _chip(f'Búsqueda: "{q}"', q="")
    for m in marcas:
        if m.selected:
            _chip(
                f"Marca: {m.nombre}",
                marca_slugs=[s for s in marca_slugs if s != m.slug],
            )
    for c in categorias:
        if c.selected:
            _chip(
                f"Categoría: {c.nombre}",
                categoria_slugs=[s for s in categoria_slugs if s != c.slug],
            )
    if disp:
        disp_label = dict(Producto.DISPONIBILIDAD_CHOICES).get(disp, disp)
        _chip(f"Disponibilidad: {disp_label}", disp="")
    if orden and orden != "destacado":
        orden_label = {
            "nombre": "Alfabético",
            "recientes": "Más recientes",
        }.get(orden, orden)
        _chip(f"Orden: {orden_label}", orden="")

    # ---- Per-control URLs the template uses to render checkboxes / selects.
    def url_toggle_marca(slug):
        new = [s for s in marca_slugs if s != slug] if slug in marca_slugs else marca_slugs + [slug]
        return _build_query(
            q=q, marca_slugs=new, categoria_slugs=categoria_slugs,
            disp=disp, orden=orden,
        )

    def url_toggle_categoria(slug):
        new = [s for s in categoria_slugs if s != slug] if slug in categoria_slugs else categoria_slugs + [slug]
        return _build_query(
            q=q, marca_slugs=marca_slugs, categoria_slugs=new,
            disp=disp, orden=orden,
        )

    def url_set_disp(value):
        return _build_query(
            q=q, marca_slugs=marca_slugs, categoria_slugs=categoria_slugs,
            disp=value, orden=orden,
        )

    def url_set_orden(value):
        return _build_query(
            q=q, marca_slugs=marca_slugs, categoria_slugs=categoria_slugs,
            disp=disp, orden=value,
        )

    for m in marcas:
        m.toggle_url = url_toggle_marca(m.slug)
    for c in categorias:
        c.toggle_url = url_toggle_categoria(c.slug)

    disp_options = [
        ("", "Todas", url_set_disp("")),
        ("en_stock", "En stock", url_set_disp("en_stock")),
        ("bajo_pedido", "Bajo pedido", url_set_disp("bajo_pedido")),
    ]

    orden_options = [
        ("destacado", "Destacados primero", url_set_orden("destacado")),
        ("nombre", "Alfabético", url_set_orden("nombre")),
        ("recientes", "Más recientes", url_set_orden("recientes")),
    ]

    # URL to apply the suggested marca (intelligent search)
    aplicar_marca_url = None
    if marca_sugerida:
        aplicar_marca_url = _build_query(
            q="",
            marca_slugs=[marca_sugerida.slug],
            categoria_slugs=categoria_slugs,
            disp=disp,
            orden=orden,
        )

    clear_all_url = _build_query()

    contexto = {
        "categoria_actual": categoria_actual,
        "categorias": categorias,
        "marcas": marcas,
        "productos": page.object_list,
        "page_obj": page,
        # Filter state
        "q": q,
        "marca_slugs": marca_slugs,
        "marca_slugs_csv": ",".join(marca_slugs),
        "categoria_slugs": categoria_slugs,
        "categoria_slugs_csv": ",".join(categoria_slugs),
        "disp_actual": disp,
        "orden_actual": orden,
        # Extras
        "chips": chips,
        "marca_sugerida": marca_sugerida,
        "aplicar_marca_url": aplicar_marca_url,
        "clear_all_url": clear_all_url,
        "disp_options": disp_options,
        "orden_options": orden_options,
        "total_productos": page.paginator.count,
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
    # Similar products: same categoria first, prefer same marca and close
    # precio_referencia. Build with Q and order by similarity heuristics.
    similares_qs = (
        Producto.objects.filter(categoria=producto.categoria, activo=True)
        .exclude(pk=producto.pk)
        .select_related("marca", "categoria")
    )

    # Prefer same marca first
    if producto.marca_id:
        misma_marca = list(similares_qs.filter(marca=producto.marca)[:4])
    else:
        misma_marca = []

    similares = list(misma_marca)
    if len(similares) < 4:
        otros = (
            similares_qs.exclude(pk__in=[p.pk for p in similares])
            .order_by("-destacado", "nombre")[: 4 - len(similares)]
        )
        similares.extend(list(otros))

    # If still short, fall back to same marca outside categoria
    if len(similares) < 4 and producto.marca_id:
        fallback = (
            Producto.objects.filter(marca=producto.marca, activo=True)
            .exclude(pk=producto.pk)
            .exclude(pk__in=[p.pk for p in similares])
            .select_related("marca", "categoria")[: 4 - len(similares)]
        )
        similares.extend(list(fallback))

    return render(
        request,
        "catalogo/detalle.html",
        {"producto": producto, "relacionados": similares[:4]},
    )
