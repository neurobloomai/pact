
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
from pact_protocol.fallback_adapter import PactAdapter, PactMessage

app = FastAPI(title="PACT Microservice", description="Fallback Adapter API for PACT Protocol")

# Define the request schema using Pydantic
class Intent(BaseModel):
    type: str
    confidence: Optional[float] = 1.0
    ambiguous: Optional[bool] = False
    suggested_alternatives: Optional[List[str]] = []

class Context(BaseModel):
    uncertainty_reason: Optional[str] = "unknown"

class PactRequest(BaseModel):
    sender: str
    receiver: str
    intent: Intent
    context: Optional[Context] = None

# Instantiate the adapter
adapter = PactAdapter(agent_id="agent://microservice")

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/process-intent")
def process_intent(request: PactRequest):
    try:
        msg = PactMessage(
            sender=request.sender,
            receiver=request.receiver,
            intent=request.intent.dict(),
            context=request.context.dict() if request.context else {}
        )
        response = adapter.process_message(msg)
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
