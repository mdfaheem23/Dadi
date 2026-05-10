"""
WhatsApp Business Cloud API client.
Handles sending text, audio, and template messages, and downloading media.
"""
import logging
from typing import Any

import httpx

from core.config import settings

logger = logging.getLogger(__name__)

_HEADERS = {
    "Authorization": f"Bearer {settings.whatsapp_access_token}",
    "Content-Type": "application/json",
}


class WhatsAppClient:
    """Async client for the Meta WhatsApp Cloud API."""

    def __init__(self) -> None:
        self._http = httpx.AsyncClient(headers=_HEADERS, timeout=30)

    # ------------------------------------------------------------------
    # Text messaging
    # ------------------------------------------------------------------

    async def send_text(self, to: str, body: str, *, preview_url: bool = False) -> dict[str, Any]:
        """Send a plain text message."""
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "text",
            "text": {"preview_url": preview_url, "body": body},
        }
        return await self._post(settings.whatsapp_messages_url, payload)

    # ------------------------------------------------------------------
    # Audio messaging
    # ------------------------------------------------------------------

    async def send_audio_by_id(self, to: str, media_id: str) -> dict[str, Any]:
        """Send an audio file that was previously uploaded to Meta."""
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "audio",
            "audio": {"id": media_id},
        }
        return await self._post(settings.whatsapp_messages_url, payload)

    async def send_audio_by_url(self, to: str, url: str) -> dict[str, Any]:
        """Send an audio file hosted on a publicly accessible URL."""
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "audio",
            "audio": {"link": url},
        }
        return await self._post(settings.whatsapp_messages_url, payload)

    # ------------------------------------------------------------------
    # Template messaging
    # ------------------------------------------------------------------

    async def send_template(
        self,
        to: str,
        template_name: str,
        language_code: str = "en_US",
        components: list[dict] | None = None,
    ) -> dict[str, Any]:
        """Send a pre-approved message template."""
        payload: dict[str, Any] = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": language_code},
            },
        }
        if components:
            payload["template"]["components"] = components
        return await self._post(settings.whatsapp_messages_url, payload)

    # ------------------------------------------------------------------
    # Reaction
    # ------------------------------------------------------------------

    async def send_reaction(self, to: str, message_id: str, emoji: str) -> dict[str, Any]:
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "reaction",
            "reaction": {"message_id": message_id, "emoji": emoji},
        }
        return await self._post(settings.whatsapp_messages_url, payload)

    # ------------------------------------------------------------------
    # Mark as read
    # ------------------------------------------------------------------

    async def mark_as_read(self, message_id: str) -> dict[str, Any]:
        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id,
        }
        return await self._post(settings.whatsapp_messages_url, payload)

    # ------------------------------------------------------------------
    # Media: upload & download
    # ------------------------------------------------------------------

    async def upload_media(self, file_bytes: bytes, mime_type: str, filename: str) -> str:
        """Upload media to Meta and return the media ID."""
        files = {"file": (filename, file_bytes, mime_type)}
        data = {"messaging_product": "whatsapp"}
        headers = {"Authorization": f"Bearer {settings.whatsapp_access_token}"}
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(settings.whatsapp_media_url, files=files, data=data, headers=headers)
        resp.raise_for_status()
        return resp.json()["id"]

    async def download_media(self, media_id: str) -> bytes:
        """Download media bytes from Meta given a media ID."""
        url = f"{settings.whatsapp_api_base_url}/{media_id}"
        headers = {"Authorization": f"Bearer {settings.whatsapp_access_token}"}
        async with httpx.AsyncClient(timeout=60) as client:
            # Step 1: get the CDN URL
            meta_resp = await client.get(url, headers=headers)
            meta_resp.raise_for_status()
            cdn_url = meta_resp.json()["url"]

            # Step 2: download the actual bytes
            media_resp = await client.get(cdn_url, headers=headers)
            media_resp.raise_for_status()
        return media_resp.content

    # ------------------------------------------------------------------
    # Internal helper
    # ------------------------------------------------------------------

    async def _post(self, url: str, payload: dict[str, Any]) -> dict[str, Any]:
        resp = await self._http.post(url, json=payload)
        if not resp.is_success:
            logger.error("WhatsApp API error %s: %s", resp.status_code, resp.text)
            resp.raise_for_status()
        data = resp.json()
        logger.debug("WhatsApp API response: %s", data)
        return data

    async def aclose(self) -> None:
        await self._http.aclose()


# Module-level singleton — imported wherever needed
whatsapp = WhatsAppClient()
