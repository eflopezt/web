from django.urls import path
from . import views

app_name = "cotizaciones"

urlpatterns = [
    path("", views.ver_carrito, name="carrito"),
    path("drawer/", views.drawer, name="drawer"),
    path("agregar/<int:producto_id>/", views.agregar, name="agregar"),
    path("actualizar/<int:producto_id>/", views.actualizar, name="actualizar"),
    path("quitar/<int:producto_id>/", views.quitar, name="quitar"),
    path("checkout/", views.checkout, name="checkout"),
    path("exito/<str:codigo>/", views.exito, name="exito"),
]
