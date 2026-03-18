# feat: dynamic intent mapping registry (closes #2)

## Problem

All intent mappings were hardcoded in two separate places:

- `pact_protocol/intent_translator_api.py` — a 2-entry `intent_mapping` dict
- `pact_protocol/pact_core.py` — `FallbackProcessor.intent_approximation()` and
  `FallbackProcessor.intent_decomposition()` both embedded dicts inline

Adding or changing any intent required editing Python source, redeploying, and
knowing where each mapping lived.

## Solution

### New file: `pact_protocol/intent_registry.py`

Introduces `IntentRegistry` — a single source of truth for all intent mappings.

**Loading order (no config needed to run):**
1. Explicit path argument
2. `PACT_REGISTRY_PATH` environment variable
3. Auto-discover `intent_registry.{json,yaml,yml}` next to the module
4. Built-in defaults (logs a warning)

**Key methods:**

| Method | Description |
|--------|-------------|
| `IntentRegistry.load(path?)` | Factory — auto-discovers or loads from path |
| `.translate(intent)` | Map an intent; returns original if no mapping |
| `.decompose(intent)` | Return sub-intent list for compound intents |
| `.register(src, tgt)` | Add/overwrite a mapping at runtime |
| `.reload()` | Hot-reload from source file without restart |

### Updated: `pact_protocol/intent_translator_api.py`

- Removed hardcoded `intent_mapping` dict
- Registry injected as a cached singleton (`lru_cache`)
- Two new utility endpoints added:
  - `GET  /registry` — inspect active mappings (observability)
  - `POST /registry/reload` — hot-reload config without server restart
- `payload.intent` now validated — returns 422 if missing

### Updated: `pact_protocol/pact_core.py`

- Removed hardcoded `approximations` dict from `FallbackProcessor.intent_approximation()`
- Removed hardcoded decomposition logic from `FallbackProcessor.intent_decomposition()`
- Both strategies now delegate to `IntentRegistry`:
  - `registry_approximation()` — calls `registry.translate()`
  - `registry_decomposition()` — calls `registry.decompose()`
- `PACTProcessor` accepts an optional `registry=` argument (testability)

### New files: sample registry configs

- `pact_protocol/intent_registry.json` — 10 mappings + 3 decompositions
- `pact_protocol/intent_registry.yaml` — same content, YAML format

## Testing

```python
from pact_protocol.intent_registry import IntentRegistry

# From file
reg = IntentRegistry.load("pact_protocol/intent_registry.json")
assert reg.translate("book_meeting") == "schedule_meeting"
assert reg.translate("unknown") == "unknown"          # passthrough
assert reg.decompose("organize_event") == ["schedule_meeting", "send_invites"]

# Programmatic (tests / CI)
reg = IntentRegistry({"foo": "bar"})
assert reg.translate("foo") == "bar"

# Env var
import os
os.environ["PACT_REGISTRY_PATH"] = "path/to/custom_registry.json"
reg = IntentRegistry.load()   # picks up env var automatically

# Hot-reload
reg.reload()
```

## Migration

No breaking changes. Existing callers of `POST /translate` work identically.
The response body now includes `registry_source` and `payload.original_intent`
as additive fields.

Deployments using Docker/Kubernetes can mount a custom `intent_registry.json`
as a ConfigMap volume and point `PACT_REGISTRY_PATH` at it to manage mappings
independently of the application image.
