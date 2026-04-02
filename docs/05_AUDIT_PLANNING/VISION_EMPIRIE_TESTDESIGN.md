# VISION_EMPIRIE_TESTDESIGN: OMEGA CORE COUNCIL

**Status:** DRAFT | **Vektor:** 2210 | **Delta:** 0.049
**Thema:** Empirische Messbarkeit von Operator-Zuständen (Fokus vs. Freizeit) via MediaPipe-Sonde (`VISION_SYNC`).

---

## 1. Executive Summary: Das Council-Urteil
Der naive Ansatz eines starren 5-Minuten-Pollings (15 Sekunden Laufzeit) wurde vom Operator zu Recht abgelehnt. Er verletzt grundlegende Prinzipien der statistischen Signifikanz und des kontextuellen Systemdesigns (Axiom 7: Verifizieren statt glauben). 

Das Council hat den Ansatz dekonstruiert und einen ereignisgesteuerten (Event-Driven) sowie baseline-kalibrierten Versuchsaufbau entworfen.

---

## 2. Methodische Kritik am 5-Minuten-Polling

### Perspektive 1: Der Sensor- & Datenanalyst
- **Die 5%-Falle:** Ein 15-Sekunden-Fenster alle 5 Minuten erfasst exakt 5% der Gesamtzeit. Für statische Zustände ("Ist eine Person im Raum?") reicht das aus. Für dynamische, flüchtige Metriken wie Blinzelraten (Blink Rate) oder Mikromimik ist das Rauschen zu hoch.
- **Blink-Raten-Problematik:** Ein durchschnittlicher Mensch blinzelt 15-20 Mal pro Minute. Bei hoher kognitiver Last fällt die Rate auf 5-7 Mal. In 15 Sekunden sehen wir im Schnitt 1 bis 4 Blinzler. Ein einziges gelesenes Wort oder ein Niesen ruiniert die Hochrechnung für die gesamten 5 Minuten.
- **Zustandsübergänge:** Wenn das 15-Sekunden-Fenster genau in dem Moment öffnet, in dem der Operator sich streckt oder kurz aus dem Fenster schaut, wird ein 4-minütiger Deep-Work-State fälschlicherweise als "Ablenkung" klassifiziert.

### Perspektive 2: Der Kognitions- & Verhaltensforscher
- **Granularität von Fokus:** Kognitive Belastung und Aufmerksamkeit sind keine konstanten Zustände, sondern hochfrequente Oszillationen. Der Wechsel zwischen Problem-Fokussierung (Tunnel) und Lösungs-Evaluierung (Weitblick) passiert im Sekundenbereich.
- **Definition von "Kognitiver Last":** Rohe Blendshapes wie `browInnerUp` (Sorgenfalte) oder `browDownLeft`/`Right` (Konzentration, Zusammenziehen der Augenbrauen - Corrugator supercilii) sind stark vom Kontext abhängig. Sie messen Muskelanspannung, nicht zwingend produktiven Output.
- **Fazit:** Eine 15-Sekunden-Momentaufnahme ohne Kontext ist kognitionswissenschaftlich wertlos. Wir brauchen den *Verlauf* (Delta) über eine zusammenhängende Aufgabe, nicht isolierte Zeitstempel.

---

## 3. Metriken & Indikatoren (Das Vektor-Mapping)

Um Zustände empirisch messbar zu machen, ordnen wir den rohen Vektoren spezifische Zustands-Signaturen zu:

### A. Indikatoren für "Abwesenheit / Freizeit-Modus"
- **Gesicht / Gaze:** `face_present: false` oder Gaze konstant abgewandt (z.B. > 30 Sekunden `left`/`right` auf zweiten Monitor/TV gerichtet).
- **Haltung:** Zurückgelehnte Posture, asymmetrische Schulterlinie (entspannt), Hände nicht im Tastatur/Maus-Bereich.
- **Objekt-Erkennung:** Erkennung von Nahrungsmitteln, Tassen (Trink-Geste), Smartphone in der Hand.
- **Emotion:** `neutral` bis `happy`, stark fluktuierend (Reaktion auf Medien).

### B. Indikatoren für "Arbeits-Modus / Kognitiver Fokus"
- **Blink-Delta:** Signifikante Reduktion der Blinzelrate (`eyeBlinkLeft`/`Right` Frequenz fällt unter die individuelle Baseline).
- **Facial Tension:** Erhöhte Werte bei `browDownLeft`/`Right` (Fokussierung der Augen) und reduzierte Kieferbewegung (verbissener Fokus).
- **Gaze-Lock:** Blickrichtung (Gaze) extrem stabil im `center` (auf dem IDE-Monitor), Mikrobewegungen der Augen (Lesen/Scannen von Code).
- **Haltung:** Symmetrische, nach vorn geneigte Körperhaltung ("T-Rex-Arme" an der Tastatur).

---

## 4. Versuchsaufbau & Architektur-Vorschlag (System-Architekt)

Anstatt blind gegen die Uhr zu messen (Time-Driven), orchestrieren wir das System **ereignisgesteuert (Event-Driven)**. Die Sonde wird gezielt als *Bestätigungs-Werkzeug* (Validator) genutzt, wenn andere Sensoren eine Hypothese aufstellen.

### Das Experiment: "Context-Triggered Validation"

**Phase 1: Baseline-Kalibrierung (Takt 0)**
Bevor wir bewerten, müssen wir lernen. Der Operator startet manuell (via Befehl) eine 5-minütige kontinuierliche Aufzeichnung, während er aktiv codet. Daraus errechnet das System die *individuelle* Baseline für Blinkraten und Brow-Tension.

**Phase 2: Event-Driven Triggers (Takt 1-3)**
Die `VISION_SYNC`-Sonde wird an den `omega-event-bus` (Home Assistant / OS-Events) gekoppelt.

1. **Hypothese: "Operator hat Freizeit" (TV/Abwesenheit)**
   - *Trigger:* Home Assistant meldet: "TV im Wohnzimmer eingeschaltet" ODER "Kein Tastatur-Input für 5 Minuten".
   - *Aktion:* Sonde startet für 10 Sekunden.
   - *Validierung:* Sucht nach Objekten (Smartphone), Gaze-Abweichung vom Hauptbildschirm, Entspannungs-Haltung.
   - *Resultat:* Zustand wechselt offiziell auf "Leisure".

2. **Hypothese: "Operator ist im Deep Work" (Fokus)**
   - *Trigger:* Aktives Cursor-Fenster im Fokus UND kontinuierlicher Tastatur-Input für > 2 Minuten.
   - *Aktion:* Sonde startet im Hintergrund eine 30-Sekunden-Messung (Micro-Sampling).
   - *Validierung:* Vergleich der aktuellen `browDown`-Werte und Blinkrate mit der Baseline.
   - *Resultat:* Messung der "Kognitiven Last" (Stress/Flow-State) und Eintrag in die Zeitreihen-Datenbank (PostgreSQL/Chroma).

### Vorteile dieses Designs
1. **Ressourcen-Effizienz:** Die Kamera läuft nur, wenn ein Zustandswechsel wahrscheinlich ist oder tiefere Metriken benötigt werden.
2. **Kognitive Validität:** Die Daten haben einen Kontext (z.B. "Messung während IDE aktiv ist").
3. **Axiom-Konformität (A7):** Das System *glaubt* dem Tastatur-Input nicht einfach, sondern *verifiziert* den kognitiven Zustand durch physische Vektoren.

---
**Nächster Schritt:** Bestätigung dieses Test-Designs durch den Operator. Bei Freigabe wird der `scout_vision_bridge.py` Daemon entsprechend auf Event-Listener umgebaut.

[LEGACY_UNAUDITED]
