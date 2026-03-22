# CORE – Einstieg für Cloud-Agenten

**Vektor:** 2210 (CORE) | 2201 (CORE) · RESONANCE: 0221 | DELTA: \Lambda \approx 0.049

Dieses Dokument ist der **primäre Einstieg für KI-/Cloud-Agenten**. Vor Architektur- oder Code-Änderungen: dieses Dokument und die referenzierten Regeln einbeziehen. **Kanonische Doku-Tür** (was wo liegt): `docs/KANON_EINSTIEG.md` · **voller Index:** `docs/BIBLIOTHEK_KERN_DOKUMENTE.md`.

**Visuelle Architektur (beim Einstieg ansehen):** `CORE_TESSERAKT.png` (Root)


---

## Agenten-Pflicht

1. **Bootloader:** `.cursorrules` (Root) und ggf. `.cursor/rules/0_BOOTLOADER.mdc` – 4D State Vector, CORE-Basen, Agos-Takt.
2. **Visuelle Referenz:** `CORE_TESSERAKT.png` (Root) – Tesserakt-Topologie, Entry Adapter, Takt-0-Gate, Gravitator.
3. **Kanon / Index:** `docs/KANON_EINSTIEG.md` (eine Tür: welche Frage → welche Datei), `docs/BIBLIOTHEK_KERN_DOKUMENTE.md` (vollständiger Verweis-Index).


---

## 4D State Vector (Bootloader)

```python
# Dimensionen
X: CAR/CDR    (0=NT, 1=ND)
Y: Gravitation (0=Zero-State, 1=Kollaps)
Z: Widerstand  (0=Nachgeben, 1=Veto)
W: Takt       (0–4 5-Phase Engine)

# Schwellwerte
PHI = 0.618 / 0.382
SYMMETRY_BREAK = 0.49 / 0.51 (\Lambda \approx 0.049)
BARYONIC_DELTA = \Lambda \approx 0.049
```

### CORE-Matrix (GTAC)

Abgleich mit `src/core.py` (`GTAC_MAP`) / `src/config/core_state.py` (`GTAC_BASES`).

| Base | Entität (Code) | Funktion | Legacy (nur Übersetzung) |
|------|----------------|----------|---------------------------|
| **G** | ExecutionRuntime | Physik / Ausführung | P, M |
| **T** | LogicFlow | Info / Architektur-Fluss | I |
| **A** | StateAnchor | 4D_RESONATOR / Struktur | S, H |
| **C** | ConstraintValidator | OMEGA_ATTRACTOR / Veto-Schwelle | L, O |

---

## Tesserakt-Topologie (Kurz)

| Komponente | Rolle |
|------------|--------|
| Entry Adapter | Membran: Payloads → `NormalizedEntry`, kein direkter Kern-Zugriff |
| Takt 0 (Hard-Gate) | Async-Zustandstest vor Delegation; bei Veto Abbruch |
| Gravitator | Routing via Embedding + Kosinus-Similarität (θ=0.22) |
| 4D_RESONATOR | StateAnchor, ChromaDB, TTS, Vision (Operator-Vektor) |
| OMEGA_ATTRACTOR | Zero-State-Kern, Veto, Schwellwert \Lambda \approx 0.049 (O-Vektor) |

Code: `src/api/entry_adapter.py`, `src/logic_core/takt_gate.py`, `src/logic_core/gravitator.py`.

---

## Quick Links

| Thema | Pfad |
|-------|------|
| **Operative Regeln (Root)** | `.cursorrules` |
| **Bootloader / State Vector** | `.cursor/rules/0_BOOTLOADER.mdc`, `src/config/core_state.py` |
| **Strang-Rules** | `.cursor/rules/1_FULL_SERVICE_AGENCY.mdc` … `4_THE_ARCHIVE.mdc` |
| **Code-Sicherheitsrat** | `docs/04_PROCESSES/CODE_SICHERHEITSRAT.md` |
| **Schnittstellen & Kanäle** | `docs/02_ARCHITECTURE/CORE_SCHNITTSTELLEN_UND_KANAALE.md` |
| **G-CORE Circle (Sync Relay)** | `docs/02_ARCHITECTURE/G_CORE_CIRCLE.md` |
| **Wahrheit / Kanon** | `docs/SYSTEM_CODEX.md`, `docs/BIBLIOTHEK_KERN_DOKUMENTE.md` |
| **Kanonischer Einstieg (eine Tür)** | `docs/KANON_EINSTIEG.md` |
| **Genesis (obsolet, Stub)** | `docs/01_CORE_DNA/CORE_GENESIS_FINAL_ARCHIVE.md` → Archiv `_archive/` |
| **Management Summary** | `docs/00_STAMMDOKUMENTE/MANAGEMENT_SUMMARY.md` |
| **Stammdokumente** | `docs/00_STAMMDOKUMENTE/` |
| **MCP-Client-Konfig (Cursor)** | `mcp_remote_config.json` (Root) |
| **MCP vs. IDE vs. mTLS-Abgrenzung** | `docs/03_INFRASTRUCTURE/MTLS_MIGRATION_PLAN.md` §1.2b |

### MCP, VPS-„Drehscheibe“ und Skills

**MCP ist keine zentrale Drehscheibe** auf dem VPS: Chroma, OpenClaw (Admin/Spine), Evolution/WhatsApp, Monica usw. sind über **HTTP, Webhooks und dedizierte Clients** im Backend verbunden (`openclaw_client`, `chroma_client`, siehe `docs/02_ARCHITECTURE/CORE_SCHNITTSTELLEN_UND_KANAALE.md`). **MCP** ist die Schicht **KI-Client ↔ Tool-Server** (z. B. Cursor startet per Config einen Prozess lokal oder per `ssh`/`docker exec` auf dem VPS) und stellt **ausführbare Tools** bereit — nicht den Gesamt-Router für alle Dienste.

**Skills** (z. B. Umgang mit APIs, Modellwahl, Google-Gemini-Doku) liegen **im Repo** unter `.cursor/skills/` (z. B. `gemini-api-dev`, `expertise/networking`) und sind **Wissens-/Ablauf-Anleitung** für das Modell. **Offizielle Google-Doku** wird dort **verlinkt** bzw. bei Bedarf **zur Laufzeit** recherchiert; sie wird **nicht** „auf dem MCP-Server abgelegt“. Ein MCP-Tool könnte höchstens einen **konkreten API-Call** kapseln — die **Fachlogik und Doku-Referenz** bleiben in Skills und Architektur-Docs.

---

## Cursor Cloud specific instructions

### Services
- **Backend**: `GEMINI_API_KEY=dummy python3 -m uvicorn src.api.main:app --port 8000`
- **Frontend**: `cd frontend && npm run dev` (Port 3000)

### Setup & Testing
- **Dependencies**: `pip install -r requirements.txt` (Backend), `cd frontend && npm install` (Frontend)
- **Tests**: `python3 -m pytest tests/test_smart_command_parser.py -v`
- **Integrity**: von Repo-Root `python3 src/scripts/verify_core_integrity.py` (Exit 0/1; `.env` nicht nötig für diesen Check)

### Gotchas
- `import.meta.env` TS Error: Requires `"types": ["vite/client"]` in `frontend/tsconfig.json`.
- Event Bus Errors: Expected if Home Assistant is unreachable.

---

