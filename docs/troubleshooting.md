# 🛠️ Troubleshooting Playbook

This guide helps you diagnose and resolve common issues when working with the PACT Protocol and agent communication workflows.

---

## 🧩 Common Integration Issues

### 1. Missing Capabilities
**Symptom**: Agent receives an intent it cannot handle.  
**Solution**: 
- Ensure `register_capability()` is used properly.
- Validate agent’s capability manifest via `/capabilities` endpoint.

### 2. Fallbacks Not Triggering
**Symptom**: Unsupported intent fails outright.  
**Solution**: 
- Verify `fallback_strategies` are properly defined.
- Log fallback application stages to confirm sequencing.

### 3. Intent Schema Validation Errors
**Symptom**: JSON validation failures.  
**Solution**: 
- Check schema definition and required fields.
- Use `PACTMessage.validate()` before processing.

---

## 📜 Debug Logging Strategies

- Enable structured logs with timestamps and intent metadata.
- Track each phase:
  - Incoming request
  - Capability match result
  - Fallback steps applied
  - Final response generated
- Use UUIDs to correlate logs across agents.

Example:
```json
{
  "timestamp": "2025-08-01T12:00:00Z",
  "intent_id": "abc-123",
  "agent": "scheduler-pro",
  "action": "schedule_meeting",
  "fallback_applied": "parameter_adaptation"
}
```

---

## 🚀 Performance Optimization Tips

- **Use async HTTP**: Consider `FastAPI` + `async` endpoints for non-blocking I/O.
- **Limit logging in production**: Use debug-level logs during dev only.
- **Optimize fallback chain**: Short-circuit once a valid response is found.
- **Scale agents horizontally**: Agents are stateless and can be deployed in parallel containers.
- **Profile negotiation time**: Use timing metrics to improve latency.

---

For persistent issues, please check:
- [GitHub Issues](https://github.com/neurobloomai/pact/issues)
- Reach out via our [community Slack](https://neurobloom.ai/slack) or email support.

