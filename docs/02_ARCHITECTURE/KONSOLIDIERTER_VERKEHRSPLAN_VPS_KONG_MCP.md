# Konsolidierter Verkehrsplan: VPS, Kong, MCP, Gedächtnis

**Vektor:** 2210 | **Delta:** 0.049  
**Status:** Kanonisches Soll-/Ist-Konzept (Operator-Audit 2026-04-04) — **§7 mit realem `docker ps` vom VPS befüllt** (Messung 2026-04-04).  
**Zweck:** Aus **Plan**, **Tickets** und **messbarer Realität** **eine** erzählfähige Ordnung machen: wer darf wen wie erreichen, was „offen“ heißt, und wo Kong/MCP/Gedächtnis **nicht** dasselbe sind.

**Querschnitt:** `LANDKARTE_CLIENTS_KNOTEN_DATENFLUSS.md` · `VPS_KNOTEN_UND_FLUSSE.md` · **`VPS_HOST_PORT_CONTRACT.md`** · **`VPS_COMPOSE_PATHS.md`** · **`infra/vps/kong/kong-deck-reference.yaml`** · **`OMEGA_DETAILFLUSS_TICKETS_4_12_PROD_RUNTIME.md`** (Detail Push/Pull/Timing, Prod ohne Dread) · `MACRO_ARCHITECTURE_AUDIT.md` · `OMEGA_RESONANCE_ANCHOR.md` (§ Git-Resonanz) · Tickets **3–12** unter `docs/05_AUDIT_PLANNING/TICKET_*.md`

### Für den Operator (Architekt / PM)

Du **pflegst** keine Portliste. **Verbindlicher Vertrag:** `docs/03_INFRASTRUCTURE/VPS_HOST_PORT_CONTRACT.md` + `src/config/vps_public_ports.py`. **Pflegepflicht:** Agenten/Producer/Infra bei jedem Deploy. **Du** stimmst ab, ob `docker ps` zur Tabelle passt (oder beauftragst einen Check). Der **Anhang A** (`docker ps`-Dump) in diesem Dokument ist ein **Abnahme-Snapshot**, kein tägliches To-do — er wird bei **Vertrags- oder VPS-Wechsel** von der Technik aktualisiert.

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


**Wichtig:** „Chroma von Dreadnought nicht per HTTP erreichbar“ kann **Soll** sein (nur intern + Tunnel), während `docker ps` **Up** zeigt. Verifikation muss dann **Tunnel oder VPS-seitigen Client** nutzen — nicht nur `curl öffentliche_IP:<Host-Port>`. **Ist (siehe Anhang):** primärer Chroma-1.0.15-Hostport ist **`32779`→8000**, nicht mehr zwingend `32768` wie in älteren Tabellen — `.env` / `verify_vps_stack` an **Ist** anbinden.

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
| **4**  | Admission Control                                | `TICKET_4_`*, Logic-Core, Einlass vor teurer Arbeit                                         |
| **5**  | Arbitration / Job-Merge                          | `TICKET_5_`*, `arbitration_engine`, Postgres-Anbindung                                      |
| **6**  | Efference Veto / Signaturpfad                    | `TICKET_6_`*, `efference_veto`                                                              |
| **7**  | Temporal Alignment                               | `TICKET_7_`*, `temporal_alignment`, ReleaseToken-Kontrakt                                   |
| **8**  | Dreadnought-Membrane / Biometrie-Telemetrie      | `TICKET_8_`*, `dread_membrane_daemon`, Pain/Planning-Flags                                  |
| **9**  | Git-Resonanz (Auto-Push/Pull)                    | `TICKET_9_GIT_RESONANCE.md`, Membrane — **siehe Anker §5**                                  |
| **10** | OpenClaw Autarkie / Heal / Gateway-NMI           | `TICKET_10_OPENCLAW_AUTARKIE.md`, `heal_openclaw_vps`, `infrastructure_heartbeat`           |
| **11** | Kognitive Membran / Event-Sourcing / MCP-State   | `TICKET_11_`*, `event_store`, `mcp_omega_state`, Context-Watchdog                           |
| **12** | Epistemischer Antrieb / Queue / Sentinel / Traum | `TICKET_12_`*, `ingest_queue_client`, `vps_sentinel`, `vps_dream_worker`, Konzepte          |


**Gestern (Session-Kontext 2026-04-02–04):** Schwerpunkt **8–12** (Membrane-Git, OpenClaw-Heilpfad, kognitive Schicht, Queue + Dream/Sentinel), dazu **Tests** und **Doku** (O2-Split VPS-Autarkie, Masterpläne). Das **ändert nicht automatisch** Kong-Routen auf dem VPS — das ist **eigenes Deploy-Artefakt**.

**Hinweis „Ticket 1–2“:** Im Ordner `docs/05_AUDIT_PLANNING/` beginnt die **explizite** `TICKET_*.md`-Nummerierung bei **3–12** (v. a. Makro-Kette, Membrane, Git, OC, kognitive Membran, Epistemik). Ältere oder vorgelagerte Arbeiten stecken in **Specs** (`SPEC_PACEMAKER_*`, `VERIFICATION_FIRST_*`, `FULL_CHAT_AUDIT_RESULT`) — inhaltlich **vor** Ticket 3, aber nicht unter denselben Dateinamen.

---

## 7. Konsolidierter Verkehrsplan (messbarer Soll-/Ist-Abgleich)

### 7.1 Messung (Ist-Quelle)

| Feld | Wert |
|------|------|
| **Zeitpunkt** | 2026-04-04 (Snapshot erneuert, laufender VPS-Betrieb) |
| **Befehl** | `docker ps -a --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}'` |
| **Zugriff** | SSH `root@<VPS_HOST>` (wie `verify_vps_stack.py` / `.env`: `VPS_SSH_KEY`) |
| **Volltext** | **Anhang A** (unveränderte Ausgabe) |

### 7.2 Inventar VPS — Container → Host-Ports (**Ist**)

Öffentlich im Sinne von **Nord–Süd**: alles mit `0.0.0.0:<Port>->…` auf dem Host (sofern Firewall nichts dagegen sperrt).

| Logischer Dienst | Container-Name(n) | Host → Container | Nord–Süd erreichbar |
|------------------|-------------------|--------------------|------------------------|
| **Chroma 1.0.15** (primär) | `chroma-uvmy-chromadb-1` | **32779 → 8000** | Ja (HTTP Chroma im Container auf 8000) |
| **Kong** | `kong-s7rk-kong-1` | **32776 → 8000** (Proxy), **32777 → 8001** (Admin API), **32778 → 8002** (Manager/GUI je nach Setup) | Ja |
| **Kong DB** | `kong-s7rk-db-1` | kein Host-Mapping (nur 5432/tcp intern) | Nein (nur Ost–West) |
| **Evolution API** | `evolution-api-yxa5-api-1` | **55775 → 8080** | Ja |
| **Evolution Postgres/Redis** | `…-postgres-1`, `…-redis-1` | kein Host-Mapping | Nein |
| **OpenClaw (kanonisch)** | `openclaw-admin` | **18789 → 18789** | Ja |
| **OpenClaw Spine** | `openclaw-spine` | **18790 → 18790** | Ja |
| **Hostinger OpenClaw (hvps)** | `openclaw-ntw5-openclaw-1` | **58105 → 58105** | Ja |
| **Hostinger OpenClaw (wslc)** | `openclaw-wslc-openclaw-1` | **55800 → 55800** | Ja |
| **MCP-Server** | `mcp-server` | **8001 → 8001** | Ja |
| **Monica** | `monica-0mip-monica-1` | **32772 → 80** | Ja |
| **Monica DB** | `monica-0mip-db-1` | kein Host-Mapping | Nein |
| **Home Assistant (Remote)** | `ha-atlas` | **18123 → 8123** | Ja |
| **atlas_agi_core** | `atlas_agi_core` | **8080 → 8080** | Ja |
| **Postgres (atlas_state)** | `atlas_postgres_state` | kein Host-Mapping | Nein |
| **Chroma (Legacy AGI-State)** | `atlas_chroma_state` | kein Host-Mapping (8000/tcp nur intern) | Nein |

**Abgleich Doku-Drift:** Vertrags- und Ist-Hostports: Chroma **32779**, Kong **32776–32778** (`VPS_HOST_PORT_CONTRACT.md`, `verify_vps_stack.py`, `verify_vps_docker_port_contract.py`). Historisch: **32768** / **32773–32775** — nicht mehr kanonisch.

### 7.3 Pfad-Matrix (Soll + **Ist** nach Messung)

| Pfad | Von | Nach | Transport (Soll) | Auth (Soll) | **Ist-Status (2026-04-04)** |
|------|-----|------|------------------|-------------|----------------------------|
| WhatsApp eingehend | Evolution | CORE `/webhook/whatsapp` | Kong → FastAPI oder direkt | Webhook-Secret / API-Key | **Evolution lauscht auf Host 55775**; Ziel-CORE meist **Dreadnought**, nicht Container auf VPS — Webhook-URL muss **öffentlich erreichbar** sein (Tunnel/Reverse-DNS). Kong-Routen dafür **nicht** im Dump sichtbar (nur Ports). |
| WhatsApp ausgehend | CORE | Evolution `sendText` | HTTP zu Evolution-API | API-Key | **Ziel erreichbar:** `http://<VPS_HOST>:55775` (API im Container 8080). |
| RAG / Vektoren | CORE | Chroma 1.0.15 | Client → Host-Port oder intern | ggf. API-Key/Tunnel | **Host-Port Ist: 32779** (healthy). Dreadnought: `CHROMA_PORT=32779` prüfen; Heartbeat: `GET …:32779/api/v2/heartbeat`. |
| Strukturiert / pgvector | CORE | `atlas_postgres_state` | Docker-Netz oder SSH-Tunnel | DB-User | **Kein Host-Port** — nur **Ost–West** oder Tunnel; Zugriff von außen nur mit **SSH/Compose-Netzwerk** oder Sidecar. |
| OC-Gateway | CORE | OpenClaw Admin | HTTP | Bearer | **18789 published** — mit `check_gateway()` von Dreadnought messbar OK (vorherige Messung). |
| OC alternativ | — | Hostinger-Instanzen | HTTP | je Instanz | **58105** und **55800** zusätzlich live — **welche Instanz Soll ist**, im Kanon festlegen (Zwillings-Risiko). |
| GitHub → Pull | GitHub | VPS/CORE | Webhook POST | Secret | **Unverändert:** nur wenn FastAPI-Webhook unter **öffentlicher URL** hängt; **nicht** durch `docker ps` allein belegt. |
| Cursor Cloud MCP | Cursor | `mcp-server` | SSH + `docker exec` | SSH-Key | **Host 8001 published** — zusätzlich zu SSH möglich, aber **aktuell** Cursor-Config nutzt SSH-Pfad; beides dokumentiert. |
| Operator / Kong Admin | Du | Kong Admin API | HTTPS/HTTP | Admin-Token | **Ist: Host 32777 → 8001** — von außen erreichbar, wenn Firewall offen; **Routes/Inhalt** weiterhin per `deck`/Admin-API prüfen, nicht aus `docker ps` ableitbar. |
| Monica CRM | CORE / Agent | Monica | HTTP | Token | **Ist: Host 32772 → 80** — Soll-URL `MONICA_URL` auf `:32772` abstimmen. |
| Remote HA UI | Du / Bridge | HA | HTTP | HA-Auth | **Ist: 18123 → 8123**. |
| AGI-State-App | intern | `atlas_agi_core` | HTTP | je Deploy | **Ist: 8080 published** — bewusst exponiert; Absicherung klären. |

---

## Anhang A — Rohausgabe `docker ps -a` (VPS)

Messung 2026-04-04, Format: `NAMES`, `IMAGE`, `STATUS`, `PORTS`.

```
NAMES                           IMAGE                                          STATUS                   PORTS
mcp-server                      mcp-server-mcp-server                          Up 2 hours               0.0.0.0:8001->8001/tcp, [::]:8001->8001/tcp
chroma-uvmy-chromadb-1          chromadb/chroma:1.0.15                         Up 15 hours (healthy)    0.0.0.0:32779->8000/tcp, [::]:32779->8000/tcp
openclaw-ntw5-openclaw-1        ghcr.io/hostinger/hvps-openclaw:latest         Up 15 hours              0.0.0.0:58105->58105/tcp, [::]:58105->58105/tcp
evolution-api-yxa5-api-1        evoapicloud/evolution-api:latest               Up 18 hours              0.0.0.0:55775->8080/tcp, [::]:55775->8080/tcp
evolution-api-yxa5-postgres-1   postgres:15                                    Up 18 hours              5432/tcp
evolution-api-yxa5-redis-1      redis:latest                                   Up 18 hours              6379/tcp
kong-s7rk-kong-1                kong:latest                                    Up 18 hours (healthy)    8443-8444/tcp, 0.0.0.0:32776->8000/tcp, [::]:32776->8000/tcp, 0.0.0.0:32777->8001/tcp, [::]:32777->8001/tcp, 0.0.0.0:32778->8002/tcp, [::]:32778->8002/tcp
kong-s7rk-kong-migrations-1     kong:latest                                    Exited (0) 2 weeks ago   
kong-s7rk-db-1                  postgres:16                                    Up 18 hours (healthy)    5432/tcp
monica-0mip-monica-1            monica:latest                                  Up 18 hours              0.0.0.0:32772->80/tcp, [::]:32772->80/tcp
monica-0mip-db-1                mariadb:11                                     Up 18 hours              3306/tcp
openclaw-wslc-openclaw-1        ghcr.io/hostinger/hvps-openclaw:latest         Up 18 hours              0.0.0.0:55800->55800/tcp, [::]:55800->55800/tcp
openclaw-admin                  ghcr.io/openclaw/openclaw:main                 Up 18 hours (healthy)    0.0.0.0:18789->18789/tcp, [::]:18789->18789/tcp
atlas_agi_core                  agi-state-agi-core:fixed                       Up 18 hours              0.0.0.0:8080->8080/tcp, [::]:8080->8080/tcp
atlas_postgres_state            pgvector/pgvector:pg15                         Up 18 hours              5432/tcp
atlas_chroma_state              chromadb/chroma:0.4.24                         Up 18 hours              8000/tcp
openclaw-spine                  268aaf9fde39                                   Up 18 hours              0.0.0.0:18790->18790/tcp, [::]:18790->18790/tcp
ha-atlas                        ghcr.io/home-assistant/home-assistant:stable   Up 18 hours              0.0.0.0:18123->8123/tcp, [::]:18123->8123/tcp
```

---

## 8. Nächste Schritte (Arbeitsaufträge an die Technik, nicht an den Operator)

1. **Erledigt (Repo-Lieferung):** Verbindliche Port-Tabelle + Python-Modul `vps_public_ports.py` + Anbindung in `verify_vps_stack`, Heartbeat, Gravitator, `chroma_client`, Vollkreis — siehe `VPS_HOST_PORT_CONTRACT.md`.
2. **Deploy auf dem VPS:** Docker-Compose **Host-Ports vernageln** (YAML), exakt wie Vertrag — kein zufälliges Re-Mapping durch Panels. **Ist-Pfade:** `docs/03_INFRASTRUCTURE/VPS_COMPOSE_PATHS.md`.
3. **Kong-Deklaration:** Services+Routes (Evolution-Webhook, Health, **omega-core-backend** → Docker-Host `http://172.17.0.1:32800`, Route **`/status`**) — **als Code** im Repo (YAML/Deck); nach Änderung Verifikation erweitern. **Artefakt:** `infra/vps/kong/kong-deck-reference.yaml` (+ `README.md`); Abgleich durch `python -m src.scripts.verify_vps_stack`. Live: deck sync / Admin-API manuell (siehe `infra/vps/kong/README.md`).
4. **`.env`:** Soll = Vertragsports; Overrides nur bewusst. Optional `VPS_GATEWAY_URL`, wenn alles über Kong soll.
5. **Snapshot:** Bei Infra-Change **Anhang A** dieses Dokuments + ggf. Session-Log durch Producer ersetzen/ergänzen.

---

## 9. Ein Satz fürs Team

**Kong** soll der **benannte Torwart** für **öffentlichen** HTTP-Verkehr werden; **MCP** bleibt das **Werkzeugkabel** für **KI-Arbeit**; **Gedächtnis** lebt in **Chroma/Postgres/Queue** und wird vom **Backend** geführt — bis das im Deploy nachvollziehbar ist, ist das Chaos **kein** Denkfehler des Operators, sondern **fehlende Deklaration** der bereits skizzierten Pläne.

---

[PASS] Konsolidierter Verkehrsplan — Kanon, Tickets 3–12, Kong/MCP/Gedächtnis; **§7 + Anhang A mit VPS-`docker ps` 2026-04-04** (messbarer Ist-Stand).