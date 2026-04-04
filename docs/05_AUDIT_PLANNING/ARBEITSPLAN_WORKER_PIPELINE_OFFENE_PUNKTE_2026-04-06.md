# Arbeitsplan: Offene Punkte — Erfassung, Planung, Umsetzung durch Worker

**Status:** OPERATOR-Steuerung | **Bezug:** `MASTER_UMSETZUNG_VPS_PROD_OHNE_DREAD_2026-04-06.md`, `O2_AUDIT_KETTEN_KOHAERENZ_2026-04-06.md`
**Zweck:** Festlegen, **wie** jedes offene Thema **nacheinander** (und wo möglich **parallel**) von spezialisierten Workern **erfasst**, **geplant** und **umgesetzt** wird — inkl. **Abnahme** und **O2-Gate**.

---

## 1. Grundprinzip: Drei-Schichten-Workflow pro Arbeitspaket

Für **jedes** Work-Paket (WP) gilt dieselbe Kette — keine Ausnahme ohne schriftliche Operator-Freigabe:

| Stufe | Wer | Output | Gate |
|-------|-----|--------|------|
| **E1 Erfassung** | Orchestrator A oder dedizierter **Scout-Worker** (Explore) | Eintrag im **Backlog** (Abschnitt 6): ID, Quelle (O2/MASTER/Ticket), Akzeptanzkriterium, Abhängigkeiten | Eintrag **nicht leer**; keine doppelte ID |
| **E2 Planung** | Orchestrator A | Kurz-Spec: Dateien/Schnittstellen, Risiken, **Veto-Traps** (Tests vor/nach Implementierung gemäß `.cursor/rules/7_TDD_ANTI_HEROIN.mdc`) | O2 **PASS** auf den **Plan** (Zero-Context: nur Plan-Text + Kanon, kein Framing) |
| **E3 Umsetzung** | **Producer** (Backend / Infra / Doc getrennt) | Code + Skripte + Doku-Änderungen; `anti_heroin_validator` auf geänderte `.py` | Grüne **Abnahme** aus MASTER (messbar); dann O2 **PASS** auf **Diff** oder Stichprobe |

**Regel:** Ohne **E2-O2-PASS** kein produktiver Code. Ohne **messbare Abnahme** kein „WP erledigt“.

---

## 2. Rollen-Matrix (wer macht was)

| Rolle | Task-Tool / Modell | Domäne |
|-------|---------------------|--------|
| **Explore-Worker** | `Task`, `subagent_type=explore` | Repo-Suche: Vorkommen alter Ports, fehlende Routen, Webhook-Pfade — liefert **evidence paths** für das Backlog |
| **Infra-Producer** | `Task`, `subagent_type=generalPurpose` | VPS, systemd, Compose, Kong live, `verify_vps_stack`, Anti-Heroin-Unit, IP/Host-Mechanismus |
| **Backend-Producer** | `Task`, `subagent_type=generalPurpose` | FastAPI, Webhooks, Postgres-Workspace, Macro-Pfad, Integrationstests |
| **Doc-Producer** | `Task`, `subagent_type=generalPurpose` oder fast | Inventar, Bibliothek, KANON, Widersprüche DOC-1…4 |
| **O2 (Orchestrator B)** | `Task`, **eigenständiger Prompt ohne Lösungshinweise** | Nur Plan oder fertigen Stand gegen Axiome + MASTER — **PASS/VETO** |
| **Shell-Worker** | `Task`, `subagent_type=shell` | Wenn nötig: Remote-SSH-Nachweise, `curl`, Deploy-Logs (niemals Secrets committen) |

Der **Orchestrator** startet **pro WP** typischerweise: Explore (optional) → O2(Plan) → Producer → Abnahme-Skript/Manuell → O2(Ergebnis).

---

## 3. Phasenfolge (Reihenvolge der Wellen)

Wellen sind **sequentiell**; innerhalb einer Welle können WP **parallel** laufen, wenn die Spalte „Blocker“ leer ist.

### Welle 0 — Fundament (vor allem weiterer E2E)

| Reihenfolge | WP / Thema | Blocker | Worker |
|-------------|------------|---------|--------|
| 0.1 | **WP-PORT** (MASTER §2): Host/IP/Ports final oder Mechanismus + automatischer `docker ps`↔Vertrag | — | Infra + Doc |
| 0.2 | **WP-A0** (`CORE_BASE_URL` public, Vollkreis A+G PASS von außerhalb Dread) | 0.1 sinnvoll (stabile URL) | Infra + Backend |
| 0.3 | **WP-ANTIHEROIN-VPS** (MASTER §3): Unit/Timer/Runner + dokumentierter grüner Lauf | 0.1 (Zielhost klar) | Infra |

### Welle 1 — Ingress & Gateway

| Reihenfolge | WP | Blocker | Worker |
|-------------|-----|---------|--------|
| 1.1 | **WP-KONG-CORE** | WP-A0 (Omega erreichbar unter Soll-URL) | Infra + Backend |
| 1.2 | **WP-OC** | 1.1 optional parallel wenn OC unabhängig erreichbar | Infra + Backend |

### Welle 2 — Kanäle & Kausalität

| Reihenfolge | WP | Blocker | Worker |
|-------------|-----|---------|--------|
| 2.1 | **WP-E2E-WA** | Kong/Evo-Routen live (1.1) | Backend + Infra |
| 2.2 | **WP-GH** | SSH/Deploy-Pfad dokumentiert | Infra |
| 2.3 | **WP-MACRO-INT** | Ticket-4-Pfad produktiv / Spec finalisiert | Backend |

### Welle 3 — Rand-Systeme & Qualität

| Reihenfolge | WP | Blocker | Worker |
|-------------|-----|---------|--------|
| 3.1 | **WP-MEM-89** | Membrane-Spec + Runtime-Host | Backend |
| 3.2 | **WP-T12** | Macro/Queue-Pfad | Backend |
| 3.3 | **WP-MCP-LIVE** | MCP-Server läuft auf Soll-Host | Infra + Backend |
| 3.4 | **WP-DOK-DRIFT** + **DOC-1…4** | — (kann früh parallel zu 0.x) | Doc |

### Welle 4 — Axiome & Abschluss

| Reihenfolge | WP | Blocker | Worker |
|-------------|-----|---------|--------|
| 4.1 | **WP-AXIOM-MATRIX** | Codepfade aus 0–3 stehen | Backend + Doc |
| 4.2 | **Gesamtabnahme** | Alle Blocker-WP grün laut MASTER §9 | Orchestrator + Operator |

---

## 4. Erfassung: wo leben die offenen Punkte?

| Ort | Inhalt | Pflege |
|-----|--------|--------|
| **Backlog-Tabelle** (Abschnitt 6 unten) | Single Source für „was ist offen“ | Nach jedem WP: Status **offen / in Arbeit / Abnahme / erledigt** |
| `SESSION_LOG_*.md` | Was wurde wann von welchem Lauf geschlossen | Doc-Producer nach Merge |
| `CORE_INVENTORY_REGISTER.md` | Neue Skripte, Units, Docs | Pflicht bei neuen Dateien |
| `O2_AUDIT_*` | Historisches Urteil; **kein** Ersatz für Backlog | Nachtrag nur bei Korrektur des Audit-Texts |

Neue Lücken (z. B. aus Operator-Nachricht): **zuerst** Zeile im Backlog, dann E2.

---

## 5. Abnahme-Disziplin (kein „simuliert grün“)

Pro WP muss mindestens **eines** dokumentiert werden:

- **Automatisch:** erweitertes Skript (z. B. `run_vollkreis_abnahme.py` oder dediziertes `src/scripts/verify_*`), Exit 0 + Log-Auszug im Session-Log
- **Semi-automatisch:** `curl`/SQL-Query mit erwartetem JSON/Feld; Ausgabe im Session-Log
- **Manuell mit Nachweis:** Screenshot/Log-Zeile **ohne** Secrets; Korrelations-ID / Git-Hash

**Verboten:** „Würde funktionieren“, „Container läuft“, Mock-only ohne Produktivpfad — widerspricht MASTER und O2 §5.

---

## 6. Backlog (Initial — vom MASTER/O2/Session)

| ID | Thema | Quelle | Status | Blocker | Abnahme-Kurzreferenz |
|----|--------|--------|--------|---------|----------------------|
| WP-PORT | IP/Port/Mechanismus + Drift-Check | MASTER §2 | **Abnahme 2026-04-06** | — | `verify_vps_stack` inkl. `verify_vps_docker_port_contract` (SSH `docker ps` ↔ `vps_public_ports.py`); live Exit 0 auf VPS |
| WP-A0 | Prod `CORE_BASE_URL`, Vollkreis A+G | MASTER WP-A0 | offen | WP-PORT empfohlen | Remote PASS |
| WP-ANTIHEROIN-VPS | Scanner auf VPS | MASTER §3 | **Deploy-Skript + Units fertig** | SSH vom Operator-Rechner | `python -m src.scripts.vps_deploy_anti_heroin_mirror` → `[PASS]`; auf VPS: `/var/log/omega-core-anti-heroin.log` + `pytest tests/test_run_anti_heroin_scan.py` |
| WP-KONG-CORE | POST Webhook → Core | MASTER | offen | WP-A0 | 200 + DB/API-Nachweis |
| WP-OC | HTTP Gateway-Check | MASTER | offen | — | wie `check_gateway()` |
| WP-E2E-WA | WhatsApp/Evolution E2E | MASTER | offen | WP-KONG-CORE | Kanal oder DB + Correlation-ID |
| WP-GH | Webhook → Pull/Deploy | MASTER | offen | — | Hash in Log |
| WP-MACRO-INT | State machine sichtbar | MASTER | offen | Ticket 4 Pfad | Postgres-States + Latenz |
| WP-MEM-89 | Membrane/Git Spec | MASTER | offen | — | Flags/Push wie Spec |
| WP-T12 | Edge abgelehnt → Audit-Log | MASTER | offen | Queue-Pfad | grep/metrics |
| WP-MCP-LIVE | Echter Tool-Call | MASTER | offen | MCP läuft | MCP-Response im Log |
| WP-DOK-DRIFT | 32768 / alte Ports | MASTER | **teilweise 2026-04-06** | aggregierte `00_*_MASTER.md` ausgelassen | `python -m src.scripts.verify_docs_chroma_port_drift` grün; Kern-Doku + Root-Skripte angeglichen; Block **J** in `run_vollkreis_abnahme.py` |
| WP-DOC | DOC-1…4 | MASTER §7 | teils | DOC-1…3 teils erledigt | Checkliste alle [x] |
| WP-AXIOM-MATRIX | A0/A5/A6/A7 Matrix | MASTER §6 | offen | Code stabil | Doc + CI-Stichproben |

*Status wird bei jedem Durchlauf aktualisiert.*

---

## 7. Operatives Vorgehen für den Orchestrator (Cursor)

1. **Welle wählen** (start: 0.1 oder parallel WP-DOK wenn Doc-Producer frei).
2. **Task(Explore)** nur wenn Unklarheit über Pfade/Ports (z. B. „wo ist Evolution-Webhook definiert?“).
3. **Spec schreiben** (E2): 1 Seite, Akzeptanzkriterium = MASTER-Zelle.
4. **Task(O2)** mit Plan — Prompt **ohne** Lösungstipps.
5. Bei **PASS:** **Task(Producer)** mit Kopie von: Datei-Hygiene, `anti_heroin_validator`, TDD-Kontrakt.
6. **Abnahme** laufen lassen; Ergebnis in `SESSION_LOG_*.md`.
7. **Task(O2)** Stichprobe oder Voll-Review je nach Risiko.
8. Backlog-Zeile → **erledigt** oder **VETO** mit Grund → neue Zeile „Rework“.

---

## 8. Erfolg

Das Projekt ist **nur** dann „erfolgreich abgeschlossen“, wenn **Backlog** keine **offenen** oder **VETO**-Zeilen mehr in den **Blocker-WPs** hat und **WP-AXIOM-MATRIX** + **WP-DOC** **erledigt** sind — gemäß **MASTER §9**.

---

**Nächster konkreter Schritt:** Welle **0.1** (WP-PORT) als erstes Producer-Paket nach O2-Freigabe des Port-/Discovery-Spec.
