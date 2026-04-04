# Konsolidierter Verkehrsplan: VPS, Kong, MCP, Gedächtnis

**Vektor:** 2210 | **Delta:** 0.049  
**Status:** Kanonisches Soll-/Ist-Konzept (Operator-Audit 2026-04-04)  
**Zweck:** Aus **Plan**, **Tickets** und **messbarer Realität** **eine** erzählfähige Ordnung machen: wer darf wen wie erreichen, was „offen“ heißt, und wo Kong/MCP/Gedächtnis **nicht** dasselbe sind.

**Querschnitt:** `LANDKARTE_CLIENTS_KNOTEN_DATENFLUSS.md` · `VPS_KNOTEN_UND_FLUSSE.md` · `MACRO_ARCHITECTURE_AUDIT.md` · `OMEGA_RESONANCE_ANCHOR.md` (§ Git-Resonanz) · Tickets **3–12** unter `docs/05_AUDIT_PLANNING/TICKET_*.md`

---

## 1. Warum es sich wie „Krampf“ anfühlt (und das strukturell ist)


| Symptom                                         | Ursache                                                                                                                                                                                                                             |
| ----------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Jeder Dienst hat **einen eigenen Port** im Kopf | Docker-Compose-Realität + `.env`-Fragmente; **kein** durchgängig dokumentierter **Ingress** auf dem VPS.                                                                                                                            |
| **Kong läuft**, aber „steht nichts drin“        | Container **Up** ≠ **Routen/Services/Upstreams** deklariert. Der Plan sagt „kann über Kong“ — die **Deklaration** fehlt operativ.                                                                                                   |
| **MCP** fühlt sich wie Gedächtnis an            | MCP ist **Protokoll KI↔Tool**; **persistente** Wahrheit bleibt **Chroma + Postgres** (siehe `MACRO_ARCHITECTURE_AUDIT.md` §3). MCP **kann** lesen/schreiben — darf aber **nicht** die einzige Definition von „wo lebt Wissen“ sein. |
| **SSH** überall                                 | **Ops- und Cursor-Cloud-Pfad** (`mcp_remote_config.json`: `ssh` → `docker exec` → MCP). Das ist **kein** Ersatz für einen **HTTP-Vertrag** nach außen — und sollte im Kanon **benannt**, nicht verleugnet werden.                   |
| **Git-Membrane** pusht nur Teilmengen           | `OMEGA_RESONANCE_ANCHOR.md` §5: Auto-Push nur `src/**/*.py` + ausgewählte `docs/**/*.md` — **kein** Gesamt-Repo-Sync.                                                                                                               |


**Fazit:** Der **Kreis** im Sinne der Theorie (geschlossene Kausalität) ist **nur dort** geschlossen, wo **messbar** (Webhook 200, Heartbeat, Test grün). Alles andere ist **Ansammlung von Sonderwegen**, bis **ein** Verkehrsplan **deklariert und deployed** ist.

---

## 2. Drei Schichten — und was „offen“ bedeutet


| Schicht                             | Frage                                      | „Offen“ heißt hier                                                                                                                                    |
| ----------------------------------- | ------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Nord–Süd (Internet → VPS)**       | Darf ein Client von außen TCP erreichen?   | **Nur** was **UFW + Publish** erlauben (typ. 22, 80/443, wenige App-Ports). Alles andere: **refused** oder **timeout** von außen ist **oft korrekt**. |
| **Ost–West (Docker intern)**        | Dürfen Container sich untereinander sehen? | **Bridge-Netz** / Compose-Netz: Dienste sprechen **Containername:Port**, **ohne** dass der Host alles nach außen mappt.                               |
| **KI-Tooling (MCP / Cursor Cloud)** | Wie kommt ein Agent an Werkzeuge?          | **Stdio/SSH-Tunnel** zum MCP-Prozess — **parallel** zur Produkt-API; **nicht** zwingend über Kong.                                                    |


**Wichtig:** „Chroma von Dreadnought nicht per HTTP erreichbar“ kann **Soll** sein (nur intern + Tunnel), während `docker ps` **Up** zeigt. Verifikation muss dann **Tunnel oder VPS-seitigen Client** nutzen — nicht nur `curl öffentliche_IP:32768`.

---

## 3. Sollbild: Ein Kreis, zwei legitime Einstiege

### 3.1 Produkt- und Daemon-Pfad (OMEGA-CORE)

**Zielbild (noch nicht überall Ist):**

1. **Ein öffentlicher Eingang** für Webhooks und ggf. API: idealerweise **Kong** auf **443/80** (TLS), nicht zehn Roh-Ports.
2. Kong **routet** zu Upstreams: z. B. CORE-FastAPI (falls auf VPS), Evolution-Webhook-Eingang, ggf. interne Health-Routen — **explizit als Deklaration** (Services, Routes, Plugins).
3. **Backend/Dreadnought** (wenn lokal): spricht **entweder** `VPS_GATEWAY_URL` (Kong) **oder** direkt interne Ports — **eine** Strategie pro Umgebung, in `.env` und Tabelle festgeschrieben.
4. **Gedächtnis:** Lesen/Schreiben der **Wahrheit** über `**chroma_client` / `multi_view_client` / Queue-DB** im Backend-Code — **nicht** über MCP als Primärpfad.

Das entspricht der **Macro-Kette** (`SPEC_STATE_HOLD.md`, `MACRO_ARCHITECTURE_AUDIT.md`): Webhook **schnell** quittieren, Arbeit **persistiert** und **entkoppelt**.

### 3.2 Entwickler- und Cloud-Agent-Pfad (MCP)

- **Rolle:** Experiment, Refactor, Dateizugriff, ggf. Chroma-Query-Tool — **Nebenbahn** zur laufenden Geschäftslogik (`LANDKARTE` §3, `MACRO` §3).
- **Heutiger pragmatischer Pfad:** SSH + `docker exec` → MCP im Container (`mcp_remote_config.json`).
- **Risiko:** Wenn Agenten **nur** MCP nutzen und Backend-Pfade **nicht** die gleichen DBs ansprechen, entsteht **Drift**. **Abhilfe:** dieselben **Connection-Strings/Collections** dokumentieren; idealerweise **ein** MCP-Tool-Layer, der dieselben Client-Module nutzt wie FastAPI.

---

## 4. Kong: Plan vs. Realität


| Aspekt                   | Plan (Doku)                                                          | Typische Realität (Ist)                                                      |
| ------------------------ | -------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| Rolle                    | Zentrales Routing, Rate-Limits, Auth (`VPS_KNOTEN_UND_FLUSSE.md` §4) | Container läuft; **Routes** oft **leer** oder Default                        |
| CORE `.env`              | `VPS_GATEWAY_URL` statt Einzelports (§4)                             | Noch **direkte** `VPS_HOST:Port`-Variablen                                   |
| Erreichbarkeit Admin-API | Port 32773 etc.                                                      | Oft **nicht** von außen (localhost bind / Firewall) — **okay**, wenn bewusst |


**Konsolidierungsregel:** Sobald Kong Soll ist, gehört **jeder neue öffentliche Endpunkt** als **Route** in Kong — **kein** zusätzlicher Host-Port ohne Review.

---

## 5. MCP vs. Gedächtnis (präzise)


| Begriff                               | Was es **ist**                                                                | Was es **nicht** ist                                                 |
| ------------------------------------- | ----------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| **Gedächtnis (persistente Wahrheit)** | Chroma (Vektoren), Postgres/pgvector (strukturiert), Ingest-Queue (Ticket 12) | „Was der Cursor gerade im Chat weiß“                                 |
| **MCP**                               | Transport für **Tools** (Filesystem, ggf. DB-Query), oft **sessiongebunden**  | Single Source of Truth                                               |
| **OpenClaw**                          | Externes **Gateway** (LLM, Kanäle)                                            | Ersatz für CORE-DBs; arbeitet **mit** ihnen, wenn richtig angebunden |


---

## 6. Tickets 3–12 — was diese Linie **thematisch** abdeckt (Repo-Stand)

*Hinweis: Im Repo sind **TICKET_3** ff. nicht alle als einzelne Datei `TICKET_3_*.md` benannt; Pacemaker/Admission sind in Specs und Repair-Plänen gebündelt. Unten: **inhaltliche** Zuordnung.*


| Nr.    | Thema (Kurz)                                     | Wo im Repo / Fokus                                                                          |
| ------ | ------------------------------------------------ | ------------------------------------------------------------------------------------------- |
| **3**  | Pacemaker / metabolische Homeostase (VAR_3)      | `MASTERPLAN_REPAIR_TICKETS_3_5_6_7.md`, `SPEC_PACEMAKER_VAR_3.md`, `omega_pacemaker`, Tests |
| **4**  | Admission Control                                | `TICKET_4_*`, Logic-Core, Einlass vor teurer Arbeit                                         |
| **5**  | Arbitration / Job-Merge                          | `TICKET_5_*`, `arbitration_engine`, Postgres-Anbindung                                      |
| **6**  | Efference Veto / Signaturpfad                    | `TICKET_6_*`, `efference_veto`                                                              |
| **7**  | Temporal Alignment                               | `TICKET_7_*`, `temporal_alignment`, ReleaseToken-Kontrakt                                   |
| **8**  | Dreadnought-Membrane / Biometrie-Telemetrie      | `TICKET_8_*`, `dread_membrane_daemon`, Pain/Planning-Flags                                  |
| **9**  | Git-Resonanz (Auto-Push/Pull)                    | `TICKET_9_GIT_RESONANCE.md`, Membrane — **siehe Anker §5**                                  |
| **10** | OpenClaw Autarkie / Heal / Gateway-NMI           | `TICKET_10_OPENCLAW_AUTARKIE.md`, `heal_openclaw_vps`, `infrastructure_heartbeat`           |
| **11** | Kognitive Membran / Event-Sourcing / MCP-State   | `TICKET_11_*`, `event_store`, `mcp_omega_state`, Context-Watchdog                           |
| **12** | Epistemischer Antrieb / Queue / Sentinel / Traum | `TICKET_12_*`, `ingest_queue_client`, `vps_sentinel`, `vps_dream_worker`, Konzepte          |


**Gestern (Session-Kontext 2026-04-02–04):** Schwerpunkt **8–12** (Membrane-Git, OpenClaw-Heilpfad, kognitive Schicht, Queue + Dream/Sentinel), dazu **Tests** und **Doku** (O2-Split VPS-Autarkie, Masterpläne). Das **ändert nicht automatisch** Kong-Routen auf dem VPS — das ist **eigenes Deploy-Artefakt**.

---

## 7. Konsolidierter Verkehrsplan (Pfad-Matrix — auszufüllen mit SSH-Inventar)

**Pflichtprozess:** Einmalig (und nach jedem Compose-Wechsel) auf dem VPS: `docker ps --format 'table {{.Names}}\t{{.Ports}}'`, Ergebnis in **Anhang** dieser Datei oder `VPS_KNOTEN_UND_FLUSSE.md` §1 spiegeln.


| Pfad               | Von       | Nach                     | Transport (Soll)                                                 | Auth (Soll)              | Ist-Status                                  |
| ------------------ | --------- | ------------------------ | ---------------------------------------------------------------- | ------------------------ | ------------------------------------------- |
| WhatsApp eingehend | Evolution | CORE `/webhook/whatsapp` | Kong → FastAPI **oder** direkt (nur **eine** Variante festlegen) | Webhook-Secret / API-Key | Teilweise HA-Pfad stärker (`VPS_KNOTEN` §6) |
| WhatsApp ausgehend | CORE      | Evolution `sendText`     | HTTP intern                                                      | API-Key                  | Implementierungslücke vs. HA                |
| RAG / Vektoren     | CORE      | chroma-uvmy              | Intern Docker **oder** Gateway                                   | Kein Welt-Port / Tunnel  | Oft nur intern                              |
| Strukturiert       | CORE      | Postgres                 | Intern Docker                                                    | DB-User                  | Üblich                                      |
| OC-Gateway         | CORE      | openclaw-admin:18789     | HTTP                                                             | Bearer                   | Zuletzt messbar OK (lokal)                  |
| GitHub → Pull      | GitHub    | VPS/CORE                 | Webhook POST                                                     | Secret                   | Nur wenn Listener auf VPS erreichbar        |
| Cursor Cloud MCP   | Cursor    | mcp-server               | **SSH** + `docker exec`                                          | SSH-Key                  | Funktional, **nicht** Kong                  |
| Operator Admin     | Du        | Kong / Docker            | SSH + optional UI                                                | SSH                      | Unvollständig dokumentiert                  |


---

## 8. Nächste Schritte (ohne neue „Sonderstraße“)

1. **SSH-Inventar** (ein Dokument, eine Tabelle): Namen, Host-Ports, Bridge-Ziele, **wer** (Dreadnought / Internet / nur localhost) darf zugreifen.
2. **Kong-Deklaration:** Minimaler Satz Services+Routes (Evolution-Webhook, ggf. Health, später CORE-Proxy) — **als Code** im Repo (deklarativ YAML/Deck), nicht nur Prosa.
3. `**.env`-Konsolidierung:** Entweder `**VPS_GATEWAY_URL`** durchsetzen **oder** bewusst „direkte Ports“ mit Tabelle — **kein** Mix ohne Doku.
4. **Verifikationsskripte** an **Soll** anbinden: Wenn Chroma nur intern, dann `verify_vps_stack` **Tunnel-Modus** oder „erwarteter Timeout von außen“ dokumentieren.
5. **Session-Log** mit Datum: Kong-Routen-Stand, offene Lücken — Makro-Audit-Empfehlung (Sequenzdiagramm In→Queue→Out) **einmal** zeichnen.

---

## 9. Ein Satz fürs Team

**Kong** soll der **benannte Torwart** für **öffentlichen** HTTP-Verkehr werden; **MCP** bleibt das **Werkzeugkabel** für **KI-Arbeit**; **Gedächtnis** lebt in **Chroma/Postgres/Queue** und wird vom **Backend** geführt — bis das im Deploy nachvollziehbar ist, ist das Chaos **kein** Denkfehler des Operators, sondern **fehlende Deklaration** der bereits skizzierten Pläne.

---

[PASS] Konsolidierter Verkehrsplan — Abgleich Kanon, Tickets 3–12, Kong/MCP/Gedächtnis; Operator-Audit 2026-04-04.