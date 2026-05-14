from django.urls import path

from . import views

app_name = "intranet"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),

    # Solicitudes
    path("solicitudes/", views.solicitudes_lista, name="solicitudes"),
    path("solicitudes/<str:codigo>/", views.solicitud_detalle, name="solicitud_detalle"),
    path("solicitudes/<str:codigo>/cotizar/", views.solicitud_cotizar, name="solicitud_cotizar"),

    # Cotizaciones
    path("cotizaciones/", views.cotizaciones_lista, name="cotizaciones"),
    path("cotizaciones/nueva/", views.cotizacion_nueva, name="cotizacion_nueva"),
    path("cotizaciones/<str:codigo>/", views.cotizacion_detalle, name="cotizacion_detalle"),
    path("cotizaciones/<str:codigo>/editar/", views.cotizacion_editar, name="cotizacion_editar"),
    path("cotizaciones/<str:codigo>/lineas/agregar/", views.cotizacion_linea_agregar, name="cotizacion_linea_agregar"),
    path("cotizaciones/<str:codigo>/lineas/<int:linea_pk>/eliminar/", views.cotizacion_linea_eliminar, name="cotizacion_linea_eliminar"),
    path("cotizaciones/<str:codigo>/enviar/", views.cotizacion_enviar, name="cotizacion_enviar"),
    path("cotizaciones/<str:codigo>/marcar/<str:estado>/", views.cotizacion_marcar, name="cotizacion_marcar"),
    path("cotizaciones/<str:codigo>/pdf/", views.cotizacion_pdf, name="cotizacion_pdf"),
    path("cotizaciones/<str:codigo>/duplicar/", views.cotizacion_duplicar, name="cotizacion_duplicar"),
    path("cotizaciones/<str:codigo>/a-pedido/", views.cotizacion_a_pedido, name="cotizacion_a_pedido"),

    # Pedidos
    path("pedidos/", views.pedidos_lista, name="pedidos"),
    path("pedidos/<str:codigo>/", views.pedido_detalle, name="pedido_detalle"),
    path("pedidos/<str:codigo>/estado/<str:estado>/", views.pedido_cambiar_estado, name="pedido_cambiar_estado"),
    path("pedidos/<str:codigo>/facturar/", views.pedido_facturar, name="pedido_facturar"),

    # Facturas
    path("facturas/", views.facturas_lista, name="facturas"),
    path("facturas/<int:pk>/", views.factura_detalle, name="factura_detalle"),
    path("facturas/<int:pk>/sunat/", views.factura_sunat, name="factura_sunat"),
    path("facturas/<int:pk>/anular/", views.factura_anular, name="factura_anular"),
    path("facturas/<int:pk>/pagos/agregar/", views.factura_pago_agregar, name="factura_pago_agregar"),
    path("facturas/<int:pk>/pdf/", views.factura_pdf, name="factura_pdf"),

    # Clientes
    path("clientes/", views.clientes_lista, name="clientes"),
    path("clientes/nuevo/", views.cliente_nuevo, name="cliente_nuevo"),
    path("clientes/<int:pk>/", views.cliente_detalle, name="cliente_detalle"),
    path("clientes/<int:pk>/editar/", views.cliente_editar, name="cliente_editar"),

    # Productos (shortcut a admin)
    path("productos/", views.productos_lista, name="productos"),
]
