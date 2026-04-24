# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================
"""
Modell-Registry: Zentrale Quelle fuer Modell-IDs, Familien und Rollen-Mapping.
Stand: April 2026
"""

import os
from typing import Optional

def _env(key: str, default: str = "") -> str:
    return (os.getenv(key) or default).strip()


# ── Gemini 3 / 3.1 Generation (Status Quo 2026) ──
GEMINI_HEAVY = _env("GEMINI_HEAVY_MODEL", "gemini-3.1-pro-preview")
GEMINI_FLASH = _env("GEMINI_FLASH_MODEL", "gemini-3.1-flash-preview")
GEMINI_FLASH_LITE = _env("GEMINI_FLASH_LITE_MODEL", "gemini-3.1-flash-lite-preview")
GEMINI_TRIAGE = "gemini-3.1-flash-lite-preview" # Missing constant

# ── Claude 4.6 Generation ──
ANTHROPIC_HEAVY = _env("ANTHROPIC_HEAVY_MODEL", "claude-opus-4-6")
ANTHROPIC_FAST = _env("ANTHROPIC_FAST_MODEL", "claude-sonnet-4-6")

# ── Gemma 4 (Ollama / Local) ──
GEMMA_TRIAGE = "gemma4:e2b"
GEMMA_REASONING = "gemma4:31b"

# ── Rollen-Mapping (Axiom A7) ──
STABLE_HEAVY = GEMINI_HEAVY
STABLE_FAST = GEMINI_FLASH


def get_model_for_role(role: str) -> Optional[str]:
    """Rollen-Mapping: Jede Rolle → optimales Modell."""
    m = {
        "heavy": STABLE_HEAVY,
        "flash": STABLE_FAST,
        "triage": GEMMA_TRIAGE,
        "dev_agent": GEMINI_FLASH,
        "wiki_expert": "claude-code-local",
        "deep_research": "deep-research-pro-preview"
    }
    return m.get(role)
