# Stop your current server (CTRL+C in the server terminal)
# Then replace the entire file:

cat > pact_cli_mock.py << 'EOF'
# pact_cli_mock.py
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

# Mock agent capability registry
AGENT_CAPABILITIES = {
    "agent_calendar": {
        "create": ["title", "start_time", "participants"],
        "update": ["event_id", "title"]
    },
    "agent_notes": {
        "create": ["content"],
        "retrieve": ["note_id"]
    }
}

def match_capabilities(action, parameters):
    best_match = None
    best_score = 0
    
    for agent, actions in AGENT_CAPABILITIES.items():
        if action in actions:
            required_params = set(actions[action])
            provided_params = set(parameters.keys())
            matched_params = required_params & provided_params
            score = len(matched_params) / len(required_params)
            
            if score > best_score:
                best_score = score
                best_match = {
                    "agent_id": agent,
                    "action": action,
                    "match_score": round(score, 2),
                    "missing_params": list(required_params - provided_params)
                }
    
    return best_match

@app.route("/negotiate", methods=["POST"])
def negotiate():
    data = request.get_json()
    action = data.get("action")
    parameters = data.get("parameters", {})
    
    result = match_capabilities(action, parameters)
    
    if result:
        return jsonify({
            "status": "matched" if result['match_score'] == 1.0 else "partial",
            "result": result
        })
    else:
        return jsonify({
            "status": "failed",
            "message": "No matching capabilities found"
        }), 404

@app.route("/translate", methods=["POST"])
def translate():
    data = request.get_json()
    
    # Extract sender and recipient platforms
    sender_platform = data.get("sender", {}).get("platform", "unknown")
    recipient_platform = data.get("recipient", {}).get("platform", "unknown")
    
    # Extract payload
    payload = data.get("payload", {})
    original_intent = payload.get("intent", "")
    entities = payload.get("entities", {})
    text = payload.get("text", "")
    
    # Simple intent translation mapping
    intent_translations = {
        "check_order_status": "order.lookup",
        "schedule_meeting": "calendar.create_event", 
        "cancel_order": "order.cancel",
        "book_appointment": "booking.schedule",
        "get_weather": "weather.current",
        "send_message": "messaging.send"
    }
    
    # Translate intent
    translated_intent = intent_translations.get(original_intent, f"translated.{original_intent}")
    
    # Build response
    response = {
        "translated_message": {
            "intent": translated_intent,
            "entities": entities,
            "text": text,
            "confidence": 0.95
        },
        "translation_metadata": {
            "source_platform": sender_platform,
            "target_platform": recipient_platform,
            "translation_time_ms": 45,
            "translation_method": "intent_mapping"
        }
    }
    
    return jsonify(response)

@app.route("/")
def index():
    return "PACT Mock API - Capability Negotiation & Intent Translation"

if __name__ == "__main__":
    app.run(debug=True, port=8000)
EOF
