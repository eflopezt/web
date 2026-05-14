# LimpiaPro — Plataforma B2B de productos de limpieza profesional

Demo completa de e-commerce + cotizaciones + intranet + portal cliente para una empresa peruana de productos de limpieza profesional.

**Stack**: Django 5.2 · Python 3.12+ · Tailwind CSS + DaisyUI · HTMX · Alpine.js · reportlab · SQLite (dev) / PostgreSQL-ready (prod).

---

## ¿Qué incluye la demo?

### 🌐 Sitio público (`/`)
- Home con hero, categorías destacadas y productos
- Catálogo con búsqueda, filtros por categoría/marca/disponibilidad y paginación
- Detalle de producto con galería y CTA WhatsApp
- **Sin precios visibles** — todo se gestiona por solicitud de cotización
- Carrito en sesión + checkout que genera una solicitud y crea cliente automáticamente

### 🧑‍💼 Portal cliente (`/portal/`)
- Login + registro propio (auto-vincula `User` ↔ `Cliente` por email)
- Dashboard con KPIs personales (solicitudes, cotizaciones, pedidos, saldo pendiente)
- Mis solicitudes (con seguimiento de estado)
- **Mis cotizaciones**: ver detalle, descargar PDF, **aceptar** (genera pedido automático) o **rechazar** con motivo
- Mis pedidos con estado de envío
- Mis facturas con saldo pendiente, descarga PDF e historial de pagos
- Mi perfil editable + cambio de contraseña

### 🏢 Intranet (`/intranet/`)
- Dashboard con KPIs operativos (solicitudes nuevas, cotizaciones pendientes, pedidos activos, facturas por cobrar, ventas y cobranza del mes)
- **Solicitudes**: lista + detalle + cambio de estado + crear cotización en 1 clic (copia items)
- **Cotizaciones**: CRUD completo, agregar/quitar líneas, recalcular IGV automático, marcar enviada/aceptada/rechazada, duplicar, generar pedido, PDF descargable
- **Pedidos**: cambio de estado (confirmado → preparando → enviado → entregado), facturar (genera factura o boleta automáticamente)
- **Facturas**: emisión, simulación SUNAT (hash + estado_sunat), anulación, registro de pagos parciales/totales, actualización automática de estado, PDF descargable
- **Clientes**: CRM básico — listado con contador de cotizaciones/pedidos/facturas, ficha con histórico completo, edición
- **Productos**: listado con búsqueda, link al admin Django para edición

### 📄 PDFs profesionales (reportlab)
- Cotización y factura/boleta con header de emisor, datos del cliente, líneas con totales IGV y condiciones

### 🇵🇪 Normativa peruana implementada
- IGV 18% calculado automáticamente
- RUC (11 dígitos) o DNI (8 dígitos) validados
- Factura (F001) para empresas / Boleta (B001) para personas naturales
- Series y correlativos por tipo de documento
- Simulación de envío a SUNAT con CDR aceptado/rechazado

### 🗄️ Apps del proyecto
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
| `/productos/p/<slug>/` | Detalle de producto |
| `/cotizacion/` | Carrito |
| `/cotizacion/checkout/` | Formulario solicitud |
| `/accounts/login/` | Login |
| `/registro/` | Alta de cliente |
| `/portal/` | Portal cliente |
| `/intranet/` | Backoffice staff |
| `/admin/` | Django admin |

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
EMISOR_RAZON_SOCIAL=LimpiaPro S.A.C.
EMISOR_RUC=20612345678
EMISOR_DIRECCION=Av. Industrial 123, Ate, Lima
EMISOR_EMAIL=ventas@limpiapro.pe
EMISOR_TELEFONO=+51 999 999 999
```

## Pendientes para producción

- [ ] Fotos reales de productos (subir vía admin)
- [ ] Logo y branding definitivo (reemplazar SVG en `templates/components/_logo.html` y `static/img/favicon.svg`)
- [ ] SMTP real (actual: console backend)
- [ ] Pasarela de pago (Culqi / Izipay / Mercado Pago) para productos con precio fijo
- [ ] Integración real Nubefact para SUNAT (actualmente simulado)
- [ ] PostgreSQL en prod + DATABASE_URL
- [ ] Sitemap.xml + meta SEO + schema.org Product
- [ ] Deploy en VPS Contabo con Docker Compose
- [ ] Plantilla de notas de crédito
- [ ] Reportes y exportes (Excel)
