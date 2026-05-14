from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def staff_intranet_required(view):
    """Permite acceso a is_staff o miembros del grupo 'Staff Intranet'."""

    @wraps(view)
    @login_required
    def _wrapped(request, *args, **kwargs):
        u = request.user
        if u.is_staff or u.groups.filter(name="Staff Intranet").exists():
            return view(request, *args, **kwargs)
        raise PermissionDenied
    return _wrapped


def cliente_required(view):
    """Permite acceso al usuario si tiene perfil Cliente asociado."""

    @wraps(view)
    @login_required
    def _wrapped(request, *args, **kwargs):
        u = request.user
        if hasattr(u, "cliente") and u.cliente:
            return view(request, *args, **kwargs)
        raise PermissionDenied
    return _wrapped
