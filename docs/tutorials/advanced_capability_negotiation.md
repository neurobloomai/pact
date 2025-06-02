# 🔁 Advanced Capability Negotiation in PACT

In complex multi-agent environments, not all capabilities are equal — and not all intents are static.

This guide walks through building dynamic, intent-aware capability negotiation.

## 1. Capability Metadata

Each capability can expose metadata like:

```json
{
  "complexity": "basic",
  "max_participants": 5,
  "timezone_support": false
}
```

Use this to rank agents or adapt intent structure.

## 2. Intent-to-Capability Matching

Implement smart matching logic based on intent parameters and capability constraints.

```python
def match_intent_to_capability(intent):
    # Score compatibility using parameters
    # Fallback to similar capabilities with lower requirements
```

## 3. Parameter Negotiation

Auto-map or simplify parameters to improve cross-agent compatibility:

```python
def negotiate_parameters(intent, capability):
    # Strip unsupported params, apply type casting, etc.
```

## 4. Intent Routing via Metadata

Allow routing based on constraints:

- Latency
- Confidence score
- System load

---

By mastering negotiation, PACT agents can dynamically adapt to real-world complexity without brittle hardcoding.
