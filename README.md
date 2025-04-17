# pact_adapter_mvp

# Rewriting README.md after code execution reset
readme_content = """
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
