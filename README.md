# PACT Protocol
## Protocol for Agent Collaboration & Transfer

**Building the universal, lightweight communication layer for intelligent agents.**

---

## Why PACT?

AI agents can't collaborate — because they don't speak the same language. We built PACT, an open-source protocol to fix that.

**The Problem:**
- Your Dialogflow agent says "check_order_status"
- Your Rasa agent expects "order.lookup"  
- Your custom AI agent wants "find_my_order"
- **Result:** Weeks of custom integration work for every connection

**PACT Solution:**
*"Let every agent have its mind... PACT translates their intents."*

---

## What is PACT?

PACT provides a simple, open, and scalable protocol for intent translation and agent interoperability — enabling diverse AI agents, platforms, and services to collaborate seamlessly.

### Protocol Positioning

| Protocol | Focus | Type | Owned By | Strength |
|----------|-------|------|----------|----------|
| **PACT** | Agent ↔ Agent | Horizontal + Middleware | **Vendor-neutral** | **Intent Translation & Interop** |
| MCP | App ↔ Model | Vertical | Anthropic | Context & Tool Enrichment |
| A2A | Agent ↔ Agent | Horizontal | - | Multi-agent Coordination |

### PACT Advantages

| Feature | PACT | MCP | A2A |
|---------|------|-----|-----|
| **Focus** | Intent translation & platform adaptation | Model-to-tool communication | Agent-to-agent collaboration |
| **Complexity** | **Lightweight** | Medium | Comprehensive |
| **ML Integration** | **Built-in** | Limited | Optional |
| **Implementation** | **Simple** | Complex | Complex |
| **Use Case** | **Cross-platform messaging** | Tool augmentation | Complex interactions |

---

## Quick Start

### Installation & Setup
```bash
# Clone the repository
git clone https://github.com/neurobloomai/pact.git
cd pact

# Install dependencies
pip install flask

# Start the PACT server
python main_server.py
```

**Server starts on:** `http://127.0.0.1:8000`

### Basic Usage

#### Intent Translation
```bash
curl -X POST http://127.0.0.1:8000/translate \
-H 'Content-Type: application/json' \
-d '{
  "sender": {"platform": "Dialogflow"},
  "recipient": {"platform": "Rasa"},
  "payload": {
    "intent": "check_order_status",
    "entities": {"order_id": "A123456"},
    "text": "Where is my order?"
  }
}'
```

**Response:**
```json
{
  "translated_message": {
    "intent": "order.lookup",
    "entities": {"order_id": "A123456"},
    "text": "Where is my order?",
    "confidence": 0.95
  },
  "translation_metadata": {
    "source_platform": "Dialogflow",
    "target_platform": "Rasa",
    "translation_time_ms": 45
  }
}
```

#### Capability Negotiation
```bash
curl -X POST http://127.0.0.1:8000/negotiate \
-H 'Content-Type: application/json' \
-d '{
  "action": "create",
  "parameters": {
    "title": "Demo Meeting",
    "start_time": "2025-08-12T10:00:00Z",
    "participants": ["alice", "bob"]
  }
}'
```

**Response:**
```json
{
  "result": {
    "agent_id": "agent_calendar",
    "action": "create",
    "match_score": 1.0,
    "missing_params": []
  },
  "status": "matched"
}
```

---

## Architecture

### Core Components
- **PACT Gateway:** Validates incoming message envelope format
- **Intent Translator:** Maps between different intent naming formats
- **Capability Matcher:** Finds appropriate agents for actions
- **Agent Router:** Routes messages to target agents
- **Response Handler:** Wraps responses in standard PACT envelope

### Message Flow
```
Agent A → PACT Gateway → Intent Translator → Agent Router → Agent B
       ← Response Handler ← Adapter Layer ← Target Agent ←
```

### Resilient Design
- **Built-in fallbacks** for low-confidence intents
- **Graceful degradation** for adapter failures
- **Timeout handling** with automatic retry
- **Platform-agnostic** architecture

---

## Examples & Use Cases

### 🏢 HR Workflows
**Complete employee lifecycle automation**
```bash
# Start employee onboarding workflow
curl -X POST http://127.0.0.1:8000/hr/workflows/onboarding \
-H 'Content-Type: application/json' \
-d '{
  "employee_name": "Alice Johnson",
  "email": "alice.johnson@company.com",
  "department": "Engineering",
  "start_date": "2025-09-01",
  "manager": "bob.smith@company.com",
  "position": "Senior Software Engineer",
  "salary": 125000
}'
```

**Coordinates across 7 agents:**
- ATS (Applicant Tracking) → HRIS → IT Access → Payroll → Calendar → Notifications → Learning Management

### 🎯 Cross-Platform Customer Support
**Multi-platform customer service coordination**
- Seamless handoffs between Slack, Teams, Discord
- Unified ticket management across platforms
- Context preservation during platform switches

### 💰 Financial Risk Management  
**Risk assessment workflow coordination**
- Multi-system risk evaluation
- Automated compliance checking
- Real-time decision coordination

### 🧠 Intent Hierarchy
**Semantic intent understanding**
- Hierarchical intent relationships
- Context-aware intent mapping
- Intelligent fallback routing

### 🔍 Semantic Intent Matching
**Advanced intent classification**
- ML-powered intent recognition
- Cross-platform intent normalization
- Confidence-based routing

---

## Repository Structure

```
/pact/
├── pact_cli_mock.py           # Core PACT protocol server
├── main_server.py             # Integrated server with extensions
├── hr_workflows/              # HR workflow automation
│   ├── __init__.py
│   ├── hr_capabilities.py     # HR agent definitions
│   ├── workflow_templates.py  # Workflow orchestration
│   ├── hr_coordinator.py      # HR coordination logic
│   ├── hr_demo_data.py        # Sample HR data
│   └── README.md              # HR workflows documentation
├── examples/                  # Domain-specific examples
│   ├── cross_platform_customer_support/
│   ├── financial_risk_management/
│   ├── intent_hierarchy/
│   ├── multiagent_devops_pipeline/
│   └── semantic_intent_matching/
└── README.md                  # This file
```

---

## API Reference

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Server status and info |
| `/translate` | POST | Translate intents between platforms |
| `/negotiate` | POST | Agent capability negotiation |
| `/status` | GET | Comprehensive server status |

### HR Workflow Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/hr/workflows/<type>` | POST | Execute HR workflow (onboarding, offboarding, etc.) |
| `/hr/workflows/<id>/status` | GET | Check workflow progress |
| `/hr/coordinate` | POST | Single HR action coordination |
| `/hr/capabilities` | GET | Available HR agent capabilities |
| `/hr/demo-data` | GET | Sample data for testing |

### Demo & Testing

```bash
# Check server status
curl http://127.0.0.1:8000/status

# Get HR demo data
curl http://127.0.0.1:8000/hr/demo-data

# List available HR workflows
curl http://127.0.0.1:8000/hr/workflows
```

---

## Development

### Adding New Domains
1. **Create domain directory** (e.g., `finance_workflows/`)
2. **Define agent capabilities** following HR workflows pattern
3. **Create workflow templates** for domain processes
4. **Register Blueprint** in `main_server.py`

### Extending Core PACT
1. **Intent mappings** in `pact_cli_mock.py`
2. **Capability definitions** in `AGENT_CAPABILITIES`
3. **Response templates** for new agent types

### Testing
```bash
# Start development server
python main_server.py

# Test core translation
curl -X POST http://127.0.0.1:8000/translate \
-H 'Content-Type: application/json' \
-d '{"sender": {"platform": "Test"}, "recipient": {"platform": "Target"}, "payload": {"intent": "test_action"}}'

# Test HR workflows
curl -X POST http://127.0.0.1:8000/hr/workflows/onboarding \
-H 'Content-Type: application/json' \
-d '$(curl -s http://127.0.0.1:8000/hr/demo-data/onboarding | jq .sample_data)'
```

---

## Key Benefits

### For Enterprises
- **Reduced integration time** from weeks to minutes
- **Vendor-neutral architecture** prevents lock-in
- **Scalable coordination** across unlimited agents
- **Built-in resilience** for mission-critical operations

### For Developers  
- **Simple API** with clear documentation
- **Modular architecture** for easy extension
- **Open source** with MIT license
- **Production-ready** with Docker support

### For System Architects
- **Universal translation layer** for any agent ecosystem
- **Foundation for multi-agent systems** at enterprise scale
- **Future-proof protocol** designed for agent explosion
- **Security and compliance** built into core design

---

## Roadmap

### Current (Phase 1)
- ✅ Core intent translation protocol
- ✅ Agent capability negotiation
- ✅ HR workflow automation
- ✅ Basic resilience and fallbacks

### Next (Phase 2)
- 🎯 Advanced ML intent classification
- 🎯 Dynamic capability discovery
- 🎯 Enhanced security features
- 🎯 Performance optimization

### Future (Phase 3)
- 🎯 Enterprise deployment tools
- 🎯 Multi-tenant architecture
- 🎯 Advanced analytics and monitoring
- 🎯 Industry-specific extensions

---

## Contributing

We welcome contributions to extend PACT toward a true open communication standard!

### Good First Issues
- Extend adapters to support new platforms (Intercom, Zendesk)
- Add dynamic intent learning capabilities  
- Enhance error and fallback handling
- Create new domain-specific workflow examples

### How to Contribute
1. **Fork the repository**
2. **Create feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit changes** (`git commit -m 'Add amazing feature'`)
4. **Push to branch** (`git push origin feature/amazing-feature`)
5. **Open Pull Request**

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Contact

**NeuroBloom.ai Team**
- 📧 Email: [founders@neurobloom.ai](mailto:founders@neurobloom.ai)
- 🌐 Website: [neurobloom.ai](https://neurobloom.ai)
- 💬 GitHub Discussions: Coming soon!

---

## Vision

We're building resilient infrastructure for the future of agent communication and coordination. We believe the next evolution of AI won't be dominated by monolithic models—but by networks of agents that understand intent, cooperate intelligently, and recover gracefully.

**Together, let's build the protocol layer for agent collaboration.** 🌍

---

**Built with ❤️ by NeuroBloom.ai**  
*Making agent coordination inevitable, not innovative.*
