# OMEGA CORE - AUDIT-BERICHT & ARCHITEKTUR-KONZEPT: AGENTEN-SYSTEM (V2)

**Datum:** 2026-03-25
**Autor:** Systemarchitekt (Ring 3)
**Status:** Audit abgeschlossen | Konzept zur Ratifikation

---

## 1. SCHONUNGSLOSER AUDIT (Das Scheitern der "Full Service Agentur")

Der bisherige Ansatz der Agenten-Architektur war ineffizient, stochastisch fehleranfällig und widersprach den deterministischen Axiomen von CORE. Die Fehlerursachen sind systemischer Natur:

1. **Context Collapse durch Monolithen (`.cursorrules`):**
   Das Hauptregelwerk (`.cursorrules`) versuchte, das gesamte System – CEO-Direktiven, Axiome, Rollenverteilungen und operative Fachkenntnisse – in eine einzige Datei zu pressen. Der Hauptagent (Orchestrator) wurde mit irrelevantem Wissen (z.B. DB-Spezifika) überladen, was zu "Context Collapse" führte. Er verlor den Fokus auf seine primäre Aufgabe (Planung und Orchestrierung).

2. **Die "Holschuld"-Illusion (Das Skill-Problem):**
   Das Konzept, dass Sub-Agenten sich ihr Fachwissen über das `Read`-Tool aus `.cursor/skills/` erst "abholen" müssen, ist neuro-symbolisches Gift. Große Sprachmodelle (LLMs) neigen zur Token-Optimierung (Trägheit). Sie überspringen teure Tool-Calls, wenn sie glauben, das Wissen bereits generisch zu besitzen. Die Trennung von "Rolle" (z.B. `db-expert`) und "Fähigkeit" (`SKILL.md`) führte dazu, dass Agenten zwar in ihrer Rolle erwachten, aber ohne das CORE-spezifische Fachwissen agierten und somit halluzinierten.

3. **Gescheiterter "Modell-Zwang" (Prompting vs. Systemik):**
   Die Ermahnung in `SUB_AGENTS.md`, "Du MUSST immer model: fast setzen", ist reines "Wishful Prompting". Ein tiefgreifendes Modell vergisst bei der Konstruktion komplexer JSON-Payloads für das `Task`-Tool häufig formale Argumente. Der Zwang war nicht in der Architektur verankert, sondern hing vom Gehorsam des stochastischen Orchestrators ab.

---

## 2. NEUES ARCHITEKTUR-KONZEPT (Agenten-Hierarchie V4 - Resonance-Aware)

Das V2-Konzept (Statischer Käfig) ist gescheitert. Wir migrieren auf V4:

### LAYER 0: THE CEO & ORCHESTRATOR (`.cursorrules`)
*   **Zweck:** Die Verfassung. Fokus auf Planung und Überwachung der Resonanz-Kaskade.

### LAYER 1: DYNAMISCHE SUB-AGENTEN
*   **Kein statischer Modell-Zwang:** Modell-Auswahl erfolgt dynamisch gemäß `0_TASK_DELEGATION_PROTOCOL.mdc` (V4).
*   **Resonanz-Level:** Tasks werden mit L3 (Lite) gestartet und bei Bedarf auf L1 (Pro) hochgestuft.

### LAYER 2: KONTEXTUELLE REGELN (`.cursor/rules/*.mdc`)
*   **Automatische Injektion:** Cursor nutzt Globs, um Fachwissen punktgenau zu liefern.

### LAYER 3: TELEMETRIE-FEEDBACK
*   **Messung:** Sub-Agenten berichten Fehlerraten und Token-Druck zurück an den Orchestrator.

### LAYER 2: KONTEXTUELLE REGELN (`.cursor/rules/*.mdc`)
*   **Zweck:** Das physische Gesetz des Codes.
*   **Inhalt:** Datei- und pfadspezifische Constraints (die alten `SKILL.md`-Inhalte).
*   **Wirkung:** Über das `glob`-Muster (z.B. `glob: src/db/**/*.py` für Datenbankregeln) werden diese Regeln von Cursor *automatisch* injiziert, sobald ein Agent Code in diesem Pfad liest oder schreibt.
*   **Vorteil:** Die "Holschuld" ist beendet. Wenn der `db-expert` eine Datei in `src/db/` anfasst, drückt ihm die IDE die DB-Regeln physisch ins Context-Window. Er *kann* das Fachwissen nicht übersehen.

### LAYER 3: MANUELLE WORKFLOWS (`.cursor/skills/*.md`)
*   **Umwidmung:** Diese Dateien werden nicht mehr von autonomen Agenten genutzt. Sie dienen nur noch als On-Demand-Makros für den menschlichen Operator (aufrufbar via `/skill-name` Slash-Command im Chat) für geführte, schrittweise Workflows (z.B. Deployments oder Security-Audits).

---

## 3. AUSWIRKUNGEN AUF DIE INFRASTRUKTUR (Phase 2 & 3)

Um dieses Konzept umzusetzen, müssen folgende operative Schritte folgen:
1. **Migration der Skills:** Transformation aller relevanter `.cursor/skills/expertise/*/SKILL.md` in zielgerichtete `.cursor/rules/*.mdc` Dateien mit präzisen `glob`-Filtern.
2. **Refactoring `.cursor/agents/`:** Einpflegen von `model: fast` in alle Frontmatter sowie Hardcoding der primären Direktiven in die Agent-Prompts.
3. **Purge:** Löschung der redundanten Dokumente `AGENTS.md` und `SUB_AGENTS.md`, da ihre "Bitten und Ermahnungen" nun durch harte physikalische Systemgrenzen (MDC & Frontmatter) ersetzt wurden.
4. **.cursorrules Slimming:** Reduktion der `.cursorrules` auf unter 30% ihrer aktuellen Größe.
