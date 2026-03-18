"""
intent_registry.py — Dynamic Intent Mapping Registry for PACT

Replaces hardcoded intent dicts with a registry that loads from:
  - JSON file  (e.g. intent_registry.json)
  - YAML file  (e.g. intent_registry.yaml)
  - Python dict (programmatic / test use)
  - Environment variable PACT_REGISTRY_PATH pointing to either format

Usage:
    # Auto-discover config next to this file:
    registry = IntentRegistry.load()

    # Explicit path:
    registry = IntentRegistry.load("path/to/intent_registry.json")

    # Programmatic (useful in tests):
    registry = IntentRegistry({"book_meeting": "schedule_meeting"})

    # Translate an intent:
    translated = registry.translate("book_meeting")   # → "schedule_meeting"
    translated = registry.translate("unknown_intent") # → "unknown_intent" (passthrough)
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Sentinel defaults — kept minimal; real mappings should live in config files
# ---------------------------------------------------------------------------
_DEFAULT_MAPPINGS: Dict[str, str] = {
    "check_order_status": "order.lookup",
    "reset_password": "user.reset_password",
    "book_meeting": "schedule_meeting",
    "find_slot": "check_availability",
}

_DEFAULT_DECOMPOSITIONS: Dict[str, List[str]] = {
    "organize_event": ["schedule_meeting", "send_invites"],
}

# Env var that can point to a custom registry file
_ENV_KEY = "PACT_REGISTRY_PATH"

# File names we search for automatically (in order of preference)
_AUTO_DISCOVER_NAMES = [
    "intent_registry.json",
    "intent_registry.yaml",
    "intent_registry.yml",
]


class RegistryLoadError(RuntimeError):
    """Raised when the registry file cannot be parsed."""


class IntentRegistry:
    """
    A dynamic, reloadable registry for PACT intent mappings.

    Attributes
    ----------
    mappings : Dict[str, str]
        Flat intent → translated-intent map.
    decompositions : Dict[str, List[str]]
        Compound-intent → list-of-sub-intents map.
    source : Optional[Path]
        File the registry was loaded from, if any.
    """

    def __init__(
        self,
        mappings: Optional[Dict[str, str]] = None,
        decompositions: Optional[Dict[str, List[str]]] = None,
        source: Optional[Path] = None,
    ) -> None:
        self.mappings: Dict[str, str] = mappings or {}
        self.decompositions: Dict[str, List[str]] = decompositions or {}
        self.source: Optional[Path] = source

    # ------------------------------------------------------------------
    # Factory / loading
    # ------------------------------------------------------------------

    @classmethod
    def load(cls, path: Optional[str | Path] = None) -> "IntentRegistry":
        """
        Load a registry from *path*.

        Resolution order when *path* is None:
          1. Environment variable ``PACT_REGISTRY_PATH``
          2. Auto-discover ``intent_registry.{json,yaml,yml}`` next to this module
          3. Built-in defaults (minimal; logs a warning)

        Parameters
        ----------
        path:
            Explicit file path (JSON or YAML).  Pass ``None`` for auto-discovery.

        Returns
        -------
        IntentRegistry
        """
        resolved = cls._resolve_path(path)

        if resolved is None:
            logger.warning(
                "No intent registry file found. "
                "Using built-in defaults. "
                "Set PACT_REGISTRY_PATH or create intent_registry.json to customise."
            )
            return cls(
                mappings=dict(_DEFAULT_MAPPINGS),
                decompositions=dict(_DEFAULT_DECOMPOSITIONS),
            )

        logger.info("Loading intent registry from %s", resolved)
        return cls._load_file(resolved)

    @classmethod
    def _resolve_path(cls, explicit: Optional[str | Path]) -> Optional[Path]:
        # 1. Explicit argument
        if explicit is not None:
            p = Path(explicit)
            if not p.exists():
                raise FileNotFoundError(f"Intent registry file not found: {p}")
            return p

        # 2. Env var
        env_path = os.environ.get(_ENV_KEY)
        if env_path:
            p = Path(env_path)
            if not p.exists():
                raise FileNotFoundError(
                    f"PACT_REGISTRY_PATH points to a missing file: {p}"
                )
            return p

        # 3. Auto-discover alongside this module
        module_dir = Path(__file__).parent
        for name in _AUTO_DISCOVER_NAMES:
            candidate = module_dir / name
            if candidate.exists():
                return candidate

        return None

    @classmethod
    def _load_file(cls, path: Path) -> "IntentRegistry":
        suffix = path.suffix.lower()
        try:
            if suffix == ".json":
                data = cls._read_json(path)
            elif suffix in {".yaml", ".yml"}:
                data = cls._read_yaml(path)
            else:
                raise RegistryLoadError(
                    f"Unsupported registry file format: {suffix}. "
                    "Use .json, .yaml, or .yml"
                )
        except (json.JSONDecodeError, Exception) as exc:
            raise RegistryLoadError(
                f"Failed to parse registry file {path}: {exc}"
            ) from exc

        mappings = data.get("mappings", {})
        decompositions = data.get("decompositions", {})

        if not isinstance(mappings, dict):
            raise RegistryLoadError("'mappings' must be a JSON object / YAML mapping.")
        if not isinstance(decompositions, dict):
            raise RegistryLoadError(
                "'decompositions' must be a JSON object / YAML mapping."
            )

        logger.info(
            "Loaded %d mappings and %d decompositions from %s",
            len(mappings),
            len(decompositions),
            path,
        )
        return cls(mappings=mappings, decompositions=decompositions, source=path)

    @staticmethod
    def _read_json(path: Path) -> dict:
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)

    @staticmethod
    def _read_yaml(path: Path) -> dict:
        try:
            import yaml  # optional dependency
        except ImportError as exc:
            raise RegistryLoadError(
                "PyYAML is required to load YAML registry files. "
                "Install it with: pip install pyyaml"
            ) from exc
        with path.open("r", encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def translate(self, intent: str) -> str:
        """
        Return the mapped intent for *intent*, or *intent* itself if no
        mapping exists (transparent passthrough).

        Parameters
        ----------
        intent : str
            The source intent string to translate.

        Returns
        -------
        str
            Translated intent name.
        """
        return self.mappings.get(intent, intent)

    def decompose(self, intent: str) -> Optional[List[str]]:
        """
        Return the sub-intent list for a compound *intent*, or ``None``
        if no decomposition is registered.
        """
        return self.decompositions.get(intent)

    def register(self, source_intent: str, target_intent: str) -> None:
        """
        Add or overwrite a single mapping at runtime (e.g. in tests).

        Parameters
        ----------
        source_intent : str
        target_intent : str
        """
        self.mappings[source_intent] = target_intent
        logger.debug("Registered mapping: %s → %s", source_intent, target_intent)

    def register_decomposition(
        self, compound_intent: str, sub_intents: List[str]
    ) -> None:
        """Register a compound intent decomposition at runtime."""
        self.decompositions[compound_intent] = sub_intents

    def reload(self) -> None:
        """
        Reload mappings from the original source file (if any).

        Useful for hot-reloading config without restarting the server.
        Raises ``RegistryLoadError`` if the source is unavailable.
        """
        if self.source is None:
            logger.warning(
                "Registry has no source file — reload is a no-op. "
                "Use register() to add mappings programmatically."
            )
            return

        refreshed = self._load_file(self.source)
        self.mappings = refreshed.mappings
        self.decompositions = refreshed.decompositions
        logger.info("Registry reloaded from %s", self.source)

    def __len__(self) -> int:
        return len(self.mappings)

    def __repr__(self) -> str:
        src = str(self.source) if self.source else "in-memory"
        return (
            f"IntentRegistry(mappings={len(self.mappings)}, "
            f"decompositions={len(self.decompositions)}, source={src!r})"
        )
