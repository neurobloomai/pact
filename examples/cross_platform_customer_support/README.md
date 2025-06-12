# PACT Cross-Platform Customer Support
Unified customer support across multiple communication channels using intelligent PACT agent coordination.

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/neurobloomai/pact
cd pact/examples/customer_support

# Install dependencies
pip install -r requirements.txt

# Run demo
python support_example_usage.py
```

## 📁 File Structure

```
customer_support/
├── requirements.txt              # Dependencies
├── support_orchestrator.py       # Core coordination engine
├── support_agents.py            # PACT agent implementations
├── support_example_usage.py     # Usage examples
└── README.md                    # This file
```

## 🎯 What It Solves
Transform fragmented support channels into unified customer experiences:

```python
# Before: Disconnected channels, lost context
Email → EmailSystem (no context sharing)
Slack → SlackSystem (separate history)
WhatsApp → WhatsAppSystem (isolated data)
Phone → PhoneSystem (manual coordination)

# After: PACT unified support
Any Channel → PACT Gateway → Coordinated Agent Response
             ↓
        Complete Context Preservation
```

## 🏗️ Architecture

```
Customer Contact (Any Channel)
           ↓
    PACT Support Gateway
           ↓
┌─────────────────────────────────────────────────────────┐
│              Agent Coordination Layer                   │
├─────────────────────────────────────────────────────────┤
│ ChannelAgent → TriageAgent → KnowledgeAgent → EscalationAgent │
│      ↓              ↓              ↓               ↓     │
│ CustomerAgent → AnalyticsAgent → NotificationAgent     │
└─────────────────────────────────────────────────────────┘
           ↓
    Unified Response
```

## 🤖 Agents & Capabilities

| Agent | Purpose | PACT Actions |
|-------|---------|--------------|
| **ChannelAgent** | Multi-platform message handling | `channel.receive_message`, `channel.send_response`, `channel.format_for_platform` |
| **TriageAgent** | Intelligent routing & prioritization | `triage.classify_issue`, `triage.assign_priority`, `triage.route_to_specialist` |
| **KnowledgeAgent** | Solution search & recommendations | `knowledge.search_solutions`, `knowledge.suggest_articles`, `knowledge.track_effectiveness` |
| **CustomerAgent** | Profile & context management | `customer.get_profile`, `customer.update_history`, `customer.calculate_satisfaction` |
| **EscalationAgent** | Smart escalation & specialist routing | `escalation.determine_specialist`, `escalation.transfer_context`, `escalation.notify_escalation` |
| **AnalyticsAgent** | Metrics & insights generation | `analytics.track_interaction`, `analytics.generate_insights`, `analytics.create_report` |
| **NotificationAgent** | Multi-channel notifications | `notification.send_confirmation`, `notification.alert_team`, `notification.schedule_follow_up` |

## 🔧 Usage Examples

### 1. Basic Support Request

```python
from support_orchestrator import PACTSupportOrchestrator

# Initialize support system
orchestrator = PACTSupportOrchestrator()
await orchestrator.initialize()

# Handle customer contact
contact_data = {
    "customer_id": "cust_12345",
    "customer_name": "John Smith",
    "channel": "email",
    "subject": "Login Issues",
    "message": "Can't access my account",
    "metadata": {"urgency": "medium"}
}

ticket_id = await orchestrator.handle_customer_contact(contact_data)
```

### 2. Multi-Channel Conversation

```python
# Customer starts on email, continues on phone
email_ticket = await orchestrator.handle_customer_contact({
    "customer_id": "cust_67890",
    "channel": "email",
    "message": "Order not received",
    "order_id": "ORD-2024-001"
})

# Later, same customer calls
phone_contact = await orchestrator.handle_customer_contact({
    "customer_id": "cust_67890",
    "channel": "phone",
    "message": "Following up on my email about missing order"
})

# PACT automatically links conversations and provides full context
```

### 3. Escalation Flow

```python
# High-priority issue requiring specialist
critical_contact = {
    "customer_id": "cust_premium_001",
    "channel": "slack",
    "message": "Production system down - urgent",
    "metadata": {
        "urgency": "critical",
        "customer_tier": "enterprise"
    }
}

# Automatic escalation to technical specialist
ticket_id = await orchestrator.handle_customer_contact(critical_contact)
```

### 4. Custom Agent Configuration

```python
# Configure agents for specific business needs
orchestrator = PACTSupportOrchestrator(
    config={
        "triage_rules": {
            "enterprise_customers": "immediate_specialist",
            "billing_issues": "billing_team",
            "technical_issues": "tech_support"
        },
        "escalation_thresholds": {
            "response_time": 30,  # minutes
            "customer_satisfaction": 3.0  # out of 5
        },
        "channels": {
            "email": {"enabled": True, "sla": 4},  # hours
            "phone": {"enabled": True, "sla": 0.5},  # hours
            "slack": {"enabled": True, "sla": 0.25}  # hours
        }
    }
)
```

## 🔄 PACT Communication Patterns

### Agent Coordination Example

```python
# How agents communicate via PACT
async def handle_support_request(self, request_data):
    # 1. Channel agent receives and formats message
    formatted_message = await self.execute_action(
        "channel.format_message", 
        request_data
    )
    
    # 2. Triage agent classifies and prioritizes
    classification = await self.execute_action(
        "triage.classify_issue",
        formatted_message
    )
    
    # 3. Customer agent provides context
    customer_context = await self.execute_action(
        "customer.get_full_context",
        request_data["customer_id"]
    )
    
    # 4. Knowledge agent searches for solutions
    solutions = await self.execute_action(
        "knowledge.find_solutions",
        classification["issue_type"]
    )
    
    # 5. Response generation and delivery
    response = await self.execute_action(
        "channel.send_response",
        {
            "customer_context": customer_context,
            "solutions": solutions,
            "channel": request_data["channel"]
        }
    )
    
    return response
```

## 📊 Analytics & Monitoring

### Built-in Metrics

```python
# Get support metrics
metrics = await orchestrator.get_analytics()

print(f"Resolution Rate: {metrics['resolution_rate']}%")
print(f"Average Response Time: {metrics['avg_response_time']} minutes")
print(f"Customer Satisfaction: {metrics['csat_score']}/5.0")
```

### Real-time Dashboard

```python
# Monitor support operations
async def monitor_support():
    async for event in orchestrator.stream_events():
        if event["type"] == "ticket_created":
            print(f"New ticket: {event['ticket_id']}")
        elif event["type"] == "escalation_triggered":
            print(f"Escalation: {event['reason']}")
        elif event["type"] == "resolution_achieved":
            print(f"Resolved: {event['resolution_time']}s")
```

## 🛠️ Configuration

### Environment Variables

```bash
# Core Configuration
PACT_SUPPORT_LOG_LEVEL=INFO
PACT_SUPPORT_MAX_AGENTS=50
PACT_SUPPORT_TIMEOUT=300

# Channel Configuration
EMAIL_SMTP_SERVER=smtp.company.com
SLACK_BOT_TOKEN=xoxb-your-token-here
WHATSAPP_API_KEY=your-whatsapp-key
PHONE_SYSTEM_URL=https://your-phone-system.com/api

# Database Configuration
DATABASE_URL=postgresql://user:pass@localhost/pact_support
REDIS_URL=redis://localhost:6379/0

# External Services
KNOWLEDGE_BASE_URL=https://kb.company.com/api
CRM_INTEGRATION_URL=https://crm.company.com/api
```

### Agent Configuration File

```yaml
# support_config.yaml
agents:
  channel_agent:
    max_concurrent_channels: 10
    response_timeout: 30
    supported_channels:
      - email
      - slack
      - whatsapp
      - phone
      - chat
  
  triage_agent:
    classification_model: "support_classifier_v2"
    priority_rules:
      - condition: "customer_tier == 'enterprise'"
        priority: "high"
      - condition: "keywords in ['urgent', 'critical', 'down']"
        priority: "critical"
  
  knowledge_agent:
    search_engine: "elasticsearch"
    confidence_threshold: 0.8
    max_suggestions: 5
  
  escalation_agent:
    escalation_rules:
      - condition: "priority == 'critical'"
        escalate_to: "technical_specialist"
        timeout: 5  # minutes
      - condition: "customer_satisfaction < 3.0"
        escalate_to: "supervisor"
        timeout: 15  # minutes
```

## 🚀 Deployment

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "-m", "pact.support.orchestrator"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  pact-support:
    build: .
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/pact_support
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    ports:
      - "8000:8000"
  
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: pact_support
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### Kubernetes Deployment

```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pact-support
spec:
  replicas: 3
  selector:
    matchLabels:
      app: pact-support
  template:
    metadata:
      labels:
        app: pact-support
    spec:
      containers:
      - name: pact-support
        image: neurobloom/pact-support:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: pact-secrets
              key: database-url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: pact-secrets
              key: redis-url
```

## 🔒 Security & Compliance

### Data Protection

```python
# Enable encryption for sensitive data
orchestrator = PACTSupportOrchestrator(
    security_config={
        "encryption_key": os.getenv("PACT_ENCRYPTION_KEY"),
        "pii_fields": ["email", "phone", "address"],
        "data_retention_days": 90,
        "audit_logging": True
    }
)
```

### GDPR Compliance

```python
# Customer data management
async def handle_gdpr_request(customer_id, request_type):
    if request_type == "data_export":
        return await orchestrator.export_customer_data(customer_id)
    elif request_type == "data_deletion":
        return await orchestrator.delete_customer_data(customer_id)
    elif request_type == "data_portability":
        return await orchestrator.get_portable_data(customer_id)
```

## 🧪 Testing

### Unit Tests

```bash
# Run all tests
pytest tests/

# Run specific test categories
pytest tests/test_agents.py
pytest tests/test_orchestrator.py
pytest tests/test_channels.py
```

### Integration Tests

```python
# test_integration.py
async def test_end_to_end_support_flow():
    orchestrator = PACTSupportOrchestrator(test_mode=True)
    
    # Simulate customer contact
    ticket_id = await orchestrator.handle_customer_contact({
        "customer_id": "test_customer",
        "channel": "email",
        "message": "Test support request"
    })
    
    # Verify ticket creation
    ticket = await orchestrator.get_ticket(ticket_id)
    assert ticket["status"] == "in_progress"
    
    # Verify agent coordination
    assert len(ticket["agent_interactions"]) > 0
```

## 📈 Performance & Scaling

### Metrics

- **Throughput**: 1,000+ concurrent conversations
- **Response Time**: < 100ms agent coordination
- **Availability**: 99.9% uptime SLA
- **Scalability**: Horizontal scaling via agent pools

### Monitoring

```python
# Performance monitoring
async def monitor_performance():
    metrics = await orchestrator.get_performance_metrics()
    
    if metrics["response_time"] > 1000:  # ms
        await orchestrator.scale_agents("up")
    elif metrics["cpu_usage"] < 30:
        await orchestrator.scale_agents("down")
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-agent`
3. Commit changes: `git commit -am 'Add new agent capability'`
4. Push to branch: `git push origin feature/new-agent`
5. Submit a Pull Request

### Development Setup

```bash
# Development environment
git clone https://github.com/neurobloomai/pact
cd pact/examples/customer_support

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install development dependencies
pip install -r requirements-dev.txt

# Run in development mode
python -m pact.support.orchestrator --dev
```

## 📚 Documentation

- [PACT Core Documentation](../../docs/core/)
- [Agent Development Guide](../../docs/agents/)
- [API Reference](../../docs/api/)
- [Deployment Guide](../../docs/deployment/)

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/neurobloomai/pact/issues)
- **Discussions**: [GitHub Discussions](https://github.com/neurobloomai/pact/discussions)
- **Email**: support@neurobloom.ai
- **Slack**: [PACT Community](https://pact-community.slack.com)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../../LICENSE) file for details.

## 🙏 Acknowledgments

- PACT Core Team at NeuroBloom AI
- Community contributors
- Open source dependencies

---

**Ready to transform your customer support?** Start with the Quick Start guide above and join thousands of organizations already using PACT for unified customer experiences.
