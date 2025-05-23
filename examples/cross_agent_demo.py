from examples.agent_a import SchedulerProAgent
from examples.agent_b import BasicCalendarAgent
from pact_core import PACTMessage

# Initialize agents
agent_a = SchedulerProAgent()
agent_b = BasicCalendarAgent()

# Simulate Agent A trying to delegate a complex meeting scheduling to Agent B
complex_intent = {
    "action": "schedule_meeting",
    "parameters": {
        "participants": ["alice@example.com", "bob@example.com", "carol@example.com", "dan@example.com", "eve@example.com", "frank@example.com"],
        "duration": "60",
        "preferences": {
            "time_range": "morning",
            "avoid_conflicts": True
        }
    }
}

print("Agent A creates intent and sends to Agent B...\n")

# Agent A constructs message
intent_message = PACTMessage(intent=complex_intent["action"], metadata=complex_intent["parameters"])

# Agent B receives the message
response = agent_b.schedule_simple_meeting({
    "action": intent_message.intent,
    "parameters": intent_message.metadata
})

print("Agent B response:")
print(response)

# Simulate fallback handling
if response.get("status") == "partial":
    print("\nAgent A receives partial response and applies fallback strategy...\n")
    retry_response = agent_a.handle_capability_mismatch({
        "action": intent_message.intent,
        "parameters": intent_message.metadata
    }, agent_b.capabilities)
    print("Agent A adjusted and retried:")
    print(retry_response)
