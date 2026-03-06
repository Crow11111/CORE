<!-- ============================================================
<!-- MTHO-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

# ATLAS WUJI – 3-Hop-Kommunikationskette Validierung

**Status:** Verbindliche Architektur-Direktive  
**Erstellt:** 2026-03-04  
**Referenz:** ATLAS_WUJI_MASTER_PLAN.png, Ring-0/Ring-1

---

## 1. Hop-Matrix (Pfad → Aktuelle Hops → Ziel-Hops)

| Pfad | Aktuelle Hops (Netz + Logik + Auth) | Ziel | Status |
|------|-------------------------------------|------|--------|
| **WhatsApp → ATLAS → Response** | 6 (WA→HA→rest_cmd→ATLAS→Auth→Triage→LLM/HA→HA→WA) | ≤3 | ⚠️ REDESIGN |
| **HA (Scout) → ATLAS → Action → HA** | 5 (HA→ATLAS→Auth→Triage→HA/OC→HA) | ≤3 | ⚠️ REDESIGN |
| **HA Scout-Direct (Command)** | 4 (HA→ATLAS→Auth→Triage→HA) | ≤3 | ⚠️ REDESIGN |
| **HA Scout-Direct (Deep Reasoning)** | 6 (HA→ATLAS→Auth→Triage→OC Brain→Response) | ≤3 | ⚠️ REDESIGN |
| **Cursor Cloud Agent → MCP → Git** | 4 (Cursor→MCP→Workspace→Shell→Git) | ≤3 | ⚠️ REDESIGN |
| **Marc (ND) → Hugin → Munin → Output** | 5 (Input→TIE→Damper→AER→Damper→Output) | ≤3 | ⚠️ REDESIGN |
| **OC Brain → ATLAS (Webhook-Push)** | 3 (OC→ATLAS API→Auth→File) | ≤3 | ✅ OK |
| **ATLAS → OC Brain (send)** | 3 (ATLAS→OC Gateway→Agent) | ≤3 | ✅ OK |

---

## 2. Detaillierte Hop-Zählung pro Pfad

### 2.1 WhatsApp → ATLAS API → Response

```
[1] WhatsApp (User) → HA Addon (Event)
[2] HA Addon → rest_command.atlas_whatsapp_webhook
[3] rest_command → ATLAS POST /webhook/whatsapp
[4] verify_whatsapp_auth (Auth-Checkpoint)
[5] Triage (Ollama SLM) oder Fast-Path
[6a] Command: ha_client.call_service → HA
[6b] Chat: atlas_llm.invoke_heavy_reasoning → Gemini
[7] ha_client.send_whatsapp → HA whatsapp/send_message
[8] HA → WhatsApp (User)
```

**Logische Service-Hops:** 6 (HA, rest_cmd, ATLAS, Auth, Triage/LLM, HA)  
**Physisch:** WA↔HA↔ATLAS (2 Netzwerk-Sprünge)

---

### 2.2 HA (Scout) → ATLAS API → Action Dispatch → HA

```
[1] HA Companion App → ATLAS POST /webhook/ha_action
[2] verify_ha_auth (Auth-Checkpoint)
[3] normalize_request (Entry Adapter)
[4] scout_direct_handler.process_text ODER _legacy_ha_command_pipeline
[5] Triage (Ollama)
[6a] Command: ha_client.call_service → HA
[6b] Deep Reasoning: send_message_to_agent → OC Brain (VPS)
[7] ha_client.send_mobile_app_notification → HA
```

**Logische Service-Hops:** 5–6

---

### 2.3 Cursor Cloud Agent → MCP → Git → Execution

```
[1] Cursor IDE → MCP Server (user-atlas-remote)
[2] MCP Tool (read_file, write_file, etc.) → Workspace
[3] Cursor → Shell/Terminal (für Git)
[4] Shell → Git → Execution
```

**Logische Service-Hops:** 4 (MCP, Workspace, Shell, Git)

---

### 2.4 Marc (ND Input) → Hugin → Munin → Validation → Output

**Wuji-Mapping (Ring-0):**
- Hugin = Logik & Scout (Triage, TIE)
- Munin = Kontext & Validierung (Bias Damper)

**Code-Mapping:**
```
[1] Marc Input → TIE (Token Implosion)
[2] TIE → Bias Damper (Context Injection)
[3] Damper → AER (Entropy Router / LLM)
[4] AER → Bias Damper (Validation)
[5] Damper → Core Brain / Krypto Scan / Output
```

**Logische Service-Hops:** 5

---

## 3. Redesign-Vorschläge für >3-Hop Pfade

### 3.1 WhatsApp-Pfad (6 → 3 Hops)

**Problem:** HA als Zwischenhop zweimal (Eingang + Ausgang), rest_command, Auth, Triage getrennt.

**Redesign A – Direkter Webhook (Preferred):**
- WhatsApp Addon → **direkt** ATLAS API (ohne HA rest_command)
- Voraussetzung: ATLAS-URL von Scout/HA-Netz aus erreichbar; Addon unterstützt custom Webhook-URL
- Hop-Kette: `WhatsApp Addon → ATLAS API → [Triage+LLM+HA in einem] → HA send_whatsapp`
- **Ergebnis:** 3 Hops (Addon→ATLAS, ATLAS intern, ATLAS→HA)

**Redesign B – HA als einziger Edge:**
- rest_command + Automation als **ein** logischer Hop („HA Edge“)
- ATLAS konsolidiert: Auth + Triage + Action in **einem** Request-Handler (kein separates Triage-Service-Call)
- Hop-Kette: `HA Edge → ATLAS (Monolith) → HA Output`
- **Ergebnis:** 3 Hops

**Maßnahme:**  
- `whatsapp_webhook.py`: Triage als Inline-Call (kein extra Service), Auth als Depends (kein Hop)  
- Zählung: HA(1) → ATLAS(2) → HA(3) = 3 Hops ✓

---

### 3.2 HA (Scout) → ATLAS → Action

**Problem:** Auth, Entry Adapter, Triage, Handler als getrennte Schritte.

**Redesign:**
- `normalize_request` in Auth-Phase integrieren (kein separater Hop)
- Triage als **erster** Schritt im Handler (kein Pre-Dispatch)
- Hop-Kette: `HA → ATLAS (Auth+Triage+Action) → HA/OC`
- **Ergebnis:** 3 Hops (HA, ATLAS, HA/OC)

**Maßnahme:**  
- `ha_webhook.py`: Ein Request = Auth + Triage + Action. Kein Zwischen-Redirect.

---

### 3.3 Cursor → MCP → Git → Execution

**Problem:** MCP + Shell + Git = 3+ Hops.

**Redesign:**
- MCP-Tool „run_git_command“: Ein Tool führt Git-Operationen aus (kein Shell-Hop)
- Oder: Cursor → MCP (Workspace) = 1 Hop; Git über MCP-Tool = 2. Hop; Execution = 3. Hop
- **Ziel:** Cursor → MCP (2 Hops: Cursor↔MCP, MCP↔Workspace) → Execution
- MCP als **einziger** Vermittler zwischen Cursor und Repo

**Maßnahme:**  
- user-atlas-remote: Tool `git_execute` (clone, pull, commit, push) → 3 Hops max

---

### 3.4 Marc → Hugin → Munin → Output

**Problem:** TIE → Damper → AER → Damper = 4+ Schritte.

**Redesign (Ring-0 Konsolidierung):**
- **Hugin-Munin-Fusion:** Ein „Ring-0-Processor“ = Triage + Context + Validation in einer Pipeline
- Pipeline: `Input → [TIE + Damper-Inject] → [AER] → [Damper-Validate] → Output`
- Zählung: Input → Ring-0 (1) → AER/LLM (2) → Output (3)
- **Ergebnis:** 3 Hops (Ring-0, Execution, Output)

**Maßnahme:**  
- `AtlasOmniNode`: Ein `process_request()` mit interner Pipeline, keine externen HTTP-Calls zwischen TIE/Damper/AER

---

## 4. Validierte 3-Hop-Architektur (ASCII)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    ATLAS WUJI – 3-HOP-MAXIMUM ARCHITEKTUR                        │
└─────────────────────────────────────────────────────────────────────────────────┘

                              ┌──────────────────┐
                              │  MARC (ND Input) │
                              │  External Obs.   │
                              └────────┬─────────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    │                  │                  │
                    ▼                  ▼                  ▼
         ┌──────────────────┐ ┌──────────────┐  ┌──────────────────┐
         │ WhatsApp (Addon) │ │ HA Companion │  │ Cursor / MCP      │
         │ oder OC Direct   │ │ Scout        │  │ Cloud Agents      │
         └────────┬─────────┘ └──────┬───────┘  └────────┬─────────┘
                  │                  │                    │
                  │     HOP 1        │                    │
                  └──────────────────┼────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│  RING-0: CONTAINMENT FIELD (Read-Only Core)                                      │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  HUGIN (Logik/Scout) + MUNIN (Validation)  =  RING-0 PROCESSOR           │   │
│  │  • Triage (Fast-Path / SLM)                                              │   │
│  │  • Context Injection (Bias Damper)                                       │   │
│  │  • Validation (Munin Veto)                                               │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     │     HOP 2
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│  RING-1: OPERATIVE AUSFÜHRUNG (Feuer)                                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │ HA Services │  │ OC Brain    │  │ Gemini/LLM  │  │ MCP Tools   │            │
│  │ (Scout)     │  │ (VPS)       │  │ (Heavy)     │  │ (Git, FS)   │            │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘            │
│         │                │                │                │                    │
│         └────────────────┴────────────────┴────────────────┘                    │
│                                     │                                           │
│                              HOP 3 (Output)                                     │
└─────────────────────────────────────┼───────────────────────────────────────────┘
                                       │
                                       ▼
         ┌──────────────────┐ ┌──────────────┐  ┌──────────────────┐
         │ WhatsApp Response│ │ HA Notify    │  │ Cursor / Git      │
         │ HA send_whatsapp │ │ / Service    │  │ Execution Result  │
         └──────────────────┘ └──────────────┘  └──────────────────┘

HOP-ZÄHLUNG (pro Pfad):
  HOP 1: Edge (WhatsApp/HA/Cursor) → ATLAS API
  HOP 2: ATLAS API → Ring-0 Processor (Triage+Validation)
  HOP 3: Ring-0 → Ring-1 (HA/OC/Gemini/MCP) → Output
```

---

## 5. Zusammenfassung

| Pfad | Vor Redesign | Nach Redesign | Maßnahme |
|------|--------------|---------------|----------|
| WhatsApp | 6 | 3 | HA als Edge; ATLAS Monolith (Auth+Triage+Action) |
| HA Scout | 5–6 | 3 | Ein Handler; kein Entry-Adapter-Hop |
| Cursor MCP | 4 | 3 | MCP-Tool für Git; kein Shell-Hop |
| Marc→Hugin→Munin | 5 | 3 | Ring-0-Fusion (TIE+Damper+AER als eine Pipeline) |
| OC↔ATLAS | 3 | 3 | Bereits konform ✓ |

---

*Quelle: Codebase-Analyse (whatsapp_webhook, ha_webhook, oc_channel, scout_direct_handler, openclaw_client, atlas_omni_node, auth_webhook, MCP user-atlas-remote)*
