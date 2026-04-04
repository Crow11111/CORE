# MASTER-UMSETZUNG: Omega-Prod auf VPS, ohne Dreadnought als Laufzeit

**Status:** OPERATOR-MANDAT (2026-04-06) — verbindlich für Producer, Infra, Audits  
**Gegenstand:** Alles, was O2 in `O2_AUDIT_KETTEN_KOHAERENZ_2026-04-06.md` als **Lücke** oder **Nicht-Implikation** benennt, wird hier in **Work-Pakete** mit **Abnahme** übersetzt — **keine Simulation** als Ersatz für persistierte/observierbare Wirkung.

---

## 0. Wahrheitshierarchie (Kanon)

| Rang | Quelle | Gilt für |
|------|--------|----------|
| **1** | Operator-Mandat (dieses Dokument + Detailfluss `OMEGA_DETAILFLUSS_TICKETS_4_12_PROD_RUNTIME.md`) | Prod-Topologie, kein Dreadnought als Runtime |
| **2** | `VPS_HOST_PORT_CONTRACT.md` + `src/config/vps_public_ports.py` | Ports; Drift = Bug bis Vertragsänderung |
| **3** | Tickets 4–12 (`TICKET_*.md`) — solange **DRAFT**, gilt: **nicht produktionsfertig** | Implementierungs-Soll |
| **4** | `KONSOLIDIERTER_VERKEHRSPLAN_VPS_KONG_MCP.md` | Nord-Süd / Kong / Pfade |
| **5** | `OMEGA_VOLLKREIS_PLAN.md` | Nur insoweit mit **(1)** vereinbart; Texte „Dreadnought zentral“ für **Prod falsch** → Abschnitt 10 |

**Explizit nicht bindend für Deploy-Entscheid:** `MACRO_CHAIN_MASTER_DRAFT.md` — **Entwurf**; Host-Trennung „Postgres nur lokal“ widerspricht Operator-Soll (**eine Runtime auf VPS**). Nutzbar als Ideensammlung, **nicht** als Override gegen (1)–(2).

---

## 1. Grundsatz: Dreadnought = nur Development

- **Dreadnought:** Cursor, lokale Builds, Membrane-Entwicklung, optionale Dev-Abnahme mit `CORE_BASE_URL=http://127.0.0.1:8000`.
- **Production-Omega:** läuft **nur** gegen konfigurierte **öffentliche oder VPS-interne URLs**; Abnahme **ohne** `localhost`/`127.0.0.1` in `CORE_BASE_URL` (siehe WP-A0).

Dokumente, die Dreadnought als **unverzichtbaren** Hub behaupten, sind für **Prod** **veraltet** und unterliegen **WP-DOC** (Abschnitt 10).

---

## 2. Port / IP / Drift (Operator: „egal wie, aber final“)

**Soll:** Entweder  
- **A)** feste Host-Ports wie Vertrag + Compose auf VPS **vernagelt**, **oder**  
- **B)** ein **einziger** Mechanismus (z. B. `VPS_PUBLIC_HOST` + zentrale `.env` auf Runtime, DuckDNS, Hostinger-API), der zur **Laufzeit** die gleichen Werte liefert wie `vps_public_ports.py` — **ohne** stilles Remapping.

**Abnahme B:** Nach Deploy `verify_vps_stack` Exit 0 **und** Vergleich `docker ps` ↔ Vertragstabelle **automatisiert** (Skript, kein Handauge).

---

## 3. Anti-Heroin & Integrität: verpflichtend auf dem VPS

**Soll:** Auf dem VPS (CI-Runner-Container oder systemd-Unit) regelmäßig:

1. Repo-Stand (Branch `main`) auschecken  
2. `python -c "… validate_file …"` über `src/**/*.py` (gleiche Logik wie Block **I** in `run_vollkreis`)  
3. Ergebnis **loggen**; bei FAIL **Alert** / Pipeline rot  

**Abnahme:** Existenz der Unit + ein **manuell nachvollziehbarer** Lauf mit **Exit 0** auf dem VPS (Log-Pfad dokumentiert).

*Referenz:* `docs/03_INFRASTRUCTURE/VPS_ANTI_HEROIN_PIPELINE.md` — Deploy: `python -m src.scripts.vps_deploy_anti_heroin_mirror` (Rechner mit `root@VPS_HOST`-SSH).

---

## 4. Tickets: narrativ ≠ fertig

- **Ticket 4 DRAFT** ⇒ **nicht abgenommen** — Postgres-Workspace + Admission live am Prod-Endpunkt + messbare Reflex-Latenz.  
- **Alle Tickets 4–12:** Abnahme nur durch **dedizierte** Integrations- und E2E-Schritte (nicht nur Unit-Tests im isolierten Modul).

---

## 5. Work-Pakete aus O2-Audit §5 („Vollkreis impliziert nicht …“) → Abnahme

| WP-ID | Thema | Abnahme (messbar, nicht simuliert) |
|-------|--------|-------------------------------------|
| **WP-A0** | Runtime-URL | `CORE_BASE_URL` gesetzt, **ohne** `localhost`/`127.0.0.1`; `run_vollkreis` **A+G** gegen diese URL **PASS** von Rechner **außerhalb** Dreadnought oder von VPS selbst. |
| **WP-E2E-WA** | WhatsApp | Evolution (oder erlaubter Kanal) sendet Test-Event; **Antwort** im Kanal **oder** persistierter Job-Status in Workspace-DB mit **Korrelations-ID**; Timeout dokumentiert. |
| **WP-GH** | GitHub→VPS | Test-Commit; Webhook **200**; nachweisbarer **Pull/Deploy** auf VPS (Hash/Log). |
| **WP-KONG-CORE** | Kong→Omega | Route `POST …/webhook/...` → Upstream Omega-Runtime; **200** + DB/API-Lesebestätigung des Events. |
| **WP-OC** | OpenClaw | HTTP `check_gateway()`-Äquivalent in Abnahme-Skript; **kein** „Container Up genügt“. |
| **WP-MACRO-INT** | Zustandsmaschine | Ein **synthetischer** Ingress durch **Produktiv-Codepfad**; erwartete **State-Transitions** in Postgres lesbar; Reflex-ACK-Ziel **unter 1 s** unter dokumentierter Last. |
| **WP-MEM-89** | Membrane/Git | Flags / Push-Pfad wie Spec; **kein** reines „Datei existiert“. |
| **WP-T12** | Ticket 12 | Abgelehntes Edge-Event ⇒ **strukturierter Audit-Log** (grep/metrics Gate). |
| **WP-MCP-LIVE** | MCP | Ein **Tool-Call** gegen laufenden Server, nicht nur JSON-Schema. |
| **WP-DOK-DRIFT** | Port-Doku | Alle Referenzen **32768**/alte Kong-Ports bereinigt oder auf Vertrag **32779**/32776–78 **automatisiert** geprüft. |

**Reihenfolge-Empfehlung:** WP-A0 → WP-KONG-CORE → WP-OC → WP-E2E-WA → WP-MACRO-INT → übrige.

---

## 6. Axiome A0, A5, A6, A7 — maximaler Detailgrad (Operator)

| Axiom | IT-Pflicht |
|-------|------------|
| **A0** | Kristall/Snapping in **Engine-Pfaden** dort, wo Schwellen gesetzt werden (`crystal_grid_engine`, Admission-Drift, keine literalen 0.5/1.0/0.0 in Resonanz — siehe Code-Review-Liste in CI). |
| **A5** | Alle Resonanz-Clamps wie Tickets; **Linter/Tests** auf verbotene Werte in API-Payloads wo spezifiziert. |
| **A6** | Resonanz **float**, Infra **int** — **typisierte** Grenzen an Service-Grenzen (OpenAPI/Validatoren). |
| **A7** | Jeder externe Eingang: Auth/Signatur/Allowlist wo Spec; **kein** „grün weil curl 200“ ohne Payload-Verifikation. |

**Abnahme:** Dediziertes Dokument „Axiom-Compliance-Matrix“ (Zeile: Modul | A0/A5/A6/A7 | Nachweis Test/Skript) — **WP-AXIOM-MATRIX**.

---

## 7. O2-Audit §6 Widersprüche — Tracking (WP-DOC)

| ID | Konflikt | Aktion |
|----|----------|--------|
| DOC-1 | Vollkreis vs. Prod ohne Dread | Vollkreis-Text + Anker §4 anpassen; Prod-Pfad `CORE_BASE_URL` kanonisch |
| DOC-2 | MACRO vs. Detailfluss Postgres | MACRO als Entwurf markiert; Detailfluss + Vertrag für Prod |
| DOC-3 | Anker „gesamte Kette“ | präzisieren: „Subset messbar; voll siehe MASTER + O2“ |
| DOC-4 | Chroma 32768 Legacy | Volltextsuche + Fix in verbleibenden Dateien |

---

## 8. Agenten-Rollen (kurz)

| Rolle | Aufgabe |
|-------|---------|
| **Infra-Producer** | WP-A0, Kong-CORE, VPS Anti-Heroin-Unit, Port-Mechanismus |
| **Backend-Producer** | Workspace-DB, Webhooks, Macro-Integrationspfad, Axiom-Validatoren |
| **Doc-Producer** | WP-DOC, Inventar, Bibliothek |
| **O2** | Nach jedem WP: Gegen **dieses MASTER** + Tickets — **PASS/VETO** |

---

## 9. Erfolgskriterium „Projekt erfolgreich“

**Nur** wenn: alle **WP** in Abschnitt 5, die der Operator als **Blocker** gesetzt hat, **Abnahme grün** haben **und** WP-AXIOM-Matrix **grün** **und** WP-DOC erledigt. Bis dahin: **kein** Abschluss durch Orchestrator-Aussage „fertig“.

---

[PASS] MASTER-UMSETZUNG angelegt — bindend gegenüber narrativen „fertig“-Behauptungen.
