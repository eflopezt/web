# LimpiaPro

Web de catálogo + sistema de cotizaciones para una empresa peruana de productos de limpieza profesional B2B.

**Stack**: Django 5.2 · Python 3.12+ · Tailwind CSS + DaisyUI · HTMX · Alpine.js · SQLite (dev) / PostgreSQL (prod).

**Nombre y branding**: temporal. Logo SVG inline en `templates/components/_logo.html` y favicon en `static/img/favicon.svg`. Reemplazables.

---

## Características

- Catálogo público con búsqueda, filtros por categoría/marca/disponibilidad, paginación HTMX.
- Productos **sin precio visible** — todo se gestiona vía solicitud de cotización.
- Carrito de cotización en sesión (drawer modal con HTMX, badge en navbar).
- Checkout con datos del cliente (persona natural o empresa con RUC).
- Email automático al cliente + email a ventas (HTML).
- Admin Django para gestionar categorías, marcas, productos, imágenes y solicitudes.
- Botones de contacto directo por WhatsApp en todo el sitio.
- Responsive (mobile-first) con DaisyUI.

## Arrancar en local

```bash
# 1. Crear y activar venv
python -m venv venv
.\venv\Scripts\activate           # PowerShell
# source venv/bin/activate         # bash

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Migrar y crear superusuario
python manage.py migrate
python manage.py createsuperuser

# 4. Sembrar datos demo (8 categorías, 5 marcas, 24 productos)
python manage.py seed_demo

# 5. Levantar dev server
python manage.py runserver
```

Abrir: http://localhost:8000

Admin: http://localhost:8000/admin

## Estructura

```
apps/
├── core/           — Home, nosotros, contacto, context processor
├── catalogo/       — Categorías, marcas, productos, imágenes, admin, seed_demo
└── cotizaciones/   — Carrito en sesión, checkout, solicitud, items, emails
config/             — settings, urls, wsgi, asgi
templates/          — base, components (navbar/footer/logo), core, catalogo, cotizaciones
static/img/         — favicon.svg
```

## Variables de entorno

Copia `.env.example` a `.env` y ajusta para producción. En dev funciona sin `.env`.

## Roadmap próximo

- [ ] Imágenes reales por producto (fotos profesionales)
- [ ] Página de cada categoría con landing dedicada
- [ ] Pasarela de pago (Culqi / Izipay / Mercado Pago) para productos con precio fijo
- [ ] Integración Nubefact para factura electrónica SUNAT
- [ ] Auth de clientes recurrentes con historial de cotizaciones
- [ ] Sitemap, schema.org Product/Offer, robots.txt
- [ ] Deploy en VPS Contabo + Docker Compose
