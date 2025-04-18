from fastapi import FastAPI  # ✅ Only import what's used
from pydantic import BaseModel
import uvicorn

app = FastAPI()

# Static intent mapping config
intent_mapping = {
    "check_order_status": "order.lookup",
    "reset_password": "user.reset_password"
}


class AgentMessage(BaseModel):
    pact_version: str
    message_id: str
    timestamp: str
    sender: dict
    recipient: dict
    session: dict
    payload: dict


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

    return {"translated_message": translated_message}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
