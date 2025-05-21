# PACT Intent Schema Documentation

Welcome to the **PACT (Protocol for Agent Collaboration & Transfer)** Intent Schema. This document provides a structured overview of the communication framework between intelligent agents using PACT.

---

## 📌 Schema Overview

```json
{
  "version": "0.1.0",
  "schema": {
    "schema_id": "PACT-INTENT-SCHEMA",
    "schema_version": "1.0.0",
    "last_updated": "2025-07-18T09:00:00Z"
  },
  "intent": {
    "action": "create",
    "parameters": {},
    "context": {}
  },
  "metadata": {
    "sender": {
      "agent_id": "agent_calendar",
      "timestamp": "2025-07-18T09:00:00Z"
    },
    "priority": "normal",
    "idempotency_key": "a1b2c3d4",
    "auth": {
      "signature": "string (JWT or HMAC)",
      "trust_level": "high | medium | low"
    }
  }
}
```

---

## ✅ Required Fields
- `intent.action`: must be one of `create`, `retrieve`, `update`, `delete`, `query`, `respond`
- `metadata.sender.agent_id`: must be a valid string
- `metadata.sender.timestamp`: must be a valid ISO 8601 timestamp

---

## 🔐 Authentication & Trust
Each request includes:
- A signed `auth.signature` (JWT or HMAC)
- A declared `trust_level` (e.g., high, medium, low)

---

## ❗ Error Handling Format

```json
{
  "status": "error",
  "code": "ERR_INVALID_INTENT",
  "message": "Intent action not supported",
  "details": "Additional debugging context here."
}
```

### Common Error Codes
| Code                  | Description                            |
|-----------------------|----------------------------------------|
| ERR_INVALID_INTENT    | Intent action not recognized           |
| ERR_MISSING_PARAMETERS| Required parameters are missing        |
| ERR_UNAUTHORIZED      | Signature invalid or trust level too low |
| ERR_TIMEOUT           | Target agent did not respond in time   |

---

## 🚦 Routing Logic
- Intent actions are mapped to handler agents.
- Fallback to default handler if no match.

---

## 🧠 Agent Capability Registration
Each agent registers:
- Supported actions (e.g., `create`, `update`)
- Required context fields

```json
{
  "agent_id": "agent_calendar",
  "supported_actions": ["create", "update", "delete"],
  "context_requirements": ["origin", "session_id"]
}
```

---

## 📡 Agent Discovery
Agents send heartbeat messages:
```json
{
  "agent_id": "string",
  "timestamp": "ISO 8601 format",
  "status": "active | inactive | degraded"
}
```

---

## 🧪 Testing Harness
Supports:
- Mock agent responses
- Pre-defined test cases

```json
{
  "intent": "create",
  "parameters": {
    "title": "Team Standup",
    "start_time": "2025-07-18T09:30:00Z"
  },
  "expected_response": "Event created successfully."
}
```

---

## 📘 API Endpoints

| Path                  | Method | Description                          |
|-----------------------|--------|--------------------------------------|
| `/intent/send`        | POST   | Send an intent to an agent           |
| `/agents/heartbeat`   | POST   | Report agent status to registry      |

---

## 📅 Calendar Scheduling Example

```json
{
  "version": "0.1.0",
  "intent": {
    "action": "create",
    "parameters": {
      "title": "Project Sync",
      "start_time": "2025-07-18T10:00:00Z",
      "duration_minutes": 30,
      "participants": ["user_123", "user_456"]
    },
    "context": {
      "origin": "calendar_ui",
      "session_id": "xyz789"
    }
  },
  "metadata": {
    "sender": {
      "agent_id": "agent_calendar",
      "timestamp": "2025-07-18T08:55:00Z"
    },
    "priority": "high",
    "idempotency_key": "event_create_001",
    "auth": {
      "signature": "abc.def.ghi",
      "trust_level": "high"
    }
  }
}
```

---

> Built with 💡 by NeuroBloom.ai using PACT
