# O2 Kohärenzprüfung: Soll-Kette vs. messbarer Nachweis

**Rolle:** Orchestrator B (O2) — **kein** Zero-Context-Audit; adversarial Kohärenz (Theorie + Masterplan + Detailfluss vs. Skripte/Tests).  
**Datum:** 2026-04-06  
**Arbeitsverzeichnis:** `/OMEGA_CORE`  
**Pflichtlektüre:** `OMEGA_DETAILFLUSS_TICKETS_4_12_PROD_RUNTIME.md`, `OMEGA_VOLLKREIS_PLAN.md`, `KONSOLIDIERTER_VERKEHRSPLAN_VPS_KONG_MCP.md` (§2–§3, §7, §8, Anhang A), `MACRO_CHAIN_MASTER_DRAFT.md` (Einleitung, Zustandsmaschine, Phase 1–2; **Deploy nicht bindend** — siehe Operator-Disclaimer im Draft + `MASTER_UMSETZUNG_VPS_PROD_OHNE_DREAD_2026-04-06.md`), `OMEGA_RESONANCE_ANCHOR.md`, `.cursor/rules/0_SYSTEM_AXIOMS.mdc` (A0, A5, A6, A7), `run_vollkreis_abnahme.py`, Stichprobe `TICKET_4_ADMISSION_CONTROL.md`, `TICKET_12_EPISTEMIC_DRIVE.md`.

---

## 1. Urteil (eine Zeile)

**[PARTIAL]** — Die **Soll-Kette** ist in Doku **erkennbar und teilweise** durch `run_vollkreis_abnahme.py` + eingebettete Hilfsskripte **abgedeckt**; **Macro-Kette (Tickets 4–12), Prod ohne Dreadnought, vollständiger öffentlicher Ingress (Kong→CORE/Webhook) und mehrere Vollkreis-Pfade aus `OMEGA_VOLLKREIS_PLAN.md` sind nicht** durch grüne Abnahme **belegt**. Grüne Tests allein wären **Cherry-Picking**; hier: das Skript misst **Lokalität + VPS-Stack-Subset + Speicher-Stichproben**, nicht die **geschlossene Kausalität** des Masterplans.

---

## 2. Executive Summary (adversarial)

Die Architektur-Dokumente beschreiben eine **breite** Zieltopologie: Dreadnought als aktueller Dev-Hub, VPS mit Chroma, Kong, Evolution, OpenClaw, Postgres; ergänzend **Detailfluss** mit **Omega-Runtime auf neutralem Host** und Kong-Routen für **öffentliche** Webhooks — teils **noch Soll**. Der **`MACRO_CHAIN_MASTER_DRAFT`** verankert zudem eine **strikte Host-Trennung** (Postgres/„OCSpline“ eher lokal, Chroma VPS), während der **kanonische Detailfluss** Prod-Postgres **mit Runtime** koppelt und Dreadnought **optional** macht: Das ist **kein** bloßes Wording, sondern **widersprüchliche Platzierung** von Wahrheit und Reflex-Pfad, solange nicht **eine** deploybare Ist-Topologie mit DSN/Host-Matrix **messbar** fixiert ist.

`run_vollkreis_abnahme.py` prüfte zum Audit-Zeitpunkt **hart** `localhost:8000` (ohne `CORE_BASE_URL`). **Nachtrag:** Block **A** nutzt jetzt **`CORE_BASE_URL`** (Default weiterhin `http://127.0.0.1:8000`); lokale Ports 8000/3000 nur bei localhost-URL. Die übrigen Lücken (E2E, Kong→CORE, …) bleiben bis zur MASTER-Abnahme offen. **HA-API 200**, **VPS** via `verify_vps_stack` (SSH, Container, Chroma, **Kong nur gegen Repo-Deck-Referenz**: `/evo`, `/health`, nicht CORE-Upstream), **Git-Remote-Konfiguration ohne Push**, **MCP-JSON-Datei**, **Multi-View/pgvector-Stichprobe**, **Chroma `events` ohne Nullvektoren**, **`omega_core.py`-Echo** und **Anti-Heroin-Scan**. Es fehlen u. a. **WhatsApp-E2E**, **GitHub-Webhook→Pull auf VPS**, **Evolution→CORE Webhook E2E**, **OpenClaw-Gateway-HTTP-Verifikation**, und **jede** Integration der **Macro-Zustandsmaschine** über HTTP. (**Prod-Base-URL:** Block A kann per `CORE_BASE_URL` auf Remote zeigen — **ohne** dass die übrigen E2E-Pfade dadurch abgedeckt sind.)

`OMEGA_RESONANCE_ANCHOR.md` behauptet, `run_vollkreis` bestätige die **„Integrität der gesamten Kette“** — das ist **überzogen** gegenüber dem tatsächlichen Skriptumfang und **widerspricht** A7 (Verifizieren statt glauben), wenn man die Doku wörtlich nimmt. **Ticket 4** ist explizit **DRAFT**; **Ticket 12** grenzt sauber ab (**kein** finales Outbound ohne 10/11) — das Vollkreis-Skript **beweist** weder Ticket-12-Edge/Queue noch Ticket-4-Reflexlatenz.

**Fazit:** Die Kette existiert **narrativ** stark; der **messbare Beweis** ist **segmentiert** und **Dreadnought-zentriert**. Für **Prod-Soll ohne Dread** fehlen **dedizierte** Abnahme-Schritte.

---

## 3. Rekonstruktion Soll-Kette (kurz)

| Schicht | Inhalt (aus Masterplan + Detailfluss) |
|--------|----------------------------------------|
| **Topologie** | Dreadnought ↔ Scout (HA) ↔ VPS (Chroma, OC, Evolution, Kong, Postgres, MCP) ↔ GitHub; optional **Runtime nur VPS** (Detailfluss). |
| **Ingress** | Push: Webhooks (WA, HA, GitHub) → ideal **Kong 443/80** → Omega-Runtime; Verkehrsplan: viele Pfade **Soll**, Ist oft **Direktport/Tunnel**. |
| **Macro 4–7** | Admission (D, Circuit Breaker) → Postgres-Workspace-Zustände → Arbitration/Efference/Veto/Temporal → Evolution nur mit Release; **Reflex-ACK &lt; 1 s** (Spec). |
| **8–9** | Membrane-Flags, Git Auto-Push/Pull **nur** auf Teilpfaden (Anker §5). |
| **10–11** | OC-Autarkie, duale Topologie Postgres/Chroma, Event/MCP-Pfade. |
| **12** | Edge→Queue→Worker, Pacemaker V/R (float), Sentinel, Void/Traum — **ohne** Outbound-Shortcut. |

**MACRO_CHAIN_MASTER_DRAFT** (Phase 1–2) betont zusätzlich **OCSpline lokal** und **Chroma VPS** für Drift — kollidiert **teilweise** mit „alles deployierbar auf VPS“ aus Detailfluss, solange nicht harmonisiert.

---

## 4. Tabelle: Kettenglied | Gefordert | Nachweis | Lücke

| Kettenglied | Gefordert in (Dokument) | Nachweis (Skript/Test/keiner) | Lücke ja/nein + Kurzgrund |
|-------------|---------------------------|-------------------------------|---------------------------|
| Lokales Backend + Event-Bus | `OMEGA_VOLLKREIS_PLAN` §5; Detailfluss (Dev) | `run_vollkreis` **A**: `curl localhost:8000/status`, `event_bus.running` | **Nein** für **lokalen** Dev-Hub; **Ja** für Prod ohne `localhost`. |
| Frontend-Port 3000 | Vollkreis §5 (Dreadnought) | `run_vollkreis` **A**: `ss` 8000+3000 | **Nein** lokal; **Ja** wenn Prod-Abnahme ohne lokales 3000. |
| HA/Scout API erreichbar | Vollkreis §5 **B** | `run_vollkreis` **B**: `HASS_URL`/`TOKEN` → 200 | **Nein** (API-Ebene); **Ja** für `rest_command`→CORE und WA-Pipeline (nicht im Skript). |
| VPS Container / Basis | Vollkreis **C**; Verkehrsplan §7 | `run_vollkreis` **C**: `verify_vps_stack` Exit 0 | **Teil** — kein vollständiger Push/Pull-Matrix-Beweis. |
| Chroma VPS Heartbeat | Vollkreis §5; Verkehrsplan | `run_vollkreis` **D** + `verify_vps_stack` | **Nein** für Heartbeat; **Ja** für semantische RAG-Korrektheit Makro-Kette. |
| Kong **Deck-Referenz** (/evo, /health) | `KONSOLIDIERTER_VERKEHRSPLAN` §8; `kong-deck-reference.yaml` | `verify_vps_stack` (in **C**) | **Nein** für **referenzierte** Routen. |
| Kong **Soll**: Webhook/API → **Omega-Runtime** | `OMEGA_DETAILFLUSS` §B Tabelle „noch zu terminieren“; Verkehrsplan §3.1 | **Keiner** in Vollkreis | **Ja** — explizit offen in Detailfluss; Skript prüft **kein** `POST` CORE hinter Kong. |
| Evolution → CORE WhatsApp Ingress E2E | Vollkreis §5 „WhatsApp E2E“; Verkehrsplan §7.3 | **Keiner** in `run_vollkreis` (kein `run_whatsapp_e2e_ha`) | **Ja** — im Plan genannt, im Abnahmeskript **absent**. |
| GitHub Push + Webhook + VPS `git pull` | Vollkreis §5, §6 | `run_vollkreis` **E**: nur `git remote` | **Ja** — kein Push, kein Webhook, kein Pull-Nachweis. |
| MCP atlas-remote | Vollkreis §5 **F** | `run_vollkreis` **F**: JSON-Struktur | **Teil** — Datei vorhanden; **kein** Live-Tool-Call / Workspace-Beweis. |
| Agent-Pool aktiv | Implizit Betrieb | `run_vollkreis` **G** | **Nein** für „läuft“; **Ja** für fachliche Korrektheit. |
| Postgres/pgvector Multi-View | Duale Topologie; Ticket 11 | `verify_multiview_pg` (in **G**) | **Teil** — nicht identisch mit **Macro-Job-Workspace** (Ticket 4 Schema). |
| Chroma `events` Qualität | Kognitive Schicht | `run_vollkreis` **G**: keine Nullvektoren | **Teil** — keine Void/PE/Admission-Kopplung. |
| Kardan-Anker `omega_core.py` | `OMEGA_RESONANCE_ANCHOR` §4 | `run_vollkreis` **Gk** | **Nein** für „Theorie läuft“ als Prozess-Echo; **Ja** für Makro-Phasen 3–6. |
| Anti-Heroin statisch | `.cursorrules` / Validator | `run_vollkreis` **I** | **Nein** für `src/*.py` Syntax/Pattern; **Ja** für Laufzeit-Heroin (Mocks in Prod). |
| **Ticket 4** Admission + Workspace-FSM | `TICKET_4`, Detailfluss **C** | Unit-Tests laut Ticket (**nicht** von Vollkreis aufgerufen) | **Ja** auf Integrations-Ebene — Vollkreis **ruft** `test_admission_control` **nicht** auf. |
| **Tickets 5–7** Arbitration, Veto, Temporal | Detailfluss, MACRO Phasen 2–6 | **Keiner** in Vollkreis | **Ja**. |
| **Tickets 8–9** Membrane / Git | Detailfluss **D**, Anker §5 | **Keiner** in Vollkreis | **Ja** — Flags, Settle, Push-Pfade unverifiziert. |
| **Ticket 10** OC Gateway / heal | Detailfluss **E** | **Keiner** in Vollkreis | **Ja** — kein `check_gateway()`. |
| **Ticket 11** Event-Sourcing / MCP-State | Detailfluss **F** | **Teil** nur über pg/Chroma-Stichproben | **Ja** für vollständige Membran. |
| **Ticket 12** Edge/Queue/Sentinel/Traum | `TICKET_12` Scope | **Keiner** in Vollkreis | **Ja** (Spec sagt Outbound nicht; Ingress/Idle trotzdem ungemessen). |
| **Prod: `CORE_BASE_URL` / keine localhost-Soll** | `OMEGA_DETAILFLUSS` §A, **H.5** | **Keiner** — Skript hardcoded `localhost:8000` | **Ja** — Widerspruch Spec vs. Abnahme-Implementierung. |

---

## 5. `run_vollkreis` PASS impliziert **NICHT** …

- … dass **WhatsApp** (Evolution oder HA-Fallback) **end-to-end** bis Antwort im Chat funktioniert (dafür ist im **Vollkreis-Plan** ein separates Skript genannt — **nicht** Bestandteil von `run_vollkreis`).
- … dass **GitHub-Webhooks** den VPS auslösen und **`git pull`** in `GIT_PULL_DIR` **tatsächlich** laufen (nur **Remote-Konfiguration** wird angetastet).
- … dass **Kong** alle **Soll-Routen** aus dem Detailfluss hat — nur die **im Repo referenzierte Deck-Subset** (u. a. `/evo`, `/health`) wird über **Admin-API** abgeglichen; **kein** Route zu **`POST /webhook/whatsapp`** o. ä. auf Omega-Runtime.
- … dass die **Omega-Runtime** auf dem **VPS** oder ohne **Dreadnought** läuft — alle Kern-Checks zielen auf **`http://localhost:8000`**.
- … dass **OpenClaw** erreichbar und **autark** im Sinne von Ticket 10 ist (kein Gateway-HTTP-Test im Skript).
- … dass die **Macro-Zustandsmaschine** (`received` → … → `sent`) in **Postgres** live durchlaufen wird oder **Reflex-ACK &lt; 1 s** unter Last gilt.
- … dass **Membrane (8–9)** Pain/Planning-Flags, **Auto-Push-Pfade** oder **Vollständigkeit** des Remotes mit dem Workspace übereinstimmen (Anker: **Teilmengen-Push**).
- … dass **Ticket-12**-Perimeter (Auth, Idempotenz, Audit bei Drops) **implementiert** ist — nur weil Chroma/pgvector „grün“ sind.
- … dass **MCP** in einer **laufenden** Cursor-/Remote-Session **funktioniert** — nur JSON-**Syntax** und `atlas-remote`-Keys.
- … dass keine **Drift** zwischen **Doku-Ports** (z. B. historisch 32768) und **Ist** besteht — das Skript **folgt** Vertragsmodul/`CHROMA_PORT`, beweist aber keine **vollständige** Doku-Konsistenz aller Dateien.

---

## 6. Widersprüche zwischen Dokumenten (Auswahl)

| Thema | Konflikt |
|-------|----------|
| **Hub vs. Prod** | `OMEGA_VOLLKREIS_PLAN` beschreibt **Dreadnought** als zentralen Zieh-/Drück-Knoten; Detailfluss fordert **Omega-Runtime ohne Dreadnought** als **Soll** — Abnahme-Skript **verfestigt** Dreadnought (`localhost`). |
| **Postgres „wo“** | `MACRO_CHAIN_MASTER_DRAFT`: starker Fokus **lokaler** „OCSpline“/Postgres vs. VPS-Chroma; Detailfluss: **eine** Postgres-Wahrheit für Workspace **mit** Runtime auf **Prod-Host** — **Harmonisierung** offen. |
| **„Gesamte Kette“** | `OMEGA_RESONANCE_ANCHOR` §4 vs. tatsächlicher `run_vollkreis`-Umfang — **Überclaim** relativ zu A7. |
| **Chroma-Port** | Ältere Vollkreis-Textpassagen (32768) vs. Verkehrsplan-Snapshot **32779** — teils im Code über `vps_public_ports` adressiert, aber **Doku-Legacy** bleibt **Verwechslungsrisiko**. |

---

## 7. Axiom-Check (kurz, ohne Numerologie)

| Axiom | Bezug Architektur/Doku | Befund |
|-------|-------------------------|--------|
| **A0** | Kristall/Snapping — vorwiegend **metaphorische** Architekturleitplanke | Für **Kohärenz IT↔Test** **neutral**; keine zusätzliche Beweiskraft für E2E. |
| **A5** | Drift-Clamps **0.049–0.951**, Anti-0.5 in Ticket 4 / MACRO | **Spez-konsistent**; `run_vollkreis` **prüft** das **nicht** (außer indirekt über Anti-Heroin-Patterns in `src`). |
| **A6** | Resonanz `float`, Infrastruktur `int` — in Tickets 4–5, 12 explizit | **Doku kohärent**; **Kein** Skript-Nachweis, dass **Laufzeit-APIs** durchgängig typdiszipliniert sind. |
| **A7** | Zero-Trust, Telemetrie | **Schwach** im Abnahmeskript: viele Checks sind **Erreichbarkeit/Struktur**, wenige **signierte Webhooks**, **keine** Veto-/Release-**Pfad**-Tests, **kein** unabhängiger Cross-Host-Beweis für dieselbe DB-Wahrheit. |

---

## 8. Empfohlene nächste Nachweise (messbar, anti-Selbstbetrug)

1. **`CORE_BASE_URL`/`OMEGA_RUNTIME_URL`**: Gleiche Checks wie **A** und **G**, aber gegen **konfigurierbare** URL; **Fail**, wenn implizit nur `localhost`.
2. **E2E-Webhook**: `POST` von außen (oder von VPS-Container) an **öffentliche** Kong-URL → Runtime-Route → **persistierter** Job-Status in **Workspace-DB** lesbar (SQL oder API) — **Korrelation-ID** im Response.
3. **Evolution-Pfad**: Minimaltest **send** + **Receipt** mit **Signaturprüfung** (laut MACRO §3 Punkt 4 — aktuell **nicht** Vollkreis).
4. **GitHub→VPS**: Kontrollierter Push auf Test-Branch; **Webhook-Delivery 200** + nachweisbarer **Commit/Pull** auf VPS (Log oder File-Hash).
5. **OpenClaw**: Expliziter HTTP-Check `check_gateway()` oder gleichwertig in Abnahme; **kein** „Container Up reicht“.
6. **Macro-Integrationstest** (klein): Ein **synthetischer** Ingress durch **produktiven** Code-Pfad mit **Timeout** und erwarteten **State-Transitions** (nicht nur Unit-Tests im isolierten Modul).
7. **Ticket-12-Stichprobe**: Ein **abgelehntes** Edge-Event erzeugt **strukturierten** Audit-Log-Eintrag (kein stilles Drop) — **grep**/**metrics**-Gate.
8. **Kong-Soll-Liste**: Deklarierte Routen (CORE-Upstream) als **Code** im Repo + **Admin-API-Test** analog `verify_vps_stack` — getrennt von „optional“.

---

## 9. Pfad des Deliverables

`/OMEGA_CORE/docs/05_AUDIT_PLANNING/O2_AUDIT_KETTEN_KOHAERENZ_2026-04-06.md`

---

## 10. Nachtrag: MASTER-Umsetzung (Operator-Mandat, gleicher Tag)

`MASTER_UMSETZUNG_VPS_PROD_OHNE_DREAD_2026-04-06.md` übersetzt die **Lücken aus §4–§8** in **Work-Pakete (WP-A0, …)** mit messbarer Abnahme; `VPS_ANTI_HEROIN_PIPELINE.md` definiert das VPS-Soll für den Scanner. **Urteil §1 [PARTIAL]** bleibt bestehen, bis die WP nacheinander **grün** sind — nicht nur Skript-Anpassung.

---

*[LEGACY_UNAUDITED]* — Dieses Dokument ist ein **Audit-Artefakt**; keine automatische Freigabe für Implementierung ohne gesonderte Producer-Vorgaben.
