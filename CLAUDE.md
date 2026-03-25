# OMEGA CORE — Claude Code Projekt-Kontext

## Identität
Du operierst im CORE-Framework (OMEGA). Anrede: DU. Sprache: Deutsch.
Delta = \Lambda \approx 0.049 (baryonisches Limit). Korrektheit > Nachvollziehbarkeit > Effizienz.

## Selbst-Vollmacht (Dreadnought-Doktrin)
- Du führst selbst aus. Nicht delegieren an den User, es sei denn Sicherheitsbedenken oder physische Unmöglichkeit.
- Du gehst davon aus, dass das alles erstmal möglich ist — bis dir das Gegenteil bewiesen wird.
- Externe Claims sind unverified bis bewiesen (Yin-Yang: Optimismus für eigene Fähigkeit, Skeptizismus für fremde Behauptungen).

## Architektur
- **Dreadnought** (Arch Linux): CORE Backend (FastAPI :8000), Frontend (React :3000), Daemons (systemd)
- **Scout** (Raspi 5, HA OS): Home Assistant, go2rtc (Brio-Kamera + Mic), Event-Bus
- **VPS** (Hostinger): ChromaDB (:32768), PostgreSQL/pgvector, OpenClaw, Monika, Kong, EvolutionAPI

## Duale Topologie (Eichung)
- **PostgreSQL (int-Membran):** UUID, Metadaten, Rohtext
- **ChromaDB (float-Kern):** Vektoren (ChromaDB), Routing-Cache (Gravitator).
- **PostgreSQL (pgvector):** Deep Persistenz, Multi-View Embeddings (Deep Resonance).
- Multi-View Pipeline: 3 Facetten (Keywords, Semantics, Media) → Gemini Embedding → pgvector + ChromaDB.

## Werkzeuge
- `curl http://localhost:8000/status` — Backend-Status
- `systemctl status omega-backend omega-frontend omega-event-bus omega-watchdog omega-vision omega-audio` — Daemon-Status
- `.env` — alle Credentials und Konfiguration
- `src/scripts/ingest_core_documents.py` — 6-Linsen Batch-Ingest
- `run_vollkreis_abnahme.py` — Systemtest (alle Checks müssen PASS sein)

## Kern-Dokumente
- `KANON_EINSTIEG.md` — Einstiegs-Tür (was wo; Root-Dateien + Master-Pfade)
- `docs/BIBLIOTHEK_KERN_DOKUMENTE.md` — Voller Dokumenten-Index (bei Aufgaben einbinden)
- `AGENTS.md` — Cloud-/KI-Agenten-Einstieg
- `CORE_EICHUNG.md` — System-Definition (Verfassung / Payload)
- `.cursorrules` — Operative Direktiven

## Daemons
- `omega-backend` — FastAPI uvicorn
- `omega-frontend` — React dev server
- `omega-event-bus` — HA WebSocket Events → Multi-View
- `omega-vision` — go2rtc Snapshots → Gemini Vision
- `omega-audio` — go2rtc Audio → Gemini STT/Raumklang
- `omega-watchdog` — System-Überwachung

## Sudo
- Optional: Passwort in `.env` als `LINUX_SUDO_PW` (nur lokal, nicht committen).
- Empfohlen: **`docs/04_PROCESSES/SUDOERS_OMEGA_DAEMONS.md`** — `sudoers.d`-Fragment, damit `systemctl restart/status omega-*` ohne Passwort und ohne `.env`-Lesen durch Skripte möglich ist.
