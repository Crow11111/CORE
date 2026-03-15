# ============================================================
# CORE-GENESIS: Verify, don't trust (AXIOM 7)
# Prüft empirisch, ob OC-Brain-Plan-Deliverables erbracht wurden.
# Exit 0 = PASS (Nachweis erbracht), Exit 1 = FAIL (kein Vertrauen).
# ============================================================
from __future__ import annotations

import os
import sys
import asyncio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

# Mindestanforderungen (Plan A4, A7 + Video-RAG)
MIN_WORLD_KNOWLEDGE_YOUTUBE = 1   # mind. 1 Dokument aus YouTube-Transkript (RAG-Referenz)
MIN_MTH_PROFILE_CHUNKS = 10       # A4: mth_user_profile mind. 10 Dokumente
REQUIRED_FILES = [
    "docs/05_AUDIT_PLANNING/OC_BRAIN_PLAN_ADDENDUM_VIDEO_RAG.md",
    "docs/05_AUDIT_PLANNING/YOUTUBE_TRANSCRIPT_GEMINI_RAG.md",
    "docs/01_CORE_DNA/MTH_PROFILE_ARCHIVE.md",
]


def _get_chroma_client_sync():
    from src.network.chroma_client import _get_chroma_client_sync as _get
    return _get()


def _get_collection_sync(name: str, create_if_missing: bool = False):
    from src.network.chroma_client import _get_collection_sync as _get_col
    return _get_col(name, create_if_missing)


def check_world_knowledge_youtube() -> tuple[bool, str]:
    """Prüft: world_knowledge enthält Einträge aus YouTube-Transkript (source oder category)."""
    try:
        col = _get_collection_sync("world_knowledge", create_if_missing=False)
        result = col.get(include=["metadatas"])
        ids, metadatas = result["ids"], result.get("metadatas") or []
        n = len(ids)
        youtube_count = 0
        for m in (metadatas or []):
            if not isinstance(m, dict):
                continue
            src = (m.get("source_file") or m.get("source") or "").upper()
            cat = (m.get("category") or "").upper()
            if "YOUTUBE" in src or "GEMINI_RAG" in src or "RAG_REFERENCE" in cat:
                youtube_count += 1
        ok = youtube_count >= MIN_WORLD_KNOWLEDGE_YOUTUBE
        msg = f"world_knowledge: {n} docs, davon YouTube/RAG-Referenz: {youtube_count} (min {MIN_WORLD_KNOWLEDGE_YOUTUBE})"
        return ok, msg
    except Exception as e:
        return False, f"world_knowledge check failed: {e}"


def check_mth_user_profile() -> tuple[bool, str]:
    """Prüft: mth_user_profile enthält mindestens MIN_MTH_PROFILE_CHUNKS Einträge."""
    try:
        col = _get_collection_sync("mth_user_profile", create_if_missing=False)
        result = col.get(include=[])
        n = len(result["ids"])
        ok = n >= MIN_MTH_PROFILE_CHUNKS
        msg = f"mth_user_profile: {n} chunks (min {MIN_MTH_PROFILE_CHUNKS})"
        return ok, msg
    except Exception as e:
        return False, f"mth_user_profile check failed: {e}"


def check_required_files(project_root: str) -> tuple[bool, str]:
    """Prüft: Alle erforderlichen Dateien existieren."""
    missing = [p for p in REQUIRED_FILES if not os.path.isfile(os.path.join(project_root, p))]
    ok = len(missing) == 0
    msg = f"Dateien: {len(REQUIRED_FILES) - len(missing)}/{len(REQUIRED_FILES)} vorhanden" + (
        f"; fehlen: {missing}" if missing else ""
    )
    return ok, msg


def check_openclaw_gateway() -> tuple[bool, str]:
    """Prüft: OpenClaw-Gateway mit .env-Zugang erreichbar (interner Nachweis A1-Proxy)."""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        from src.network.openclaw_client import check_gateway, is_configured
        if not is_configured():
            return True, "OpenClaw nicht konfiguriert (skip)"
        ok, msg = check_gateway(timeout=8.0)
        return ok, msg or "Gateway prüfbar"
    except Exception as e:
        return False, f"OpenClaw-Check fehlgeschlagen: {e}"


def main() -> int:
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    os.chdir(project_root)

    all_ok = True
    reports = []

    # ChromaDB nur prüfen wenn erreichbar (sonst Skip mit Warnung)
    try:
        _get_chroma_client_sync()
        ok, msg = check_world_knowledge_youtube()
        reports.append(("world_knowledge (YouTube/RAG)", ok, msg))
        if not ok:
            all_ok = False

        ok, msg = check_mth_user_profile()
        reports.append(("mth_user_profile", ok, msg))
        if not ok:
            all_ok = False
    except Exception as e:
        reports.append(("ChromaDB", False, f"ChromaDB nicht erreichbar: {e}"))
        all_ok = False

    ok, msg = check_required_files(project_root)
    reports.append(("Required files", ok, msg))
    if not ok:
        all_ok = False

    ok, msg = check_openclaw_gateway()
    reports.append(("OpenClaw Gateway (A1-Proxy)", ok, msg))
    if not ok:
        all_ok = False

    for name, ok, msg in reports:
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {name}: {msg}")
    print()
    if all_ok:
        print("VERIFY_OK: Alle maschinell prüfbaren Nachweise erbracht.")
        print("Weitere Prüfung durch Orchestrator/Team mit .env (Browser/API) – Nutzer muss nicht bestätigen.")
        return 0
    print("VERIFY_FAIL: Mindestens ein Nachweis fehlt. Kein Abnahme.")
    return 1


if __name__ == "__main__":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
