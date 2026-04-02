# Kanonischer Einstieg

| Was ist überhaupt kanonisch? Wo fange ich an? | **`docs/BIBLIOTHEK_KERN_DOKUMENTE.md`** (vollständiger Index, Regeln „immer einbinden“). |
| Diese Übersicht (eine Tür) | **`KANON_EINSTIEG.md`** (diese Datei) |
| Agenten-Workflow & Gewaltenteilung | **`docs/00_STAMMDOKUMENTE/OMEGA_RESONANCE_ANCHOR.md`** und **`.cursorrules`** (Zwingend: Orchestrator A plant, Orchestrator B prüft blind, Producer codet nach Test-Definition) |
| Regeln / Grounding / Entities | **`docs/SYSTEM_CODEX.md`** |
| Cloud-/KI-Agenten (Cursor, Remote) | **`.cursorrules`** (Root) |
| System-Eichung / Session-Payload | **`CORE_EICHUNG.md`** (Root) |
| Operative IDE-/Agenten-Regeln (Stufen 1–3) | **`.cursorrules`** (Root) |
| Kurzüberblick für Menschen | **`README.md`** (Root) |
| Python-Abhängigkeiten (kein Architekturersatz) | **`requirements.txt`** — Verweis in Kopfkommentar auf Kanon |
| **Kardanischer Punkt (Theorie → messbares Echo)** | **`omega_core.py`** (Root): Ω_b-Schwelle, Dual-Membran **S float / P int**, MRI-Spannung, Operator **`?`** als Phasensprung (`complex`); **`python omega_core.py`**. **Eingebunden in** `run_vollkreis_abnahme.py` (Block **Gk**) — dreht mit der Abnahme, nicht nur im Index. |
| **Tesserakt Architektur** | **`docs/02_ARCHITECTURE/OPENCLAW_MEMBRAN_TESSERAKT.md`** | Blueprint für Facetten-Atomisierung, isolierte Räume und kreuz-modale Konvergenz. |
| **Neuer Chatbot (UI)** | **`gemini-flash-lite-chat/`** (Root): Port 3005. Primäres Interface für OMEGA Interaction. |
| **VISION SYNC App** | **`vision-sync-app/`** (Root): Port 3006. Original AI Studio Multimodal Live UI. |
| Wer pusht/pullt, Cursor vs. VPS vs. HA vs. MCP? | **`docs/02_ARCHITECTURE/LANDKARTE_CLIENTS_KNOTEN_DATENFLUSS.md`** |
| VPS-Container, Ports, Monica, Kong, Evolution, … | **`docs/03_INFRASTRUCTURE/VPS_KNOTEN_UND_FLUSSE.md`** |
| Infrastruktur-Soll (Lang-Master, kanonisch) | **`docs/00_STAMMDOKUMENTE/00_CORE_INFRASTRUCTURE_MASTER.md`** |
| Alter Pfad `docs/00_CORE_INFRASTRUCTURE_MASTER.md` | **Nur Stub** → weiter nach `00_STAMMDOKUMENTE/…` (kein zweiter Volltext) |
| Architektur-Soll (aggregiert) | **`docs/00_STAMMDOKUMENTE/00_CORE_ARCHITECTURE_MASTER.md`** |
| Prozesse-Soll (aggregiert) | **`docs/00_STAMMDOKUMENTE/00_CORE_PROCESSES_MASTER.md`** |
| Genesis-Name nur noch Anker | **`docs/01_CORE_DNA/CORE_GENESIS_FINAL_ARCHIVE.md`** (Stub → Archiv + aktive Docs) |
| Alter Link `docs/CORE_GENESIS_FINAL_ARCHIVE.md` | Nur Weiterleitung; kanonisch der Stub unter `01_CORE_DNA/`. |
| Inventar-Pflicht (was existiert im Repo) | **`docs/00_STAMMDOKUMENTE/CORE_INVENTORY_REGISTER.md`** |

---

## Warum so?

- **Theorie** (Whitepaper, Axiome) und **Betrieb** (Ports, Container, Webhooks) haben unterschiedliche **Änderungsfrequenz** — in einer Datei gegeneinander.
- **Cursor / Agenten** brauchen einen **kurzen Pfad** (`@docs/BIBLIOTHEK_KERN_DOKUMENTE.md` oder **diese Datei**), nicht 6000 Zeilen Kontext.
- Der **Kreis schließt sich** durch **messbare** Ketten (Webhook, `curl`, Skripte), nicht durch Seitenzahl. Dazu gehört bewusst auch der **kleine** Kardan-Bogen: `omega_core.py` (stdout), neben großen Integritäts-Skripten.

---

## Pflege-Regel (kurz)

1. Neues Thema → **passender Ordner** (`02_`, `03_`, …), dann **Bibliothek + Inventar** nachziehen.
2. Große Sammelbände (`00_*_MASTER.md` unter `00_STAMMDOKUMENTE/`) per **`python -m src.scripts.compile_docs_master`** *ergänzen* oder bewusstem Edit pflegen — **keine** zweite Volltext-Kopie unter `docs/00_CORE_INFRASTRUCTURE_MASTER.md` (dort nur Stub). *Hinweis:* Das Skript kann bei Bedarf ein zusammengefügtes Artefakt unter `docs/03_INFRASTRUCTURE/00_CORE_INFRASTRUCTURE_MASTER.md` erzeugen; der **kanonische** Lang-Master für den Gesamt-Soll bleibt **`docs/00_STAMMDOKUMENTE/00_CORE_INFRASTRUCTURE_MASTER.md`**, bis ihr bewusst migriert.
3. **Diese Datei** (`KANON_EINSTIEG.md`) nur anpassen, wenn sich die **Rolle** einer Einstiegsdatei ändert (nicht jeden Feinschliff).

---

**Referenz:** `@docs/BIBLIOTHEK_KERN_DOKUMENTE.md` · `@.cursorrules` · `@CLAUDE.md` · `@README.md`
