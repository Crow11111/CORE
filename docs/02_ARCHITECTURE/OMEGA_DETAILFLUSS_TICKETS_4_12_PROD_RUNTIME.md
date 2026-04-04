# OMEGA: Detailfluss Tickets 4–12 + Produktions-Runtime (kanonisch)

**Vektor:** 2210 | **Delta:** 0.049  
**Zweck:** Eine **einzige** Stelle, die aus den **Ticket-Spezifikationen** und dem **Verkehrsplan** ableitet: **wer** mit **wem**, **wo** (Host/Container/Port/Route), **Push vs. Pull**, **Timing** — und das **Pflichtbild „Omega ohne Dreadnought“**.

**Quellen (Primärtexte):** `TICKET_4` … `TICKET_12` unter `docs/05_AUDIT_PLANNING/`, `MACRO_CHAIN_MASTER_DRAFT.md`, `KONSOLIDIERTER_VERKEHRSPLAN_VPS_KONG_MCP.md` §7, `VPS_HOST_PORT_CONTRACT.md`, `infra/vps/kong/kong-deck-reference.yaml`.

---

## A. Produktionsprinzip: Dreadnought ≠ Omega-Runtime

| Begriff | Rolle |
|--------|--------|
| **Dreadnought (dein Arch-PC)** | **Entwicklungs- und Membran-Werkstatt:** Cursor, lokale Daemons (`omega-*`), schnelle Iteration, Git-Membrane (Ticket 9) misst hier physisch Dateien. |
| **Omega-Runtime (Prod-Ziel)** | **Kanal-unabhängiger Kern:** Gleiches Verhalten, ob Eingang **WhatsApp**, **OpenClaw**, **HTTP-API**, **Cursor-Remote** oder später anderer Client. **Kein** fester Bezug „Logik lebt nur auf Dreadnought“. |
| **Konsequenz** | Alles, was heute nur auf Dreadnought läuft (FastAPI :8000, Membrane, Worker), muss für Prod **deployierbar auf einem neutralen Host** sein (typ. **VPS** + definierte URLs). Dreadnought bleibt **Dev-Spiegel**, nicht **Soll-Endzustand**. |

**Messbar:** Dieselben Abnahmen (`run_vollkreis_abnahme.py` o. ä.) müssen gegen die **Prod-URL** der Omega-Runtime laufen können (Konfiguration über `CORE_BASE_URL` / `.env`, nicht hardcodiert `localhost`).

---

## B. Kong: Route → Upstream → Container (Ist + geplante Lücken)

**Host-Vertrag (Proxy/Admin/Manager):** `32776` / `32777` / `32778` → Container `kong-s7rk-kong-1` (8000/8001/8002).  
**Repo-Spiegel:** `infra/vps/kong/kong-deck-reference.yaml`.

| Kong-Route (Proxy) | Service-Name | Upstream (Docker DNS) | Container-Port | Strip | Status |
|--------------------|----------------|------------------------|----------------|-------|--------|
| `/evo` | `evolution-api` | `evolution-api-yxa5-api-1` | 8080 | ja | **live** (Deck) |
| `/health` | `omega-kong-health` | *dummy* + `request-termination` | — | nein | **live** (Body `OMEGA_KONG_HEALTH_OK`) |

**Aus `KONSOLIDIERTER_VERKEHRSPLAN` §7.3 — noch in Kong zu terminieren (Soll, nicht automatisch im Deck):**

| Gewünschter öffentlicher Pfad | Von | Nach (Soll) | Hinweis |
|------------------------------|-----|-------------|---------|
| Webhook WhatsApp / CORE-Ingress | Internet | **Omega-Runtime** `POST /webhook/whatsapp` (o. ä.) | Heute oft **Dreadnought-URL** oder Tunnel; **Prod:** hinter Kong + TLS, Secret |
| Weitere API | Internet | Omega FastAPI-Upstream | Upstream-Service + Route in Kong anlegen |
| Optional: OC hinter Kong | Internet | `openclaw-admin:18789` | Nur wenn bewusst gewünscht; heute oft **direkter Host-Port** |

---

## C. Tickets 4–7: Macro-Chain (Logik, Speicher, Timing)

**Speicher-Soll (Ticket 4):** Global Workspace / Job-Zustände in **Postgres** (Schema mit Zustandsmaschine `received` → `queued` → `processing` → …).  
**Laufzeit-Modul:** `src/logic_core/admission_control.py` (+ Tests `test_admission_control.py`).

| Ticket | Phase | Was passiert | Push / Pull | Timing / harte Grenze |
|--------|-------|--------------|-------------|------------------------|
| **4** | Admission / Reflex | Drift `D = clamp(0.049, R/(I+ε), 0.951)`; Circuit Breaker `admission_check`: ab **0.90** abweisen | **Pull:** R, I (Ressource, Info-Gewinn) aus Cache/Näherung — **darf synchronen Ingress nicht blockieren** | Reflex-ACK **extrem schnell** (Macro: **&lt; 1 s** bis ACK; Details `MACRO_CHAIN_MASTER_DRAFT.md`) |
| **5** | Arbitration | Scheduler nach `priority` **int** + `expected_arrival` **float**; Merge First-Wins; Liveness Heartbeat; A10 Evidenz | Jobs **lesen/schreiben** Workspace Postgres | Heartbeat-Timeout → Status `failed` (float-Zeit) |
| **6** | Efference / Veto | Efferenzkopie → `attractor_evaluate` → Release- oder Veto-Token; Signatur / A5-Werte | Push **Pain** async bei Veto (`dispatch_pain_signal`) | Veto-Fenster „blitzschnell“ (spec); kein Release ohne Token |
| **7** | Temporal / PE | PE berechnen, Trust adjust, kardanischer Rescue (`complex`, **P int**); `dispatch_to_evolution` nur mit ReleaseToken | Push zu Evolution nach Freigabe | Timeout → PE **0.951** (max Schmerz, gekappt) |

**Wo läuft das in Prod?** **Omega-Runtime-Prozess** (heute: FastAPI + Worker auf Dreadnought; **Soll:** derselbe Stack auf VPS oder Kubernetes) mit **Zugriff auf dieselbe Postgres-Instanz** wie im Workspace-Soll (kann `atlas_postgres_state` oder dedizierte DB sein — **eine** Wahrheit festlegen und nicht splitten).

---

## D. Tickets 8–9: Membrane & Git

| Ticket | Mechanik | Ort **heute** | Push / Pull | Timing |
|--------|-----------|---------------|-------------|--------|
| **8** | Pain-Flag `.py` bei Anti-Heroin-Verstoß; Planning-Flag `.md` ohne `[PASS]` | Dateisystem **Dev-Host** (`/tmp/omega_membrane_*.flag`) | **Push:** Flags blockieren Admission (Drift 0.951) / Ausführung | Reaktion auf **mtime** / Validator-Lauf |
| **9** | Auto-Push: `git add` → `commit` → `push` pro Datei nach Settle; Pull: `fetch` + `pull --rebase` | **Nur dort, wo das Repo liegt** (heute Dreadnought) | **Push** zu `origin/main`; **Pull** Remote → lokal | Settle **10 s**; Pull-Rhythmus **61 s** (Primzahl-Takt); Konflikt → Pain-Flag |

**Prod ohne Dread:** Membrane-Logik muss auf dem **Omega-DevOps-Host** laufen (kann derselbe VPS sein, auf dem das **Git**-Repo für Deploy liegt), **oder** durch CI/CD ersetzt werden — aber **semantisch** dieselben Sperren (kein Commit bei Heroin, kein Push bei Draft ohne PASS).

---

## E. Ticket 10: OpenClaw-Autarkie

| Kante | Von | Nach | Transport | Port (Vertrag) |
|-------|-----|------|-----------|----------------|
| Gateway | Omega-Runtime / Heartbeat | `openclaw-admin` | HTTP + Bearer | Host **18789** |
| Diagnose | Dreadnought-Skript | VPS per SSH | SSH + Docker | `VPS_SSH_KEY` |
| Autonomie-Veto | `infrastructure_heartbeat` | Datei-Flag | lokal auf **Runtime-Host** | z. B. `/tmp/omega_autonomy_veto.flag` bei Gateway-Fail |

**Timing:** Kein „Restart = Heilung“ ohne **unabhängigen** `check_gateway()`-HTTP-OK (Ticket 10 Schicht 1).

---

## F. Ticket 11: Kognitive Membran (Duale Topologie)

| Domäne | Technologie | Inhalt | Typ-Disziplin |
|--------|-------------|--------|----------------|
| **Int / Relationen** | **PostgreSQL** | Events, Kausalität, Metadaten | int / strukturiert |
| **Float / Semantik** | **ChromaDB** | Resonanzen, Lektionen | **float** (A6) |
| Pre-Flight | Agent-Start | `memory_hash` / Event-Stream via MCP | Zero-Trust |
| Apoptose | Idle-Cycle | Entropie &lt; Δ → Kardanischer Operator | Float-Cluster |
| Shapiro | Persistenz | Nur verzögert „stabile“ Lektionen persistieren | topologische Verzögerung (spec) |

**VPS-Bezug:** Chroma **Host `32779`** → `chroma-uvmy-chromadb-1:8000`. Postgres ggf. `atlas_postgres_state` **nur intern** — Omega-Runtime braucht **Connection String** (Tunnel oder gleiches Docker-Netz in Prod).

---

## G. Ticket 12: Epistemischer Antrieb (Inbound / Idle)

| Stufe | Komponente | Richtung | Timing / Steuerung |
|-------|------------|----------|---------------------|
| Edge | AuthN/Z, Schema, Rate | **Push** extern → Edge | TLS/mTLS/JWT |
| Queue | Streams + Idempotenz + `priority_float` | Puffer | Kein direkter Sprung in Business-Logik |
| Worker | Normalisierung → Event-Store / Ingest | **Pull** aus Queue | — |
| Pacemaker | **V**, **R** (nur float, nie 0/0.5/1.0) | Moduliert Sampling, Budget, Traum | **Eine** autoritative Schreiber-Instanz (Anti-Split-Brain) |
| Sentinel | HA, Vision, … | **Push** → Edge → Queue | Intervall ∝ **V** |
| Traum / Void | Consumer bei hohem **R**, leerer Queue | **Pull** + Synthese | OpenClaw **nur** aus erlaubtem Worker, **nicht** vom HA-Hot-Path |

**VPS:** Sentinel / Dream-Worker / Queue-Komponenten laut Masterplan **auf VPS** betreibbar; Kopplung an dieselbe Omega-Runtime-API wie Makro-Kette.

---

## H. Umsetzungs-Checkliste bis „Omega ohne Dread“

1. **Omega-Runtime** als Container oder systemd auf **VPS** (oder anderem Prod-Host): gleiche FastAPI-App wie lokal, `.env` mit `VPS_HOST`, DB-URLs, **kein** `localhost` als stiller Default für Webhooks.  
2. **Kong:** Routen für **öffentliche** Webhooks und API auf die Prod-Base-URL der Runtime (Tabelle B „Soll-Lücken“ schließen).  
3. **Postgres-Workspace** (Ticket 4–5): ein **definierter** DSN für Prod, identische Migrationen wie Dev.  
4. **Membrane (8–9):** entweder auf Prod-Host replizieren oder durch **CI-Pipeline** mit gleichen Invarianten ersetzen.  
5. **Abnahme:** `run_vollkreis_abnahme.py` parametrierbar auf `CORE_BASE_URL=https://…` (Implementierungs-Ticket falls noch nicht vorhanden).

---

[PASS] Detailfluss aus Tickets 4–12 konsolidiert; Prod-Ziel **Dreadnought optional** explizit.

**Pflege:** Bei Ticket-Änderung **diese Datei** und ggf. `kong-deck-reference.yaml` im **selben** Änderungssatz anpassen.
