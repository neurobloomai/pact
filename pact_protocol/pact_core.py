"""
pact_core.py — Core PACT protocol logic

FallbackProcessor now delegates all intent mapping lookups to IntentRegistry
instead of embedding hardcoded dicts.  This keeps business logic in one place
and makes it trivially easy to extend mappings without touching Python code.
"""

import json
import logging
from typing import Any, Callable, Dict, List, Optional

import jsonschema
from jsonschema import validate

from pact_protocol.intent_registry import IntentRegistry

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Core message type
# ---------------------------------------------------------------------------

class PACTMessage:
    def __init__(self, intent: str, metadata: Optional[Dict[str, Any]] = None):
        self.version = "0.1.0"
        self.intent = intent
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "intent": self.intent,
            "metadata": self.metadata,
        }


# ---------------------------------------------------------------------------
# Capability management
# ---------------------------------------------------------------------------

class CapabilityManager:
    def __init__(self) -> None:
        self.capabilities: Dict[str, Callable] = {}

    def register_capability(self, action: str, handler: Callable) -> None:
        self.capabilities[action] = handler

    def advertise_capabilities(self) -> List[str]:
        return list(self.capabilities.keys())

    def match_intent_to_capability(self, intent: str) -> Optional[str]:
        return intent if intent in self.capabilities else None

    def negotiate_parameters(
        self, intent: str, capability: str
    ) -> Dict[str, Any]:
        return {"mapped_capability": capability}


# ---------------------------------------------------------------------------
# Fallback processor — now registry-driven
# ---------------------------------------------------------------------------

class FallbackProcessor:
    """
    Attempt to resolve an intent through a cascade of strategies.

    All mapping lookups delegate to *registry* so that approximation /
    decomposition rules live in config files rather than in source code.
    """

    def __init__(
        self,
        capability_manager: CapabilityManager,
        registry: Optional[IntentRegistry] = None,
    ) -> None:
        self.capability_manager = capability_manager
        # Use the provided registry or auto-discover one
        self.registry = registry or IntentRegistry.load()

        self.fallback_strategies = [
            self.exact_match,
            self.registry_approximation,   # was: hardcoded dict
            self.registry_decomposition,   # was: hardcoded dict
            self.parameter_adaptation,
            self.graceful_failure,
        ]

    def process_with_fallbacks(self, intent: str) -> Dict[str, Any]:
        for strategy in self.fallback_strategies:
            result = strategy(intent)
            if result:
                return {
                    "status": "handled_with_fallback",
                    "strategy": strategy.__name__,
                    "result": result,
                }
        return self.graceful_failure(intent)  # guaranteed non-None

    # ------------------------------------------------------------------
    # Individual strategies
    # ------------------------------------------------------------------

    def exact_match(self, intent: str) -> Optional[Dict[str, Any]]:
        """Direct hit in CapabilityManager — no translation needed."""
        if self.capability_manager.match_intent_to_capability(intent):
            return {"handled_by": "exact_match"}
        return None

    def registry_approximation(self, intent: str) -> Optional[Dict[str, Any]]:
        """
        Translate *intent* via the registry mappings.

        Returns a result only when a mapping actually exists (i.e. the
        registry didn't return the original intent unchanged).
        """
        translated = self.registry.translate(intent)
        if translated != intent:
            logger.debug(
                "registry_approximation: %s → %s", intent, translated
            )
            return {"approximated_to": translated}
        return None

    def registry_decomposition(self, intent: str) -> Optional[Dict[str, Any]]:
        """
        Expand a compound intent into sub-intents via the registry.
        """
        sub_intents = self.registry.decompose(intent)
        if sub_intents:
            logger.debug(
                "registry_decomposition: %s → %s", intent, sub_intents
            )
            return {"decomposed_intents": sub_intents}
        return None

    def parameter_adaptation(self, intent: str) -> Optional[Dict[str, Any]]:
        """
        Heuristic last-resort: try to find a capability by inspecting
        keyword tokens in the intent string.

        Extend or replace this with a proper ML-based matcher (issue #4).
        """
        for token in intent.split("_"):
            for capability in self.capability_manager.advertise_capabilities():
                if token in capability:
                    logger.debug(
                        "parameter_adaptation: matched %r via token %r → %r",
                        intent,
                        token,
                        capability,
                    )
                    return {"adapted_intent": capability}
        return None

    def graceful_failure(self, intent: str) -> Dict[str, Any]:
        logger.warning("Unable to resolve intent: %r", intent)
        return {"error": "Unable to process intent", "intent": intent}


# ---------------------------------------------------------------------------
# Top-level processor
# ---------------------------------------------------------------------------

class PACTProcessor:
    def __init__(self, registry: Optional[IntentRegistry] = None) -> None:
        self.capability_manager = CapabilityManager()
        self.registry = registry or IntentRegistry.load()
        self.fallback_processor = FallbackProcessor(
            self.capability_manager, registry=self.registry
        )

    def register_capability(self, action: str, handler: Callable) -> None:
        self.capability_manager.register_capability(action, handler)

    def process_intent(self, message: PACTMessage) -> Dict[str, Any]:
        matched = self.capability_manager.match_intent_to_capability(message.intent)
        if matched:
            handler = self.capability_manager.capabilities[matched]
            try:
                result = handler(message)
                return {"status": "success", "result": result}
            except Exception as exc:
                logger.error("Handler raised: %s", exc)
                return {"status": "error", "message": str(exc)}
        return self.fallback_processor.process_with_fallbacks(message.intent)


# ---------------------------------------------------------------------------
# JSON schema validation (unchanged)
# ---------------------------------------------------------------------------

PACT_MESSAGE_SCHEMA = {
    "type": "object",
    "properties": {
        "version": {"type": "string"},
        "intent": {"type": "string"},
        "metadata": {"type": "object"},
    },
    "required": ["version", "intent"],
}


def validate_message(message: dict):
    try:
        validate(instance=message, schema=PACT_MESSAGE_SCHEMA)
        return True, "Validation successful"
    except jsonschema.exceptions.ValidationError as err:
        return False, str(err)


# ---------------------------------------------------------------------------
# Sample capability handler (used in tests / demos)
# ---------------------------------------------------------------------------

def sample_schedule_handler(message: PACTMessage) -> Dict[str, Any]:
    return {"scheduled": True, "details": message.metadata}
