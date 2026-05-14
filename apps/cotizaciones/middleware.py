from . import carrito


class CarritoContadorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.carrito_count = carrito.total_unidades(request.session)
        return self.get_response(request)
