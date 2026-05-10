"""
Dadi — Voice WhatsApp food ordering agent for elderly Indians.
Entry point: FastAPI application with WhatsApp Meta Cloud API integration.
"""
import logging

import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from core.config import settings
from whatsapp.webhook import router as webhook_router
from whatsapp.client import whatsapp

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Dadi",
    description="Voice WhatsApp food ordering agent for elderly Indians",
    version="0.1.0",
)

app.include_router(webhook_router)


@app.get("/", include_in_schema=False)
async def health() -> JSONResponse:
    return JSONResponse({"status": "ok", "service": "Dadi WhatsApp Agent"})


@app.on_event("shutdown")
async def on_shutdown() -> None:
    await whatsapp.aclose()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
    )
