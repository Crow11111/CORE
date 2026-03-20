# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# ============================================================
"""
Modell-Registry: Zentrale Quelle fuer Modell-IDs, Familien und Rollen-Mapping.

Vollstaendige Matrix (Maerz 2026):
  Gemini 3 Pro             — Heavy Reasoning, Hauptagent
  Gemini 3 Flash           — Vision Daemon, schnelle Analyse
  gemini-3.1-flash-lite    — Triage (ultraschnell, ersetzt Ollama-Triage)
  gemini-2.5-pro           — Diktat-STT Deep
  gemini-2.5-pro-preview-tts — TTS (hoehere Qualitaet)
  gemini-2.5-computer-use  — Desktop-Automation (Cursor/ydotool-Ersatz)
  gemini-embedding-2       — Multimodale Embeddings (Text/Bild/Audio/Video/PDF → 3072 dim)
  gemini-robotics-er-1.5   — Physischer Raum, Sensordaten-Interpretation
  deep-research-pro        — Deep Research, Multi-Agent Reasoning
"""

import os
from typing import Optional

def _env(key: str, default: str = "") -> str:
    return (os.getenv(key) or default).strip()


# ── Gemini 3 Generation (neueste) ──
GEMINI_HEAVY = _env("GEMINI_HEAVY_MODEL", "gemini-3.1-pro-preview")
GEMINI_FLASH = _env("GEMINI_FLASH_MODEL", "gemini-3-flash-preview")
GEMINI_DEV_AGENT = _env("GEMINI_DEV_AGENT_MODEL", "gemini-3.1-pro-preview")

# ── Gemini 3.1 ──
GEMINI_TRIAGE = _env("GEMINI_TRIAGE_MODEL", "gemini-3.1-flash-lite-preview")

# ── Gemini 2.5 (spezialisiert) ──
DICTATE_STT_MODEL = _env("GEMINI_DICTATE_STT_MODEL", "gemini-2.5-pro")
DICTATE_STT_LIVE_MODEL = _env("GEMINI_DICTATE_STT_LIVE_MODEL", "gemini-3.1-flash-lite-preview")
GEMINI_TTS_MODEL = _env("GEMINI_TTS_MODEL", "gemini-2.5-flash-preview-tts")
GEMINI_COMPUTER_USE = _env("GEMINI_COMPUTER_USE_MODEL", "gemini-2.5-computer-use-preview")

# ── Embedding: Gemini Embedding 2 — nativ multimodal (Text/Bild/Audio/Video/PDF → 3072 dim) ──
EMBED_MODEL = _env("GEMINI_EMBED_MODEL", "gemini-embedding-2-preview")

# ── Spezialmodelle ──
GEMINI_ROBOTICS = _env("GEMINI_ROBOTICS_MODEL", "gemini-robotics-er-1.5-preview")
GEMINI_DEEP_RESEARCH = _env("GEMINI_DEEP_RESEARCH_MODEL", "deep-research-pro-preview")
GEMINI_AUDIO = _env("GEMINI_AUDIO_MODEL", "gemini-3-flash-preview")
VOICE_BRIDGE_MODEL = _env("GEMINI_VOICE_BRIDGE_MODEL", "gemini-3-flash-preview")

# ── Vision ──
VISION_DAEMON_MODEL = _env("GEMINI_VISION_MODEL", "gemini-3-flash-preview")

# ── Anthropic (Cursor-Kontext, nicht API-gesteuert) ──
ANTHROPIC_HEAVY = _env("ANTHROPIC_HEAVY_MODEL", "claude-opus-4-6")
ANTHROPIC_FAST = _env("ANTHROPIC_FAST_MODEL", "claude-sonnet-4-6")

# ── Ollama (lokaler Fallback, Scout-Schicht) ──
OLLAMA_MODEL = _env("OLLAMA_MODEL", "llama3.2:1b")
OLLAMA_HEAVY = _env("OLLAMA_HEAVY_MODEL", "llama3.1:latest")
OLLAMA_HOST = _env("OLLAMA_HOST", "http://192.168.178.54:11434")
OLLAMA_LOCAL = _env("OLLAMA_LOCAL_HOST", "http://localhost:11434")


def get_model_for_role(role: str) -> Optional[str]:
    """Rollen-Mapping: Jede Rolle → optimales Modell."""
    m = {
        # Kern-Rollen
        "heavy": GEMINI_HEAVY,
        "flash": GEMINI_FLASH,
        "triage": GEMINI_TRIAGE,
        "dev_agent": GEMINI_DEV_AGENT,

        # Sprache
        "dictate_stt": DICTATE_STT_MODEL,
        "dictate_stt_live": DICTATE_STT_LIVE_MODEL,
        "tts": GEMINI_TTS_MODEL,
        "whatsapp_audio": GEMINI_AUDIO,
        "voice_bridge": VOICE_BRIDGE_MODEL,

        # Perception
        "vision_daemon": VISION_DAEMON_MODEL,
        "embedding": EMBED_MODEL,

        # Spezial
        "computer_use": GEMINI_COMPUTER_USE,
        "robotics": GEMINI_ROBOTICS,
        "deep_research": GEMINI_DEEP_RESEARCH,

        # Fallback
        "ollama_light": OLLAMA_MODEL,
        "ollama_heavy": OLLAMA_HEAVY,
    }
    return m.get(role)


def get_ollama_base_url(layer: str = "scout") -> str:
    """Scout = OLLAMA_HOST, local = OLLAMA_LOCAL_HOST."""
    return OLLAMA_LOCAL if layer == "local" else OLLAMA_HOST
