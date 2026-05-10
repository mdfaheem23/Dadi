"""
Pydantic models for incoming WhatsApp webhook payloads (Cloud API format).
Reference: https://developers.facebook.com/docs/whatsapp/cloud-api/webhooks/payload-examples
"""
from typing import Any, Optional
from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Inbound webhook payload models
# ---------------------------------------------------------------------------

class Profile(BaseModel):
    name: str


class Contact(BaseModel):
    profile: Profile
    wa_id: str


class Text(BaseModel):
    body: str


class Audio(BaseModel):
    id: str
    mime_type: str


class Image(BaseModel):
    id: str
    mime_type: str
    sha256: Optional[str] = None
    caption: Optional[str] = None


class Document(BaseModel):
    id: str
    mime_type: str
    filename: Optional[str] = None
    caption: Optional[str] = None


class Reaction(BaseModel):
    message_id: str
    emoji: str


class ReferredProduct(BaseModel):
    catalog_id: str
    product_retailer_id: str


class Context(BaseModel):
    from_: Optional[str] = None
    id: Optional[str] = None

    class Config:
        populate_by_name = True
        fields = {"from_": "from"}


class Message(BaseModel):
    id: str
    from_: str
    timestamp: str
    type: str
    context: Optional[Context] = None
    text: Optional[Text] = None
    audio: Optional[Audio] = None
    image: Optional[Image] = None
    document: Optional[Document] = None
    reaction: Optional[Reaction] = None

    class Config:
        populate_by_name = True
        fields = {"from_": "from"}


class Metadata(BaseModel):
    display_phone_number: str
    phone_number_id: str


class Status(BaseModel):
    id: str
    status: str          # sent | delivered | read | failed
    timestamp: str
    recipient_id: str


class Value(BaseModel):
    messaging_product: str
    metadata: Metadata
    contacts: Optional[list[Contact]] = None
    messages: Optional[list[Message]] = None
    statuses: Optional[list[Status]] = None


class Change(BaseModel):
    value: Value
    field: str


class Entry(BaseModel):
    id: str
    changes: list[Change]


class WebhookPayload(BaseModel):
    object: str
    entry: list[Entry]


# ---------------------------------------------------------------------------
# Helper: extract first message from a webhook payload
# ---------------------------------------------------------------------------

def extract_message(payload: WebhookPayload) -> Optional[tuple[Message, Contact | None, Metadata]]:
    """Return (message, contact, metadata) from the first change that has a message."""
    for entry in payload.entry:
        for change in entry.changes:
            val = change.value
            if val.messages:
                msg = val.messages[0]
                contact = val.contacts[0] if val.contacts else None
                return msg, contact, val.metadata
    return None
