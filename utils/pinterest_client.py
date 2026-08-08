from __future__ import annotations

import base64
import mimetypes
import time
from pathlib import Path
from typing import Any

import requests


PINTEREST_API_BASE = "https://api.pinterest.com/v5"
PINTEREST_TOKEN_URL = f"{PINTEREST_API_BASE}/oauth/token"
PINTEREST_SCOPES = "boards:read,boards:write,pins:read,pins:write"


class PinterestAPIError(RuntimeError):
    """Error devuelto por Pinterest o producido al comunicarse con su API."""


def _response_message(response: requests.Response) -> str:
    try:
        payload = response.json()
    except ValueError:
        payload = None

    if isinstance(payload, dict):
        message = payload.get("message") or payload.get("error") or payload.get("error_description")
        if message:
            return str(message)
        return str(payload)

    text = response.text.strip()
    return text[:500] if text else f"HTTP {response.status_code}"


def obtener_access_token(app_id: str, app_secret: str) -> str:
    """Genera un token nuevo mediante Client Credentials.

    Este flujo representa a la cuenta propietaria de la app y evita almacenar
    access tokens de larga duración en el repositorio.
    """
    response = requests.post(
        PINTEREST_TOKEN_URL,
        auth=(app_id, app_secret),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "client_credentials",
            "scope": PINTEREST_SCOPES,
        },
        timeout=30,
    )

    if not response.ok:
        raise PinterestAPIError(
            f"No se pudo obtener el access token de Pinterest: "
            f"HTTP {response.status_code} - {_response_message(response)}"
        )

    token = response.json().get("access_token")
    if not token:
        raise PinterestAPIError("Pinterest no devolvió access_token.")
    return str(token)


class PinterestClient:
    def __init__(self, access_token: str) -> None:
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
        max_attempts: int = 5,
    ) -> requests.Response:
        url = f"{PINTEREST_API_BASE}{path}"
        last_response: requests.Response | None = None

        for attempt in range(1, max_attempts + 1):
            response = self.session.request(
                method,
                url,
                params=params,
                json=json_data,
                timeout=60,
            )
            last_response = response

            if response.ok:
                return response

            retryable = response.status_code == 429 or 500 <= response.status_code <= 599
            if not retryable or attempt == max_attempts:
                raise PinterestAPIError(
                    f"Pinterest API {method} {path}: HTTP {response.status_code} - "
                    f"{_response_message(response)}"
                )

            retry_after = response.headers.get("Retry-After")
            try:
                delay = max(float(retry_after), 1.0) if retry_after else min(2 ** attempt, 30)
            except ValueError:
                delay = min(2 ** attempt, 30)
            print(f"⏳ Pinterest pidió reintentar. Nuevo intento en {delay:.0f}s...")
            time.sleep(delay)

        raise PinterestAPIError(
            f"Pinterest API no respondió correctamente: {last_response.status_code if last_response else 'sin respuesta'}"
        )

    def listar_tableros(self) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        bookmark: str | None = None

        while True:
            params: dict[str, Any] = {"page_size": 100}
            if bookmark:
                params["bookmark"] = bookmark

            response = self._request("GET", "/boards", params=params)
            payload = response.json()
            items.extend(payload.get("items", []))
            bookmark = payload.get("bookmark")
            if not bookmark:
                break

        return items

    def listar_pins_tablero(self, board_id: str) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        bookmark: str | None = None

        while True:
            params: dict[str, Any] = {"page_size": 100}
            if bookmark:
                params["bookmark"] = bookmark

            response = self._request(
                "GET",
                f"/boards/{board_id}/pins",
                params=params,
            )
            payload = response.json()
            items.extend(payload.get("items", []))
            bookmark = payload.get("bookmark")
            if not bookmark:
                break

        return items

    def crear_pin_imagen(
        self,
        *,
        board_id: str,
        image_path: Path,
        title: str,
        description: str,
        link: str,
        alt_text: str,
        declarar_ia: bool = True,
    ) -> dict[str, Any]:
        if not image_path.exists():
            raise FileNotFoundError(f"No existe la imagen para Pinterest: {image_path}")

        mime_type, _ = mimetypes.guess_type(image_path.name)
        if mime_type not in {"image/png", "image/jpeg"}:
            mime_type = "image/png" if image_path.suffix.lower() == ".png" else "image/jpeg"

        encoded_image = base64.b64encode(image_path.read_bytes()).decode("ascii")

        payload: dict[str, Any] = {
            "board_id": board_id,
            "title": title[:100],
            "description": description[:800],
            "alt_text": alt_text[:500],
            "link": link[:2048],
            "media_source": {
                "source_type": "image_base64",
                "is_standard": True,
                "content_type": mime_type,
                "data": encoded_image,
            },
        }

        if declarar_ia:
            payload["ai_disclosures"] = {"values": ["AI_MODIFIED"]}

        response = self._request("POST", "/pins", json_data=payload)
        return response.json()
