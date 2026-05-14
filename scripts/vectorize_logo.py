"""Vectoriza el logo original con vtracer (alta fidelidad).

Lee static/img/logo-original.jpeg y produce:
  - logo.svg            (versión completa)
  - logo-horizontal.svg (versión completa optimizada para navbar)
  - logo-mark.svg       (recorte: solo imagotipo, sin texto)
  - favicon.svg         (imagotipo simplificado para 64x64)
  - logo-white.svg      (versión monocroma blanca para fondos oscuros)

También regenera:
  - logo.png            (PNG transparente del original con fondo blanco quitado)
"""
from __future__ import annotations

import re
from pathlib import Path

import vtracer
from PIL import Image

BASE = Path(__file__).resolve().parent.parent
IMG = BASE / "static" / "img"
ORIGINAL = IMG / "logo-original.jpeg"

# ============== PRE-PROCESAMIENTO ==============
# Cargar original, escalar a mayor resolución, quitar fondo blanco

print("Cargando original...")
orig = Image.open(ORIGINAL).convert("RGBA")
w, h = orig.size
print(f"  Dimensiones originales: {w}x{h}")

# Convertir blanco puro a transparente (umbral)
def remove_white_bg(img, threshold=240):
    """Reemplaza píxeles con R,G,B >= threshold por transparencia."""
    px = img.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = px[x, y]
            if r >= threshold and g >= threshold and b >= threshold:
                px[x, y] = (255, 255, 255, 0)
    return img

# Versión con fondo transparente para PNG y para vtracer (mejor trace)
print("Quitando fondo blanco...")
orig_transparent = orig.copy()
orig_transparent = remove_white_bg(orig_transparent)

# Crop al área no transparente (bounding box)
bbox = orig_transparent.getbbox()
print(f"  Bounding box detectado: {bbox}")
orig_cropped = orig_transparent.crop(bbox)
print(f"  Tamaño cropped: {orig_cropped.size}")

# Guardar versiones temporales para trace
tmp_full = IMG / "_tmp_full.png"
tmp_mark = IMG / "_tmp_mark.png"

# Versión completa con fondo blanco (mejor trace)
full_white = Image.new("RGB", orig_cropped.size, (255, 255, 255))
full_white.paste(orig_cropped, mask=orig_cropped.split()[3] if orig_cropped.mode == "RGBA" else None)
full_white.save(tmp_full, "PNG")

# Versión solo imagotipo (recortar la parte de arriba con el imagotipo y skyline)
# El imagotipo ocupa los 2/3 superiores del logo en horizontal, con el texto en el medio
# Mejor: recortar al área cuadrada centrada en el imagotipo
mw, mh = orig_cropped.size
# El imagotipo (anillo + skyline + hoja) ocupa toda la imagen — recortar solo la parte sin texto
# es difícil sin máscara. Mejor: trazar el logo completo y luego usar transformaciones SVG.
# Para el mark: tomar el imagotipo entero (es un imagotipo + logotipo unificado).

# Generar PNG transparente alta resolución para los placeholders y card
print("Guardando logo.png con fondo transparente...")
orig_cropped.save(IMG / "logo.png", "PNG", optimize=True)

# ============== VECTORIZACIÓN PRINCIPAL ==============
print("\nVectorizando logo completo (puede tardar 30-60s)...")
vtracer.convert_image_to_svg_py(
    str(tmp_full),
    str(IMG / "logo.svg"),
    colormode="color",
    hierarchical="stacked",
    mode="spline",
    filter_speckle=4,
    color_precision=8,
    layer_difference=16,
    corner_threshold=60,
    length_threshold=4.0,
    splice_threshold=45,
    path_precision=8,
)
print("  logo.svg generado")

# ============== POST-PROCESAMIENTO ==============
# El SVG generado por vtracer no tiene viewBox amigable ni acepta CSS scaling fácil.
# Lo arreglamos.

def fix_svg(svg_path: Path, width: int, height: int):
    """Añade viewBox correcto y atributos para que escale bien."""
    content = svg_path.read_text(encoding="utf-8")
    # Reemplazar el <svg ...> inicial
    pattern = re.compile(r'<svg[^>]*>')
    new_svg_tag = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" preserveAspectRatio="xMidYMid meet" role="img" aria-label="ProClean Servid Innova">'
    content = pattern.sub(new_svg_tag, content, count=1)
    svg_path.write_text(content, encoding="utf-8")

print("Ajustando viewBox de logo.svg...")
fix_svg(IMG / "logo.svg", orig_cropped.width, orig_cropped.height)

# ============== VARIANTES ==============
# Para horizontal: mismo contenido, solo ajustamos viewBox
print("Copiando como logo-horizontal.svg (mismo vector, diferente uso)...")
import shutil
shutil.copy(IMG / "logo.svg", IMG / "logo-horizontal.svg")

# Para logo-white: reemplazar TODOS los fills por #ffffff
print("Generando logo-white.svg (todo en blanco)...")
white_content = (IMG / "logo.svg").read_text(encoding="utf-8")
# Reemplazar todos los fill="#..." y stroke="#..." por blanco
white_content = re.sub(r'fill="#[0-9a-fA-F]{3,6}"', 'fill="#ffffff"', white_content)
white_content = re.sub(r'stroke="#[0-9a-fA-F]{3,6}"', 'stroke="#ffffff"', white_content)
# Eliminar el rectángulo de fondo blanco si lo tiene
white_content = re.sub(r'<path[^>]*fill="#ffffff"[^>]*d="M0 0[^"]*"[^/]*/>', '', white_content, count=1)
(IMG / "logo-white.svg").write_text(white_content, encoding="utf-8")

# Para logo-mark: recortar al cuadrante superior izquierdo (imagotipo sin texto)
# Como el texto "ProClean" está en el centro, mejor cropear el JPEG original al área del imagotipo
print("Generando logo-mark.svg (solo imagotipo, cropeado)...")
# Aproximadamente: el imagotipo ocupa el área 0,0 al ancho completo, 0 al 55% del alto
mark_crop = orig_cropped.crop((0, 0, mw, int(mh * 0.55)))
# Hacer cuadrado centrando
mw2, mh2 = mark_crop.size
side = max(mw2, mh2)
square = Image.new("RGB", (side, side), (255, 255, 255))
square.paste(mark_crop, ((side - mw2) // 2, (side - mh2) // 2), mask=mark_crop.split()[3] if mark_crop.mode == "RGBA" else None)
tmp_mark.write_bytes(b"")  # asegurar que existe
square.save(tmp_mark, "PNG")
vtracer.convert_image_to_svg_py(
    str(tmp_mark),
    str(IMG / "logo-mark.svg"),
    colormode="color",
    hierarchical="stacked",
    mode="spline",
    filter_speckle=4,
    color_precision=8,
    layer_difference=16,
    corner_threshold=60,
    length_threshold=4.0,
    splice_threshold=45,
    path_precision=8,
)
fix_svg(IMG / "logo-mark.svg", side, side)
print("  logo-mark.svg generado")

# Para favicon: usar el mark a 64x64
print("Copiando como favicon.svg (versión compacta del mark)...")
shutil.copy(IMG / "logo-mark.svg", IMG / "favicon.svg")
# Ajustar viewBox del favicon para que sea 0 0 64 64 manteniendo proporción
fav_content = (IMG / "favicon.svg").read_text(encoding="utf-8")
# Reemplazar viewBox actual por 0 0 64 64 (proporcional al original)
fav_content = re.sub(r'viewBox="[^"]+"', f'viewBox="0 0 {side} {side}"', fav_content)
(IMG / "favicon.svg").write_text(fav_content, encoding="utf-8")

# ============== LIMPIEZA ==============
print("\nLimpiando temporales...")
for tmp in [tmp_full, tmp_mark]:
    if tmp.exists():
        tmp.unlink()

print("\n[DONE] SVGs generados con vtracer:")
for f in ["logo.svg", "logo-horizontal.svg", "logo-mark.svg", "logo-white.svg", "favicon.svg"]:
    path = IMG / f
    if path.exists():
        size_kb = path.stat().st_size / 1024
        print(f"  {f}: {size_kb:.1f} KB")
