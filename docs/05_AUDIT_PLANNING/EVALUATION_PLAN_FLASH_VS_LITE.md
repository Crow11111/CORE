# EVALUATION PLAN: Gemini 3.1 Flash vs. Flash-Lite (Agent Efficiency)

**Hypothese (Operator-Einsicht):**
`gemini-3.1-flash-lite-preview` ist strukturell auf hochvolumige Agentenaufgaben, reines Parsing und funktionale Ausführung ohne "Prosa und Lyrik" ausgelegt (siehe Google Dev Specs). Es sollte daher bei abstrakten, entpersonalisierten Rollen (z.B. Triage, Code-Formatierung, Data-Extraction) schneller, billiger und präziser agieren als das vollwertige `gemini-3.1-flash-preview` Modell, welches eher in Konversation ("Lyrik") abdriftet.

## Test-Setup (A/B Testing in CORE)

### Metriken
1. **Time-to-First-Token (TTFT) & Total Latency** (Millisekunden)
2. **Token-Effizienz** (Verhältnis Input zu Output Token -> Wie viel unnötige Prosa generiert das Modell?)
3. **Instruction Adherence** (Strikte Einhaltung des Boolean-Feedbacks oder JSON-Schemas ohne Erklärung)
4. **Rate Limit Hit-Rate** (Verbrauch der 1.048.576 Input-Token Grenze)

### Szenario 1: Der "Auditor" (Boolean Feedback)
*   **Prompt:** Abstrakter Auditor-Prompt ("Antworte nur mit [SUCCESS] oder [FAIL: Grund]").
*   **Input:** 50 verschiedene Code-Diffs mit eingebauten Regelverstößen (z.B. Float vs Int Verstoß gegen Axiom 6).
*   **Erwartung:** Flash-Lite liefert exakt das Tag. Flash tendiert dazu, die Lösung noch erklären zu wollen.

### Szenario 2: Der "Triage-Router"
*   **Prompt:** JSON-Klassifikator (User-Input -> Route zu Orchestrator, Audio, oder Direct-Response).
*   **Input:** 500 simulierte User-Prompts.
*   **Erwartung:** Flash-Lite bewältigt die hohe Frequenz ohne Rate-Limit-Bruch und mit extremer Geschwindigkeit (sub 500ms).

### Szenario 3: Code-Producer (Micro-Tasks)
*   **Prompt:** "Schreibe eine Python-Funktion für X. Keine Markdown-Erklärungen, nur Code."
*   **Erwartung:** Flash-Lite könnte bei extrem komplexer Architektur scheitern (fehlende Reasoning-Tiefe), ist aber bei klaren Micro-Tasks effizienter, weil es nicht versucht, den Code zu erklären.

## Ausführung
Die Evaluation wird durch ein Skript `src/scripts/evaluate_flash_vs_lite.py` automatisiert. Das Skript jagt die Test-Batches parallel durch beide Modelle und aggregiert die Ergebnisse in ChromaDB zur Analyse.
