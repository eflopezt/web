# Estado de la demo · LimpiaPro

> Snapshot del 13/05/2026 — demo completa lista para mostrar.

## Cómo arrancarla en 4 comandos

```powershell
cd C:\Users\edwii\iCloudDrive\CSRT\D\Web
.\venv\Scripts\python.exe manage.py migrate
.\venv\Scripts\python.exe manage.py seed_full
.\venv\Scripts\python.exe manage.py runserver
```

Abrir http://localhost:8000

## Usuarios para probar

| Usuario | Contraseña | Para qué |
|---------|------------|----------|
| `admin` / `admin` | superuser (Django admin completo) |
| `staff` / `staff` | **Intranet** `/intranet/` — vendedor que gestiona cotizaciones, pedidos, facturas |
| `cliente` / `cliente` | **Portal** `/portal/` — cliente que ve sus cotizaciones, acepta/rechaza, ve facturas |

## Recorrido sugerido (15 min)

### 1️⃣ Sitio público (modo cliente potencial)
1. Abrir http://localhost:8000 → home con hero + categorías + destacados
2. Click "Ver catálogo" → buscar "detergente", filtrar por categoría
3. Abrir un producto → "Agregar a cotización"
4. Click en el ícono carrito del navbar → drawer → "Solicitar cotización"
5. Completar el formulario → ver pantalla de éxito con código `SOL-XXXXXX`

### 2️⃣ Intranet (modo staff / vendedor)
1. Logout → login con `staff` / `staff` → redirige a `/intranet/`
2. **Dashboard**: ver KPIs (solicitudes nuevas, cotizaciones enviadas, ventas del mes)
3. **Solicitudes** → abrir la del paso 5 anterior → click "📄 Crear cotización"
4. La cotización aparece en borrador → agregar líneas con precio, descuento → "Marcar como enviada"
5. Descargar PDF de la cotización (botón ⬇ PDF)
6. **Pedidos** → abrir uno → cambiar estado a "Enviado" → "Emitir factura"
7. **Facturas** → abrir la nueva → "Enviar a SUNAT (simul.)" → registrar un pago parcial
8. **Reportes** → ver gráfico de ventas, top productos, top clientes

### 3️⃣ Portal cliente
1. Logout → login con `cliente` / `cliente` → redirige a `/portal/`
2. **Dashboard**: saldo pendiente, últimas cotizaciones, pedidos, facturas
3. **Mis cotizaciones** → abrir una con estado "Enviada" → **Aceptar** → se genera pedido automático
4. **Mis facturas** → abrir una → ver historial de pagos → descargar PDF

## Lo que está terminado

### Sitio público ✓
- Home + nosotros + contacto + términos + privacidad
- Catálogo con búsqueda, filtros por categoría/marca/disponibilidad, paginación HTMX
- Detalle de producto con galería, productos relacionados, WhatsApp prellenado
- Carrito en sesión con drawer modal
- Checkout que crea solicitud + cliente automáticamente

### Portal cliente (`/portal/`) ✓
- Login + registro + cambio de contraseña
- Dashboard con KPIs personales
- Listado y detalle de solicitudes, cotizaciones, pedidos, facturas
- Aceptar cotización → genera pedido automático
- Rechazar cotización con motivo
- PDF de cotización y factura descargables
- Perfil editable

### Intranet (`/intranet/`) ✓
- Dashboard con KPIs operativos + ventas + cobranza del mes
- Solicitudes (CRUD + cambio de estado + crear cotización)
- Cotizaciones (CRUD + líneas + recálculo IGV + duplicar + enviar + marcar estado + generar pedido + PDF)
- Pedidos (gestión de estado + facturar como factura o boleta)
- Facturas (emisión + simulación SUNAT + anulación + pagos parciales/totales + PDF)
- Clientes (CRM con contadores y ficha histórica)
- Productos (listado + link a admin)
- Reportes (top productos, top clientes, gráfico de ventas 6 meses)

### Infraestructura ✓
- 13 tests pasando (cálculo IGV, descuentos, correlativos, accesos)
- Dockerfile + docker-compose.yml para deploy
- Página 404 custom + 500
- Settings preparados para PostgreSQL (env DATABASE_URL)
- Whitenoise para estáticos
- Seed idempotente que recrea toda la demo en 1 comando

## Datos demo cargados

- 8 categorías de productos
- 5 marcas + 24 productos
- 4 clientes (3 empresas + 1 persona natural)
- 3 solicitudes (con distintos estados)
- 3 cotizaciones (aceptada, enviada, borrador)
- 2 pedidos (entregado, preparando)
- 1 factura emitida + SUNAT aceptada + pago parcial registrado

## Para pasar a producción (pendiente)

- [ ] Subir fotos reales de productos vía admin
- [ ] Reemplazar nombre `LimpiaPro` por el nombre comercial definitivo
- [ ] Reemplazar logo SVG en `templates/components/_logo.html` y `static/img/favicon.svg`
- [ ] Configurar SMTP real (env EMAIL_*)
- [ ] Integrar pasarela de pago (Culqi/Izipay/Mercado Pago) si quieres pago online
- [ ] Integrar Nubefact real para emitir facturas electrónicas SUNAT (hoy es simulado)
- [ ] Migrar a PostgreSQL (env DATABASE_URL)
- [ ] Deploy en VPS Contabo con `docker compose up -d`
- [ ] Configurar dominio + Let's Encrypt
- [ ] SEO: sitemap.xml + meta tags + schema.org Product
- [ ] Anti-spam en formulario público de cotización (honeypot o reCAPTCHA)

## Tecnologías

- Django 5.2 · Python 3.12+
- Tailwind CSS + DaisyUI v4 (CDN)
- HTMX 2 + Alpine.js 3
- SQLite (dev) / PostgreSQL-ready (prod)
- reportlab 4.5 (PDFs)
- WhiteNoise (estáticos)
- gunicorn + Docker compose (deploy)

## Repo y commits

- **GitHub**: https://github.com/eflopezt/web
- 3 commits en `main`:
  1. `10c3f21` — scaffold inicial (catálogo + cotizaciones B2B)
  2. `fc4406c` — intranet + portal cliente + cotizaciones formales + facturación
  3. `0bb6485` — polish: reportes, páginas legales, 404/500, tests, Docker

## Comando útil: regenerar la demo desde cero

```powershell
.\venv\Scripts\python.exe manage.py flush --noinput
.\venv\Scripts\python.exe manage.py seed_full
```
