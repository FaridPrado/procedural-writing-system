import json
import random
import re
from typing import Any
from urllib.parse import quote

from groq import Groq

from config import BIBLIA_PATH, GROQ_API_KEY, GROQ_MODEL, PROJECT_NAME


if not GROQ_API_KEY:
    raise RuntimeError(
        "Falta GROQ_API_KEY. Crea un archivo .env local o configura el secret en GitHub Actions."
    )

client = Groq(api_key=GROQ_API_KEY)


def cargar_guia() -> dict[str, Any]:
    with open(BIBLIA_PATH, "r", encoding="utf-8") as archivo:
        return json.load(archivo)


GUIA = cargar_guia()


def limpiar_respuesta(texto: str) -> str:
    texto = texto.strip()
    if texto.startswith("```"):
        partes = texto.split("```")
        if len(partes) >= 2:
            texto = partes[1].strip()
            if texto.lower().startswith("json"):
                texto = texto[4:].strip()
    return texto.strip().strip('"').strip()


def extraer_json(texto: str) -> dict[str, Any]:
    limpio = limpiar_respuesta(texto)
    try:
        return json.loads(limpio)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", limpio, flags=re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise


def seleccionar_tema(temas_recientes: list[str] | None = None) -> dict[str, str]:
    temas_recientes = temas_recientes or []
    temas_disponibles = GUIA["temas"]
    temas_filtrados = [
        tema for tema in temas_disponibles if tema["nombre"] not in temas_recientes
    ]
    return random.choice(temas_filtrados if temas_filtrados else temas_disponibles)


# --- Agente 1: El Poeta ---
def agente_poeta(temas_recientes: list[str] | None = None) -> tuple[str, dict[str, str]]:
    print("🖋️ El Poeta comienza a escribir...")

    tema_elegido = seleccionar_tema(temas_recientes)
    print(f"   Tema elegido: {tema_elegido['nombre']}")

    system_prompt = f"""
Eres El Poeta, la voz editorial de {PROJECT_NAME}.

Tu trabajo es escribir un texto poético breve, íntimo y publicable. No escribes frases motivacionales genéricas: escribes escenas pequeñas que alguien podría sentir como propias.

## Guía de estilo
- Género: {GUIA['tono_estilo']['genero']}
- Atmósfera: {GUIA['tono_estilo']['atmosfera']}
- Longitud: {GUIA['tono_estilo']['longitud']}
- Recursos permitidos: {', '.join(GUIA['tono_estilo']['recursos_permitidos'])}
- Evitar: {', '.join(GUIA['tono_estilo']['prohibido'])}
- Restricción especial: {GUIA['restriccion_adicional']}

## Tema de hoy
Nombre: {tema_elegido['nombre']}
Descripción: {tema_elegido['descripcion']}

## Estructura sugerida
{chr(10).join(f'- {item}' for item in GUIA['estructura_poetica'])}

## Reglas de salida
- Devuelve solo el texto final.
- No incluyas título.
- No incluyas firma.
- No expliques el proceso.
- No uses hashtags dentro del texto.
"""

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"Escribe un texto nuevo sobre: {tema_elegido['nombre']}.",
            },
        ],
        temperature=0.9,
        max_tokens=360,
    )

    texto = limpiar_respuesta(response.choices[0].message.content or "")
    print(f"✅ Texto generado: {texto[:70]}...")
    return texto, tema_elegido


# --- Agente 2: El Guardián de la Emoción ---
def agente_guardian(
    texto: str, tema: dict[str, str]
) -> tuple[str | list[str], bool, dict[str, Any]]:
    print("🛡️ El Guardián de la Emoción revisa...")

    check_prompt = f"""
Actúa como editor literario. Evalúa si este texto puede publicarse en {PROJECT_NAME}.

Tema: {tema['nombre']} - {tema['descripcion']}

## Criterios
1. Evita clichés y frases hechas.
2. Usa imágenes sensoriales concretas.
3. Suena humano, vulnerable y natural.
4. Respeta la restricción: {GUIA['restriccion_adicional']}
5. No parece texto corporativo ni autoayuda genérica.
6. Mantiene una extensión razonable para una publicación poética breve.

## Texto
{texto}

Responde únicamente con JSON válido, sin markdown, con esta estructura exacta:
{{
  "es_valido": true,
  "violaciones": [],
  "puntuacion_emocional": 8,
  "comentario_editorial": "comentario breve"
}}
"""

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": check_prompt}],
        temperature=0.0,
        max_tokens=260,
    )

    raw = response.choices[0].message.content or "{}"

    try:
        resultado = extraer_json(raw)
    except Exception as exc:
        resultado = {
            "es_valido": False,
            "violaciones": [f"No se pudo interpretar la revisión editorial: {exc}"],
            "puntuacion_emocional": 0,
            "comentario_editorial": "Respuesta inválida del revisor.",
        }

    es_valido = bool(resultado.get("es_valido"))
    puntuacion = int(resultado.get("puntuacion_emocional", 0) or 0)

    if es_valido and puntuacion >= 7:
        print(f"✅ Aprobado ({puntuacion}/10)")
        return texto, True, resultado

    violaciones = resultado.get("violaciones") or ["No alcanzó la puntuación mínima."]
    print(f"❌ Rechazado: {violaciones}")
    return violaciones, False, resultado


# --- Agente 3: El Visualizador ---
def agente_visualizador(texto: str, tema: dict[str, str]) -> tuple[str, str]:
    print("🎨 El Visualizador crea la dirección visual...")

    prompt = f"""
Create an English image prompt for a square editorial artwork that accompanies this Spanish poetic text.

Theme: {tema['nombre']}
Text: {texto[:500]}

Visual style: emotional editorial poster, soft paper texture, subtle grain, warm minimalism, muted tones, cinematic natural light, no readable text, no logos, no detailed faces.

Return only the image prompt. Maximum 70 words.
"""

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.75,
        max_tokens=130,
    )

    prompt_imagen = limpiar_respuesta(response.choices[0].message.content or "")
    imagen_url = (
        "https://image.pollinations.ai/prompt/"
        f"{quote(prompt_imagen)}?width=1080&height=1080&nologo=true&enhance=true"
    )

    print(f"   Prompt visual: {prompt_imagen[:90]}...")
    return imagen_url, prompt_imagen
