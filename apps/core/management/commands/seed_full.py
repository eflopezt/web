"""Seed completo de demo: usuarios + clientes + solicitudes + cotizaciones + pedidos + facturas + pagos.

Idempotente: usa get_or_create por documento/email/codigo y sale temprano si ya hay datos.
"""

import random
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.catalogo.models import Producto
from apps.clientes.models import Cliente
from apps.cotizaciones.models import (
    Cotizacion,
    ItemSolicitud,
    LineaCotizacion,
    SolicitudCotizacion,
)
from apps.facturacion.models import Factura, LineaFactura, Pago
from apps.pedidos.models import LineaPedido, Pedido


User = get_user_model()


CLIENTES_DEMO = [
    {
        "tipo": "empresa", "razon_social": "Hoteles Brisamar SAC",
        "nombre_comercial": "Brisamar Hotels", "documento": "20512345671",
        "email": "compras@brisamar.com.pe", "telefono": "+51 998 111 222",
        "direccion": "Av. Larco 1234", "departamento": "Lima", "ciudad": "Miraflores",
    },
    {
        "tipo": "empresa", "razon_social": "Industrias Andinas SAC",
        "nombre_comercial": "InduAndina", "documento": "20512345672",
        "email": "logistica@induandina.pe", "telefono": "+51 998 222 333",
        "direccion": "Carretera Central km 8.5", "departamento": "Lima", "ciudad": "Ate",
    },
    {
        "tipo": "empresa", "razon_social": "Clínica Vida Plena EIRL",
        "nombre_comercial": "Vida Plena", "documento": "20512345673",
        "email": "admin@vidaplena.pe", "telefono": "+51 998 333 444",
        "direccion": "Calle Los Médicos 456", "departamento": "Lima", "ciudad": "San Isidro",
    },
    {
        "tipo": "persona", "razon_social": "Carlos Eduardo Mendoza Rojas",
        "documento": "45678123", "email": "cmendoza.demo@gmail.com",
        "telefono": "+51 998 444 555", "direccion": "Jr. Las Begonias 789",
        "departamento": "Lima", "ciudad": "Surco",
    },
]


SOLICITUDES_DEMO = [
    {
        "tipo_cliente": "empresa", "razon_social": "Hoteles Brisamar SAC", "ruc": "20512345671",
        "nombre_contacto": "Sandra Pérez", "email": "compras@brisamar.com.pe", "telefono": "+51 998 111 222",
        "ciudad": "Miraflores", "departamento": "Lima",
        "mensaje": "Necesitamos reabastecimiento mensual para 3 hoteles. Por favor coordinar visita.",
        "items": [("DETERGENTE", 24), ("DESINFECTANTE", 24), ("PAPEL", 50)],
    },
    {
        "tipo_cliente": "empresa", "razon_social": "Industrias Andinas SAC", "ruc": "20512345672",
        "nombre_contacto": "Roberto Aguilar", "email": "logistica@induandina.pe", "telefono": "+51 998 222 333",
        "ciudad": "Ate", "departamento": "Lima",
        "mensaje": "Cotizar productos de mantenimiento para planta industrial 8000m².",
        "items": [("DESENGRASANTE", 12), ("HIDROLAVADORA", 1), ("ASPIRADORA", 1)],
    },
    {
        "tipo_cliente": "persona", "razon_social": "Carlos Eduardo Mendoza Rojas", "ruc": "",
        "nombre_contacto": "Carlos Mendoza", "email": "cmendoza.demo@gmail.com", "telefono": "+51 998 444 555",
        "ciudad": "Surco", "departamento": "Lima",
        "mensaje": "Productos para empresa de limpieza pequeña, 6 empleados.",
        "items": [("PAPEL", 5), ("DETERGENTE", 4)],
    },
]


class Command(BaseCommand):
    help = "Seed completo de demo (usuarios, clientes, solicitudes, cotizaciones, pedidos, facturas)."

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true", help="Borra datos transaccionales antes.")

    @transaction.atomic
    def handle(self, *args, **opts):
        random.seed(42)

        # 1) productos + categorías
        call_command("seed_demo")
        self.stdout.write(self.style.SUCCESS("[OK] catalogo base"))

        # 2) grupos
        staff_group, _ = Group.objects.get_or_create(name="Staff Intranet")
        cliente_group, _ = Group.objects.get_or_create(name="Cliente")

        # 3) usuarios demo
        admin, created = User.objects.get_or_create(
            username="admin",
            defaults={"email": "admin@limpiapro.pe", "is_staff": True, "is_superuser": True},
        )
        if created:
            admin.set_password("admin")
            admin.save()
        staff, created = User.objects.get_or_create(
            username="staff",
            defaults={"email": "staff@limpiapro.pe", "is_staff": True, "first_name": "Vendedor", "last_name": "Demo"},
        )
        if created:
            staff.set_password("staff")
            staff.save()
        staff.groups.add(staff_group)

        cliente_user, created = User.objects.get_or_create(
            username="cliente",
            defaults={"email": "compras@brisamar.com.pe", "first_name": "Sandra", "last_name": "Pérez"},
        )
        if created:
            cliente_user.set_password("cliente")
            cliente_user.save()
        cliente_user.groups.add(cliente_group)
        self.stdout.write(self.style.SUCCESS("[OK] usuarios: admin/admin · staff/staff · cliente/cliente"))

        # 4) Clientes
        clientes = {}
        for data in CLIENTES_DEMO:
            c, _ = Cliente.objects.get_or_create(
                email=data["email"],
                defaults=data,
            )
            clientes[c.email] = c
        # Vincular cliente_user
        c0 = clientes["compras@brisamar.com.pe"]
        if not c0.usuario_id:
            c0.usuario = cliente_user
            c0.save(update_fields=["usuario"])
        self.stdout.write(self.style.SUCCESS(f"[OK] {len(clientes)} clientes"))

        # Idempotencia: si ya hay cotizaciones, no duplicar el resto del seed transaccional
        if Cotizacion.objects.exists() and not opts["reset"]:
            self.stdout.write(self.style.WARNING("Datos transaccionales ya existen. Usa --reset para regenerar."))
            return
        if opts["reset"]:
            Pago.objects.all().delete()
            LineaFactura.objects.all().delete()
            Factura.objects.all().delete()
            LineaPedido.objects.all().delete()
            Pedido.objects.all().delete()
            LineaCotizacion.objects.all().delete()
            Cotizacion.objects.all().delete()
            ItemSolicitud.objects.all().delete()
            SolicitudCotizacion.objects.all().delete()
            self.stdout.write(self.style.WARNING("Datos transaccionales borrados."))

        productos_por_keyword = {
            "DETERGENTE": Producto.objects.filter(nombre__icontains="Detergente líquido").first(),
            "DESENGRASANTE": Producto.objects.filter(nombre__icontains="Desengrasante").first(),
            "DESINFECTANTE": Producto.objects.filter(nombre__icontains="Amonio cuaternario").first(),
            "PAPEL": Producto.objects.filter(nombre__icontains="Papel higiénico").first(),
            "HIDROLAVADORA": Producto.objects.filter(nombre__icontains="Hidrolavadora").first(),
            "ASPIRADORA": Producto.objects.filter(nombre__icontains="Aspiradora").first(),
        }

        # Precios sugeridos demo (con IGV incluido)
        precios = {
            "DETERGENTE": Decimal("48.90"),
            "DESENGRASANTE": Decimal("89.50"),
            "DESINFECTANTE": Decimal("65.00"),
            "PAPEL": Decimal("180.00"),
            "HIDROLAVADORA": Decimal("1890.00"),
            "ASPIRADORA": Decimal("1450.00"),
        }

        # 5) Solicitudes públicas
        solicitudes_creadas = []
        for sd in SOLICITUDES_DEMO:
            email = sd["email"]
            sol = SolicitudCotizacion.objects.create(
                tipo_cliente=sd["tipo_cliente"],
                razon_social=sd["razon_social"],
                ruc=sd["ruc"],
                nombre_contacto=sd["nombre_contacto"],
                email=email,
                telefono=sd["telefono"],
                ciudad=sd["ciudad"],
                departamento=sd["departamento"],
                mensaje=sd["mensaje"],
                cliente=clientes.get(email),
                estado="cotizada",
            )
            for key, cant in sd["items"]:
                prod = productos_por_keyword.get(key)
                if prod:
                    ItemSolicitud.objects.create(
                        solicitud=sol,
                        producto=prod,
                        nombre_snapshot=prod.nombre,
                        sku_snapshot=prod.sku,
                        cantidad=cant,
                    )
            solicitudes_creadas.append(sol)
        self.stdout.write(self.style.SUCCESS(f"[OK] {len(solicitudes_creadas)} solicitudes"))

        # 6) Cotizaciones a partir de las solicitudes
        cotizaciones = []
        estados = ["aceptada", "enviada", "borrador"]
        for i, sol in enumerate(solicitudes_creadas):
            estado = estados[i % len(estados)]
            cot = Cotizacion.objects.create(
                cliente=sol.cliente,
                solicitud=sol,
                creada_por=staff,
                estado=estado,
                enviada_en=timezone.now() if estado != "borrador" else None,
                observaciones="Precios sujetos a confirmación de stock al momento de la orden.",
            )
            for it in sol.items.all():
                key = next((k for k, p in productos_por_keyword.items() if p and p.pk == it.producto_id), None)
                precio = precios.get(key, Decimal("50.00"))
                LineaCotizacion.objects.create(
                    cotizacion=cot,
                    producto=it.producto,
                    descripcion=it.nombre_snapshot,
                    sku=it.sku_snapshot,
                    unidad="UND",
                    cantidad=it.cantidad,
                    precio_unitario=precio,
                    descuento_pct=Decimal("5.00") if i == 0 else Decimal("0"),
                    orden=it.pk,
                )
            cot.recalcular_totales()
            cotizaciones.append(cot)
        self.stdout.write(self.style.SUCCESS(f"[OK] {len(cotizaciones)} cotizaciones"))

        # 7) Pedidos a partir de cotizaciones aceptadas
        pedidos = []
        for cot in [c for c in cotizaciones if c.estado == "aceptada"]:
            pedido = Pedido.objects.create(
                cliente=cot.cliente,
                cotizacion=cot,
                direccion_envio=cot.cliente.direccion,
                creado_por=staff,
                estado="entregado",
                fecha_entrega_estimada=timezone.localdate() - timedelta(days=3),
                fecha_entrega_real=timezone.localdate() - timedelta(days=2),
            )
            for l in cot.lineas.all():
                LineaPedido.objects.create(
                    pedido=pedido,
                    producto=l.producto,
                    descripcion=l.descripcion,
                    sku=l.sku,
                    unidad=l.unidad,
                    cantidad=l.cantidad,
                    precio_unitario=l.precio_unitario,
                    descuento_pct=l.descuento_pct,
                    orden=l.orden,
                )
            pedido.recalcular_totales()
            pedidos.append(pedido)

        # Crear un par de pedidos extra para mostrar variedad de estados
        if cotizaciones:
            cot_base = cotizaciones[0]
            extra_p1 = Pedido.objects.create(
                cliente=cot_base.cliente, cotizacion=cot_base,
                direccion_envio=cot_base.cliente.direccion, creado_por=staff,
                estado="preparando", fecha=timezone.localdate() - timedelta(days=1),
            )
            for l in cot_base.lineas.all()[:2]:
                LineaPedido.objects.create(
                    pedido=extra_p1, producto=l.producto, descripcion=l.descripcion,
                    sku=l.sku, unidad=l.unidad, cantidad=l.cantidad,
                    precio_unitario=l.precio_unitario, descuento_pct=l.descuento_pct, orden=l.orden,
                )
            extra_p1.recalcular_totales()
            pedidos.append(extra_p1)
        self.stdout.write(self.style.SUCCESS(f"[OK] {len(pedidos)} pedidos"))

        # 8) Facturas para los pedidos entregados
        facturas = []
        for p in [x for x in pedidos if x.estado == "entregado"]:
            f = Factura.objects.create(
                tipo="factura", serie="F001",
                cliente=p.cliente, pedido=p,
                creada_por=staff,
                estado_sunat="aceptada",
                hash_sunat=("a3f9b7" + str(p.pk)).ljust(40, "0")[:40],
                fecha_vencimiento=timezone.localdate() + timedelta(days=15),
            )
            for l in p.lineas.all():
                LineaFactura.objects.create(
                    factura=f, producto=l.producto, descripcion=l.descripcion,
                    sku=l.sku, unidad=l.unidad, cantidad=l.cantidad,
                    precio_unitario=l.precio_unitario, descuento_pct=l.descuento_pct, orden=l.orden,
                )
            f.recalcular_totales()
            facturas.append(f)

        # 9) Pagos: una factura totalmente pagada, otra parcial
        if facturas:
            f_pagada = facturas[0]
            Pago.objects.create(
                factura=f_pagada, monto=f_pagada.total, metodo="transferencia",
                referencia="OP-2025-AB12", nota="Pago a 7 días vista",
                fecha=timezone.localdate() - timedelta(days=1), registrado_por=staff,
            )
            f_pagada.actualizar_estado_pago()

        if len(facturas) > 1:
            f_parcial = facturas[1] if len(facturas) > 1 else facturas[0]
            mitad = (f_parcial.total / 2).quantize(Decimal("0.01"))
            Pago.objects.create(
                factura=f_parcial, monto=mitad, metodo="deposito",
                referencia="DEP-99812", fecha=timezone.localdate(),
                registrado_por=staff,
            )
            f_parcial.actualizar_estado_pago()

        # Una boleta a la persona natural
        cliente_persona = clientes.get("cmendoza.demo@gmail.com")
        if cliente_persona and Cotizacion.objects.filter(cliente=cliente_persona, estado="aceptada").exists():
            pass  # ya cubierto arriba

        self.stdout.write(self.style.SUCCESS(f"[OK] {len(facturas)} facturas y pagos"))

        self.stdout.write(self.style.SUCCESS("\n=== Seed completo ==="))
        self.stdout.write("Usuarios demo:")
        self.stdout.write("  admin   / admin    (superuser)")
        self.stdout.write("  staff   / staff    (Staff Intranet → /intranet/)")
        self.stdout.write("  cliente / cliente  (Brisamar → /portal/)")
