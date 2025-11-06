# HX ↔ AX Integration Architecture

**Document Location:** `pact/docs/architecture/hx_ax_integration.md`

**Purpose:** Architectural overview of how Human Experience (HX) and Agent Collaboration (AX) layers integrate through shared substrate primitives.

---

## Overview

PACT is built on two complementary layers:

- **AX (Agent Collaboration Layer):** Enables AI agents to coordinate with each other
- **HX (Human Experience Layer):** Enables AI systems to personalize and adapt to humans

These layers are not separate silos. They integrate through **shared substrate primitives** that provide foundation for both agent-to-agent and human-to-agent interaction.

---

## What is HX vs AX?

### AX Layer (Agent Collaboration)

**Audience:** AI agents coordinating with each other 🤖↔️🤖

**Purpose:** 
- Context sharing between agents
- Coherent handoffs during multi-agent workflows
- Distributed coordination protocols
- Maintaining consistency across agent interactions

**Interface:**
- APIs and protocols for agent-to-agent communication
- Structured data exchange formats
- Coordination state management

**Example Use Case:**
Agent A completes analysis → Agent B synthesizes findings → Agent C presents to user
- All agents share coherent narrative thread
- Context preserved across handoffs
- User experiences seamless collaboration

---

### HX Layer (Human Experience)

**Audience:** Humans interacting with AI systems 👤↔️🤖

**Purpose:**
- Personalization based on user preferences
- Adaptive communication tone and style
- Emotional awareness and response
- Maintaining relationship continuity over time

**Interface:**
- User-facing conversational interfaces
- Emotional state tracking and adaptation
- Preference learning and application

**Example Use Case:**
System remembers:
- User prefers morning reflections
- User gets stressed by data overload
- User values direct communication style

System adapts:
- Timing of interactions
- Amount of detail provided
- Communication approach

---

## Why Integration Matters

### Without Integration (Siloed Layers)

```
┌─────────────────┐
│   HX Layer      │  User gets personalized experience
│   (Isolated)    │  but agents underneath don't coordinate
└─────────────────┘

┌─────────────────┐
│   AX Layer      │  Agents coordinate well
│   (Isolated)    │  but user never sees/feels the coordination
└─────────────────┘
```

**Result:**
- User experiences lack depth (no relationship continuity)
- Agent coordination stays hidden (no transparency)
- Improvements in one layer don't benefit the other

---

### With Integration (Shared Substrate)

```
        ┌──────────────┐
        │   Human      │
        └──────┬───────┘
               │ HX Interface (personalization, adaptation)
               ↓
    ┌──────────────────────┐
    │  Shared Substrate    │ ← Story Keeper, context primitives
    │  (Narrative Layer)   │
    └──────────────────────┘
               ↑
               │ AX Interface (coordination, handoffs)
        ┌──────┴───────┐
        │   AI Agents  │
        └──────────────┘
```

**Result:**
- User benefits from agent coordination (transparency)
- Agents use user preferences (better coordination)
- System grows coherently across both layers
- **Circulatory improvement loop**

---

## Integration Patterns

### Pattern 1: Shared Substrate

**Core Concept:** Both HX and AX use the same underlying primitives, but with different interfaces.

**Example: Story Keeper as Substrate**

```
Story Keeper (Substrate)
    ↕️
├─ AX Interface: maintain agent coordination narrative
└─ HX Interface: surface relationship continuity to user
```

**Benefits:**
- Single source of truth for system narrative
- Changes in one layer visible to other layer
- Consistent context across all interactions
- Natural coordination between layers

---

### Pattern 2: Layered Translation

**Core Concept:** HX primitives build on top of AX substrate.

```
HX Primitives (memory, tone_adapt, attention)
       ↓ uses
AX Substrate (story_keeper, context_share)
       ↓ enables
Agent Coordination
```

**Example Flow:**
1. Story Keeper maintains narrative substrate (AX)
2. Memory primitive reads/writes to Story Keeper for user preferences (HX)
3. Agents use same Story Keeper for coordination (AX)
4. User sees both their preferences AND agent coordination (HX surface)

**Benefits:**
- Clear layering and separation of concerns
- HX extends AX without modifying it
- Substrate remains stable while HX adapts

---

### Pattern 3: Bidirectional Enhancement

**Core Concept:** Each layer improves the other through shared learning.

```
Human Interaction → HX Layer → Story Keeper Substrate
                                      ↓
                              (shared learning)
                                      ↓
Story Keeper Substrate → AX Layer → Better Agent Coordination
                                      ↓
                              (coordination visible)
                                      ↓
Better Agent Coordination → HX Layer → Enhanced User Experience
```

**Circular Flow:**
- Human teaches system → Story Keeper captures → Agents coordinate better
- Agents learn → Story Keeper updates → User experiences improvement
- Continuous circulatory enhancement

**Benefits:**
- System improves from both human input and agent learning
- Improvements compound over time
- Natural feedback loops between layers

---

## Substrate Primitives

These primitives serve as integration points between HX and AX:

### Story Keeper (Primary Substrate)

**Purpose:** Maintain narrative continuity across all interactions

**AX Use:** 
- Agents share coherent context across handoffs
- Coordination history preserved
- Multi-agent workflows maintain thread

**HX Use:**
- User relationship continuity over time
- System "remembers" interaction history
- Personalization based on narrative understanding

**Integration:** Same narrative substrate, different interfaces

---

### Context Management

**Purpose:** Track and share relevant context

**AX Use:**
- Inter-agent context sharing
- Coordination state management
- Distributed context synchronization

**HX Use:**
- User context awareness
- Situational adaptation
- Personalized context filtering

**Integration:** Shared context pool, layered access patterns

---

### Memory Systems

**Purpose:** Store and retrieve relevant information

**AX Use:**
- Agent coordination patterns
- Workflow templates
- Shared knowledge base

**HX Use:**
- User preferences and history
- Relationship memory
- Personalized recall

**Integration:** Unified memory substrate with tagged access (agent vs user facing)

---

## Design Principles

### 1. Substrate First

Build strong substrate primitives (like Story Keeper) that serve both layers naturally.

**Don't:**
- Build HX primitives in isolation
- Build AX primitives that can't extend to HX
- Create parallel systems for each layer

**Do:**
- Design substrate that both layers need
- Enable extension upward (AX → HX)
- Maintain single source of truth

---

### 2. Different Interfaces, Same Foundation

Each layer should have appropriate interfaces while sharing core substrate.

**AX Interface:** Structured, protocol-oriented, agent-focused  
**HX Interface:** Natural, adaptive, user-focused  
**Substrate:** Neutral, extensible, foundational

---

### 3. Transparency When Appropriate

HX layer should surface AX coordination when it helps the user understand system behavior.

**Example:**
User sees: "Claude analyzed the data patterns, GPT-4 synthesized insights"
- Transparency builds trust
- User understands multi-agent collaboration
- System behavior becomes less "magical" and more understandable

---

### 4. Privacy and Appropriate Filtering

Not all AX layer details should be visible at HX layer.

**Filter:**
- Show: High-level coordination flow
- Show: Which agents contributed what
- Hide: Low-level protocol details
- Hide: Internal agent communication minutiae

---

## Implementation Guidance

### For AX Developers

When building AX primitives, consider:

1. **Extensibility:** Can HX layer use this substrate?
2. **Exposure:** What should be visible to users?
3. **Documentation:** How would HX developers use this?

See: `pact-ax/primitives/[primitive]/extending_to_hx.md`

---

### For HX Developers

When building HX primitives, consider:

1. **Substrate Use:** Which AX primitives provide foundation?
2. **Reading:** What context do you need from AX layer?
3. **Writing:** What user data should inform AX coordination?

See: `pact-hx/primitives/[primitive]/using_ax_substrate.md`

---

## Architecture Diagram

```
┌─────────────────────────────────────────────┐
│           HX LAYER (User-Facing)            │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐    │
│  │  memory  │ │tone_adapt│ │attention │    │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘    │
│       │            │            │           │
└───────┼────────────┼────────────┼───────────┘
        │            │            │
        └────────────┼────────────┘
                     │
        ┌────────────▼────────────┐
        │    SHARED SUBSTRATE     │
        │  Story Keeper, Context, │
        │  Memory, Coordination   │
        └────────────┬────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
┌───────┼────────────┼────────────┼───────────┐
│       │            │            │           │
│  ┌────▼─────┐ ┌───▼──────┐ ┌──▼───────┐   │
│  │context_  │ │ handoff  │ │collab_   │   │
│  │share     │ │ protocol │ │intel     │   │
│  └──────────┘ └──────────┘ └──────────┘   │
│           AX LAYER (Agent-Facing)          │
└─────────────────────────────────────────────┘
```

---

## Example: Story Keeper Integration

### User Scenario

**Context:** User working with multiple AI agents for data analysis

**Interaction Flow:**

1. **User Request (HX):** "Analyze my sales data and explain trends"

2. **AX Layer Coordination:**
   - GPT-4 agent: Analyzes data patterns
   - Claude agent: Synthesizes insights
   - Story Keeper: Maintains coordination narrative

3. **HX Layer Experience:**
   - User sees: "GPT-4 found the patterns, I'm helping explain them"
   - System remembers: User prefers data-first explanations
   - System adapts: Starts with data, then insights

4. **Shared Learning:**
   - Story Keeper captures: User's preferred analysis style
   - AX agents learn: How to coordinate for this user
   - HX layer improves: Better personalization next time

**Result:**
- User experiences coherent collaboration
- Agents coordinate effectively
- System improves from interaction
- Both layers benefit from shared substrate

---

## Next Steps

For detailed implementation guidance:

- **AX Developers:** See `pact-ax/primitives/story_keeper/extending_to_hx.md`
- **HX Developers:** See `pact-hx/primitives/memory/using_ax_substrate.md`
- **Examples:** See `pact-integration/examples/`

---

## Key Takeaways

1. **HX and AX are complementary, not separate**
2. **Shared substrate enables natural integration**
3. **Both layers benefit from unified foundation**
4. **Integration creates circulatory improvement loops**
5. **Design substrate first, then layer-specific interfaces**

---

**Document Version:** 1.0  
**Last Updated:** November 2025  
**Related Documents:**
- `pact/docs/philosophy/substrate.md`
- `pact-ax/README.md`
- `pact-hx/README.md`
