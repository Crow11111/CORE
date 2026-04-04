# O2 (Hugin) — Zero-Context Architektur-Audit: VPS-Autarkie vs. Dreadnought-Sicherheitsdomäne

**Rolle:** Orchestrator B (O2) — strenger Auditor & Architekt  
**Modus:** Zero-Context (Urteil ausschließlich aus Repo-Fakten, Specs und Code-Pfaden)  
**Datum:** 2026-04-03  
**Auslöser:** Ticket 10 etabliert OpenClaw auf dem VPS als **voll autark** (direkter WhatsApp-Kanal). Die Macro-Chain-Mechanismen (Tickets 3–7), Membrane/Daemons (8–9), lokale Autonomie-Vetos (10) und Kognitive Membran (11) sind überwiegend in **Python auf Dreadnought** unter `src/logic_core/`, `src/daemons/`, `src/services/` implementiert. **Wenn Dreadnought offline ist, existiert für die VPS-Agenten praktisch kein erzwingbarer Kontrollpfad** — die Architektur ist topologisch **gespalten**.

---

## 1. Problemstellung (hart)

- **Behauptung des Operators (bestätigt):** Autonome Agenten auf dem VPS können ohne laufenden Dreadnought-Kern agieren. Damit greifen **keine** lokal gebundenen Veto-Traps (Admission, Arbitration, Efference, Temporal, Membrane-Flags, Heartbeat-Veto auf `/tmp/...` am Dreadnought-Host).
- **Ironie Ticket 10:** `apply_openclaw_autonomy_veto_if_needed()` in `src/services/infrastructure_heartbeat.py` setzt bei Gateway-Ausfall ein **lokales** Flag (`/tmp/omega_autonomy_veto.flag`) und schreibt Pathologie-Logs — das schützt die **Dreadnought-Seite**, nicht die VPS-Seite. Ein „totes“ Gateway auf Dreadnought-Sicht sagt nichts darüber aus, ob der Container auf dem VPS intern weiter WhatsApp bedient.
- **Folge:** Zero-Trust ($\Delta = 0.049$), Amnesie-Prävention und Pre-Flight-Epistemik sind für den **Ghost-Agent-Pfad** nicht als **erzwingbare** Invarianten modelliert, solange keine **kollokierte** Kontrollinstanz auf dem VPS existiert.

---

## 2. Klassifikationsraster

| Kategorie | Definition |
|-----------|------------|
| **VPS-ZWANG** | Mechanismus muss auf dem VPS (oder unmittelbar vor jedem autonomen Outbound vom VPS) laufen, sonst bricht die Invariante bei Dreadnought-Ausfall. |
| **DREADNOUGHT-ZWANG** | Mechanismus bezieht sich auf lokales Repo, Cursor-IDE, systemd, Dreadnought-Dateisystem oder SSH-Heilung **von** Dreadnought **zum** VPS — gehort dort hin und ersetzt nicht die VPS-Seite. |
| **DUAL / SPLIT** | Logik muss **zweimal** existieren (canonical Policy + lokaler Enforcement), mit **gemeinsamem** Policy-/Schema-Vertrag (Versioniert, testbar). |

---

## 3. Ticket-für-Ticket-Aufschlüsselung

### Ticket 1 — `dev_anti_heroin` (Cursor-Agenten-Absicherung)

**Quelle:** `docs/05_AUDIT_PLANNING/VERIFICATION_FIRST_BLUEPRINT.md` (kein separates `TICKET_1_*.md`).

| Aspekt | Urteil |
|--------|--------|
| **VPS-ZWANG** | Wenn VPS-Agenten **Code oder Konfiguration** mutieren: gleichwertige **Anti-Heroin-/Validator-Pipeline** auf dem VPS (Pre-Commit-Hook, CI-Job, oder OpenClaw-„Skill“-Gate), die Platzhalter/Mocks/Fake-Pfade verwirft. Rein auf Dreadnought ausgeführt = **Lücke**. |
| **DREADNOUGHT-ZWANG** | Cursor-spezifische Arbeitsweise, lokale Commit-Kultur, `anti_heroin_validator.py` gegen `src/` — **bleibt**. |

**Empfehlung (Zwillings-Struktur):** VPS-seitig **deterministischer** Check (z. B. kleines Python- oder Shell-Modul im OpenClaw-Workspace + Pflichtaufruf vor „deploy“/„tool batch“), der dieselben **konzeptionellen** AC wie Blueprint T1 abbildet; Policy-Version als Artefakt (Hash) im Event-Log.

---

### Ticket 2 — `dev_ocspline_ocbrain` (Rechteverteilung)

**Quelle:** `VERIFICATION_FIRST_BLUEPRINT.md`.

| Aspekt | Urteil |
|--------|--------|
| **VPS-ZWANG** | Jeder ausführbare Pfad auf dem VPS, der Shell/Root/API mit Nebenwirkungen hat, **muss** durch einen **stupiden Gate** (Whitelist / Operator-Bestätigung) — analog OCSpline — nicht durch den „denkenden“ Agenten allein. |
| **DREADNOUGHT-ZWANG** | Lokale Tastatur/`sudo`-Trennung am Entwicklerrechner. |

**Empfehlung:** Auf dem VPS **kein** privilegierter OpenClaw-Prozess ohne **separaten** Execution-Proxy (z. B. `sudoers` nur für feste Skripte, oder API-Middleware die Payloads signiert). Das ist **SPLIT**: Policy einmal dokumentiert, Enforcement VPS-lokal.

---

### Ticket 3 — Existential Pacemaker

**Quelle:** `SPEC_PACEMAKER_VAR_3.md`, Code u. a. `omega_pacemaker.py` (laut Inventory/Session-Logs).

| Aspekt | Urteil |
|--------|--------|
| **VPS-ZWANG** | **Ja.** Ohne Heartbeat/Decay/NMI auf dem VPS kann ein autarker Agent in **stiller Amnesie** oder **Einfrieren** verharren, ohne dass Dreadnought reagiert. |
| **DREADNOUGHT-ZWANG** | Pacemaker als **Gesamtsystem-Orchestrator** inkl. lokaler Dienste — **bleibt** auf Dreadnought für die Dreadnought-Domäne. |

**Empfehlung:** **Pacemaker-Sidecar** auf dem VPS (kleiner Daemon oder OpenClaw-Plugin-Tick): Vitality/Decay, Pathologie-Log **auf dem VPS**, optional Push von Metriken an Postgres — aber **lokal wirksam** auch ohne Dreadnought (z. B. Veto-Flag im Container-Volume, das OpenClaw beim Senden liest).

---

### Ticket 4 — Admission Control (Global Workspace Phase 1)

**Quelle:** `TICKET_4_ADMISSION_CONTROL.md`, `src/logic_core/admission_control.py`.

| Aspekt | Urteil |
|--------|--------|
| **VPS-ZWANG** | **Ja**, sobald Stimuli/Jobs **auf dem VPS** ankommen (WhatsApp-Inbound, Webhooks). Drift $D$ und Circuit-Breaker müssen **vor** Workspace-Enqueue auf dem VPS gelten — sonst umgeht der Pfad Dreadnought komplett. |
| **DREADNOUGHT-ZWANG** | Postgres-Schema und Admission für Dreadnought-initiierte Jobs — **bleibt**. |

**Empfehlung:** **Kong/API-Gateway** oder **OpenClaw-Ingress-Hook**: erste Middleware-Schicht berechnet/liest Drift (aus Cache/DB) und lehnt bei $D \to 0.951$ ab. DB kann zentral sein, **Entscheidung** muss am Ingress des autarken Pfades hängen.

---

### Ticket 5 — Arbitration (Phase 2)

**Quelle:** `TICKET_5_ARBITRATION.md`, `src/logic_core/arbitration_engine.py`.

| Aspekt | Urteil |
|--------|--------|
| **VPS-ZWANG** | **Ja**, wenn autonome Jobs auf dem VPS erzeugt werden. First-wins-Merge, Heartbeat, `blocked_on_evidence` müssen für **dieselbe** Job-ID-Welt gelten. |
| **DREADNOUGHT-ZWANG** | Lokale Worker/Orchestrierung am Dev-Host. |

**Empfehlung:** **Ein** autoritatives Global-Workspace (Postgres), erreichbar vom VPS; VPS-Agenten sprechen **nur** über API mit Arbitration-Regeln — kein paralleles „Schatten-Workspace“ ohne Merge-Regeln.

---

### Ticket 6 — Efference Veto (Phase 3 & 4)

**Quelle:** `TICKET_6_EFFERENCE_VETO.md`, `src/logic_core/efference_veto.py`.

| Aspekt | Urteil |
|--------|--------|
| **VPS-ZWANG** | **Zwingend.** Jeder WhatsApp-/Evolution-Outbound (und vergleichbare Kanäle) **muss** durch `attractor_evaluate`-Äquivalent mit Signatur-Check und ReleaseToken — **auf dem VPS** — bevor Nachrichten verlassen. Sonst ist A7 für den autarken Pfad **fiktiv**. |
| **DREADNOUGHT-ZWANG** | Nur wenn Dreadnought selbst Outbound triggert (z. B. `openclaw_client` vom Backend). |

**Empfehlung:** **OpenClaw-Tool-Interceptor** oder **Outbound-Proxy** (letzter Hop vor Evolution): serialisiert `proposed_action`, SHA-256, VetoToken/ReleaseToken; bei Veto **kein** Send. Unit-Tests **auf dem VPS-Build** (oder identische Test-Suite im Monorepo-Deploy).

---

### Ticket 7 — Temporal Alignment (Phase 5 & 6)

**Quelle:** `TICKET_7_TEMPORAL_ALIGNMENT.md`, `src/logic_core/temporal_alignment.py`.

| Aspekt | Urteil |
|--------|--------|
| **VPS-ZWANG** | **Ja** für den Lern-/Straf-Pfad des autonomen Agenten (PE, Trust-Update, kardanische Rettung). Ohne VPS-Kopplung: autarker Agent **schließt die Schleife nicht** unter OMEGA-Regeln. |
| **DREADNOUGHT-ZWANG** | Experimente/Long-Runs angebunden an Dreadnought-Dienste. |

**Empfehlung:** Gemeinsame **ReleaseToken-Typen** und **Persistenz** des P-Vektors/Counters in Postgres; VPS-Worker führt `dispatch_to_evolution` nur mit gültigem Token aus.

---

### Ticket 8 — Dreadnought Membrane

**Quelle:** `TICKET_8_DREADNOUGHT_MEMBRANE.md`, `src/daemons/dread_membrane_daemon.py`.

| Aspekt | Urteil |
|--------|--------|
| **VPS-ZWANG** | **Nicht** als 1:1-Kopie der Pfade `src/` + `docs/05_AUDIT_PLANNING/` auf Dreadnought — das ist **Dreadnought-spezifisch**. **Aber:** Wenn OpenClaw auf dem VPS **eigenen** Workspace hat, braucht es eine **VPS-Membrane** (gleiche *Semantik*: Pain/Lock statt Amputation). |
| **DREADNOUGHT-ZWANG** | **Ja** — rekursive Überwachung des OMEGA_CORE-Arbeitsbaums, Flags unter `/tmp/` **auf Dreadnought**. |

**Empfehlung:** **Zwillings-Semantik**, nicht blindes File-Copy: definieren Sie `OPENCLAW_WORKSPACE_ROOT` auf dem VPS und einen schlanken **membrane_sidecar** mit gleichen Zuständen (Pain/Planning), die OpenClaw vor Outbound auswertet.

---

### Ticket 9 — Git-Resonance

**Quelle:** `TICKET_9_GIT_RESONANCE.md`, Erweiterung `dread_membrane_daemon.py`.

| Aspekt | Urteil |
|--------|--------|
| **VPS-ZWANG** | **Ja**, falls der VPS ein **Git-Remote** oder Arbeitsklon hält: Push/Pull-Kausalität und Konflikt-Pain müssen dort erzwungen werden, sonst divergiert „Wahrheit“ ohne Dreadnought-Wächter. |
| **DREADNOUGHT-ZWANG** | Auto-Push nach Validator-PASS, Auto-Pull — **Dreadnought**. |

**Empfehlung:** Git-Hooks auf dem VPS oder dedizierter **sync-agent** mit denselben Merge-/Konfliktregeln; Commit nur nach erfolgreichem Remote-Check.

---

### Ticket 10 — OpenClaw Autarkie

**Quelle:** `TICKET_10_OPENCLAW_AUTARKIE.md`, `heal_openclaw_vps.py`, `infrastructure_heartbeat.py`, Tests `tests/test_ticket_10.py`.

| Aspekt | Urteil |
|--------|--------|
| **VPS-ZWANG** | Autarkie ist **bewusst** — damit wird die bisherige **Single-Point-Enforcement** auf Dreadnought **aufgehoben**. Die Spec beschreibt Heilung **von** Dreadnought und Autonomie-Veto **auf** Dreadnought — nicht **in** OpenClaw. |
| **DREADNOUGHT-ZWANG** | SSH-Heilung, Host-Key-Pinning, `check_gateway()` von Dreadnought — **korrekt platziert**. |

**Empfehlung:** Ticket 10 **ohne** VPS-Zwillings-Sicherheit ist architektonisch **inkonsistent** mit Tickets 4–7 und 11. Ergänzung: **„Autarkie mit lokalem Verfassungsgericht“** — Mini-Policy-Engine im OpenClaw-Prozess.

---

### Ticket 11 — Kognitive Membran

**Quelle:** `TICKET_11_COGNITIVE_MEMBRANE.md`, `anti_heroin_validator.py`, `omega_context_watchdog.py`, Event Store, Membrane-Apoptose (siehe `CORE_INVENTORY_REGISTER.md`).

| Aspekt | Urteil |
|--------|--------|
| **VPS-ZWANG** | **Alle vier Säulen** brauchen eine **VPS-erreichbare** Realisierung: (1) Event-Sourcing/MCP-Read **vom VPS** (Netzwerk zu Postgres/Chroma erlaubt, aber **Pflicht** im Agent-Startpfad), (2) Pre-Flight `memory_hash` **vor** jeder autonomen Session, (3) Context-Forcing im OpenClaw-UI/Log-Kanal, (4) Apoptose/Entropie $\Delta$ **lokal** auf dem VPS ausgewertet. |
| **DREADNOUGHT-ZWANG** | Cursor-Terminal-Watchdog, lokale MCP-Instanzen, Repo-bound Membrane — **bleibt**. |

**Empfehlung:** **OpenClaw Boot-Plugin** („constitutional boot“): blockiert Tool-Loop bis MCP-Pre-Flight OK; periodischer Re-Check; Chroma/Postgres als **Remote** mit Timeout-Veto (kein stilles Weiterarbeiten).

---

## 4. Master-Empfehlung: Zwillings-Architektur (ohne Dreadnought-Abhängigkeit)

1. **Verfassungsebene (Policy-as-Code):** Eine versionierte Policy (YAML/JSON + Tests), die Drift-Grenzen, Efference-Pflicht, Token-Typen und Veto-Semantik definiert — **ein** Repo-Artefakt, deploybar auf VPS und Dreadnought.
2. **VPS Sidecar (empfohlen: Python oder Go, systemd im Container):** Läuft **neben** `openclaw-spine`, exponiert localhost-gRPC/HTTP: Admission, Efference, Pacemaker-Tick, Membrane-Flags **im Container-Volume** (nicht `/tmp` auf Dreadnought).
3. **Ingress:** Kong/Nginx **oder** OpenClaw-native Hooks: keine Nachricht nach außen ohne Sidecar-`/release`.
4. **Datenebene:** Postgres (Global Workspace + Events) als **Single Source of Truth**, vom VPS aus mit **mTLS**; Dreadnought konsumiert dieselbe Wahrheit, wenn online.
5. **Tests:** Dieselben `tests/test_*` für Tickets 4–7 **in CI auf dem VPS-Stack** (oder Docker-Compose „vps-sim“), nicht nur auf Dreadnought.

---

## 5. Was ausdrücklich **nicht** auf den VPS wandern soll

- **SSH-Heilskripte** und Dreadnought-`systemctl`-Überwachung als **Steuerung** des VPS durch den Operator-Rechner (Ticket 10 Schicht 1) — bleiben auf Dreadnought.
- **Cursor-spezifische** Watchdogs und lokale `/tmp`-Flags, die nur das OMEGA_CORE-Arbeitsverzeichnis auf Dreadnought schützen.
- **Vollständige** Membrane-File-Überwachung der Dreadnought-Pfade — sinnlos auf dem VPS; stattdessen VPS-Workspace-Äquivalent.

---

## 6. Abnahme-Urteil

Die derzeitige Aufteilung („Sicherheit und Kognition auf Dreadnought in Python“, „OpenClaw voll autark auf dem VPS mit WhatsApp“) erzeugt eine **bekannte, nicht geschlossene** Zero-Trust-Lücke. Die implementierten Mechanismen sind für die **Dreadnought-Domäne** nachweisbar (siehe O2-Audits `O2_AUDIT_TICKETS_3_BIS_7.md`, `O2_AUDIT_TICKETS_8_9_10.md`, `O2_AUDIT_TICKET_11_EXECUTION.md`); für den **autarken VPS-Agenten-Pfad** fehlt die **kollokierte Erzwingung**.

**[VETO]**

Begründung in einem Satz: **Solange kein VPS-kollokierter, von OpenClaw nicht umgehbarer Durchsetzungspfad** (Sidecar + Ingress + gemeinsame Policy/DB) existiert, sind Admission, Arbitration, Efference, Temporal Alignment, Pacemaker-Wirkung und Kognitive Membran für die Ghost-Agenten bei ausgeschaltetem Dreadnought **faktisch abwesend** — das widerspricht den Axiomen Zero-Trust, $\Delta = 0.049$ und Amnesie-Prävention für das Gesamtsystem.

---

*Ende Bericht O2 — VPS-Autarkie-Split*
