"""
PACT Protocol

An open, modular framework for AI agent collaboration,
intent translation, fallback negotiation, and capability coordination.

Author: Neurobloom.ai
"""

__version__ = "0.1.0"

# Optional: lightweight logger setup
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Console handler (used if not integrated into larger system)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter('[PACT] %(levelname)s: %(message)s'))
    logger.addHandler(ch)

# Safe imports — only bring in what you need
try:
    from .pact_core import AgentIntentTranslator, CapabilityNegotiator
    from .pact_demo import run_demo_server
except ImportError as e:
    logger.warning(f"Optional module import failed: {e}")
