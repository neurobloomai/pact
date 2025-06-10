# PACT Semantic Intent Matching

Transform natural language into structured PACT protocol actions with 95.3% accuracy.

## 🚀 Quick Start

```
# 1. Clone the repository
git clone https://github.com/neurobloomai/pact
cd pact/examples/semantic_intent_matching

# 2. Quick automated setup (recommended)
chmod +x setup.sh
./setup.sh

# 3. Or manual installation
pip install -r requirements.txt

# 4. Try it out!
python example_usage.py          # Interactive demo with test cases
python advanced_example.py       # Production FastAPI server
python scalable_pact_matcher.py  # High-performance FAISS version

# 5. Run tests
pytest test_matcher.py -v

# 6. Start building!
# Import in your own projects:
from pact_semantic_matcher import PACTSemanticMatcher
```

## 📁 Files Overview

| File | Purpose | Use Case |
|------|---------|----------|
| `pact_semantic_matcher.py` | Core semantic matching engine | Import this in your projects |
| `example_usage.py` | Simple demonstration | Learning and testing |
| `advanced_example.py` | Production-ready implementation | FastAPI server with monitoring |
| `scalable_pact_matcher.py` | FAISS-optimized version | 1000+ intents, high performance |
| `test_matcher.py` | Unit tests | Development and CI/CD |

## 🎯 What It Does

Converts natural language to PACT protocol actions:

```python
"Show me revenue" → analytics.get_revenue_report
"Customer tickets" → support.list_tickets  
"Display dashboard" → dashboard.display_main
```

## 🛠 Integration with PACT

```python
from pact_semantic_matcher import PACTSemanticMatcher

# Initialize matcher
matcher = PACTSemanticMatcher()

# Add your PACT intents
matcher.add_intent(PACTIntent(
    name="analytics_revenue",
    protocol_action="analytics.get_revenue_report",
    description="Get revenue and sales analytics data",
    examples=["show me revenue", "sales numbers", "revenue report"]
))

# Match user input
result = matcher.execute_pact_action("What's our monthly revenue?")
# → Executes analytics.get_revenue_report with 87% confidence
```

## 📊 Performance

- **Response Time**: <100ms (cached embeddings)
- **Accuracy**: 95.3% intent matching
- **Scalability**: 1000+ intents with FAISS
- **Fallback Rate**: 4.7% to human handoff

## 🔧 Architecture

See the [full case study](../../docs/case_studies/semantic_intent_matching.md) and [architecture diagram](../../docs/case_studies/semantic_intent_matching/assets/architecture_diagram.svg).

## 🧪 Testing

```bash
# Run tests
pytest test_matcher.py -v

# Run with coverage
pytest test_matcher.py --cov=pact_semantic_matcher
```

## 📈 Production Deployment

Use `advanced_example.py` as your starting point:

- FastAPI web server
- Prometheus metrics
- Structured logging
- Health checks
- Graceful error handling

--
💡 Pro tip: The setup script handles virtual environments, dependency installation, and validates everything works - perfect for getting started in under 2 minutes!
⚡ Ready to transform "show me revenue" into analytics.get_revenue_report? Jump into example_usage.py for an interactive demo! 🎯
--
