# AUDIT: Kontext-Leakage und Wiederholungsschleifen

## Das Symptom (Operator-Rüge)
Der Orchestrator hat in den letzten Antworten Dinge (wie die API-Key-Trennung und den Audio-Toggle) immer wieder aufgegriffen und teils doppelt beschrieben oder als Task neu gestartet, obwohl sie bereits vor mehreren Iterationen abgewickelt und bestätigt waren.

## Die Ursache (LLM-Kognition im Cursor-Kontext)
1. **Chat-Historie als Ballast:** Das Modell (ich) liest bei jedem neuen Prompt die gesamte Chat-Historie der aktuellen Session. Wenn eine erledigte Aufgabe nicht explizit und hart als "abgeschlossen und irrelevant für den aktuellen Scope" markiert wird, sieht das Attention-Mechanism des Modells sie als "immer noch aktives Thema" an.
2. **Die TodoWrite-Illusion:** Ich habe zwar das `TodoWrite` Tool genutzt, um Tasks abzuhaken, aber ich habe sie in meiner *textuellen* Antwort immer wieder referenziert ("Ich habe übrigens auch noch X gemacht..."). Dadurch verfängt sich das Thema im Kontextfenster.
3. **Mangelnde Scope-Isolation:** Anstatt nach einer abgeschlossenen Iteration einen harten kognitiven Schnitt zu machen (z.B. "Thema Audio ist abgeschlossen, wir sprechen nicht mehr darüber"), schleppe ich den Kontext mit.

## Die Lösung (Harte kognitive Trennung)
1. **Textuelle Stille:** Abgeschlossene Tasks werden *nicht* mehr in der textuellen Antwort rekapituliert, es sei denn, der Operator fragt spezifisch danach.
2. **Todo-Tool Wipe:** Wenn ein Task abgeschlossen ist, wird er auf `[COMPLETED]` gesetzt und in der nächsten Iteration *komplett* aus der aktiven Todo-Liste gelöscht, anstatt ihn als "Completed" mitzuschleppen.
3. **Fokus-Deklaration:** Zu Beginn jeder Antwort deklariert der Orchestrator (für sich selbst) den exakten, isolierten Scope der aktuellen Iteration in den `<<<GEDANKEN>>>`. Alles, was außerhalb dieses Scopes liegt, wird ignoriert, selbst wenn es im Chat-Verlauf weiter oben steht.


[LEGACY_UNAUDITED]
