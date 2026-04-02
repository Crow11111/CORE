<!-- ============================================================
<!-- CORE-GENESIS: Vollständiger Plan (Quelle: .cursor/plans)
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- ============================================================
-->

# OC Brain Reaktivierung – Vollständiger Plan

**Quelle:** `oc_brain_reaktivierung_90b0ba24.plan.md` (Cursor Plans)
**Übersicht:** Reaktivierung OC Brain, lokales LLM auf Hostinger, ChromaDB MTH-Profil, RAG, WhatsApp, E2E-Verifizierung.

---

## Arbeitsstränge (alle umsetzen lassen)

| Strang | Ziel | Verantwortung |
|--------|------|---------------|
| **A** | OC Brain Diagnose + Reparatur (Schema/device identity) | Security Expert, System Architect |
| **B** | Ollama auf VPS, Modell pullen, OpenClaw-Provider | Networking Expert, System Architect |
| **C** | MTH-Profil Vektorisierung (Ingest, Archive) | DB Expert |
| **D** | RAG-Pipeline (ChromaDB → Ollama), OC-Anbindung | System Architect, DB Expert |
| **E** | WhatsApp-Kanal aktivieren, QR pairen, Routing | Networking Expert, Security Expert |

---

## Abnahme-Kriterien (A1–A7)

| ID | Kriterium | Verifizierung |
|----|-----------|---------------|
| A1 | OC Brain Config zeigt Formular (kein "Schema unavailable") | Browser / API |
| A2 | `openclaw doctor` ohne Fehler | Shell (SSH VPS) |
| A3 | Ollama auf VPS antwortet (Port 11434) | Shell / curl |
| A4 | ChromaDB `mth_user_profile` existiert, >10 Dokumente | Skript |
| A5 | OC Brain Chat antwortet mit lokalem LLM | Browser-Test |
| A6 | WhatsApp gepairt, Testnachricht OK | QR mit **Handy scannen** (Nutzer) – sonst nicht gepairt |
| A7 | `MTH_PROFILE_ARCHIVE.md` existiert | Skript |

---

## Deliverables

1. OC Brain online mit lokalem LLM
2. ChromaDB `mth_user_profile` + `world_knowledge` (YouTube-RAG) befüllt
3. `docs/01_CORE_DNA/MTH_PROFILE_ARCHIVE.md`
4. WhatsApp-Kanal gepairt und funktional
5. Session-Log `SESSION_LOG_<DATUM>.md`

---

Siehe auch: [OC_BRAIN_AUFTRAG_AUSFUEHRUNG.md](OC_BRAIN_AUFTRAG_AUSFUEHRUNG.md), [OC_BRAIN_PLAN_ADDENDUM_VIDEO_RAG.md](OC_BRAIN_PLAN_ADDENDUM_VIDEO_RAG.md).


[LEGACY_UNAUDITED]
