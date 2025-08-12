# PACT Demo Script
## 5-Minute Partner Demo: AI Agent Universal Translator

---

## **Opening Hook (30 seconds)**

*"AI agents can't collaborate — because they don't speak the same language."*

**The Problem Everyone Faces:**
- Your Dialogflow agent says "check_order_status"
- Your Rasa agent expects "order.lookup"  
- Your custom AI agent wants "find_my_order"
- **Result:** Weeks of custom integration work for every connection

**Today, we'll show you how PACT solves this in minutes, not weeks.**

---

## **Live Demo Flow (3.5 minutes)**

### **Setup (Hidden - Pre-demo)**
```bash
# Have this running before demo starts
git clone https://github.com/neurobloomai/pact.git
cd pact
pip install -r requirements.txt
uvicorn main:app --reload
```

### **Demo Scenario: E-commerce Order Lookup**

**Situation:** Customer asks about order status across different platforms

#### **1. The Translation Magic (90 seconds)**

**Input:** Dialogflow format
```bash
curl -X POST http://localhost:8000/translate \
-H 'Content-Type: application/json' \
-d '{
  "pact_version": "0.1",
  "message_id": "demo-001",
  "timestamp": "2025-08-11T12:00:00Z",
  "sender": { 
    "agent_id": "customer-service-bot", 
    "platform": "Dialogflow" 
  },
  "recipient": { 
    "agent_id": "order-system", 
    "platform": "Rasa" 
  },
  "session": { 
    "session_id": "demo-session-123", 
    "context": {"customer_tier": "premium"} 
  },
  "payload": {
    "intent": "check_order_status",
    "entities": { "order_id": "A123456" },
    "text": "Where is my order A123456?"
  }
}'
```

**Output:** Rasa format (instant translation)
```json
{
  "translated_message": {
    "intent": "order.lookup",
    "entities": {
      "order_id": "A123456"
    },
    "text": "Where is my order A123456?",
    "confidence": 0.95
  },
  "translation_metadata": {
    "source_platform": "Dialogflow",
    "target_platform": "Rasa",
    "translation_time_ms": 45
  }
}
```

**Key Message:** *"45 milliseconds to translate between platforms. No custom code needed."*

#### **2. Show Platform Flexibility (60 seconds)**

**Different platforms, same result:**

```bash
# Slack to Microsoft Teams translation
curl -X POST http://localhost:8000/translate \
-H 'Content-Type: application/json' \
-d '{
  "sender": { "platform": "Slack" },
  "recipient": { "platform": "Teams" },
  "payload": {
    "intent": "schedule_meeting",
    "entities": { "date": "tomorrow", "attendees": ["john", "sarah"] },
    "text": "Schedule meeting with John and Sarah for tomorrow"
  }
}'
```

**Key Message:** *"Same protocol works across any platform. Add new platforms without breaking existing integrations."*

#### **3. Resilience Demo (30 seconds)**

**Show built-in fallbacks:**
```bash
# Low confidence intent - shows fallback behavior
curl -X POST http://localhost:8000/translate \
-H 'Content-Type: application/json' \
-d '{
  "sender": { "platform": "Custom" },
  "recipient": { "platform": "Dialogflow" },
  "payload": {
    "intent": "unclear_user_input",
    "entities": {},
    "text": "help me with the thing"
  }
}'
```

**Response shows graceful degradation:**
```json
{
  "translated_message": {
    "intent": "fallback.human_handoff",
    "confidence": 0.3,
    "fallback_reason": "low_confidence_intent"
  }
}
```

**Key Message:** *"Built-in resilience. When translation fails, PACT fails gracefully."*

---

## **Architecture Advantage (45 seconds)**

**Show the PACT Flow Diagram:**
```
Agent A (Dialogflow) → PACT Gateway → ML Classifier → Intent Translator → Agent Router → Adapter Layer → Agent B (Rasa)
```

**Three Key Differentiators:**
1. **Vendor Neutral:** Works with ANY platform (not locked to one vendor)
2. **Lightweight:** Millisecond translations, not heavyweight transformations  
3. **Resilient:** Built-in fallbacks for every failure mode

---

## **Market Positioning (30 seconds)**

### **Why This Matters Now**

**The Agent Explosion:**
- Companies average 7+ different AI agents
- Each speaks its own "language"  
- Integration complexity grows exponentially

**PACT's Solution:**
- **Universal translator** for agent ecosystems
- **Open source protocol** (no vendor lock-in)
- **Network effects:** Every new adapter helps everyone

---

## **Call to Action (15 seconds)**

**Immediate Next Steps:**
1. **Try it now:** `pip install pact-protocol`
2. **5-minute setup:** Follow our Quick Start Guide
3. **Join the ecosystem:** Contribute adapters for your platforms

**Partnership Opportunities:**
- Platform adapter development
- Enterprise deployment support  
- Protocol standardization collaboration

---

## **Demo Preparation Checklist**

### **Before the Demo:**
- [ ] PACT adapter running on localhost:8000
- [ ] Test all curl commands work
- [ ] Have backup slides if live demo fails
- [ ] Prepare for Q&A about security, scalability, roadmap

### **Key Stats to Memorize:**
- **Translation speed:** <50ms average
- **Supported platforms:** Growing ecosystem (show current list)
- **Installation:** Single pip command
- **Open source:** MIT license, community-driven

### **Common Questions & Answers:**

**Q: "How is this different from MCP or other protocols?"**
**A:** "MCP focuses on model-to-tool communication. PACT focuses on agent-to-agent translation. We're complementary, not competitive."

**Q: "What about security?"**
**A:** "PACT is stateless by design. All security happens at the platform level. We translate intent, not data."

**Q: "How do you handle custom intents?"**
**A:** "Our ML classifier learns from usage. Plus, easy custom mapping for domain-specific intents."

**Q: "What's your business model?"**
**A:** "Open source protocol. Revenue from enterprise deployment, custom adapters, and managed services."

---

## **Success Metrics**

**Demo is successful if partner:**
- Understands the agent interoperability problem
- Sees PACT as infrastructure solution (not just another tool)
- Wants to explore partnership opportunities
- Asks about integration timeline

**Follow-up:** Send Quick Start Guide and schedule technical deep-dive session.

---

*Ready to demonstrate the future of agent collaboration. PACT: Because every agent deserves to be understood.*
