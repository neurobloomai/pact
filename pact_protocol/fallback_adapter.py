
"""
fallback_adapter.py

This module defines a basic PACT adapter implementation
with logic for handling intent fallbacks and ambiguous messages.

Intended to be placed under: pact/pact_protocol/
"""

import uuid
import datetime
from typing import Dict, Optional


class PactMessage:
    def __init__(self, sender: str, receiver: str, intent: Dict, context: Optional[Dict] = None, meta: Optional[Dict] = None):
        self.message_id = str(uuid.uuid4())
        self.sender = sender
        self.receiver = receiver
        self.intent = intent
        self.context = context or {}
        self.meta = meta or {
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "protocol_version": "1.1"
        }


class PactAdapter:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id

    def process_message(self, message: PactMessage) -> Dict:
        intent = message.intent
        confidence = intent.get("confidence", 1.0)
        ambiguous = intent.get("ambiguous", False)

        if ambiguous or confidence < 0.7:
            return self._handle_fallback(message)
        else:
            return self._handle_intent(message)

    def _handle_intent(self, message: PactMessage) -> Dict:
        return {
            "status": "executed",
            "message_id": message.message_id,
            "response": f"Intent '{message.intent['type']}' processed successfully."
        }

    def _handle_fallback(self, message: PactMessage) -> Dict:
        suggested = message.intent.get("suggested_alternatives", [])
        reason = message.context.get("uncertainty_reason", "unknown")

        if suggested:
            return {
                "status": "fallback_triggered",
                "message_id": message.message_id,
                "action": "suggest_alternative",
                "suggested_intents": suggested,
                "reason": reason
            }
        else:
            return {
                "status": "fallback_failed",
                "message_id": message.message_id,
                "action": "error",
                "reason": f"Unable to resolve ambiguous intent. Cause: {reason}"
            }


# Optional direct test usage
if __name__ == "__main__":
    import json

    adapter = PactAdapter(agent_id="agent://beta")
    incoming = PactMessage(
        sender="agent://alpha",
        receiver="agent://beta",
        intent={
            "type": "analyze",
            "confidence": 0.6,
            "ambiguous": True,
            "suggested_alternatives": ["summarize", "translate"]
        },
        context={
            "uncertainty_reason": "intent_conflict_with_capabilities"
        }
    )
    result = adapter.process_message(incoming)
    print(json.dumps(result, indent=2))
