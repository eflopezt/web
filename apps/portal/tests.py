"""Tests del portal cliente."""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.catalogo.models import Categoria, Producto
from apps.clientes.models import Cliente
from apps.cotizaciones.models import Cotizacion, LineaCotizacion


User = get_user_model()


class PortalAccessTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("cli", "c@c.pe", "pass1234")
        self.cliente = Cliente.objects.create(
            razon_social="ClienteTest", email="c@c.pe", usuario=self.user
        )

    def test_dashboard_redirect_si_no_logged(self):
        r = self.client.get(reverse("portal:dashboard"))
        self.assertEqual(r.status_code, 302)
        self.assertIn("login", r["Location"])

    def test_dashboard_accesible_con_cliente(self):
        self.client.login(username="cli", password="pass1234")
        r = self.client.get(reverse("portal:dashboard"))
        self.assertEqual(r.status_code, 200)

    def test_no_ve_cotizacion_de_otro_cliente(self):
        otro_cliente = Cliente.objects.create(razon_social="Otro", email="o@o.pe")
        cot = Cotizacion.objects.create(cliente=otro_cliente)
        self.client.login(username="cli", password="pass1234")
        r = self.client.get(reverse("portal:cotizacion_detalle", args=[cot.codigo]))
        self.assertEqual(r.status_code, 404)

    def test_aceptar_cotizacion_genera_pedido(self):
        cot = Cotizacion.objects.create(cliente=self.cliente, estado="enviada")
        cat = Categoria.objects.create(nombre="C")
        prod = Producto.objects.create(nombre="P", sku="P-1", categoria=cat)
        LineaCotizacion.objects.create(
            cotizacion=cot, producto=prod, descripcion="P",
            cantidad=1, precio_unitario=Decimal("118.00"),
        )
        cot.recalcular_totales()

        self.client.login(username="cli", password="pass1234")
        r = self.client.post(reverse("portal:cotizacion_aceptar", args=[cot.codigo]), follow=True)
        self.assertEqual(r.status_code, 200)
        cot.refresh_from_db()
        self.assertEqual(cot.estado, "aceptada")
        self.assertEqual(self.cliente.pedidos.count(), 1)


class IntranetAccessTests(TestCase):
    def setUp(self):
        from django.contrib.auth.models import Group
        self.staff_group = Group.objects.create(name="Staff Intranet")
        self.staff = User.objects.create_user("st", "s@s.pe", "pass1234")
        self.staff.groups.add(self.staff_group)
        self.cli_user = User.objects.create_user("cl", "cl@cl.pe", "pass1234")
        Cliente.objects.create(razon_social="X", email="cl@cl.pe", usuario=self.cli_user)

    def test_intranet_no_accesible_para_cliente(self):
        self.client.login(username="cl", password="pass1234")
        r = self.client.get(reverse("intranet:dashboard"))
        self.assertEqual(r.status_code, 403)

    def test_intranet_accesible_para_staff(self):
        self.client.login(username="st", password="pass1234")
        r = self.client.get(reverse("intranet:dashboard"))
        self.assertEqual(r.status_code, 200)
