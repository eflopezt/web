"""Carrito en sesión: dict {producto_id: cantidad}."""

from apps.catalogo.models import Producto

SESSION_KEY = "carrito"


def _get(session):
    if SESSION_KEY not in session:
        session[SESSION_KEY] = {}
    return session[SESSION_KEY]


def agregar(session, producto_id, cantidad=1):
    carrito = _get(session)
    pid = str(producto_id)
    carrito[pid] = carrito.get(pid, 0) + int(cantidad)
    session.modified = True
    return carrito


def actualizar(session, producto_id, cantidad):
    carrito = _get(session)
    pid = str(producto_id)
    cantidad = int(cantidad)
    if cantidad <= 0:
        carrito.pop(pid, None)
    else:
        carrito[pid] = cantidad
    session.modified = True
    return carrito


def quitar(session, producto_id):
    carrito = _get(session)
    carrito.pop(str(producto_id), None)
    session.modified = True
    return carrito


def vaciar(session):
    session[SESSION_KEY] = {}
    session.modified = True


def items(session):
    carrito = _get(session)
    if not carrito:
        return []
    ids = [int(k) for k in carrito.keys()]
    productos = {
        p.id: p
        for p in Producto.objects.filter(id__in=ids, activo=True).select_related(
            "categoria", "marca"
        )
    }
    out = []
    for pid_str, cant in carrito.items():
        prod = productos.get(int(pid_str))
        if prod:
            out.append({"producto": prod, "cantidad": cant})
    return out


def total_unidades(session):
    return sum(int(v) for v in _get(session).values())
