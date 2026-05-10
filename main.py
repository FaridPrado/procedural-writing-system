from __future__ import annotations

from datetime import datetime
import json
from typing import Any
from zoneinfo import ZoneInfo

from agentes.agentes import agente_guardian, agente_poeta, agente_visualizador
from config import (
    MAX_INTENTOS,
    MEMORIA_PUBLICACION_PATH,
    MEMORIA_TEMAS_PATH,
    POSTS_DIR,
    PROJECT_TIMEZONE,
    TEMAS_RECIENTES_A_EVITAR,
)
from utils.render_social import generar_tarjeta_social


def cargar_json(path, valor_por_defecto: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        guardar_json(path, valor_por_defecto)
        return valor_por_defecto

    with open(path, "r", encoding="utf-8") as archivo:
        return json.load(archivo)


def guardar_json(path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as archivo:
        json.dump(data, archivo, indent=2, ensure_ascii=False)
        archivo.write("\n")


def yaml_quote(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def actualizar_temas_usados(memoria_temas: dict[str, Any], tema: str) -> dict[str, Any]:
    ultimos = memoria_temas.get("ultimos_temas", [])
    ultimos.append(tema)
    memoria_temas["ultimos_temas"] = ultimos[-TEMAS_RECIENTES_A_EVITAR:]
    return memoria_temas


def crear_markdown(
    *,
    titulo: str,
    fecha: datetime,
    tema: str,
    texto: str,
    imagen_relativa: str | None,
    prompt_visual: str | None = None,
    comentario_editorial: str | None = None,
) -> str:
    fecha_frontmatter = fecha.strftime("%Y-%m-%d %H:%M:%S %z")
    image_line = f"image: {yaml_quote(imagen_relativa)}\n" if imagen_relativa else ""

    return f"""---
layout: post
title: {yaml_quote(titulo)}
date: {fecha_frontmatter}
categories: [ecos-del-alma]
tema: {yaml_quote(tema)}
{image_line}---

{texto.strip()}
"""


def main() -> None:
    memoria_publicacion = cargar_json(
        MEMORIA_PUBLICACION_PATH,
        {"ultimo_id": 0, "fecha_ultima_publicacion": "", "publicaciones": []},
    )
    memoria_temas = cargar_json(MEMORIA_TEMAS_PATH, {"ultimos_temas": []})

    texto_final = None
    tema_final = None
    revision_final = None

    for intento in range(1, MAX_INTENTOS + 1):
        texto, tema = agente_poeta(memoria_temas.get("ultimos_temas", []))
        resultado, es_valido, revision = agente_guardian(texto, tema)

        if es_valido:
            texto_final = str(resultado)
            tema_final = tema
            revision_final = revision
            print(f"🎉 Texto aprobado en el intento {intento}.")
            break

        print(f"⏳ Reintentando ({intento}/{MAX_INTENTOS})...")

    if not texto_final or not tema_final:
        raise RuntimeError("No se logró generar un texto válido después de varios intentos.")

    ahora = datetime.now(ZoneInfo(PROJECT_TIMEZONE))
    nuevo_id = int(memoria_publicacion.get("ultimo_id", 0)) + 1
    nombre_archivo = f"{ahora.strftime('%Y-%m-%d')}-escrito-{nuevo_id:04d}.md"
    ruta_publicacion = POSTS_DIR / nombre_archivo

    imagen_url = None
    prompt_visual = None
    try:
        imagen_url, prompt_visual = agente_visualizador(texto_final, tema_final)
    except Exception as exc:
        print(f"⚠️ No se pudo crear la imagen base: {exc}")

    imagen_relativa = generar_tarjeta_social(
        texto=texto_final,
        tema=tema_final["nombre"],
        imagen_url=imagen_url,
        publicacion_id=nuevo_id,
    )
    print(f"🖼️ Tarjeta visual creada: docs{imagen_relativa}")

    contenido_md = crear_markdown(
        titulo=tema_final["nombre"],
        fecha=ahora,
        tema=tema_final["nombre"],
        texto=texto_final,
        imagen_relativa=imagen_relativa,
        prompt_visual=prompt_visual,
        comentario_editorial=(revision_final or {}).get("comentario_editorial"),
    )

    POSTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(ruta_publicacion, "w", encoding="utf-8") as archivo:
        archivo.write(contenido_md)

    memoria_publicacion["ultimo_id"] = nuevo_id
    memoria_publicacion["fecha_ultima_publicacion"] = ahora.date().isoformat()
    memoria_publicacion.setdefault("publicaciones", []).append(
        {
            "id": nuevo_id,
            "fecha": ahora.isoformat(),
            "tema": tema_final["nombre"],
            "archivo": str(ruta_publicacion.relative_to(POSTS_DIR.parent.parent)),
            "imagen": imagen_relativa,
            "puntuacion_emocional": (revision_final or {}).get("puntuacion_emocional"),
        }
    )
    guardar_json(MEMORIA_PUBLICACION_PATH, memoria_publicacion)

    memoria_temas = actualizar_temas_usados(memoria_temas, tema_final["nombre"])
    guardar_json(MEMORIA_TEMAS_PATH, memoria_temas)

    print(f"📄 Publicado en {ruta_publicacion}")
    print("🧠 Memoria actualizada.")


if __name__ == "__main__":
    main()
