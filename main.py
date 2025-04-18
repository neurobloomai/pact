from fastapi import FastAPI, Request
from pydantic import BaseModel
import uvicorn
import json

app = FastAPI()

# Static intent mapping config (platform A -> platform B)
intent_mapping = {
    "check_order_status": "order.lookup",
    "reset_password": "user.reset_password"
}

# Example message envelope format
class AgentMessage(BaseModel):
    pact_version: str
    message_id: str
    timestamp: str
    sender: dict
    recipient: dict
    session: dict
    payload: dict

# Webhook endpoint for receiving messages
@app.post("/translate")
async def translate_message(msg: AgentMessage):
    original_intent = msg.payload.get("intent")
    translated_intent = intent_mapping.get(original_intent, original_intent)
    translated_message = {
        "pact_version": msg.pact_version,
        "message_id": msg.message_id,
        "timestamp": msg.timestamp,
        "sender": msg.sender,
        "recipient": msg.recipient,
        "session": msg.session,
        "payload": {
            "intent": translated_intent,
            "entities": msg.payload.get("entities", {}),
            "text": msg.payload.get("text")
        }
    }
    # For demo purposes, just echo the translated message
    return {"translated_message": translated_message}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
