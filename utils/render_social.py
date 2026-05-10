from __future__ import annotations

from io import BytesIO
from pathlib import Path
import random
import re

import requests
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

from config import SOCIAL_ASSETS_DIR

CARD_SIZE = (1080, 1080)

INK = (53, 41, 31, 255)
MUTED = (126, 99, 72, 255)
ACCENT = (171, 123, 72, 255)
PAPER = (252, 247, 238, 238)


def _font(size: int, serif: bool = True, italic: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    if serif:
        candidates = [
            Path("C:/Windows/Fonts/georgiai.ttf") if italic else Path("C:/Windows/Fonts/georgia.ttf"),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf") if italic else Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"),
            Path("/usr/share/fonts/truetype/liberation2/LiberationSerif-Italic.ttf") if italic else Path("/usr/share/fonts/truetype/liberation2/LiberationSerif-Regular.ttf"),
        ]
    else:
        candidates = [
            Path("C:/Windows/Fonts/segoeui.ttf"),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
            Path("/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"),
        ]

    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def _fallback_background(seed: str = "") -> Image.Image:
    width, height = CARD_SIZE
    rnd = random.Random(seed)
    start = (249, 241, 228)
    end = (225, 210, 190)
    image = Image.new("RGB", CARD_SIZE, start)
    draw = ImageDraw.Draw(image)

    for y in range(height):
        ratio = y / (height - 1)
        r = int(start[0] * (1 - ratio) + end[0] * ratio)
        g = int(start[1] * (1 - ratio) + end[1] * ratio)
        b = int(start[2] * (1 - ratio) + end[2] * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    glow = Image.new("RGBA", CARD_SIZE, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    for _ in range(5):
        x = rnd.randint(-180, 900)
        y = rnd.randint(-120, 850)
        radius = rnd.randint(260, 540)
        color = rnd.choice([
            (255, 248, 236, 62),
            (199, 166, 122, 38),
            (155, 124, 91, 30),
        ])
        glow_draw.ellipse([x, y, x + radius, y + radius], fill=color)
    glow = glow.filter(ImageFilter.GaussianBlur(70))
    image = Image.alpha_composite(image.convert("RGBA"), glow).convert("RGB")

    noise = Image.new("L", CARD_SIZE)
    noise_data = [rnd.randint(0, 22) for _ in range(width * height)]
    noise.putdata(noise_data)
    noise_rgba = ImageOps.colorize(noise, black="#000000", white="#ffffff").convert("RGBA")
    noise_rgba.putalpha(18)
    return Image.alpha_composite(image.convert("RGBA"), noise_rgba).convert("RGB")


def _download_background(url: str | None, seed: str) -> Image.Image:
    if not url:
        return _fallback_background(seed)

    try:
        response = requests.get(url, timeout=35)
        response.raise_for_status()
        image = Image.open(BytesIO(response.content)).convert("RGB")
        return ImageOps.fit(image, CARD_SIZE, method=Image.Resampling.LANCZOS)
    except Exception:
        return _fallback_background(seed)


def _make_background(url: str | None, seed: str) -> Image.Image:
    fondo = _download_background(url, seed)
    fondo = ImageEnhance.Color(fondo).enhance(0.58)
    fondo = ImageEnhance.Contrast(fondo).enhance(0.86)
    fondo = ImageEnhance.Brightness(fondo).enhance(1.04)
    fondo = fondo.filter(ImageFilter.GaussianBlur(radius=7))

    wash = Image.new("RGBA", CARD_SIZE, (246, 235, 219, 112))
    vignette = Image.new("L", CARD_SIZE, 0)
    vdraw = ImageDraw.Draw(vignette)
    vdraw.ellipse([-260, -210, 1340, 1320], fill=210)
    vignette = vignette.filter(ImageFilter.GaussianBlur(90))
    dark = Image.new("RGBA", CARD_SIZE, (60, 42, 26, 52))
    dark.putalpha(ImageOps.invert(vignette))

    composed = Image.alpha_composite(fondo.convert("RGBA"), wash)
    composed = Image.alpha_composite(composed, dark)
    return composed


def _wrap_by_pixels(text: str, font: ImageFont.ImageFont, max_width: int, draw: ImageDraw.ImageDraw) -> list[str]:
    lines: list[str] = []
    for paragraph in text.splitlines():
        paragraph = " ".join(paragraph.split())
        if not paragraph:
            continue

        current = ""
        for word in paragraph.split():
            candidate = f"{current} {word}".strip()
            if draw.textlength(candidate, font=font) <= max_width:
                current = candidate
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
    return lines


def _sentence_excerpt(text: str, max_chars: int = 170) -> str:
    clean = " ".join(text.split())
    if len(clean) <= max_chars:
        return clean

    sentences = re.split(r"(?<=[.!?¿])\s+", clean)
    output = ""
    for sentence in sentences:
        candidate = f"{output} {sentence}".strip()
        if len(candidate) <= max_chars:
            output = candidate
        else:
            break

    if len(output) >= 70:
        return output.rstrip()

    return clean[:max_chars].rsplit(" ", 1)[0].rstrip(".,;:") + "…"


def _text_block(draw: ImageDraw.ImageDraw, text: str, max_width: int, max_height: int):
    for size in [50, 47, 44, 41, 38, 35]:
        font = _font(size, serif=True)
        line_height = int(size * 1.42)
        lines = _wrap_by_pixels(text, font, max_width, draw)
        if len(lines) * line_height <= max_height and len(lines) <= 5:
            return font, lines, line_height

    font = _font(35, serif=True)
    line_height = int(35 * 1.42)
    lines = _wrap_by_pixels(text, font, max_width, draw)[:5]
    if len(_wrap_by_pixels(text, font, max_width, draw)) > 5 and lines:
        lines[-1] = lines[-1].rstrip(".,;:…") + "…"
    return font, lines, line_height


def _rounded_shadow(size: tuple[int, int], radius: int, shadow: int = 36) -> Image.Image:
    width, height = size
    canvas = Image.new("RGBA", (width + shadow * 2, height + shadow * 2), (0, 0, 0, 0))
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([0, 0, width, height], radius=radius, fill=255)
    shadow_layer = Image.new("RGBA", canvas.size, (55, 38, 22, 0))
    shadow_mask = Image.new("L", canvas.size, 0)
    shadow_mask.paste(mask, (shadow, shadow))
    shadow_mask = shadow_mask.filter(ImageFilter.GaussianBlur(shadow // 2))
    shadow_layer.putalpha(shadow_mask.point(lambda p: int(p * 0.18)))
    return shadow_layer


def generar_tarjeta_social(
    texto: str,
    tema: str,
    imagen_url: str | None,
    publicacion_id: int,
) -> str:
    """Genera una tarjeta editorial cuadrada y devuelve su ruta para Jekyll."""

    SOCIAL_ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    seed = f"{tema}-{publicacion_id}-{texto[:40]}"
    card = _make_background(imagen_url, seed)

    # Panel principal
    panel_x, panel_y = 132, 132
    panel_w, panel_h = 816, 816
    shadow = _rounded_shadow((panel_w, panel_h), radius=46, shadow=42)
    card.alpha_composite(shadow, (panel_x - 42, panel_y - 32))

    panel = Image.new("RGBA", CARD_SIZE, (0, 0, 0, 0))
    pdraw = ImageDraw.Draw(panel)
    pdraw.rounded_rectangle(
        [panel_x, panel_y, panel_x + panel_w, panel_y + panel_h],
        radius=46,
        fill=PAPER,
        outline=(255, 255, 255, 92),
        width=2,
    )
    card = Image.alpha_composite(card, panel)

    draw = ImageDraw.Draw(card)

    label_font = _font(23, serif=False)
    body_text = _sentence_excerpt(texto)
    body_font, lines, line_height = _text_block(draw, body_text, max_width=620, max_height=285)
    brand_font = _font(36, serif=True)
    author_font = _font(20, serif=False)

    content_x = panel_x + 88
    top_y = panel_y + 82

    label = tema.upper()
    draw.text((content_x, top_y), label, fill=ACCENT, font=label_font)
    draw.line((content_x, top_y + 42, content_x + 96, top_y + 42), fill=(171, 123, 72, 150), width=2)

    text_height = len(lines) * line_height
    text_y = panel_y + 335 + max(0, (285 - text_height) // 2)
    for line in lines:
        draw.text((content_x, text_y), line, fill=INK, font=body_font)
        text_y += line_height

    brand = "Ecos del Alma"
    brand_w = draw.textlength(brand, font=brand_font)
    draw.text(((CARD_SIZE[0] - brand_w) / 2, panel_y + panel_h - 132), brand, fill=(93, 68, 45, 255), font=brand_font)

    signature = "Farid Prado"
    sig_w = draw.textlength(signature, font=author_font)
    draw.text(((CARD_SIZE[0] - sig_w) / 2, panel_y + panel_h - 86), signature, fill=(128, 104, 82, 215), font=author_font)

    filename = f"escrito-{publicacion_id:04d}.png"
    output = SOCIAL_ASSETS_DIR / filename
    card.convert("RGB").save(output, format="PNG", optimize=True)

    return f"/assets/social/{filename}"
