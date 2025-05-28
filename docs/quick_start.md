# 🚀 PACT Quick Start: 5 Minutes to Agent Communication

Welcome to the PACT protocol — enabling seamless communication between intelligent agents.

---

## 1. 📦 Install the PACT Library

```bash
pip install pact-protocol
```

> *(Note: Replace with your local install or GitHub link if not published on PyPI yet.)*

---

## 2. 🤖 Create Your First PACT Agent

```python
from pact_core import PACTProcessor, PACTMessage

class MyAgent(PACTProcessor):
    def __init__(self):
        super().__init__()
        self.register_capability("say_hello", self.say_hello)

    def say_hello(self, message):
        return {"message": "Hello from MyAgent!"}

agent = MyAgent()
message = PACTMessage(intent="say_hello")
print(agent.process_intent(message))
```

---

## 3. 🔁 Test Agent Communication

Start a second agent with different capabilities and test fallback handling.

```bash
python examples/cross_agent_demo.py
```

Explore how PACT handles negotiation, fallback, and capability matching.

---

## ✅ What’s Next?

- [x] Build your own capability handler
- [x] Add fallback logic in case of unsupported intents
- [x] Simulate multi-agent workflows with PACT demo scripts

---

## 🧠 Learn More

- [Protocol Specification](specs/protocol.md)
- [Agent Integration Guide](docs/integration_guide.md)
- [Fallback Patterns](docs/fallback_strategies.md)

