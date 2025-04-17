
# PACT Adapter MVP

**PACT (Protocol for Agent Collaboration & Transfer)** — a universal communication layer for intelligent AI agents.

This microservice provides a simple FastAPI-based adapter that translates intent messages between two AI platforms using a static mapping configuration.

---

## 🚀 Features

- FastAPI webhook listener at `/translate`
- Static intent mapping (platform A -> platform B)
- Standardized message envelope for agent communication
- Docker-ready deployment
- Postman collection for easy testing

---

## 🛠 Installation

```bash
git clone https://github.com/aknbloom/pact_adapter_mvp.git
cd pact_adapter_mvp
pip install -r requirements.txt
uvicorn main:app --reload
```

---

## 🧪 Usage

POST to the `/translate` endpoint with the following format:

```json
{
  "pact_version": "0.1",
  "message_id": "abc123",
  "timestamp": "2025-04-14T12:00:00Z",
  "sender": { "agent_id": "agent-A", "platform": "Dialogflow" },
  "recipient": { "agent_id": "agent-B", "platform": "Rasa" },
  "session": { "session_id": "xyz-123", "context": {} },
  "payload": {
    "intent": "check_order_status",
    "entities": { "order_id": "A123456" },
    "text": "Where is my order?"
  }
}
```

---

## 🐳 Docker

```bash
docker build -t pact-adapter .
docker run -p 8000:8000 pact-adapter
```

---

## 📬 Postman

Import the included `PACT_Adapter_Postman_Collection.json` and test the `/translate` endpoint locally or with Ngrok.

---

## 🤝 Contributing

We welcome contributions! Start by checking the pinned issue on extending adapter logic or adding dynamic mapping. PRs welcome!

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## 🌍 Vision

PACT is the SMTP of AI — a future-forward protocol for enabling seamless communication and collaboration across platforms.

> Protocol for Agent Collaboration & Transfer
