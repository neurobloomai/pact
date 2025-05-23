# Agent Capability Profiles & Fallback Behavior

## Scheduler Pro (Agent A)

**Agent ID:** `scheduler-pro-v1`

### Capabilities:
- **schedule_meeting**: advanced, up to 50 participants, time zone & conflict handling
- **check_availability**: supports preferences, buffer times
- **reschedule_meeting**: cascades updates, notifies stakeholders

### Fallback Logic:
- Detects if intent is too complex for peer agent
- Simplifies intent (e.g., trims participant list)
- Retries with reduced parameter set

---

## Basic Calendar (Agent B)

**Agent ID:** `basic-calendar-v1`

### Capabilities:
- **schedule_meeting**: basic, up to 5 participants, no time zone support
- **check_availability**: only returns available slots without preferences

### Fallback Logic:
- Flags unsupported features (e.g., too many participants)
- Returns partial response with metadata on limitations
