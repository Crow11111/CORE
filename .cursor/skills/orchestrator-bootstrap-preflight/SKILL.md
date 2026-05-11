---
name: orchestrator-bootstrap-preflight
description: Vor größeren OMEGA-Aufgaben MCP get_orchestrator_bootstrap mit task_hint; gaps/recommendations in Plan und Producer-Tasks verankern.
---

# SKILL: Orchestrator-Bootstrap Pre-Flight

## Wann

Architektur-/Infra-/Multi-Datei-Arbeit, VPS/Kong, große Refactors, Audit-Pläne — wenn **`user-omega-state-mcp`** verfügbar ist.

## Ablauf

1. **`x00C_collect_bootstrap`** aufrufen mit **`task_hint`**: 3–15 Stichworte.
2. **`gaps`**: (in der LISP S-Expression enthalten) zuerst adressieren.
3. **`recommendations`**: in nächste Schritte übernehmen.
4. **Pointer Soll vs. Ist:** Kanon/Plan → **`x0C0_navigate_manifold`** mit collection=`core_canon`. Schnittstellen, Ports, reale Laufzeit → **`x0C0_navigate_manifold`** mit collection=`core_operational`. Orientierung: **`docs/04_PROCESSES/KERNARBEITER_ORIENTIERUNG.md`**.
5. **C3-Egress:** Abschluss via **`xC00_causal_egress`**.

## Nicht verwechseln

- **8049 / `state_mtls_proxy`**: nur **lokal** auf der Dev-Workstation; im Bootstrap nur bei `OMEGA_BOOTSTRAP_PROBE_LOCAL_PROXY=1` geprüft.
- **InfrastructureSentinel**: prüft **kein** localhost — andere Endpunkte.

## Verweise

- `.cursor/rules/9_ORCHESTRATOR_BOOTSTRAP_MCP.mdc`
- `docs/04_PROCESSES/CANON_REGISTRY_AGENT_BINDUNG.md`
