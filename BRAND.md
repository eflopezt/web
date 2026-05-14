# BRAND · ProClean Servid Innova

Guía rápida de marca para mantener consistencia en sitio, intranet, portal, PDFs y mensajes de WhatsApp.

---

## 1. Nombre comercial

- **Nombre comercial**: **ProClean**
- **Razón social / suffix**: *Servid Innova* (acompaña al imagotipo)
- **Forma completa**: **ProClean Servid Innova**
- **No usar**: *ProClean SI*, *PCSI*, *Pro Clean*, *PROCLEAN* en mayúsculas pegadas (excepto en tagline `SERVID INNOVA`).

En texto siempre escribir **ProClean** con la P y la C en mayúscula y sin espacio. La italica del logo
es decorativa — en cuerpo de texto se escribe en redonda.

---

## 2. Tagline y propuesta

> **Catálogo de productos de limpieza profesional. Cotiza por WhatsApp.**

Variantes admitidas según contexto:

- Hero corto: *"Productos de limpieza profesional para tu negocio."*
- Subhead: *"Cotiza por WhatsApp. Atendemos Lima y Callao."*
- Footer: *"ProClean Servid Innova — Lima y Callao."*

---

## 3. Paleta de color

### Primarios

| Token | Hex | Uso |
|-------|-----|-----|
| `green-600` (primario) | **`#3FAE2A`** | Texto "Pro", botones CTA primarios, badges éxito |
| `green-700` (oscuro) | `#2E8B1F` | Hover de botón verde, gradientes |
| `green-500` (claro) | `#6BCB3A` | Highlights, gradientes, hojas |
| `blue-600` (primario) | **`#1B75BC`** | Texto "Clean", botones secundarios, enlaces |
| `blue-800` (oscuro) | `#1A4F8B` | Texto "SERVID INNOVA", footer, fondos oscuros |
| `blue-400` (claro) | `#2BA0E0` | Acentos, gradientes |

### Neutros

| Token | Hex | Uso |
|-------|-----|-----|
| `white` | `#FFFFFF` | Fondo principal del sitio |
| `gray-50` | `#F8FAFC` | Fondo de secciones alternas |
| `gray-100` | `#F1F5F9` | Cards, separadores |
| `gray-600` | `#475569` | Texto secundario |
| `gray-900` | `#0F172A` | Texto principal |

### Gradientes oficiales

- **Verde (hoja, edificios izq.)**: `linear-gradient(180deg, #6BCB3A 0%, #2E8B1F 100%)`
- **Azul (edificios der.)**: `linear-gradient(180deg, #2BA0E0 0%, #1A4F8B 100%)`
- **Cinta verde (logo)**: `linear-gradient(225deg, #6BCB3A 0%, #3FAE2A 55%, #2E8B1F 100%)`
- **Cinta azul (logo)**: `linear-gradient(45deg, #1A4F8B 0%, #1B75BC 55%, #2BA0E0 100%)`

---

## 4. Tipografía

- **Sistema**: `'Inter', 'Helvetica Neue', Arial, sans-serif`
- **Logo**: Inter italic 800 (extra-bold italic)
- **Headings**: Inter 700 (bold), tracking ligero
- **Body**: Inter 400/500
- **Tagline en SERVID INNOVA**: Inter 700 con `letter-spacing: 6` y mayúsculas

Si Inter no está disponible, fallback automático a Helvetica Neue / Arial.

---

## 5. Uso del logo

### Archivos disponibles (`static/img/`)

| Archivo | viewBox | Uso recomendado |
|---------|---------|-----------------|
| `logo.svg` | 900×560 | Logo completo a color — homepage, splash, presentaciones |
| `logo-mark.svg` | 200×200 | Imagotipo circular sin texto — favicon grande, avatar, social |
| `logo-horizontal.svg` | 520×120 | Compacto: imagotipo + texto en línea — navbar (h-10 a h-12) |
| `logo-white.svg` | 900×560 | Todo blanco para fondos oscuros (sobre `#1A4F8B`) |
| `logo-original.jpeg` | — | **Referencia visual del cliente, NO usar en web** |
| `logo.png` | 1024×640 | Versión raster del logo principal |
| `favicon.svg`, `favicon.ico` | 64×64 | Tabs del browser |
| `favicon-192.png`, `favicon-512.png` | — | PWA / manifest |
| `apple-touch-icon.png` | 180×180 | iOS home screen |
| `og-image.png` | 1200×630 | OpenGraph / Twitter Cards |

### Clear space

Dejar al menos el ancho de la letra "P" del logotipo como espacio en blanco alrededor del logo en
todas direcciones. No incrustar el logo dentro de cajas con color saturado distinto a los oficiales.

### Fondos válidos

- Blanco `#FFFFFF` (preferido)
- Gris muy claro `#F8FAFC` o `#F1F5F9`
- Azul oscuro `#1A4F8B` (usar `logo-white.svg`)
- Negro `#0F172A` (usar `logo-white.svg`)

**Evitar**: fondos verdes saturados, fondos azules saturados (compiten con la paleta del logo),
fondos con patrones, fotos sin overlay oscuro.

### Tamaños mínimos legibles

- Logo completo: 180px de ancho
- Logo horizontal: 200px de ancho
- Logo mark: 32px (favicon: hasta 16px)

---

## 6. CTAs estándar

Texto y comportamiento de los CTAs principales:

| Contexto | Texto del botón | Color de fondo | Acción |
|----------|-----------------|----------------|--------|
| Producto / categoría / home | **Cotizar por WhatsApp** | Verde `#3FAE2A` | Abrir `wa.me` con mensaje prellenado |
| Catálogo (secundario) | Ver catálogo | Azul `#1B75BC` | Lleva a `/productos/` |
| Carrito | Solicitar cotización | Verde `#3FAE2A` | Lleva a checkout |
| Portal cliente | Aceptar cotización | Verde `#3FAE2A` | Genera pedido automático |
| Portal cliente | Rechazar | Outline rojo | Modal con motivo |
| Intranet | Crear cotización | Verde `#3FAE2A` | Acción primaria |
| Footer / contacto | Contáctanos | Azul `#1B75BC` | Lleva a `/contacto/` |

---

## 7. Convención de mensajes de WhatsApp

El número oficial se guarda en `WHATSAPP_NUMERO` (formato E.164 sin `+`, ej. `51999999999`).

Formato base del link:
```
https://wa.me/{WHATSAPP_NUMERO}?text={mensaje url-encoded}
```

### Mensaje genérico (home / footer)

> Hola ProClean, quisiera consultar sobre sus productos de limpieza. ¿Me pueden orientar?

### Mensaje por categoría

> Hola ProClean, me interesa cotizar productos de la categoría **{nombre_categoria}**. ¿Me pueden enviar más información?

### Mensaje por producto (con código)

> Hola ProClean, quisiera cotizar el producto **{nombre_producto}** (cód. {sku}). ¿Tienen stock y cuál es el precio por mayor?

### Mensaje por carrito / múltiples productos

> Hola ProClean, quisiera cotizar los siguientes productos:
>
> - {producto_1} x {cantidad}
> - {producto_2} x {cantidad}
>
> ¿Me confirman disponibilidad y precio?

### Reglas
- Siempre saludar con **"Hola ProClean"** (humaniza, identifica la fuente).
- Mencionar el contexto (producto / categoría / genérico) en la primera línea.
- Cerrar con una pregunta abierta ("¿Tienen stock?", "¿Cuál es el precio?", "¿Me orientan?").
- Codificar bien con `urlencode` o `urllib.parse.quote_plus`.
- En las plantillas Django se preferirá un filtro `whatsapp_url` ya existente.

---

## 8. Tono de comunicación

Estilo de redacción en español peruano. Características:

- **Directo**: ir al grano, frases cortas, sin rodeos.
- **Profesional**: lenguaje correcto, sin coloquialismos excesivos.
- **Cercano**: tutear al cliente en formularios cortos; "usted" en facturación formal.
- **Útil**: enfatizar beneficios y soluciones, no jerga técnica gratuita.

### Vocabulario preferido

- "Cotizar" (no "obtener un presupuesto" ni "request a quote")
- "Productos de limpieza profesional" (no "soluciones de aseo")
- "Para tu negocio / para tu hogar" (no "para sus instalaciones")
- "Pedido" (no "orden de compra" en sitio público)
- "Stock" o "disponibilidad" (no "inventario")
- "Lima y Callao" (cuando se hable de cobertura geográfica)

### Evitar
- Exclamaciones múltiples (`¡!!`) y emojis decorativos abundantes.
- Anglicismos innecesarios (`shipping`, `delivery` → "envío"; `checkout` → "finalizar pedido").
- Promesas vagas tipo "el mejor precio del mercado" — preferir "precio por mayor" o "descuentos por volumen".
- Mayúsculas para énfasis (`COMPRA AHORA`) — usar bold o color.

### Ejemplos

- ✅ "Detergente concentrado para uso industrial. Cotiza por WhatsApp."
- ❌ "¡¡¡EL MEJOR DETERGENTE!!! Compra YA"

- ✅ "Hola, soy del área de compras de un hotel y quisiera cotizar limpiadores multiuso."
- ❌ "Hi, I'm looking for cleaning supplies, please send pricing."

---

## 9. Iconografía y estilos secundarios

- Border radius: `8px` en cards/botones, `12px` en modales, `9999px` (full) en badges/pills.
- Sombras: ligeras y verticales (`shadow-sm`, `shadow-md` de Tailwind), no efectos neumórficos.
- Iconos: Heroicons outline 24px o solid 20px. Evitar mezclar estilos en una misma vista.
- Imágenes de producto: fondo blanco, encuadre cuadrado, padding interno consistente.

---

## 10. Checklist rápido antes de publicar contenido

- [ ] El nombre se escribió como **ProClean** (no LimpiaPro, no Pro Clean)
- [ ] Si hay logo, está sobre fondo válido
- [ ] CTAs principales en verde `#3FAE2A`, secundarios en azul `#1B75BC`
- [ ] Texto en español peruano, directo y profesional
- [ ] Si hay link a WhatsApp, usa el número oficial y un mensaje contextual
- [ ] No hay menciones residuales a "LimpiaPro" en copias antiguas
