from django.urls import path

from . import views

app_name = "portal"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("solicitudes/", views.solicitudes, name="solicitudes"),
    path("solicitudes/<str:codigo>/", views.solicitud_detalle, name="solicitud_detalle"),
    path("cotizaciones/", views.cotizaciones, name="cotizaciones"),
    path("cotizaciones/<str:codigo>/", views.cotizacion_detalle, name="cotizacion_detalle"),
    path("cotizaciones/<str:codigo>/aceptar/", views.cotizacion_aceptar, name="cotizacion_aceptar"),
    path("cotizaciones/<str:codigo>/rechazar/", views.cotizacion_rechazar, name="cotizacion_rechazar"),
    path("cotizaciones/<str:codigo>/pdf/", views.cotizacion_pdf, name="cotizacion_pdf"),
    path("pedidos/", views.pedidos, name="pedidos"),
    path("pedidos/<str:codigo>/", views.pedido_detalle, name="pedido_detalle"),
    path("facturas/", views.facturas, name="facturas"),
    path("facturas/<int:pk>/", views.factura_detalle, name="factura_detalle"),
    path("facturas/<int:pk>/pdf/", views.factura_pdf, name="factura_pdf"),
    path("perfil/", views.perfil, name="perfil"),
]
