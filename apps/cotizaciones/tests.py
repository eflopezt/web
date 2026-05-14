"""Tests básicos de cálculo de cotización (IGV)."""

from decimal import Decimal

from django.test import TestCase

from apps.catalogo.models import Categoria, Producto
from apps.clientes.models import Cliente

from .models import Cotizacion, LineaCotizacion


class CotizacionTotalesTests(TestCase):
    def setUp(self):
        self.cat = Categoria.objects.create(nombre="Test")
        self.producto = Producto.objects.create(
            nombre="Detergente test", sku="TEST-1", categoria=self.cat
        )
        self.cliente = Cliente.objects.create(
            razon_social="Test Corp",
            email="test@example.com",
        )

    def test_iva_incluido_calcula_base_e_igv(self):
        cot = Cotizacion.objects.create(cliente=self.cliente, incluye_igv=True)
        LineaCotizacion.objects.create(
            cotizacion=cot,
            descripcion="Item",
            cantidad=Decimal("2"),
            precio_unitario=Decimal("59.00"),  # 118 total con IGV incluido
        )
        cot.recalcular_totales()
        cot.refresh_from_db()
        self.assertEqual(cot.total, Decimal("118.00"))
        self.assertEqual(cot.subtotal, Decimal("100.00"))
        self.assertEqual(cot.igv, Decimal("18.00"))

    def test_iva_no_incluido_suma_18pct(self):
        cot = Cotizacion.objects.create(cliente=self.cliente, incluye_igv=False)
        LineaCotizacion.objects.create(
            cotizacion=cot,
            descripcion="Item",
            cantidad=Decimal("1"),
            precio_unitario=Decimal("100.00"),
        )
        cot.recalcular_totales()
        cot.refresh_from_db()
        self.assertEqual(cot.subtotal, Decimal("100.00"))
        self.assertEqual(cot.igv, Decimal("18.00"))
        self.assertEqual(cot.total, Decimal("118.00"))

    def test_descuento_se_aplica_a_subtotal_linea(self):
        cot = Cotizacion.objects.create(cliente=self.cliente, incluye_igv=True)
        LineaCotizacion.objects.create(
            cotizacion=cot,
            descripcion="Item",
            cantidad=Decimal("1"),
            precio_unitario=Decimal("100.00"),
            descuento_pct=Decimal("10.00"),
        )
        cot.recalcular_totales()
        cot.refresh_from_db()
        self.assertEqual(cot.total, Decimal("90.00"))

    def test_codigo_se_genera_automaticamente(self):
        cot = Cotizacion.objects.create(cliente=self.cliente)
        self.assertTrue(cot.codigo.startswith("COT-"))
        self.assertIn(str(cot.pk).zfill(5), cot.codigo)

    def test_fecha_vencimiento_se_calcula_segun_validez(self):
        from datetime import date, timedelta
        cot = Cotizacion.objects.create(
            cliente=self.cliente,
            fecha_emision=date(2025, 1, 1),
            validez_dias=10,
        )
        self.assertEqual(cot.fecha_vencimiento, date(2025, 1, 11))


class FacturaCorrelativoTests(TestCase):
    def test_correlativo_se_autoincrementa_por_serie(self):
        from apps.facturacion.models import Factura

        cliente = Cliente.objects.create(razon_social="X", email="x@x.pe")
        f1 = Factura.objects.create(cliente=cliente, serie="F001")
        f2 = Factura.objects.create(cliente=cliente, serie="F001")
        f_b1 = Factura.objects.create(cliente=cliente, serie="B001", tipo="boleta")
        self.assertEqual(f1.correlativo, 1)
        self.assertEqual(f2.correlativo, 2)
        self.assertEqual(f_b1.correlativo, 1)
        self.assertEqual(f1.numero, "F001-00000001")
        self.assertEqual(f_b1.numero, "B001-00000001")

    def test_saldo_y_estado_pago(self):
        from decimal import Decimal
        from apps.facturacion.models import Factura, LineaFactura, Pago

        cliente = Cliente.objects.create(razon_social="X", email="x@x.pe")
        f = Factura.objects.create(cliente=cliente)
        LineaFactura.objects.create(
            factura=f, descripcion="x", cantidad=1, precio_unitario=Decimal("118.00")
        )
        f.recalcular_totales()
        self.assertEqual(f.total, Decimal("118.00"))
        self.assertEqual(f.saldo, Decimal("118.00"))

        Pago.objects.create(factura=f, monto=Decimal("50.00"))
        f.actualizar_estado_pago()
        self.assertEqual(f.estado, "parcial")

        Pago.objects.create(factura=f, monto=Decimal("68.00"))
        f.actualizar_estado_pago()
        self.assertEqual(f.estado, "pagada")
        self.assertEqual(f.saldo, Decimal("0.00"))
