from pact_core import PACTProcessor, PACTMessage

class BasicCalendarAgent(PACTProcessor):
    def __init__(self):
        super().__init__()
        self.agent_id = "basic-calendar-v1"
        self.capabilities = {
            "schedule_meeting": {
                "complexity": "basic",
                "max_participants": 5,
                "timezone_support": False,
                "single_calendar_only": True
            },
            "check_availability": {
                "basic_slots_only": True,
                "no_preferences": True
            }
        }

    def schedule_simple_meeting(self, intent):
        participants = intent.get("parameters", {}).get("participants", [])
        if len(participants) > self.capabilities["schedule_meeting"]["max_participants"]:
            return self.handle_unsupported_features(intent)
        return {
            "status": "success",
            "meeting_id": "B78901",
            "scheduled_time": "2025-06-01T14:00:00Z",
            "limitations": {
                "no_timezone_conversion": True,
                "basic_notifications_only": True
            }
        }

    def handle_unsupported_features(self, intent):
        supported = {
            "participants": intent["parameters"]["participants"][:5]
        }
        return {
            "status": "partial",
            "response": supported,
            "fallback_applied": {
                "level": 2,
                "description": "Processed basic parameters only",
                "unsupported_features": ["timezone", "advanced_preferences"]
            }
        }
