from django import forms

from apps.clientes.models import Cliente
from apps.cotizaciones.models import Cotizacion, LineaCotizacion
from apps.facturacion.models import Factura, Pago
from apps.pedidos.models import Pedido


class CotizacionForm(forms.ModelForm):
    class Meta:
        model = Cotizacion
        fields = ("cliente", "fecha_emision", "validez_dias", "incluye_igv", "moneda", "observaciones", "condiciones")
        widgets = {
            "fecha_emision": forms.DateInput(attrs={"type": "date"}),
            "observaciones": forms.Textarea(attrs={"rows": 2}),
            "condiciones": forms.Textarea(attrs={"rows": 4}),
        }


class LineaCotizacionForm(forms.ModelForm):
    class Meta:
        model = LineaCotizacion
        fields = ("producto", "descripcion", "sku", "unidad", "cantidad", "precio_unitario", "descuento_pct")


class PedidoEstadoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ("estado", "fecha_entrega_estimada", "fecha_entrega_real", "observaciones")
        widgets = {
            "fecha_entrega_estimada": forms.DateInput(attrs={"type": "date"}),
            "fecha_entrega_real": forms.DateInput(attrs={"type": "date"}),
            "observaciones": forms.Textarea(attrs={"rows": 2}),
        }


class FacturaForm(forms.ModelForm):
    class Meta:
        model = Factura
        fields = ("tipo", "serie", "cliente", "pedido", "fecha_emision", "fecha_vencimiento", "observaciones")
        widgets = {
            "fecha_emision": forms.DateInput(attrs={"type": "date"}),
            "fecha_vencimiento": forms.DateInput(attrs={"type": "date"}),
            "observaciones": forms.Textarea(attrs={"rows": 2}),
        }


class PagoForm(forms.ModelForm):
    class Meta:
        model = Pago
        fields = ("fecha", "monto", "metodo", "referencia", "nota")
        widgets = {
            "fecha": forms.DateInput(attrs={"type": "date"}),
        }


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = (
            "tipo",
            "razon_social",
            "nombre_comercial",
            "documento",
            "email",
            "telefono",
            "direccion",
            "departamento",
            "ciudad",
            "notas",
            "activo",
        )
