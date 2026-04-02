# Cockpit: gestaffelte Warnungen + kritische Meldung

## Pflicht für KI (am Puls, nicht nur Doku)

Wenn Logs/Ticker im Kontext sind: **dieselbe Triage selbst ausführen** — zuerst ERROR, dann WARNs als zusammenhängende Kette. Nicht „der User sollte…“, sondern die Antwort strukturiert danach aufbauen.

---

## Erwartete Reaktion (Operator / KI / UI)

Wenn im Ticker **mehrere gelbe Stufen** (Heuristik / WARNING) und **darunter eine rote** (ERROR / System) erscheinen:

1. **Rot zuerst** — Die kritische Meldung hat Vorrang: Ursache klären, nicht unter den Warnungsstapel begraben.
2. **Gelb bündeln** — Mehrere WARNs derselben Klasse (z. B. TTS-Fallback-Kette) als **ein** Problemfeld lesen, nicht als N unabhängige Katastrophen.
3. **Reihenfolge** — Chronologie beachten: oft declariert die letzte rote Zeile das **Endresultat** („alle TTS fehlgeschlagen“), die gelben Zeilen sind **Kette/Fallback**.
4. **UI** — Kategorie **System (rot)** und **Heuristik (gelb)** getrennt einblendbar; bei Alarm erst **rot** sichtbar lassen, dann gelb nachziehen.

## Performance (Ticker / Filter)

Polling + clientseitiges Filtern moderner Logs (einige hundert Zeilen im Ringbuffer) ist **nicht** vergleichbar mit „Task Manager frisst Ressourcen“ (90er): Netzwerk und DOM-Updates im Sekundenbereich sind vernachlässigbar, solange keine Massen-WebSockets ungebremst laufen.


[LEGACY_UNAUDITED]
