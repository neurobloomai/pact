# PACT — Persistent Agentic Context Trust

> *MCP defines how agents communicate. PACT verifies whether those communications can be trusted — across time, across handoffs, across systems.*

[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Status: Early Stage](https://img.shields.io/badge/status-early--stage-orange.svg)]()

---

## The Problem

BigTech built the compute layer. The model layer. The protocol layer.

Nobody built the **trust layer** — not because they forgot, because they assumed it existed.

When an AI agent acts on your behalf — across sessions, across systems, across handoffs — who verifies it's still behaving as authorized? Who catches the drift between what was approved and what is actually happening?

Policy engines catch rule violations. They don't catch **behavioral drift over time.**

That gap is what PACT addresses.

---

## What PACT Is

PACT is **trust infrastructure for AI agent deployments.**

Not a platform. Not an agent framework. Not a competitor to MCP or A2A.

PACT is the layer that sits between agents and the systems they operate on — measuring, recording, and verifying relational continuity over time.

Think TCP/IP moved packets. HTTPS verified the connection could be trusted. MCP moves agent context. **PACT verifies the agent carrying that context is still who it claimed to be — and behaving as authorized.**

---

## Core Concepts

### Relational Intelligence (RI)
The capacity of an agent — or a system of agents — to maintain consistent, authorized behavior across time and context. RI is the engine.

### Relational Quality (RQ)
The measurable output of that capacity. RQ is the currency. It answers: *how trustworthy has this agent demonstrated itself to be, over what conditions, over what duration?*

### PACT as Infrastructure
PACT converts RI into RQ. It is the accounting system that makes trust measurable — not as a moment, but as a track record.

> *Safety is a moment. Trust is duration.*

---

## The Trust Gap PACT Fills

| Layer | What It Does | Who Built It |
|---|---|---|
| Compute | Run models at scale | Cloud providers |
| Model | Reason, generate, act | AI labs |
| Protocol (MCP) | Agent-to-system communication | Anthropic |
| Orchestration (A2A) | Agent-to-agent coordination | Google |
| **Trust (PACT)** | **Verify agent behavior over time** | **NeuroBloom** |

---

## PACT-AX: The Entry Point

**PACT-AX** is a relational security proxy layer sitting between MCP clients and servers.

It detects what policy engines miss: behavioral drift that accumulates across sessions without triggering any single rule violation.

### The Authority Boundary Check

The first PACT-AX service offering. Three questions asked on every agent interaction:

1. **Is this agent acting within its authorized scope?**
2. **Has its behavior drifted from its established baseline?**
3. **Has a rupture occurred — and if so, has it been acknowledged and recovered from?**

No existing system answers all three. Most answer none.

---

## How It Works

PACT uses a three-layer trust measurement architecture:

```
SMA (StoryKeeper)        — Long baseline. What has this agent consistently been?
EMA (Rupture Detection)  — Recency-sensitive. What just changed?
WMA (Trust Score)        — Weighted judgment. What does the pattern say?

SMA + EMA + WMA → RI → RQ
```

**StoryKeeper** maintains the long behavioral baseline — the agent's relational history.

**Rupture Detection (RLP-0)** flags when recent behavior deviates from that baseline. Recency-sensitive by design — because drift that just started is more dangerous than drift that resolved.

**Trust Score** synthesizes both into a queryable, portable signal: this agent's demonstrated trustworthiness, weighted by recency and severity.

---

## Stable Packets

The portable primitive that makes trust transferable.

When an agent moves between systems — session to session, handoff to handoff — its trust state travels with it as a **Stable Packet**: a verified, signed record of behavioral history that any receiving system can verify.

> *Stablecoins made value portable across financial systems. Stable Packets make trust portable across agent systems.*

A Stable Packet is not a credential. It's a track record.

---

## RLP-0: Relational Ledger Protocol

The state primitive underlying PACT.

Three-layer design:
- **Semantic layer** — what was intended
- **Protocol layer** — what was communicated
- **Storage layer** — what was recorded and persisted

RLP-0's design philosophy: **serve, not resolve.** It maintains relational tensions rather than collapsing them into false certainty. The ledger records drift — it doesn't adjudicate it.

---

## What PACT Is Not

- Not an agent framework — PACT doesn't build agents
- Not a policy engine — PACT doesn't write rules
- Not a competitor to MCP — PACT sits on top of MCP
- Not a monitoring dashboard — PACT is infrastructure, not tooling built on infrastructure
- Not a product that pivots — PACT is substrate

> *Substrate doesn't pivot.*

---

## Current Status

Early stage. PACT-AX is the active development focus.

The infrastructure being built:
- RLP-0 state primitive
- Authority Boundary Check (v0.1)
- StoryKeeper baseline architecture
- Rupture Detection layer
- Trust Score query interface

PACT-HX (human experience layer) is deprioritized. PACT-AX is the entry point.

---

## Who This Is For

**Security teams** deploying AI agents and asking: *how do we know if an agent starts behaving outside its authorized boundary?*

**Platform builders** deploying MCP-native architectures and asking: *what does post-deployment accountability look like?*

**GovCon and enterprise** asking: *how do we demonstrate that our AI systems are behaving as approved — not just at deployment, but over time?*

---

## The Canonical Framing

PACT is to AI agent trust what:
- **TCP/IP** is to packet routing
- **GAAP** is to financial reporting
- **SWIFT** is to value transfer

Invisible substrate. Completing infrastructure. The layer that makes everything built on top of it trustworthy — not by controlling it, but by accounting for it.

---

## Repository Structure

```
pact/
├── pact_protocol/       # Core PACT protocol implementation
├── spec/                # Protocol specification
├── schemas/             # RLP-0 and Stable Packet schemas
├── examples/            # Reference implementations
├── docs/                # Documentation
└── tests/               # Test suite
```

---

## Contributing

PACT is open source. The trust layer for AI infrastructure should be community-owned — not vendor-controlled.

If you're working on:
- MCP deployments and thinking about post-deployment accountability
- Multi-agent coordination and behavioral verification
- AI governance and authority boundary enforcement

We want to hear from you.

**GitHub:** [github.com/neurobloomai/pact](https://github.com/neurobloomai/pact)  
**Email:** [support@neurobloom.ai](mailto:support@neurobloom.ai)  
**LinkedIn:** [NeuroBloom AI](https://www.linkedin.com/company/neurobloomdotai/)

---

## License

MIT License — see [LICENSE](./LICENSE) for details.

Open protocols. Community ownership. Infrastructure that endures.

---

*Built by [NeuroBloom AI](https://www.neurobloom.ai)*  
*The trust layer BigTech assumed existed. We're building it.*
