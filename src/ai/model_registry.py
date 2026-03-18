# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# ============================================================
"""
Modell-Registry: Zentrale Quelle für Modell-IDs, Familien und Rollen-Mapping.
Liest aus .env; vollständige Tabelle siehe docs/02_ARCHITECTURE/AI_MODEL_CAPABILITIES.md.
"""

import os
from typing import Optional

# Aus .env (mit Fallbacks wie im Codebase)
def _env(key: str, default: str = "") -> str:
    return (os.getenv(key) or default).strip()


# --- Familien ---
GEMINI_DEV_AGENT = _env("GEMINI_DEV_AGENT_MODEL", "gemini-3.1-pro-preview")
GEMINI_HEAVY = _env("GEMINI_HEAVY_MODEL", "gemini-3.1-pro-preview")
ANTHROPIC_HEAVY = _env("ANTHROPIC_HEAVY_MODEL", "claude-opus-4-6")
ANTHROPIC_FAST = _env("ANTHROPIC_FAST_MODEL", "claude-sonnet-4-6")
OLLAMA_MODEL = _env("OLLAMA_MODEL", "llama3.2:1b")
OLLAMA_HEAVY = _env("OLLAMA_HEAVY_MODEL", "llama3.1:latest")
OLLAMA_HOST = _env("OLLAMA_HOST", "http://192.168.178.54:11434")
OLLAMA_LOCAL = _env("OLLAMA_LOCAL_HOST", "http://localhost:11434")
GEMINI_AUDIO = _env("GEMINI_AUDIO_MODEL", "gemini-3.1-pro-preview")

# Feste IDs aus Routes/Daemons
DICTATE_STT_MODEL = "gemini-2.5-flash"
VISION_DAEMON_MODEL = "gemini-2.0-flash-exp"
EMBED_MODEL = "gemini-embedding-001"


def get_model_for_role(role: str) -> Optional[str]:
    """Rollen-Mapping (siehe AI_MODEL_CAPABILITIES.md)."""
    m = {
        "triage": OLLAMA_MODEL,
        "heavy": GEMINI_HEAVY,
        "dictate_stt": DICTATE_STT_MODEL,
        "whatsapp_audio": GEMINI_AUDIO,
        "vision_daemon": VISION_DAEMON_MODEL,
        "embedding": EMBED_MODEL,
    }
    return m.get(role)


def get_ollama_base_url(layer: str = "scout") -> str:
    """Scout = OLLAMA_HOST, local = OLLAMA_LOCAL_HOST."""
    return OLLAMA_LOCAL if layer == "local" else OLLAMA_HOST
