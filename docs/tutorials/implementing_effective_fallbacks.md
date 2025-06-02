# 🧠 Implementing Effective Fallbacks in PACT

Fallbacks aren’t just error-handling — they’re the backbone of agent resilience.

This tutorial will guide you through designing and implementing layered fallback strategies in PACT:

## Overview

In PACT, fallback strategies allow agents to gracefully degrade intent handling through structured alternatives:

- `exact_match`
- `parameter_adaptation`
- `intent_approximation`
- `intent_decomposition`
- `graceful_failure`

## 1. Define Fallback Layers

```python
self.fallback_strategies = [
    self.exact_match,
    self.parameter_adaptation,
    self.intent_approximation,
    self.intent_decomposition,
    self.graceful_failure
]
```

## 2. Implement Specific Strategies

- Parameter adaptation: trim unsupported fields
- Intent approximation: map to simpler known intents
- Decomposition: split into multiple intents the agent can handle

## 3. Log and Respond Transparently

Provide metadata in fallback responses so downstream agents or users understand what was applied.

## 4. Test Fallbacks

Use malformed, incomplete, or unsupported intents to ensure proper fallback sequencing.

---

**Next:** Integrate fallback-aware response formatting and create traceable logs for decision auditability.
