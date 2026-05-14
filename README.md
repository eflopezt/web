# ProClean Servid Innova — Catálogo de productos de limpieza profesional

Catálogo web + intranet + portal cliente para **ProClean Servid Innova**, proveedor peruano de
productos de limpieza profesional para hogares, negocios e industria en Lima y Callao.

> **Tagline**: *Catálogo de productos de limpieza profesional. Cotiza por WhatsApp.*

**Stack**: Django 5.2 · Python 3.12+ · Tailwind CSS + DaisyUI · HTMX · Alpine.js · reportlab · SQLite (dev) / PostgreSQL-ready (prod).

---

## Scope actual del sitio público

El sitio público es **un catálogo orientado a cotización por WhatsApp**, NO un e-commerce con pasarela
de pago. Cada producto y cada categoría tienen un CTA de WhatsApp con mensaje prellenado que abre
una conversación directa con ventas. El carrito y el checkout siguen disponibles internamente como
ruta opcional para generar una solicitud de cotización formal desde el sitio.

- **Sí**: catálogo navegable, búsqueda, filtros, fichas de producto, CTAs de WhatsApp, formulario
  de solicitud, intranet, portal cliente, cotizaciones formales con PDF, facturación SUNAT
  simulada.
- **No** (al menos en sitio público): pasarela de pago online, carrito persistente, precios públicos
  visibles. Los precios se acuerdan en la cotización formal.

## ¿Qué incluye?

### Sitio público (`/`)
- Home con hero, categorías destacadas y productos
- Catálogo con búsqueda, filtros por categoría/marca/disponibilidad y paginación
- Detalle de producto con galería y **CTA WhatsApp con mensaje prellenado** (producto + ficha)
- **Sin precios visibles** — todo se gestiona por solicitud de cotización o WhatsApp
- Carrito en sesión + checkout que genera una solicitud y crea cliente automáticamente

### Portal cliente (`/portal/`)
- Login + registro propio (auto-vincula `User` ↔ `Cliente` por email)
- Dashboard con KPIs personales (solicitudes, cotizaciones, pedidos, saldo pendiente)
- Mis solicitudes (con seguimiento de estado)
- **Mis cotizaciones**: ver detalle, descargar PDF, **aceptar** (genera pedido automático) o **rechazar** con motivo
- Mis pedidos con estado de envío
- Mis facturas con saldo pendiente, descarga PDF e historial de pagos
- Mi perfil editable + cambio de contraseña

### Intranet (`/intranet/`)
- Dashboard con KPIs operativos (solicitudes nuevas, cotizaciones pendientes, pedidos activos, facturas por cobrar, ventas y cobranza del mes)
- **Solicitudes**: lista + detalle + cambio de estado + crear cotización en 1 clic (copia items)
- **Cotizaciones**: CRUD completo, agregar/quitar líneas, recalcular IGV automático, marcar enviada/aceptada/rechazada, duplicar, generar pedido, PDF descargable
- **Pedidos**: cambio de estado (confirmado → preparando → enviado → entregado), facturar (genera factura o boleta automáticamente)
- **Facturas**: emisión, simulación SUNAT (hash + estado_sunat), anulación, registro de pagos parciales/totales, actualización automática de estado, PDF descargable
- **Clientes**: CRM básico — listado con contador de cotizaciones/pedidos/facturas, ficha con histórico completo, edición
- **Productos**: listado con búsqueda, link al admin Django para edición

### PDFs profesionales (reportlab)
- Cotización y factura/boleta con header de emisor, datos del cliente, líneas con totales IGV y condiciones

### Normativa peruana implementada
- IGV 18% calculado automáticamente
- RUC (11 dígitos) o DNI (8 dígitos) validados
- Factura (F001) para empresas / Boleta (B001) para personas naturales
- Series y correlativos por tipo de documento
- Simulación de envío a SUNAT con CDR aceptado/rechazado

### Apps del proyecto
```
apps/
├── core/         decoradores, PDF builder, context processor
├── catalogo/     Categoria, Marca, Producto, ImagenProducto + seed_demo
├── clientes/     Cliente (persona/empresa) + signal de vinculación User↔Cliente
├── cotizaciones/ SolicitudCotizacion (lead público) + Cotizacion (formal con precios)
├── pedidos/      Pedido + LineaPedido
├── facturacion/  Factura, LineaFactura, Pago (simulación SUNAT)
├── portal/       Vistas portal cliente
└── intranet/     Vistas backoffice staff
```

---

## Arrancar en local

```powershell
# 1. Clonar y crear venv
cd C:\Users\edwii\iCloudDrive\CSRT\D\Web
python -m venv venv
.\venv\Scripts\Activate.ps1

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Migrar y sembrar TODO (idempotente)
python manage.py migrate
python manage.py seed_full

# 4. Levantar dev server
python manage.py runserver
```

→ http://localhost:8000

## Usuarios demo (creados por `seed_full`)

| Usuario | Contraseña | Acceso |
|---------|------------|--------|
| `admin` | `admin` | Django admin (superuser) |
| `staff` | `staff` | Intranet `/intranet/` — Staff Intranet |
| `cliente` | `cliente` | Portal `/portal/` — vinculado a Hoteles Brisamar |

## Datos demo sembrados

- 8 categorías de productos de limpieza profesional
- 5 marcas + 24 productos
- 4 clientes (3 empresas + 1 persona)
- 3 solicitudes con distintos estados
- 3 cotizaciones (aceptada, enviada, borrador)
- 2 pedidos (entregado, preparando)
- 1 factura emitida con SUNAT aceptada + pago parcial

## URLs principales

| URL | Descripción |
|-----|-------------|
| `/` | Home pública |
| `/productos/` | Catálogo |
| `/productos/p/<slug>/` | Detalle de producto (con CTA WhatsApp) |
| `/cotizacion/` | Carrito |
| `/cotizacion/checkout/` | Formulario solicitud |
| `/accounts/login/` | Login |
| `/registro/` | Alta de cliente |
| `/portal/` | Portal cliente |
| `/intranet/` | Backoffice staff |
| `/admin/` | Django admin |

En producción: `https://proclean.pe/` (dominio referencial).

## Commands útiles

```bash
python manage.py seed_demo         # Solo catálogo (categorías + productos)
python manage.py seed_full         # Catálogo + usuarios + clientes + cotizaciones + pedidos + facturas
python manage.py seed_full --reset # Borra datos transaccionales y re-siembra
python manage.py createsuperuser   # Crear superuser manual
```

## Variables de entorno (opcionales)

Copia `.env.example` y ajusta para producción. En dev funciona sin `.env`.

```
SECRET_KEY=...
DEBUG=1
EMISOR_RAZON_SOCIAL=ProClean Servid Innova S.A.C.
EMISOR_RUC=20XXXXXXXXX
EMISOR_DIRECCION=Av. ..., Lima
EMISOR_EMAIL=ventas@proclean.pe
EMISOR_TELEFONO=+51 999 999 999
WHATSAPP_NUMERO=51999999999
```

## Branding

El logo y la paleta están finalizados. Ver [`BRAND.md`](BRAND.md) para la guía de marca completa
(colores hex, archivos disponibles en `static/img/`, tono de comunicación y convenciones de
mensajes de WhatsApp).

## Pendientes para producción

- [ ] Fotos reales de productos (subir vía admin)
- [ ] RUC real de la empresa + datos de emisor (`EMISOR_*`)
- [ ] Número real de WhatsApp Business (`WHATSAPP_NUMERO`)
- [ ] SMTP real (actual: console backend)
- [ ] Integración real Nubefact para SUNAT (actualmente simulado)
- [ ] PostgreSQL en prod + `DATABASE_URL`
- [ ] Sitemap.xml + meta SEO + schema.org Product
- [ ] Deploy en VPS Contabo con Docker Compose
- [ ] Plantilla de notas de crédito
- [ ] Reportes y exportes (Excel)
- [ ] Inscripción ANPDP (si se manejan datos personales sensibles)
