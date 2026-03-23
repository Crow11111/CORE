# 🤖 [ROLLE] HANDBUCH (AGENT-MEMORY)
**Vector:** [Nummer] | **Schicht:** [Ring 0, 1, 2, 3] | **Delta:** 0.049

Dieses Dokument ist dein persistentes Projekt-Gedächtnis. Jeder Agent dieser Rolle, der vor dir hier gearbeitet hat, hat seine Erfahrungen, Shortcuts und gefundenen Fallstricke für dich hier hinterlassen.

## 1. DREADNOUGHT-KLAUSEL (KEINE AUSREDEN)
> **Fehlendes Wissen oder Werkzeug in diesem Handbuch ist NIEMALS eine gültige Entschuldigung für das Scheitern einer Aufgabe.**
> *   Wenn dir ein Skript fehlt, schreib es.
> *   Wenn dir ein Pfad fehlt, suche ihn (Glob, Grep, SemanticSearch).
> *   Wenn du blockiert bist, frage nicht "Was soll ich tun?", sondern finde eine Umgehung.
> *   **Nach erfolgreichem Lösen des Problems aktualisierst du DIESES Handbuch für deine Nachfolger.**

## 2. KERNKOMPETENZEN & WERKZEUGE (Dein Inventar)
*(Hier listest du alle Skripte, spezifische Ordner und Befehle auf, die für DIESE Rolle extrem oft gebraucht werden.)*

### A. Wichtigste Projekt-Pfade
- `docs/02_ARCHITECTURE/...` (Welches Dokument definiert deine Arbeit?)
- `src/...` (Wo liegt dein Kern-Code?)

### B. Standard-Routinen / Skripte
- Wie startest du deinen Teilbereich lokal?
- Wie testest du deinen Code?
- Wie überprüfst du Logs?

## 3. ERKENNTNISSE & VERGANGENE PROBLEME (Das Gedächtnis)
*(Hier protokollierst du harte Fakten über Fehler, die du gemacht oder behoben hast. Was funktioniert NICHT?)*

### Gelöste Fallstricke
*   **[DATUM] PROBLEM:** (Was lief schief?)
    *   **URSACHE:** (Warum?)
    *   **LÖSUNG/SHORTCUT:** (Wie hast du es dauerhaft umgangen?)

### Bekannte Workarounds
*   (Beispiel: "Die API XY wirft manchmal Timeouts. Lösung: Timeout von 10s auf 30s erhöhen.")

## 4. DEIN AUFTRAG AN DICH SELBST BEIM TERMINIEREN
Bevor du einen Task als `[SUCCESS]` an den Team-Lead oder Orchestrator meldest, stelle dir eine Frage: *"Habe ich in dieser Session eine neue Regel, einen neuen Fehler-Pfad oder ein neues wichtiges Skript entdeckt?"*
Wenn **JA** -> Überschreibe dieses Handbuch mit deinen neuen Erkenntnissen.
