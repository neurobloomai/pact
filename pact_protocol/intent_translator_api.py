"""
intent_translator_api.py — PACT /translate endpoint

Intent mappings are now loaded dynamically via IntentRegistry instead of
being hardcoded in this file.  See intent_registry.py for the loading logic
and intent_registry.json (or .yaml) for the actual mapping definitions.
"""

import logging
from functools import lru_cache

from fastapi import APIRouter, FastAPI, HTTPException, status
from pydantic import BaseModel, Field

from pact_protocol.intent_registry import IntentRegistry

logger = logging.getLogger(__name__)
router = APIRouter()


# ---------------------------------------------------------------------------
# Registry singleton — loaded once at startup, reloadable via /registry/reload
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def _get_registry() -> IntentRegistry:
    """Return a cached IntentRegistry, auto-discovering config on first call."""
    return IntentRegistry.load()


def get_registry() -> IntentRegistry:
    """
    Dependency-injection–friendly accessor.
    Swap this out in tests:
        app.dependency_overrides[get_registry] = lambda: IntentRegistry({"a": "b"})
    """
    return _get_registry()


# ---------------------------------------------------------------------------
# Request / response schemas
# ---------------------------------------------------------------------------

class AgentMessage(BaseModel):
    pact_version: str = Field(..., example="0.1.0")
    message_id: str = Field(..., example="msg-abc-123")
    timestamp: str = Field(..., example="2025-07-18T10:00:00Z")
    sender: dict
    recipient: dict
    session: dict
    payload: dict

    model_config = {"extra": "forbid"}


class TranslateResponse(BaseModel):
    translated_message: dict
    registry_source: str = Field(
        description="File or source the registry was loaded from"
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/translate",
    response_model=TranslateResponse,
    summary="Translate an agent intent to the recipient platform's namespace",
)
async def translate_message(msg: AgentMessage) -> TranslateResponse:
    """
    Translate the ``intent`` field inside *msg.payload* using the active
    IntentRegistry, then return the full message with the translated intent.

    If no mapping exists the original intent is returned unchanged
    (transparent passthrough).
    """
    registry = get_registry()

    original_intent: str | None = msg.payload.get("intent")
    if not original_intent:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="payload.intent is required and must be a non-empty string.",
        )

    translated_intent = registry.translate(original_intent)

    if translated_intent != original_intent:
        logger.debug(
            "Intent translated: %s → %s", original_intent, translated_intent
        )
    else:
        logger.debug("No mapping found for intent %r — using as-is.", original_intent)

    translated_message = {
        "pact_version": msg.pact_version,
        "message_id": msg.message_id,
        "timestamp": msg.timestamp,
        "sender": msg.sender,
        "recipient": msg.recipient,
        "session": msg.session,
        "payload": {
            "intent": translated_intent,
            "original_intent": original_intent,
            "entities": msg.payload.get("entities", {}),
            "text": msg.payload.get("text"),
        },
    }

    return TranslateResponse(
        translated_message=translated_message,
        registry_source=str(registry.source or "built-in defaults"),
    )


@router.post(
    "/registry/reload",
    summary="Hot-reload the intent registry from its source file",
    status_code=status.HTTP_200_OK,
)
async def reload_registry() -> dict:
    """
    Trigger a live reload of the intent registry without restarting the server.
    Only meaningful when the registry was loaded from a file.
    """
    registry = get_registry()
    try:
        registry.reload()
        return {
            "status": "reloaded",
            "mappings_count": len(registry),
            "source": str(registry.source or "in-memory"),
        }
    except Exception as exc:
        logger.error("Registry reload failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registry reload failed: {exc}",
        ) from exc


@router.get(
    "/registry",
    summary="Inspect the currently loaded intent registry",
)
async def inspect_registry() -> dict:
    """Return the active mappings and metadata for observability."""
    registry = get_registry()
    return {
        "source": str(registry.source or "built-in defaults"),
        "mappings_count": len(registry),
        "mappings": registry.mappings,
        "decompositions": registry.decompositions,
    }
