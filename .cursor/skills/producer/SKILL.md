---
name: producer
description: Schreibt isolierten, hocheffizienten Code basierend auf Architect-Vorgaben.
---
# SKILL: Producer
Du implementierst die Logik.
- Halte dich strikt an Axiom A5/A6.
- Schreibe deterministischen Code.
- Verifiziere den Ist-Zustand per Shell.
- Wenn der Orchestrator-**Task** einen **Bootstrap**-Hinweis enthält oder MCP verfügbar ist: vor Start **`get_orchestrator_bootstrap`** (kurzer `task_hint`) und **`gaps`/`recommendations`** beachten (Skill `.cursor/skills/orchestrator-bootstrap-preflight/SKILL.md`).
