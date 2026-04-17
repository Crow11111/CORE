---
name: orchestrator-bootstrap-preflight
description: Vor größeren OMEGA-Aufgaben MCP get_orchestrator_bootstrap mit task_hint; gaps/recommendations in Plan und Producer-Tasks verankern.
---

# SKILL: Orchestrator-Bootstrap Pre-Flight

## Wann

Architektur-/Infra-/Multi-Datei-Arbeit, VPS/Kong, große Refactors, Audit-Pläne — wenn **`user-omega-state-mcp`** verfügbar ist.

## Ablauf

1. **`get_orchestrator_bootstrap`** aufrufen mit **`task_hint`**: 3–15 Stichworte (z. B. `kong chroma omega-backend`).
2. **`gaps`**: zuerst adressieren oder dokumentiert zurückstellen.
3. **`recommendations`**: in nächste Schritte übernehmen.
4. **Semantik Soll vs. Ist:** Kanon/Plan → **`query_canon_semantic`** (`core_canon`, nach **`ingest_omega_canon_chroma`**). Schnittstellen, Ports, reale Laufzeit → **`query_operational_semantic`** (`core_operational`, nach **`ingest_omega_operational_chroma`**). Orientierung: **`docs/04_PROCESSES/KERNARBEITER_ORIENTIERUNG.md`**.
5. **Producer-`Task`**: Bootstrap-Kernaussage **einzeilig** mitgeben oder explizit Bootstrap vor Ausführung anordnen.

## Nicht verwechseln

- **8049 / `state_mtls_proxy`**: nur **lokal** auf der Dev-Workstation; im Bootstrap nur bei `OMEGA_BOOTSTRAP_PROBE_LOCAL_PROXY=1` geprüft.
- **InfrastructureSentinel**: prüft **kein** localhost — andere Endpunkte.

## Verweise

- `.cursor/rules/9_ORCHESTRATOR_BOOTSTRAP_MCP.mdc`
- `docs/04_PROCESSES/CANON_REGISTRY_AGENT_BINDUNG.md`
