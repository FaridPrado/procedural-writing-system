from __future__ import annotations

from io import BytesIO
from pathlib import Path
import textwrap

import requests
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

from config import SOCIAL_ASSETS_DIR

CARD_SIZE = (1080, 1080)


def _font(size: int, serif: bool = True) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        Path("C:/Windows/Fonts/georgia.ttf") if serif else Path("C:/Windows/Fonts/segoeui.ttf"),
        Path("C:/Windows/Fonts/georgiai.ttf") if serif else Path("C:/Windows/Fonts/seguisb.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf") if serif else Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("/usr/share/fonts/truetype/liberation2/LiberationSerif-Regular.ttf") if serif else Path("/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"),
    ]
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def _download_background(url: str | None) -> Image.Image:
    if not url:
        return _fallback_background()

    try:
        response = requests.get(url, timeout=45)
        response.raise_for_status()
        image = Image.open(BytesIO(response.content)).convert("RGB")
        return ImageOps.fit(image, CARD_SIZE, method=Image.Resampling.LANCZOS)
    except Exception:
        return _fallback_background()


def _fallback_background() -> Image.Image:
    width, height = CARD_SIZE
    image = Image.new("RGB", CARD_SIZE, "#efe7da")
    draw = ImageDraw.Draw(image)
    for y in range(height):
        ratio = y / height
        r = int(245 - ratio * 22)
        g = int(237 - ratio * 26)
        b = int(225 - ratio * 32)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    return image


def _wrap_by_pixels(text: str, font: ImageFont.ImageFont, max_width: int, draw: ImageDraw.ImageDraw) -> list[str]:
    lines: list[str] = []
    for paragraph in text.splitlines():
        paragraph = paragraph.strip()
        if not paragraph:
            lines.append("")
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


def _limit_lines(lines: list[str], max_lines: int = 11) -> list[str]:
    visible = lines[:max_lines]
    if len(lines) > max_lines and visible:
        visible[-1] = visible[-1].rstrip(".,;:…") + "…"
    return visible


def _shorten_text(text: str, max_chars: int = 410) -> str:
    clean = " ".join(text.split())
    if len(clean) <= max_chars:
        return clean
    cut = clean[:max_chars].rsplit(" ", 1)[0].rstrip(".,;:")
    return cut + "…"


def generar_tarjeta_social(
    texto: str,
    tema: str,
    imagen_url: str | None,
    publicacion_id: int,
) -> str:
    """Genera una pieza cuadrada 1080x1080 lista para web/redes.

    Devuelve la ruta relativa que debe guardarse en el front matter de Jekyll.
    """

    SOCIAL_ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    fondo = _download_background(imagen_url)
    fondo = ImageEnhance.Color(fondo).enhance(0.65)
    fondo = ImageEnhance.Contrast(fondo).enhance(0.88)
    fondo = fondo.filter(ImageFilter.GaussianBlur(radius=2.2))

    overlay = Image.new("RGBA", CARD_SIZE, (40, 32, 25, 95))
    card = Image.alpha_composite(fondo.convert("RGBA"), overlay)

    panel = Image.new("RGBA", CARD_SIZE, (0, 0, 0, 0))
    panel_draw = ImageDraw.Draw(panel)
    panel_draw.rounded_rectangle(
        [92, 112, 988, 968],
        radius=34,
        fill=(253, 248, 240, 226),
        outline=(255, 255, 255, 75),
        width=2,
    )
    card = Image.alpha_composite(card, panel)

    draw = ImageDraw.Draw(card)
    title_font = _font(42, serif=False)
    small_font = _font(28, serif=False)

    draw.text((140, 160), tema.upper(), fill=(128, 93, 58, 255), font=small_font)
    draw.line((140, 210, 260, 210), fill=(178, 145, 100, 180), width=3)

    texto_card = _shorten_text(texto)
    max_width = 800
    body_font = _font(44, serif=True)
    lines = []
    line_height = 58

    for size in [44, 40, 36, 34, 32]:
        candidate_font = _font(size, serif=True)
        candidate_lines = _limit_lines(_wrap_by_pixels(texto_card, candidate_font, max_width, draw), max_lines=11)
        candidate_line_height = int(size * 1.35)
        if len(candidate_lines) * candidate_line_height <= 590:
            body_font = candidate_font
            lines = candidate_lines
            line_height = candidate_line_height
            break

    if not lines:
        lines = _limit_lines(_wrap_by_pixels(texto_card, body_font, max_width, draw), max_lines=10)

    total_height = len(lines) * line_height
    start_y = 275 + max(0, int((560 - total_height) / 2))

    for line in lines:
        if not line:
            start_y += int(line_height * 0.55)
            continue
        draw.text((140, start_y), line, fill=(62, 49, 38, 255), font=body_font)
        start_y += line_height

    footer = "Ecos del Alma"
    footer_width = draw.textlength(footer, font=title_font)
    draw.text(((1080 - footer_width) / 2, 865), footer, fill=(90, 66, 45, 255), font=title_font)
    draw.text((140, 920), "escritura generativa · edición automática · imagen editorial", fill=(130, 109, 88, 230), font=small_font)

    filename = f"escrito-{publicacion_id:04d}.png"
    output = SOCIAL_ASSETS_DIR / filename
    card.convert("RGB").save(output, format="PNG", optimize=True)

    return f"/assets/social/{filename}"
