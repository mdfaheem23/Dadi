"""
Message dispatcher — routes incoming WhatsApp messages to the right logic.

Currently echoes back a confirmation; replace the stubs below with your
Gemini / Swiggy MCP agent logic.
"""
import logging
from typing import Optional

from whatsapp.models import Contact, Message
from whatsapp.client import whatsapp

logger = logging.getLogger(__name__)


async def handle_message(
    message: Message,
    contact: Optional[Contact],
    sender: str,
) -> None:
    name = contact.profile.name if contact else "there"

    match message.type:
        case "text":
            await _handle_text(sender, name, message.text.body)
        case "audio":
            await _handle_audio(sender, name, message.audio.id)
        case "image":
            await _handle_image(sender, name, message.image.id)
        case _:
            logger.info("Unhandled message type '%s' from %s", message.type, sender)
            await whatsapp.send_text(
                sender,
                f"Namaste {name}! 🙏 I can understand voice notes and text. Please send me a voice note or type your order.",
            )


async def _handle_text(sender: str, name: str, body: str) -> None:
    logger.info("Text from %s: %s", sender, body)

    # TODO: pipe `body` through Gemini Flash 2.0 agent + Swiggy MCP
    await whatsapp.send_text(
        sender,
        f"Namaste {name}! 🙏 You said: \"{body}\"\n\nFor best experience, send a voice note and I'll handle your order!",
    )


async def _handle_audio(sender: str, name: str, media_id: str) -> None:
    logger.info("Audio from %s, media_id=%s", sender, media_id)

    # Step 1: download audio bytes from Meta
    audio_bytes = await whatsapp.download_media(media_id)
    logger.info("Downloaded %d bytes of audio from %s", len(audio_bytes), sender)

    # TODO: transcribe with Gemini Flash 2.0 (audio → text)
    # TODO: process order with Swiggy MCP
    # TODO: generate TTS reply and upload, then send_audio_by_id

    await whatsapp.send_text(
        sender,
        f"Namaste {name}! 🙏 Got your voice note! I'm processing your order... (agent coming soon!)",
    )


async def _handle_image(sender: str, name: str, media_id: str) -> None:
    logger.info("Image from %s, media_id=%s", sender, media_id)
    await whatsapp.send_text(
        sender,
        f"Namaste {name}! 🙏 I received your image. For food orders, please send a voice note or type your request!",
    )
