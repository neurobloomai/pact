from fastapi import APIRouter, FastAPI
from pydantic import BaseModel

router = APIRouter()

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

@router.post("/translate")
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
