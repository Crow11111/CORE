# Reality Check: VPS 187.77.68.250 vs. Ticket-/Session-Behauptungen

**Rolle:** Ring-1 Zero-Trust Infrastructure Auditor & Docker Specialist  
**Ziel-Host:** `187.77.68.250` (root, SSH mit Hostinger-Key wie in `src/scripts/verify_vps_stack.py`)  
**Prüfzeitpunkt:** 2026-04-03 (Live-Abgleich, keine Rekonstruktion aus Logs allein)

**Methodik:** `docker exec` auf `atlas_postgres_state` (DB `atlas_state`, User `atlas_admin`), `docker ps -a`, `find` nach Daemon-Dateien, `systemctl`, Lesen der Compose-Dateien unter `/docker/…`, Kong Admin API (`/services`), HTTP-Proben.

**Einschränkung (Ehrlichkeit):** Ein erster SSH-Versuch aus einer Agent-Umgebung **ohne** expliziten Key endete mit `Permission denied (publickey,password)`. Die hier dokumentierten **physischen** Fakten stammen von einer erfolgreichen Session mit `-i /home/mth/.ssh/id_ed25519_hostinger`. Ohne diesen Schlüssel (oder gleichwertige Credentials) ist die gleiche Verifikation für Dritte nicht reproduzierbar.

---

## 1. WAS WURDE BEHAUPTET (Illusion)

Quellen: `SESSION_LOG_2026-04-01_COGNITIVE_MEMBRANE.md`, `SESSION_LOG_2026-04-03_EPISTEMIC_DRIVE_EXEC.md`, `MASTERPLAN_TICKET_11_EXECUTION.md`, `MASTERPLAN_TICKET_12_EXECUTION.md`, `O2_AUDIT_TICKET_11_EXECUTION.md`, `O2_AUDIT_TICKET_12_EXECUTION.md`.

| Behauptung / Implikation | Quelle (kurz) |
|--------------------------|---------------|
| Ticket 11: Event-Sourcing mit `omega_events` in PostgreSQL; Membran-Säulen „operativ“; Neuentwicklungen der „Datenbank beigefügt“. | Session 2026-04-01 §1, §4 |
| Ticket 12: Ingest-Perimeter und Queue **auf dem VPS**; Tabelle `omega_ingest_queue`; Sentinel- und Dream-Daemon als VPS-Steuerung; Fazit: hybride Architektur **„physisch“** umgesetzt; OpenClaw habe autarkes Sensorik-/Denk-Subsystem **auf dem VPS**. | `SESSION_LOG_2026-04-03_EPISTEMIC_DRIVE_EXEC.md` (insb. Fazit) |
| Masterplan 12 Phase 1: Queue **und** Normalisierung in `omega_events` (Dedupe, validierte Events). | `MASTERPLAN_TICKET_12_EXECUTION.md` |
| O2 Ticket 11: Formale Abnahme, pytest-grün = ausreichender Nachweis für die Ausführungsphase. | `O2_AUDIT_TICKET_11_EXECUTION.md` |
| O2 Ticket 12: Nach Re-Audit `[PASS]`, aber Architektur nur **teilweise** (Queue→`omega_events` fehlt im Code; Dream ohne echten RAG/OpenClaw/Chroma-Schreibpfad). | `O2_AUDIT_TICKET_12_EXECUTION.md` §3 |

**Kern der Illusion:** Session-Logs und Orchestrator-Sprache mischen **Repo-Artefakte + lokale pytest-Läufe** mit **„physisch auf dem VPS“**. Das ist ohne unabhängige VPS-Evidenz nicht dasselbe wie Axiom A7-konforme Wahrheit.

---

## 2. WAS IST DIE REALITÄT AUF DEM VPS (Fakt)

### 2.1 PostgreSQL `atlas_postgres_state` → Datenbank `atlas_state`

- **`omega_events`:** Tabelle **existiert**. Spalten: `id` (uuid, default `gen_random_uuid()`), `timestamp`, `agent_id`, `event_type`, `content` (jsonb), `memory_hash` (text). Indizes wie erwartet (`idx_omega_events_ts`, `agent`, `type`).
- **`omega_events` Daten:** `SELECT COUNT(*) FROM omega_events` → **0 Zeilen**. Die DB „weiß“ strukturell von Events; es gibt **keinen** persistierten episodischen Verlauf aus realem Betrieb auf diesem Stand.
- **`omega_ingest_queue`:** `to_regclass('public.omega_ingest_queue')` → **NULL**. Tabelle **fehlt vollständig**. Kein `FOR UPDATE SKIP LOCKED`, kein Perimeter in dieser Datenbank.

### 2.2 Dateisystem und Prozesse (Ticket-12-Daemons)

- Suche nach `vps_sentinel_daemon.py` / `vps_dream_worker.py` unter typischen Pfaden (`/root`, `/opt`, `/var`, `/home`, begrenzte Tiefe): **keine Treffer**.
- **systemd:** Keine Units mit `sentinel` oder `dream` im Namen. Vorhanden u. a. `omega-logos.service` (**inactive dead**), `omega-nerve-stem.service` (**active running**) — das sind **nicht** die im Repo unter `src/daemons/vps_*.py` geführten Ticket-12-Prozesse.

**Fakt:** Die in `src/daemons/vps_sentinel_daemon.py` und `vps_dream_worker.py` implementierte Logik ist **nicht** als deployte Dateien oder Dienste auf diesem VPS nachweisbar.

### 2.3 Docker-Gesamtbild (Auszug)

Zur Prüfzeit lief u. a.:

- **Evolution:** `evolution-api-yxa5-api-1` **Up**, Port **55775→8080**. Eigener Compose-Pfad: `/docker/evolution-api-yxa5/docker-compose.yml` mit **Postgres + Redis + API**, Traefik-Labels (`websecure`, Host `evolution-api-yxa5.srv1423569.hstgr.cloud`), `SERVER_URL` mit `VPS_IP` und `PORT`. HTTP-Root liefert JSON „Welcome to the Evolution API“ (Version 2.3.7).
- **Kong:** `kong-s7rk-kong-1` **Up (healthy)**; eigene Postgres-DB im Stack; `kong-s7rk-kong-migrations-1` **Exited (0)**. Ports 32773 (Proxy), 32774 (Admin), 32775 (GUI).
- **OpenClaw:** `openclaw-admin` **Up**; `openclaw-spine` **Up**; zusätzlich `openclaw-wslc-openclaw-1`.
- **Chroma (öffentlicher Port laut Doku/Verify):** `chroma-uvmy-chromadb-1` **Exited (255)** mit Mapping **32768→8000**. Der Heartbeat über `http://187.77.68.250:32768` ist damit **nicht** nutzbar.
- **Weitere:** `atlas_postgres_state`, `atlas_chroma_state`, `atlas_agi_core`, `mcp-server`, `ha-atlas`, Monica-Stack (`monica-0mip-monica-1` mit Host-Port **32772**→80; in `VPS_KNOTEN_UND_FLUSSE.md` ist **32769** dokumentiert — **Doku/Realität divergent**), usw.

`/opt/atlas-vps-stack/docker-compose.yml` beschreibt u. a. `chroma-atlas` auf **127.0.0.1:8000** und andere Port-Mappings; die **laufende** Containerlandschaft weicht teils ab (z. B. Spine-Port in `docker ps` vs. Datei — Anzeichen paralleler Deploy-/Panel-Generation vs. statische Repo-Compose).

---

## 3. WAS IST „BULLSHIT“ UND NICHT FERTIG

1. **„Physisch auf dem VPS umgesetzt“ (Session 2026-04-03 Fazit)** für Ticket 12: **Falsch** in der strengen Bedeutung. Auf dem VPS fehlen `omega_ingest_queue`, deployte `vps_*`-Daemons und jeder systemd-Haken dafür. Was existiert, ist **hauptsächlich im Git-Repo + pytest**.
2. **„OpenClaw verfügt nun über … Subsystem auf dem VPS“** als Folge dieser Session: **Nicht belegbar** durch die geprüften Artefakte. OpenClaw-Container laufen, aber die neue Queue-/Sentinel-/Dream-Kette ist **nicht** in `atlas_state` oder als Prozess angekommen.
3. **Masterplan 12 Phase 1 (Normalisierung in `omega_events`):** Im Repo bestätigt O2 selbst: **kein** Codepfad, der aus der Queue dedupliziert und nach `omega_events` schreibt. Auf dem VPS fehlt zusätzlich die Queue-Tabelle — **doppelte Lücke**.
4. **Masterplan 12 Phase 3 (RAG/Chroma/OpenClaw im Dream Worker):** O2: **Gerüst**, `_trace_has_chroma_counterpart` u. ä. nicht als End-to-End implementiert. **Kein Widerspruch zur VPS-Realität** — beides ist unvollständig.
5. **Ticket-11-Session-Formulierung „Datenbank beigefügt“:** Schema für `omega_events` ist auf dem VPS vorhanden, **Inhalt 0**. Wer „beigefügt“ als „Zeilen aus Produktivnutzung“ meint: **nicht erfüllt**.

---

## 4. DOCKER/INFRASTRUKTUR-ZUSTAND (Kong, Evolution, OpenClaw)

### 4.1 Warum wirkt es „teilweise eingerichtet“?

- **Zwei parallele Welten:** Stacks unter **`/docker/<projekt>`** (Kong `kong-s7rk`, Evolution `evolution-api-yxa5`) vs. **`/opt/atlas-vps-stack/docker-compose.yml`**. Das erzeugt den Eindruck von **mehreren Halb-Topologien** ohne eine einzige kanonische Compose-Quelle auf dem Host.
- **Kong:** Läuft, DB erreichbar, Healthcheck grün — aber **Kong Admin API `GET /services` liefert `"data":[]`**. Es sind **keine Services/Routen** konfiguriert. Aufruf der **Proxy**-Port (32773) auf `/` → **404** „no Route matched“. Das Gateway ist ein **leerer Rahmen**: betriebsbereite Shell, **keine** produktive Weiterleitung zu Evolution, Chroma, OpenClaw o. ä.
- **Evolution:** Im Gegensatz dazu **vollständiger** Mini-Stack (eigene DB, Redis, Env, Volumes, Traefik für HTTPS, plus Host-Port 55775). Das ist **nicht** „halbfertig“ im Kong-Sinne; es ist **eigenständig nutzbar**, während Kong **noch nicht** als einheitlicher Eingang verdrahtet ist.
- **OpenClaw:** Mehrere Images/Container (Admin, Spine, WSLC-One-Click). Das ist **operativ mächtig**, aber erhöht **Konfigurations- und Secret-Fläche**; keine der geprüften Stellen zeigt die Ticket-12-Python-Daemons als Teil dieses Stacks.
- **Chroma:** Der für Dreadnought-Skripte dokumentierte öffentliche Port **32768** hängt an einem **gestoppten** `chroma-uvmy-chromadb-1`. Parallel existiert `atlas_chroma_state` (intern 8000). **Ergebnis:** „Chroma auf dem VPS“ ist **nicht** ein klarer Single Point of Truth aus Sicht des Host-Ports 32768.

**Kurzfassung:** Evolution ist **stack-complete**; Kong ist **runtime-complete, config-empty**; Gesamtstack ist **fragmentiert** (Pfade, Ports, gestorbene uvmy-Chroma-Instanz).

---

## 5. DATENBANK-ZUSTAND — WAS SIE WISSEN, WAS SIE WISSEN SOLLTE

| Thema | Soll (laut Plänen / Tickets) | Ist auf VPS (`atlas_state`) |
|-------|------------------------------|-----------------------------|
| Episodische Historie | Append-only `omega_events`, MCP/Clients lesen/schreiben | **Schema ja**, **0 Events** — keine episodische „Wahrheit“ im Store |
| Ingest-Queue | `omega_ingest_queue`, Sentinel nur Queue | **Tabelle fehlt** |
| Überführung Queue → Events | Normalisierung, Idempotenz, Schreiben nach `omega_events` | **Weder DB noch (laut O2) vollständiger Codepfad** |
| Evolution/Kong-DBs | Eigene Datenbanken in deren Compose | **Separat** (Evolution-Postgres im Evolution-Stack, Kong-Postgres im Kong-Stack) — **nicht** identisch mit `atlas_state` |

**Fazit Datenlage:** `atlas_state` ist für Ticket 11 **strukturell vorbereitet**, **inhaltlich leer**. Für Ticket 12 ist der **kritische neue Speicher** (`omega_ingest_queue`) **abwesend**. Die „Wahrheit“, die Session-Logs nahelegen, **existiert in dieser Datenbank nicht**.

---

## 6. Abgleich Axiom A7 (Zero-Trust)

Behauptungen aus Cursor-Sessions und PASS-Urteilen wurden **ohne** diesen VPS-Abgleich als „Wahrheit“ ausgegeben. Empirischer Beleg für **Deploy + Laufzeit + Schema + Daten** auf 187.77.68.250 war für Ticket 12 **nicht** Teil der Abnahme.

**Status dieses Dokuments:** Fertig. Nächster sinnvoller Schritt (operativ, nicht Teil dieses Berichts): Migration `core_infrastructure.sql` auf `atlas_state` inkl. `omega_ingest_queue`, dann messbare Zeilen/Healthchecks; Kong-Services declarative definieren oder Kong absichtlich entfernen; Chroma-Single-Source und Port-Doku mit `docker ps` synchronisieren; Daemons als systemd oder Compose-Service mit Nachweis auf dem Host.
