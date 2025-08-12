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

@app.route("/")
def index():
    return "PACT Capability Negotiation Mock API"

if __name__ == "__main__":
    app.run(debug=True, port=8000)
EOF
