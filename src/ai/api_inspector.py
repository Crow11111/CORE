# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# ============================================================
"""
API-Inspector: Fragt verfügbare Modelle bei Gemini und Ollama ab.
Für Task-Router und Agenten; siehe docs/02_ARCHITECTURE/AI_MODEL_CAPABILITIES.md.
"""

import os
import asyncio
from typing import Any

from dotenv import load_dotenv
load_dotenv("/OMEGA_CORE/.env")


def list_gemini_models() -> list[dict[str, Any]]:
    """Gemini Model-Liste (google-genai). Bei Fehler leere Liste."""
    try:
        from google import genai
        key = os.getenv("GEMINI_API_KEY", "").strip()
        if not key:
            return []
        client = genai.Client(api_key=key)
        # list_models gibt Generator/Liste von Model-Objekten
        models = list(client.models.list())
        return [{"name": getattr(m, "name", str(m)), "display_name": getattr(m, "display_name", "")} for m in models]
    except Exception:
        return []


def list_ollama_models(base_url: str | None = None) -> list[dict[str, Any]]:
    """Ollama api/tags. base_url z.B. aus OLLAMA_HOST."""
    import httpx
    url = (base_url or os.getenv("OLLAMA_HOST", "http://localhost:11434")).rstrip("/")
    try:
        r = httpx.get(f"{url}/api/tags", timeout=5.0)
        if r.status_code != 200:
            return []
        data = r.json()
        models = data.get("models") or []
        return [{"name": m.get("name"), "size": m.get("size")} for m in models]
    except Exception:
        return []


async def list_all_models() -> dict[str, list[dict[str, Any]]]:
    """Gemini + Ollama (Scout) + Ollama (local) parallel."""
    loop = asyncio.get_event_loop()
    gemini = await loop.run_in_executor(None, list_gemini_models)
    scout = await loop.run_in_executor(None, lambda: list_ollama_models(os.getenv("OLLAMA_HOST")))
    local = await loop.run_in_executor(None, lambda: list_ollama_models(os.getenv("OLLAMA_LOCAL_HOST")))
    return {"gemini": gemini, "ollama_scout": scout, "ollama_local": local}


if __name__ == "__main__":
    import json
    print("Gemini:", json.dumps(list_gemini_models(), indent=2)[:500])
    print("Ollama (Scout):", list_ollama_models(os.getenv("OLLAMA_HOST")))
    print("Ollama (Local):", list_ollama_models(os.getenv("OLLAMA_LOCAL_HOST")))
