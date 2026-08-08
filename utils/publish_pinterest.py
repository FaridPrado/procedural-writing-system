from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
from typing import Any

try:
    from .pinterest_client import PinterestAPIError, PinterestClient, obtener_access_token
except ImportError:  # Ejecución directa: python utils/publish_pinterest.py
    from pinterest_client import PinterestAPIError, PinterestClient, obtener_access_token


ROOT_DIR = Path(__file__).resolve().parent.parent
POSTS_DIR = ROOT_DIR / "docs" / "_posts"
DOCS_DIR = ROOT_DIR / "docs"
STATE_PATH = ROOT_DIR / "memoria" / "pinterest_publicados.json"
DEFAULT_SITE_URL = "https://faridsprado.github.io/procedural-writing-system"
DEFAULT_BOARD_NAME = "Ecos del Alma"


def cargar_estado() -> dict[str, Any]:
    if not STATE_PATH.exists():
        return {"board_id": "", "board_name": "", "publicaciones": {}}

    with STATE_PATH.open("r", encoding="utf-8") as archivo:
        data = json.load(archivo)

    data.setdefault("board_id", "")
    data.setdefault("board_name", "")
    data.setdefault("publicaciones", {})
    return data


def guardar_estado(data: dict[str, Any]) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with STATE_PATH.open("w", encoding="utf-8") as archivo:
        json.dump(data, archivo, ensure_ascii=False, indent=2)
        archivo.write("\n")


def _parse_scalar(value: str) -> str:
    raw = value.strip()
    if not raw:
        return ""
    if raw.startswith(('"', "'")):
        try:
            return str(json.loads(raw))
        except json.JSONDecodeError:
            return raw.strip('"\'')
    return raw


def leer_post(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\s*\n(.*?)\n---\s*\n?(.*)\Z", text, flags=re.DOTALL)
    if not match:
        raise ValueError(f"Front matter inválido en {path}")

    frontmatter_text, body = match.groups()
    frontmatter: dict[str, str] = {}
    for line in frontmatter_text.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        frontmatter[key.strip()] = _parse_scalar(value)

    filename_match = re.match(
        r"(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})-(?P<slug>.+)\.md$",
        path.name,
    )
    if not filename_match:
        raise ValueError(f"Nombre de publicación Jekyll no reconocido: {path.name}")

    image = frontmatter.get("image", "")
    image_path = DOCS_DIR / image.lstrip("/") if image else None

    clean_body = re.sub(r"\s+", " ", body.strip())
    return {
        "key": str(path.relative_to(ROOT_DIR)).replace("\\", "/"),
        "path": path,
        "title": frontmatter.get("title") or filename_match.group("slug"),
        "tema": frontmatter.get("tema", ""),
        "image": image,
        "image_path": image_path,
        "body": clean_body,
        "year": filename_match.group("year"),
        "month": filename_match.group("month"),
        "day": filename_match.group("day"),
        "slug": filename_match.group("slug"),
    }


def construir_link(post: dict[str, Any], site_url: str) -> str:
    return (
        f"{site_url.rstrip('/')}/"
        f"{post['year']}/{post['month']}/{post['day']}/{post['slug']}/"
    )


def construir_descripcion(post: dict[str, Any]) -> str:
    body = post["body"]
    tema = post["tema"]
    suffix = f" · Ecos del Alma · {tema}" if tema else " · Ecos del Alma"
    max_body = max(0, 800 - len(suffix))
    return f"{body[:max_body].rstrip()}{suffix}"[:800]


def construir_alt_text(post: dict[str, Any]) -> str:
    tema = f" sobre {post['tema']}" if post["tema"] else ""
    return f"Tarjeta editorial de Ecos del Alma titulada «{post['title']}»{tema}."[:500]


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() not in {"0", "false", "no", "off"}


def obtener_cliente() -> PinterestClient:
    app_id = os.getenv("PINTEREST_APP_ID", "").strip()
    app_secret = os.getenv("PINTEREST_APP_SECRET", "").strip()
    if not app_id or not app_secret:
        raise RuntimeError(
            "Faltan PINTEREST_APP_ID y/o PINTEREST_APP_SECRET en las variables de entorno."
        )
    token = obtener_access_token(app_id, app_secret)
    return PinterestClient(token)


def resolver_tablero(client: PinterestClient) -> tuple[str, str]:
    requested_id = os.getenv("PINTEREST_BOARD_ID", "").strip()
    requested_name = os.getenv("PINTEREST_BOARD_NAME", DEFAULT_BOARD_NAME).strip() or DEFAULT_BOARD_NAME

    boards = client.listar_tableros()
    if requested_id:
        for board in boards:
            if str(board.get("id", "")) == requested_id:
                return requested_id, str(board.get("name", requested_name or requested_id))
        raise RuntimeError(
            f"No se encontró el tablero con ID {requested_id} entre los tableros accesibles."
        )

    matches = [
        board
        for board in boards
        if str(board.get("name", "")).strip().casefold() == requested_name.casefold()
    ]
    if len(matches) == 1:
        return str(matches[0]["id"]), str(matches[0].get("name", requested_name))

    disponibles = ", ".join(
        f"{board.get('name', '(sin nombre)')} [{board.get('id', '?')}]" for board in boards
    ) or "ninguno"
    if not matches:
        raise RuntimeError(
            f"No existe un tablero llamado '{requested_name}'. Tableros accesibles: {disponibles}"
        )
    raise RuntimeError(
        f"Hay más de un tablero llamado '{requested_name}'. Define PINTEREST_BOARD_ID. "
        f"Tableros: {disponibles}"
    )


def listar_tableros() -> int:
    client = obtener_cliente()
    boards = client.listar_tableros()
    if not boards:
        print("No se encontraron tableros.")
        return 0

    print("Tableros disponibles:")
    for board in boards:
        print(f"- {board.get('name', '(sin nombre)')} | ID: {board.get('id', '?')}")
    return 0


def sincronizar(*, limit: int = 0, dry_run: bool = False) -> int:
    posts = [leer_post(path) for path in sorted(POSTS_DIR.glob("*.md"))]
    estado = cargar_estado()
    publicaciones = estado["publicaciones"]
    site_url = os.getenv("PINTEREST_SITE_URL", DEFAULT_SITE_URL).strip() or DEFAULT_SITE_URL

    pendientes = [post for post in posts if post["key"] not in publicaciones]
    if limit > 0:
        pendientes = pendientes[:limit]

    print(f"📚 Publicaciones encontradas: {len(posts)}")
    print(f"✅ Ya registradas en Pinterest: {len(publicaciones)}")
    print(f"📌 Pendientes en esta ejecución: {len(pendientes)}")

    if dry_run:
        for post in pendientes:
            print(f"- {post['key']} -> {construir_link(post, site_url)}")
        return 0

    if not pendientes:
        print("✨ Pinterest ya está sincronizado.")
        return 0

    client = obtener_cliente()
    board_id, board_name = resolver_tablero(client)
    estado["board_id"] = board_id
    estado["board_name"] = board_name
    guardar_estado(estado)

    print(f"📍 Tablero destino: {board_name} ({board_id})")

    # Dedupe remoto: si un Pin ya existe con la URL del escrito, se recupera
    # en el estado local y no se crea un duplicado.
    remote_pins = client.listar_pins_tablero(board_id)
    remote_by_link = {
        str(pin.get("link", "")).rstrip("/") + "/": pin
        for pin in remote_pins
        if pin.get("link")
    }

    errores: list[str] = []
    declarar_ia = _env_bool("PINTEREST_AI_DISCLOSURE", True)

    for index, post in enumerate(pendientes, start=1):
        link = construir_link(post, site_url)
        normalized_link = link.rstrip("/") + "/"
        print(f"\n[{index}/{len(pendientes)}] {post['title']}")

        existing = remote_by_link.get(normalized_link)
        if existing:
            pin_id = str(existing.get("id", ""))
            publicaciones[post["key"]] = {
                "pin_id": pin_id,
                "pin_url": f"https://www.pinterest.com/pin/{pin_id}/" if pin_id else "",
                "post_url": link,
                "board_id": board_id,
                "recuperado": True,
                "publicado_en": datetime.now(timezone.utc).isoformat(),
            }
            guardar_estado(estado)
            print(f"♻️ Ya existía en Pinterest. Estado recuperado: {pin_id}")
            continue

        image_path = post["image_path"]
        if image_path is None or not image_path.exists():
            message = f"{post['key']}: no existe la imagen {image_path}"
            print(f"❌ {message}")
            errores.append(message)
            continue

        try:
            pin = client.crear_pin_imagen(
                board_id=board_id,
                image_path=image_path,
                title=post["title"],
                description=construir_descripcion(post),
                link=link,
                alt_text=construir_alt_text(post),
                declarar_ia=declarar_ia,
            )
        except (PinterestAPIError, OSError) as exc:
            message = f"{post['key']}: {exc}"
            print(f"❌ {message}")
            errores.append(message)
            continue

        pin_id = str(pin.get("id", ""))
        publicaciones[post["key"]] = {
            "pin_id": pin_id,
            "pin_url": f"https://www.pinterest.com/pin/{pin_id}/" if pin_id else "",
            "post_url": link,
            "board_id": board_id,
            "recuperado": False,
            "publicado_en": datetime.now(timezone.utc).isoformat(),
        }
        guardar_estado(estado)
        remote_by_link[normalized_link] = pin
        print(f"✅ Pin creado: {pin_id}")

    if errores:
        print("\n⚠️ La sincronización terminó con errores:")
        for error in errores:
            print(f"- {error}")
        return 1

    print("\n🎉 Sincronización con Pinterest completada.")
    return 0



def crear_pin_prueba() -> int:
    posts = [leer_post(path) for path in sorted(POSTS_DIR.glob("*.md"))]
    if not posts:
        raise RuntimeError("No hay publicaciones disponibles para usar como imagen de prueba.")

    post = posts[-1]
    image_path = post["image_path"]
    if image_path is None or not image_path.exists():
        raise RuntimeError(f"No existe la imagen de prueba: {image_path}")

    client = obtener_cliente()
    board_id, board_name = resolver_tablero(client)
    site_url = os.getenv("PINTEREST_SITE_URL", DEFAULT_SITE_URL).strip() or DEFAULT_SITE_URL
    declarar_ia = _env_bool("PINTEREST_AI_DISCLOSURE", True)

    pin = client.crear_pin_imagen(
        board_id=board_id,
        image_path=image_path,
        title="Prueba técnica · Ecos del Alma",
        description=(
            "Pin de prueba para verificar la integración automática entre "
            "Ecos del Alma, GitHub Actions y la API de Pinterest."
        ),
        link=f"{site_url.rstrip('/')}/",
        alt_text="Tarjeta editorial usada para probar la integración automática de Ecos del Alma con Pinterest.",
        declarar_ia=declarar_ia,
    )
    pin_id = str(pin.get("id", ""))
    print(f"✅ Pin de prueba creado en {board_name}: {pin_id}")
    print("ℹ️ Este Pin de prueba NO se registra como una publicación histórica.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Sincroniza Ecos del Alma con Pinterest.")
    parser.add_argument(
        "--list-boards",
        action="store_true",
        help="Muestra los tableros accesibles y sus IDs.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Máximo de Pins nuevos a crear. 0 = todos los pendientes.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Muestra qué se publicaría sin llamar a Pinterest.",
    )
    parser.add_argument(
        "--test-pin",
        action="store_true",
        help="Crea un único Pin técnico de prueba sin modificar el historial de sincronización.",
    )
    args = parser.parse_args()

    if args.limit < 0:
        parser.error("--limit no puede ser negativo")

    try:
        if args.list_boards:
            return listar_tableros()
        if args.test_pin:
            return crear_pin_prueba()
        return sincronizar(limit=args.limit, dry_run=args.dry_run)
    except (PinterestAPIError, RuntimeError, OSError, ValueError) as exc:
        print(f"❌ Error de Pinterest: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
