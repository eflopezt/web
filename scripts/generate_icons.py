"""Genera iconos PNG/ICO del logo ProClean usando solo Pillow (sin cairosvg)."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE = Path(__file__).resolve().parent.parent
IMG = BASE / "static" / "img"
IMG.mkdir(parents=True, exist_ok=True)


# ============== PALETA ==============
GREEN_DARK = (46, 139, 31)
GREEN = (63, 174, 42)
GREEN_LIGHT = (107, 203, 58)
BLUE_DARK = (26, 79, 139)
BLUE = (27, 117, 188)
BLUE_LIGHT = (43, 160, 224)
WHITE = (255, 255, 255)


def linear_gradient(size, top, bottom, vertical=True):
    """Crear gradiente lineal."""
    w, h = size
    base = Image.new("RGBA", size, top + (255,))
    top_color = top
    bottom_color = bottom
    for y in range(h) if vertical else range(w):
        t = y / max(1, (h if vertical else w) - 1)
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * t)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * t)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * t)
        if vertical:
            for x in range(w):
                base.putpixel((x, y), (r, g, b, 255))
        else:
            for x in range(h):
                base.putpixel((y, x), (r, g, b, 255))
    return base


def rounded_mask(size, radius):
    mask = Image.new("L", size, 0)
    d = ImageDraw.Draw(mask)
    d.rounded_rectangle((0, 0, size[0], size[1]), radius=radius, fill=255)
    return mask


def draw_mark(canvas_size: int, transparent_bg=False, white_only=False) -> Image.Image:
    """Dibuja el imagotipo (cÃ­rculo + edificios + destellos + hoja) en NxN.

    white_only=True â†’ todo en blanco (para usar sobre fondos oscuros).
    """
    s = canvas_size
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0) if transparent_bg else (255, 255, 255, 255))
    d = ImageDraw.Draw(img)

    # Si no es transparente, fondo blanco con esquinas redondeadas
    if not transparent_bg:
        bg = Image.new("RGBA", (s, s), (255, 255, 255, 255))
        mask = rounded_mask((s, s), int(s * 0.18))
        img.paste(bg, (0, 0), mask)
        d = ImageDraw.Draw(img)

    # Anillo: cÃ­rculo dividido en dos colores (verde arriba, azul abajo)
    pad = int(s * 0.10)
    ring_w = max(3, int(s * 0.07))
    ring_bbox = (pad, pad, s - pad, s - pad)

    if white_only:
        d.arc(ring_bbox, start=180, end=360, fill=WHITE, width=ring_w)  # top â†’ green slot
        d.arc(ring_bbox, start=0, end=180, fill=WHITE, width=ring_w)
    else:
        # Verde (parte superior, 180Â°-360Â°)
        d.arc(ring_bbox, start=180, end=360, fill=GREEN, width=ring_w)
        # Azul (parte inferior, 0Â°-180Â°)
        d.arc(ring_bbox, start=0, end=180, fill=BLUE, width=ring_w)

    # Skyline edificios â€” centrado en el cuadrante superior
    cx = s // 2
    cy = int(s * 0.42)
    bw_unit = int(s * 0.032)   # ancho base
    bh_unit = int(s * 0.04)    # alto base

    buildings = [
        # (offset_x_factor, width_factor, height_factor, color_kind)
        (-3.5, 1.0, 2.6, "green"),
        (-2.3, 1.2, 3.8, "green"),
        (-0.9, 1.4, 5.4, "green"),
        (0.6, 1.4, 4.6, "blue"),
        (2.1, 1.2, 5.2, "blue"),
        (3.4, 1.1, 3.6, "blue"),
    ]
    for off, wf, hf, kind in buildings:
        x0 = cx + int(off * bw_unit)
        bw = int(wf * bw_unit)
        bh = int(hf * bh_unit)
        x1 = x0 + bw
        y1 = cy + int(s * 0.08)
        y0 = y1 - bh
        color = GREEN_DARK if (kind == "green" and not white_only) else (BLUE_DARK if not white_only else WHITE)
        d.rectangle((x0, y0, x1, y1), fill=color)

    # Hoja verde abajo
    leaf_color = GREEN if not white_only else WHITE
    leaf_w = int(s * 0.50)
    leaf_h = int(s * 0.14)
    leaf_x = cx - leaf_w // 2
    leaf_y = int(s * 0.62)
    # Hoja con dos curvas (elipses)
    d.ellipse((leaf_x, leaf_y, leaf_x + leaf_w, leaf_y + leaf_h), fill=leaf_color)
    # Vena central blanca
    d.line(
        (leaf_x + int(leaf_w * 0.05), leaf_y + leaf_h // 2,
         leaf_x + int(leaf_w * 0.95), leaf_y + leaf_h // 2),
        fill=WHITE if not white_only else (0, 0, 0, 0),
        width=max(1, int(s * 0.008)),
    )

    # Destello pequeÃ±o a la izquierda del skyline
    spark_x = cx - int(s * 0.20)
    spark_y = cy - int(s * 0.05)
    spark_r = int(s * 0.025)
    points = []
    import math
    for i in range(8):
        ang = math.pi * 2 * i / 8 - math.pi / 2
        r = spark_r if i % 2 == 0 else spark_r * 0.4
        points.append((spark_x + r * math.cos(ang), spark_y + r * math.sin(ang)))
    d.polygon(points, fill=WHITE if not white_only else WHITE)

    # Destello mediano
    spark_x2 = cx - int(s * 0.13)
    spark_y2 = cy + int(s * 0.02)
    spark_r2 = int(s * 0.018)
    points2 = []
    for i in range(8):
        ang = math.pi * 2 * i / 8 - math.pi / 2
        r = spark_r2 if i % 2 == 0 else spark_r2 * 0.4
        points2.append((spark_x2 + r * math.cos(ang), spark_y2 + r * math.sin(ang)))
    d.polygon(points2, fill=WHITE if not white_only else WHITE)

    return img


def draw_full_logo(w: int, h: int, bg=None) -> Image.Image:
    """Logo horizontal con texto ProClean + SERVID INNOVA."""
    img = Image.new("RGBA", (w, h), bg if bg else (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Imagotipo a la izquierda (sin fondo, transparent_bg=True)
    mark_size = int(h * 0.85)
    mark = draw_mark(mark_size, transparent_bg=True)
    img.paste(mark, (int(h * 0.08), (h - mark_size) // 2), mark)

    # Texto a la derecha
    text_x = int(h * 0.95) + mark_size
    try:
        font_main = ImageFont.truetype("arialbi.ttf", int(h * 0.42))
        font_sub = ImageFont.truetype("arialbd.ttf", int(h * 0.10))
    except OSError:
        try:
            font_main = ImageFont.truetype("DejaVuSans-BoldOblique.ttf", int(h * 0.42))
            font_sub = ImageFont.truetype("DejaVuSans-Bold.ttf", int(h * 0.10))
        except OSError:
            font_main = ImageFont.load_default()
            font_sub = ImageFont.load_default()

    pro_y = int(h * 0.28)
    d.text((text_x, pro_y), "Pro", fill=GREEN, font=font_main)
    pro_bbox = d.textbbox((text_x, pro_y), "Pro", font=font_main)
    clean_x = pro_bbox[2] + int(h * 0.02)
    d.text((clean_x, pro_y), "Clean", fill=BLUE, font=font_main)

    sub_y = pro_bbox[3] + int(h * 0.03)
    d.text((text_x, sub_y), "SERVID INNOVA", fill=BLUE_DARK, font=font_sub)

    return img


def make_favicon_png(size: int, out: Path):
    img = draw_mark(size, transparent_bg=False)
    img.save(out, "PNG")
    print(f"  [ok] {out.relative_to(BASE)} ({size}x{size})")


def make_apple_touch(size: int, out: Path):
    img = draw_mark(size, transparent_bg=False)
    img.save(out, "PNG")
    print(f"  [ok] {out.relative_to(BASE)} ({size}x{size})")


def make_og_image(out: Path):
    """OG image 1200x630 con logo + tagline sobre fondo gradient."""
    w, h = 1200, 630
    # Fondo gradient diagonal azul-verde
    bg = Image.new("RGB", (w, h), BLUE_DARK)
    pixels = bg.load()
    for y in range(h):
        for x in range(w):
            t = (x / w * 0.5) + (y / h * 0.5)
            r = int(BLUE_DARK[0] + (GREEN[0] - BLUE_DARK[0]) * t)
            g = int(BLUE_DARK[1] + (GREEN[1] - BLUE_DARK[1]) * t)
            b = int(BLUE_DARK[2] + (GREEN[2] - BLUE_DARK[2]) * t)
            pixels[x, y] = (r, g, b)
    img = bg.convert("RGBA")

    # Cuadro blanco semi-transparente centrado con logo+texto
    card_w = int(w * 0.78)
    card_h = int(h * 0.72)
    card_x = (w - card_w) // 2
    card_y = (h - card_h) // 2
    card = Image.new("RGBA", (card_w, card_h), (255, 255, 255, 245))
    mask = rounded_mask((card_w, card_h), 32)
    img.paste(card, (card_x, card_y), mask)

    d = ImageDraw.Draw(img)

    # Logo centrado horizontal
    mark_size = int(card_h * 0.55)
    mark = draw_mark(mark_size, transparent_bg=True)
    img.paste(mark, (card_x + int(card_w * 0.08), card_y + int(card_h * 0.18)), mark)

    # Texto a la derecha del logo
    try:
        font_pro = ImageFont.truetype("arialbi.ttf", 120)
        font_sub = ImageFont.truetype("arialbd.ttf", 32)
        font_tag = ImageFont.truetype("arialbd.ttf", 36)
    except OSError:
        try:
            font_pro = ImageFont.truetype("DejaVuSans-BoldOblique.ttf", 120)
            font_sub = ImageFont.truetype("DejaVuSans-Bold.ttf", 32)
            font_tag = ImageFont.truetype("DejaVuSans-Bold.ttf", 36)
        except OSError:
            font_pro = ImageFont.load_default()
            font_sub = ImageFont.load_default()
            font_tag = ImageFont.load_default()

    text_x = card_x + int(card_w * 0.08) + mark_size + 40
    text_y = card_y + int(card_h * 0.22)
    d.text((text_x, text_y), "Pro", fill=GREEN, font=font_pro)
    pbox = d.textbbox((text_x, text_y), "Pro", font=font_pro)
    d.text((pbox[2] + 4, text_y), "Clean", fill=BLUE, font=font_pro)

    sub_y = pbox[3] + 10
    d.text((text_x, sub_y), "SERVID INNOVA", fill=BLUE_DARK, font=font_sub)

    # Tagline abajo del card
    tagline_y = card_y + card_h - 110
    d.text((card_x + 60, tagline_y), "Productos de limpieza profesional", fill=BLUE_DARK, font=font_tag)
    d.text((card_x + 60, tagline_y + 50), "EnvÃ­o gratis Lima y Callao  Â·  WhatsApp +51 918 570 814", fill=GREEN_DARK, font=font_sub)

    img.convert("RGB").save(out, "PNG", optimize=True)
    print(f"  âœ“ {out.relative_to(BASE)} (1200x630)")


def make_logo_png(out: Path):
    """Logo principal PNG con fondo transparente (versiÃ³n web)."""
    img = Image.new("RGBA", (900, 560), (0, 0, 0, 0))
    mark = draw_mark(400, transparent_bg=True)
    img.paste(mark, (40, 80), mark)

    d = ImageDraw.Draw(img)
    try:
        font_pro = ImageFont.truetype("arialbi.ttf", 150)
        font_sub = ImageFont.truetype("arialbd.ttf", 42)
    except OSError:
        try:
            font_pro = ImageFont.truetype("DejaVuSans-BoldOblique.ttf", 150)
            font_sub = ImageFont.truetype("DejaVuSans-Bold.ttf", 42)
        except OSError:
            font_pro = ImageFont.load_default()
            font_sub = ImageFont.load_default()

    text_x = 470
    text_y = 180
    d.text((text_x, text_y), "Pro", fill=GREEN, font=font_pro)
    pbox = d.textbbox((text_x, text_y), "Pro", font=font_pro)
    d.text((pbox[2] + 4, text_y), "Clean", fill=BLUE, font=font_pro)
    d.text((text_x, pbox[3] + 16), "SERVID INNOVA", fill=BLUE_DARK, font=font_sub)

    img.save(out, "PNG", optimize=True)
    print(f"  âœ“ {out.relative_to(BASE)} (900x560 transparent)")


def make_ico(out: Path):
    """ICO multi-size desde el favicon."""
    sizes = [(16, 16), (32, 32), (48, 48)]
    imgs = []
    for size, _ in sizes:
        imgs.append(draw_mark(size, transparent_bg=False))
    # ICO multi-resoluciÃ³n
    imgs[0].save(out, format="ICO", sizes=sizes, append_images=imgs[1:])
    print(f"  âœ“ {out.relative_to(BASE)} (multi-size ICO)")


if __name__ == "__main__":
    print("Generando assets ProClean...")
    make_favicon_png(64, IMG / "favicon-64.png")
    make_favicon_png(192, IMG / "favicon-192.png")
    make_favicon_png(512, IMG / "favicon-512.png")
    make_apple_touch(180, IMG / "apple-touch-icon.png")
    make_ico(IMG / "favicon.ico")
    make_logo_png(IMG / "logo.png")
    make_og_image(IMG / "og-image.png")
    print("Done.")

