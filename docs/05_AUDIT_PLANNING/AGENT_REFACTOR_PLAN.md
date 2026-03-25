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

## 2. NEUES ARCHITEKTUR-KONZEPT (Agenten-Hierarchie V2)

Um die Informationsasymmetrie zu beheben und deterministisches Verhalten zu erzwingen, wird die Architektur in drei entkoppelte, aber hart über das Dateisystem verdrahtete Schichten (Layers) restrukturiert.

### LAYER 0: THE CEO & ORCHESTRATOR (`.cursorrules`)
*   **Zweck:** Die Verfassung.
*   **Inhalt:** Ausschließlich Kern-Axiome (A5/A6), die Dreadnought-Doktrin und die Zwangsanweisung, *wie* der Orchestrator delegiert. Keine operativen Regeln (kein Frontend-, Backend-, oder DB-Wissen).
*   **Wirkung:** Maximale Token-Effizienz und klarer Fokus für den Orchestrator.

### LAYER 1: DIE SUB-AGENTEN (`.cursor/agents/*.md`)
*   **Zweck:** Die Blackbox-Rollen (Produzenten).
*   **Systemischer Modell-Zwang:** In den Frontmatter **jeder** Sub-Agenten-Datei wird zwingend `model: fast` eingetragen. 
    ```yaml
    ---
    name: db-expert
    description: Expert database engineer...
    model: fast
    ---
    ```
    Dadurch wird auf Engine-Ebene nativ erzwungen, dass dieser Sub-Agent *immer* das schnelle, kosteneffiziente Modell nutzt, selbst wenn der Orchestrator beim Aufruf den Parameter vergisst. Die Fehlerquelle "Hauptagent" ist eliminiert.
*   **Harte Kopplung von Skill & Rolle:** Anstatt auf externe Dateien zu verweisen, wird die essenzielle System-DNA der Rolle *direkt* in ihren System-Prompt (die `.md`-Datei) einkompiliert. Der Agent *erwacht* bereits mit seiner spezifischen Fähigkeit.

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