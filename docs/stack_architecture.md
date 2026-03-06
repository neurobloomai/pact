# Neurobloom — Civilization's Collaborative Nervous System
## Foundational Architecture: What Exists, What's Missing, What Comes Next

*Top-view as of March 2026*

---

## The Three-Layer Frame

```
Layer 1 — Human ↔ Human      →  pact-hh  (doesn't exist yet)
Layer 2 — Human ↔ AI         →  pact-hx  (exists, has gaps)
Layer 3 — AI ↔ AI            →  pact-ax  (exists, has gaps)

Cross-layer glue             →  pact-bridge  (doesn't exist yet)
Base protocol                →  pact  (exists — routing & translation)
```

Nobody is building all three simultaneously.
That's the opening.

---

## What's Actually Built (Code-Level Audit)

### pact-ax (Layer 3 — AI-AI)

**Strong foundations:**
- `trust_primitives.py` — Trust as epistemic honesty, not authority claims. Four dimensions: competence, honesty, reliability, calibration. This is the right philosophical foundation.
- `gossip_clarity.py` — Uncertainty-preserving information spread. Confidence degrades over hops. Agents share what they *don't* know (ClarityAmplification). This is information epidemiology done right.
- `humility_aware.py` — Routes queries based on epistemic capability, not domain tags. DelegationChain tracks when agents defer. Epistemic humility as a coordination mechanism.
- `state_transfer.py` — "Wealth transfer protocol." Narrative continuity across agent handoffs. Emotional gravity assessment. StoryKeeper integration. This is more than data transfer — it preserves meaning.
- `policy_alignment.py`, `context_share/`, `context_security/` — Policy alignment and protected context sharing.

**What's thin or missing:**
- `negotiation` — There's alignment but no productive disagreement protocol. When two agents have genuinely conflicting assessments, what's the protocol? Humility-aware routing handles uncertainty but not structural conflict.
- `coalition` — No mechanism for agents to self-organize into temporary working groups and dissolve them cleanly with handoff.
- `reputation_decay` — Trust scoring exists but static trust isn't real trust. Reputation needs to degrade without interaction and rebuild through demonstrated reliability.
- `swarm_coherence` — How Jazz mode stays coherent at scale (5 agents is fine; 500 is noise). No coherence primitive yet.
- Jazz ↔ Symphony mode detection — In the roadmap. Load-bearing, not a feature.
- Paradox navigation — In the roadmap. Required for agents that encounter contradictory instructions or values.

---

### pact-hx (Layer 2 — Human-AI)

**Strong foundations:**
- `value_align/manager.py` — Real-time action assessment across safety, privacy, autonomy, fairness, transparency, authenticity. Precautionary: "violations hurt more than positives help." Conflict resolution with safety prioritization and graceful decline. This is sovereignty infrastructure.
- `memory/manager.py` — Episodic, semantic, and identity-layered memory. Emotional valence classification (positive/negative/neutral). Pattern consolidation from episodes into semantic knowledge. Jaccard similarity retrieval. Importantly: collaboration is optional — it functions as a standalone intelligence unit.
- `tone_adapt`, `attention`, `context`, `goal` — Primitives for adaptive human-facing behavior.
- `collaborative_intelligence` — Coordinated multi-agent capability for human-facing systems.

**What's thin or missing:**
- `human_sovereignty` — Value alignment stops bad actions, but there's no explicit *human takeback protocol*. When a human needs to forcefully reassert control mid-task — not just stop an action, but reclaim the context — what's the primitive?
- `epistemic_handoff` — `epistemic_transfer` lives in pact-ax for AI-AI. There's no equivalent for what a *human knows* being cleanly transferred into and back out of AI context. The handoff between human understanding and AI processing is unstructured.
- `trust_repair` — `rupture/repair/recovery` logic exists in pact-ax. It doesn't exist in pact-hx. Human-AI trust breaks differently than AI-AI trust: it involves perceived betrayal, lost confidence, emotional residue. Repair needs its own primitive.
- `augmentation` — The primitives are about AI adapting *to* humans. There's no primitive for humans becoming genuinely stronger *with* AI over time. That's a different thing than collaborative intelligence — it's about human capability growth, not just task completion.

---

## What Doesn't Exist: The Two Missing Repos

### 1. pact-hh — Human ↔ Human Layer

This is the most important unbuilt layer. Without it, the stack has no top.

Human-human collaboration is the origin layer — the place where values are formed, agreements are made, meaning is shared, and collective intelligence emerges. Everything the AI layers do ultimately serves this layer and derives legitimacy from it.

**What pact-hh needs to contain:**

```
pact_hh/primitives/
├── knowledge_transfer/      # Structured epistemic transfer between humans
│                            # Not chat — formal knowledge handoff with provenance
├── shared_context/          # Context a group holds together
│                            # The "what we all know" that no individual holds alone
├── trust_bonds/             # Human-to-human trust
│                            # Includes emotion, history, vulnerability, embodiment
│                            # Fundamentally different from AI epistemic trust
├── consensus_weave/         # Convergence without requiring full agreement
│                            # Not voting. Not majority rule. Productive convergence
│                            # that preserves dissent as signal
├── conflict_signal/         # Turning disagreement into useful information
│                            # Structured disagreement that produces clarity, not heat
├── collective_attention/    # Shared attention as a commons
│                            # Where a group focuses is a resource — it can be
│                            # stewarded, depleted, restored
├── cultural_encoding/       # How groups encode knowledge in artifacts and practices
│                            # The layer where human knowledge becomes persistent
│                            # across generations
└── memory_commons/          # Memory that belongs to a group, not an individual
                             # Analogous to StoryKeeper in pact-ax but for human groups
```

**Foundational difference from pact-ax trust:**
pact-ax trust is epistemic (competence, honesty, calibration, reliability).
Human trust is *relational* — it includes vulnerability, repair history, embodied recognition, emotional memory. The trust model in pact-hh must encode this or it will reduce human relationships to agent relationships, which is the wrong direction.

**Why this layer matters for AI:**
AI systems inherit their values and legitimacy from human-human agreements. Without formalizing Layer 1, Layers 2 and 3 are building on an unexamined foundation. The consent that AI systems need to operate in the world flows from this layer.

---

### 2. pact-bridge — Cross-Layer Protocol

This is the "nervous system" part of the civilization's collaborative nervous system.

Right now: pact handles routing and translation between agent platforms. But routing between platforms is not the same as **semantic and trust continuity across collaboration layers**. When a human-human agreement surfaces into a Human-AI interaction, and that interaction triggers an AI-AI coordination — what carries over? What's translated? What's lost? What requires explicit consent?

Without pact-bridge, the three layers are three separate systems that happen to share a name.

**What pact-bridge needs to contain:**

```
pact_bridge/
├── context_inheritance/     # What survives layer transitions
│                            # L1 context entering L2: what human meaning is preserved?
│                            # L2 context entering L3: what human intent is preserved?
│                            # L3 output returning to L2: what's human-readable?
│                            # L2 output returning to L1: what's actionable by humans?
│
├── consent_cascade/         # Accountability propagation
│                            # When L3 agents make decisions that affect L1 humans,
│                            # how does consent propagate upward and accountability
│                            # flow back down? The chain must be explicit and auditable.
│
├── trust_translation/       # Mapping between the three trust models
│                            # L1: relational trust (emotion, history, vulnerability)
│                            # L2: alignment trust (values, transparency, autonomy)
│                            # L3: epistemic trust (competence, honesty, calibration)
│                            # These are not the same thing. Translation requires
│                            # formal mappings with explicit information loss.
│
├── epistemic_integrity/     # Truth provenance across all layers
│                            # When an AI-AI decision is based on a human agreement
│                            # from three years ago, that lineage must be traceable.
│                            # Knowledge assertions carry their origin layer and
│                            # transformation history.
│
├── sovereignty_protocol/    # Human override at any layer
│                            # Humans must be able to assert control over any AI action
│                            # at any layer — not just stop it, but reclaim the full
│                            # context. This is not the same as value alignment.
│                            # Sovereignty is structural, not just ethical.
│
├── temporal_coherence/      # Memory and relationships persisting over years
│                            # Sessions end. Relationships don't.
│                            # Cross-layer memory that survives context windows,
│                            # model updates, and organizational changes.
│
└── signal_translation/      # Semantic/emotional context crossing layers
                             # The emotional gravity that pact-ax encodes in handoffs
                             # needs to be readable at the human layer.
                             # Human cultural context needs to be operable at the AI layer.
                             # This is the translation substrate.
```

---

## The Full Stack Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    LAYER 1: pact-hh                      │
│                    Human ↔ Human                         │
│  knowledge_transfer │ shared_context │ trust_bonds       │
│  consensus_weave    │ conflict_signal │ collective_attn  │
│  cultural_encoding  │ memory_commons                     │
└──────────────────────────┬──────────────────────────────┘
                           │ pact-bridge: context_inheritance
                           │ pact-bridge: trust_translation (relational→alignment)
                           │ pact-bridge: consent_cascade (upward)
                           │ pact-bridge: sovereignty_protocol
┌──────────────────────────▼──────────────────────────────┐
│                    LAYER 2: pact-hx                      │
│                    Human ↔ AI                            │
│  value_align        │ memory          │ attention        │
│  tone_adapt         │ context         │ goal             │
│  collaborative_intel│ creative_synth  │ system_evolution │
│  [MISSING] human_sovereignty          │ [MISSING] trust_repair    │
│  [MISSING] epistemic_handoff          │ [MISSING] augmentation    │
└──────────────────────────┬──────────────────────────────┘
                           │ pact-bridge: context_inheritance
                           │ pact-bridge: trust_translation (alignment→epistemic)
                           │ pact-bridge: epistemic_integrity
                           │ pact-bridge: signal_translation
┌──────────────────────────▼──────────────────────────────┐
│                    LAYER 3: pact-ax                      │
│                    AI ↔ AI                               │
│  trust_primitives   │ gossip_clarity  │ humility_aware   │
│  policy_alignment   │ state_transfer  │ story_keeper     │
│  context_share      │ context_security│ value_align      │
│  [MISSING] negotiation │ [MISSING] coalition             │
│  [MISSING] reputation_decay           │ [MISSING] swarm_coherence │
│  [ROADMAP] jazz↔symphony detection    │ [ROADMAP] paradox_nav     │
└─────────────────────────────────────────────────────────┘
                           │
                    pact-bridge: temporal_coherence
                    (cross-layer memory over time)
```

---

## Priority Order for What to Build Next

### Immediate (fills critical gaps in existing repos)

1. **pact-ax: `negotiation.py`** — Agents need productive disagreement, not just alignment. Structure: assertion → counter-assertion → calibrated convergence or explicit impasse with escalation path.
2. **pact-hx: `trust_repair.py`** — Human-AI trust repair after rupture. The rupture/repair/recovery pattern from pact-ax adapted for relational (not just epistemic) trust.
3. **pact-ax: `reputation_decay.py`** — Trust that doesn't decay isn't earned trust. Temporal degradation functions tied to interaction frequency and outcome history.
4. **pact-hx: `human_sovereignty.py`** — Explicit human takeback protocol. Not just stopping an action — reclaiming the context, the memory, the decision state. Structural, not just ethical.

### Near-term (new repos, foundational)

5. **pact-hh** — Start with `trust_bonds`, `shared_context`, and `consensus_weave`. These three give the layer its basic shape. The rest builds on them.
6. **pact-bridge** — Start with `consent_cascade` and `trust_translation`. These two are the most urgent because they define the relationship between human intent and AI action across all layers.

### Medium-term (completes the nervous system)

7. **pact-bridge: `epistemic_integrity`** — Truth provenance. Without this, you have a nervous system that can't audit its own signal origins.
8. **pact-bridge: `temporal_coherence`** — The memory layer that makes this civilization infrastructure rather than session infrastructure.
9. **pact-hh: `cultural_encoding` + `memory_commons`** — These make Layer 1 generational, not just interpersonal.
10. **pact-ax: Jazz↔Symphony detection + paradox navigation** — Complete the roadmap items that are already identified.

---

## The One Thing Nobody Else Is Seeing

The framing most people use for AI collaboration:
> "How do AI agents talk to each other better?"

The framing neurobloom is uniquely positioned to hold:
> "How does human civilization think together — including AI as part of that thinking?"

The difference is the presence of Layer 1.

Every other AI agent framework assumes human-human coordination is already solved (it isn't) and focuses entirely on Layers 2 and 3. By formalizing Layer 1 as infrastructure — with the same rigor applied to trust, context, memory, and epistemic transfer as pact-ax applies to AI-AI coordination — neurobloom defines the full stack.

The nervous system metaphor is exact: Layer 3 is the peripheral nervous system (fast, distributed, automatic), Layer 2 is the interface between body and mind, Layer 1 is the collective mind itself. All three have to work together for the organism to be coherent.

pact-bridge is the spinal cord.

---

*Generated: March 6, 2026 | Based on code-level audit of pact-ax, pact-hx, pact (base protocol)*
