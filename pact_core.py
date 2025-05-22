# Merging pact_core with validation and testing into a single executable block for this environment

import json
from typing import Callable, Dict, Any, List
import jsonschema
from jsonschema import validate


# Core message and processor classes
class PACTMessage:
    def __init__(self, intent: str, metadata: Dict[str, Any] = None):
        self.version = "0.1.0"
        self.intent = intent
        self.metadata = metadata or {}

    def to_dict(self):
        return {
            "version": self.version,
            "intent": self.intent,
            "metadata": self.metadata
        }


class CapabilityManager:
    def __init__(self):
        self.capabilities: Dict[str, Callable] = {}

    def register_capability(self, action: str, handler: Callable):
        self.capabilities[action] = handler

    def advertise_capabilities(self) -> List[str]:
        return list(self.capabilities.keys())

    def match_intent_to_capability(self, intent: str) -> str:
        if intent in self.capabilities:
            return intent
        return None

    def negotiate_parameters(self, intent: str, capability: str) -> Dict[str, Any]:
        return {"mapped_capability": capability}


class FallbackProcessor:
    def __init__(self, capability_manager: CapabilityManager):
        self.capability_manager = capability_manager
        self.fallback_strategies = [
            self.exact_match,
            self.parameter_adaptation,
            self.intent_approximation,
            self.intent_decomposition,
            self.graceful_failure
        ]

    def process_with_fallbacks(self, intent: str) -> Dict[str, Any]:
        for strategy in self.fallback_strategies:
            result = strategy(intent)
            if result:
                return {
                    "status": "handled_with_fallback",
                    "strategy": strategy.__name__,
                    "result": result
                }
        return self.graceful_failure(intent)

    def exact_match(self, intent: str):
        if self.capability_manager.match_intent_to_capability(intent):
            return {"handled_by": "exact_match"}

    def parameter_adaptation(self, intent: str):
        if "meeting" in intent:
            return {"adapted_intent": "schedule_meeting_basic"}
        return None

    def intent_approximation(self, intent: str):
        approximations = {
            "book_meeting": "schedule_meeting",
            "find_slot": "check_availability"
        }
        if intent in approximations:
            return {"approximated_to": approximations[intent]}
        return None

    def intent_decomposition(self, intent: str):
        if intent == "organize_event":
            return {"decomposed_intents": ["schedule_meeting", "send_invites"]}
        return None

    def graceful_failure(self, intent: str):
        return {"error": "Unable to process intent", "intent": intent}


class PACTProcessor:
    def __init__(self):
        self.capability_manager = CapabilityManager()
        self.fallback_processor = FallbackProcessor(self.capability_manager)

    def register_capability(self, action: str, handler: Callable):
        self.capability_manager.register_capability(action, handler)

    def process_intent(self, message: PACTMessage) -> Dict[str, Any]:
        matched = self.capability_manager.match_intent_to_capability(message.intent)
        if matched:
            handler = self.capability_manager.capabilities[matched]
            try:
                result = handler(message)
                return {"status": "success", "result": result}
            except Exception as e:
                return {"status": "error", "message": str(e)}
        else:
            return self.fallback_processor.process_with_fallbacks(message.intent)


# JSON schema for validation
PACT_MESSAGE_SCHEMA = {
    "type": "object",
    "properties": {
        "version": {"type": "string"},
        "intent": {"type": "string"},
        "metadata": {"type": "object"}
    },
    "required": ["version", "intent"]
}


def validate_message(message: dict):
    try:
        validate(instance=message, schema=PACT_MESSAGE_SCHEMA)
        return True, "Validation successful"
    except jsonschema.exceptions.ValidationError as err:
        return False, str(err)


# Sample capability handler
def sample_schedule_handler(message: PACTMessage):
    return {"scheduled": True, "details": message.metadata}


# Example agent test
def test_agents():
    agent = PACTProcessor()
    agent.register_capability("schedule_meeting", sample_schedule_handler)

    # Valid message
    message_dict = {
        "version": "0.1.0",
        "intent": "schedule_meeting",
        "metadata": {"time": "10:00 AM", "date": "2025-06-01"}
    }
    valid, msg = validate_message(message_dict)
    assert valid, msg

    message = PACTMessage(**message_dict)
    result = agent.process_intent(message)
    print("Test Result (Valid):", result)

    # Unknown intent, triggers fallback
    message_dict["intent"] = "book_meeting"
    message = PACTMessage(**message_dict)
    result = agent.process_intent(message)
    print("Test Result (Fallback):", result)


# Run test
test_agents()
