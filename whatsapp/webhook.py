"""
WhatsApp webhook router.

GET  /webhook  — Meta token verification challenge
POST /webhook  — Incoming messages and status updates
"""
import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Query, Request, Response
from fastapi.responses import PlainTextResponse

from core.config import settings
from whatsapp.models import WebhookPayload, extract_message
from whatsapp.client import whatsapp
from whatsapp.handlers import handle_message

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhook", tags=["webhook"])


# ---------------------------------------------------------------------------
# GET: Meta webhook verification
# ---------------------------------------------------------------------------

@router.get("", response_class=PlainTextResponse)
async def verify_webhook(
    hub_mode: str = Query(alias="hub.mode"),
    hub_verify_token: str = Query(alias="hub.verify_token"),
    hub_challenge: str = Query(alias="hub.challenge"),
) -> str:
    """
    Meta sends a GET request to verify the webhook endpoint.
    Respond with the hub.challenge value when the verify token matches.
    """
    if hub_mode == "subscribe" and hub_verify_token == settings.whatsapp_webhook_verify_token:
        logger.info("Webhook verified successfully.")
        return hub_challenge

    logger.warning("Webhook verification failed — token mismatch.")
    raise HTTPException(status_code=403, detail="Verification token mismatch")


# ---------------------------------------------------------------------------
# POST: Receive incoming messages / status updates
# ---------------------------------------------------------------------------

@router.post("")
async def receive_webhook(request: Request) -> Response:
    """
    Handle all incoming WhatsApp events: messages, reactions, status updates.
    Always returns 200 immediately so Meta doesn't retry.
    """
    body: dict[str, Any] = await request.json()
    logger.debug("Incoming webhook payload: %s", body)

    try:
        payload = WebhookPayload.model_validate(body)
    except Exception as exc:
        logger.error("Failed to parse webhook payload: %s", exc)
        # Still return 200 to prevent Meta from retrying unknown payloads
        return Response(status_code=200)

    if payload.object != "whatsapp_business_account":
        return Response(status_code=200)

    result = extract_message(payload)
    if result is None:
        # Status update (delivered/read) — acknowledge and move on
        return Response(status_code=200)

    message, contact, metadata = result

    # Mark message as read immediately
    try:
        await whatsapp.mark_as_read(message.id)
    except Exception as exc:
        logger.warning("Could not mark message as read: %s", exc)

    # Dispatch to the message handler (non-blocking background logic)
    try:
        sender = message.from_
        await handle_message(message=message, contact=contact, sender=sender)
    except Exception as exc:
        logger.exception("Error handling message from %s: %s", message.from_, exc)

    return Response(status_code=200)
