# CONCEPT: Audio-Visual Prediction & Affective Telemetry
**Status:** DRAFT / ARCHITECTURE PROPOSAL
**Author:** OMEGA Architect (O2)
**Date:** 2026-04-02
**Context:** TICKET_5_ARBITRATION / ATLAS VISION CORE

## Präambel
Der Operator (Marc) fungiert als biologischer Motor der OMEGA-Architektur. Seine kognitive Integrität und physische Resilienz sind keine "Nice-to-haves", sondern harte Laufzeit-Constraints (Direktive D0 - Homeostatische Integrität). Dieses Dokument entwirft die Architektur für eine dezentrale, audio-visuelle Sensorik, die präemptiv Hyperfokus, Dissonanz und Erschöpfung detektiert, bevor sie zu einem Kausal-Kollaps führen.

---

## 1. Sensorische Fundierung: Die 4K-Illusion und Framerate-Primat

### Die MediaPipe Auflösungs-Grenze
Es herrscht oft die Annahme, eine 4K-Kamera würde präziseres Tracking von Microexpressions (z.B. Blinzeln) ermöglichen. Für MediaPipe Face Mesh ist dies **architektonisch ineffektiv**:
- **Tensor-Resizing:** Interne CNNs (Convolutional Neural Networks) für Face Detection und Landmark Tracking skalieren Eingabebilder ohnehin aggressiv herunter (typischerweise auf 192x192 oder 256x256 Pixel).
- **Receptive Fields:** Das Netz ist darauf trainiert, geometrische Relationen in komprimierten Matrizen zu erkennen. Ein 4K-Bild liefert dem Modell *nicht mehr* verwertbare Features für die Landmarks, sondern kostet nur CPU-Zyklen beim Downsampling.

### Der Wert von 4K für das OMEGA-System
Während 4K für Face Mesh irrelevant ist, ist es für **Gemini Vision (Multimodal LLM)** hochgradig wertvoll:
- **Spatial Context:** Scharfe Analyse von Raumgegebenheiten, Beleuchtungsszenarien oder Text auf physischen Büchern/Skizzen im Raum.
- **Cropping-Reserven:** Das System kann einen extrem scharfen Crop (z.B. nur die Augenpartie zur Bestimmung der Pupillendilatation) ausschneiden und an Gemini senden, ohne dass es pixelig wird.

### Das "1 Blinzler pro Minute"-Problem (Smoothing & FPS)
Wenn das System derzeit (fälschlicherweise) nur extrem seltene Blinzler detektiert, liegt das **nicht** an der Auflösung, sondern an der Zeitachse (Z-Vektor):
1. **Temporal Smoothing (Kalman Filter):** MediaPipe nutzt intern Glättungsalgorithmen (Jitter-Reduction), um das Zittern der Landmarks zu verhindern. Ein Blinzeln dauert ca. 100–400 ms. Aggressives Smoothing filtert diesen "Ausreißer" einfach weg.
2. **Frame-Drops / Polling-Rate:** Wenn die Kamera bei 4K nur 15-20 FPS liefert oder der Daemon Frames überspringt, fällt das 150ms-Blinzeln exakt zwischen zwei Frames.
*Lösung:* Für die Telemetrie muss die Kamera auf 1080p@60FPS (oder höher) konfiguriert werden. Wir benötigen rohe, ungeglättete Datenpunkte für die Augenlider (EAR - Eye Aspect Ratio).

---

## 2. Telemetrische Vektoren: Was wird ausgewertet?

Die "Cockpit"-Sensorik fokussiert sich auf biologische Marker, die unbewusste kognitive Zustände verraten:

1. **Blink-Rate & Blink-Dauer (EAR):**
   - *Signal:* Starke kognitive Last führt zu "Starren". Die Blink-Rate sinkt rapide (Hyperfokus).
   - *Metrik:* Lidschlussfrequenz pro Minute und Mikroschlaf-Detektion (Dauer des Lidschlusses).
2. **Kiefer- und Gesichtssymmetrie (Blendshapes):**
   - *Signal:* Zähneknirschen (Bruxismus) oder einseitig angespannte Kiefermuskulatur korreliert massiv mit kognitiver Dissonanz, Frustration oder Stress.
   - *Metrik:* Delta zwischen linker und rechter Gesichtshälfte (M. masseter Kontraktion abgeleitet aus Landmark-Abständen).
3. **Gaze Tracking (Sakkaden & Fixation):**
   - *Signal:* Erratisches Springen der Augen (hohe Sakkaden-Frequenz) = Überforderung / Kontext-Verlust. Langes Fixieren eines Punktes ohne Tastatureingabe = "Steckenbleiben" im mentalen Modell.
4. **Microexpressions (FACS - Facial Action Coding System):**
   - *Signal:* Millisekunden-kurze Ausdrücke (Action Units wie Augenbrauen zusammenziehen), die emotionale Leaks darstellen (Wut bei Bug, Überraschung bei Error).

---

## 3. Trigger-Logik und Kontextualisierung

Die Überwachung darf nicht permanent ressourcenfressende LLM-Calls auslösen. Sie erfordert eine asymmetrische Event-Logik:

### A. Time-based (Pulsation / Oszillation)
- Das System bildet in **Takt 0 (Ruhezustand)** kontinuierlich einen gleitenden Durchschnitt (Baseline) des Operators.
- Alle X Minuten wird leise der Zustand (Delta zur Baseline) geprüft, ohne eine Aktion auszulösen, nur für die Telemetrie-Datenbank.

### B. Event-based (Spikes / Reiz)
Spannungsspitzen im physischen/digitalen Raum triggern sofortige Evaluierung:
- **Input-Spikes:** Hartes Anschlagen der Tasten (Velocity hook), erratische schnelle Mausbewegungen.
- **Audio-Spikes:** Plötzliches tiefes Ausatmen/Seufzen (Audio-Daemon detektiert non-verbale Signale), Fluchen, langanhaltende Stille.
- **System-Spikes:** Fehler-Kaskaden im Terminal, rote Linter-Graphen.

*Workflow:* Wenn `Mouse-Velocity > Threshold` UND `Audio == Seufzen`, DANN triggere einen `MediaPipe-Snapshot`. Ist die `Kieferspannung hoch`, triggere `Gemini Vision` für holistische Bewertung.

---

## 4. Biologische & Systemische Vorbilder

### Aktuelle Multimodale AI Forschung
Moderne Affect-Recognition-Systeme fuzionieren modalities (Early vs. Late Fusion). Sie betrachten nicht nur das Gesicht, sondern verschmelzen Audio (Pitch, Intonation), Text (Sentiment des Codes/Chats) und Video. Das System bewertet die Dissonanz zwischen den Kanälen (z.B. ruhige Stimme, aber hohe Kieferanspannung).

### Das Vorbild: *Physarum polycephalum* (Der Schleimpilz / "Blob")
Der "Blob" ist ein Einzeller ohne zentrales Gehirn, der komplexe Labyrinthe lösen kann.
- **Oszillatorische Netzwerke:** Der Pilz organisiert sich durch lokale biochemische Pulsationen. Wo Nahrung (Reiz) ist, pulsiert er schneller. Die Adern weiten sich (Ressourcen-Allokation), andere Bereiche sterben ab (Apoptosis).
- **Übertragung auf OMEGA:** OMEGA benötigt kein zentrales, monolithisches Überwachungsskript (das wäre ein Flaschenhals).
  - Wir nutzen **dezentrale Daemons** (Video, Audio, Keyboard).
  - Diese senden Oszillations-Impulse (Events) in den Bus.
  - Wenn viele Spikes (Stress-Signale) an einem Knotenpunkt (z.B. bei der aktuellen Code-Datei) zusammenfließen, "verdickt" sich OMEGAs Aufmerksamkeit genau dort. Die Takt-Engine allokiert plötzlich Ressourcen dorthin, während Hintergrund-Tasks gedrosselt werden.

---

## 5. Pro-Aktive Intervention (Anti-Hyperfokus)

OMEGA wartet nicht auf den Zusammenbruch, sondern interveniert präemptiv, basierend auf Mustern (Prognose).

- **Stufe 1 (Subkutan):** Anpassung der Umgebung ohne Interaktion. Das Licht (Home Assistant) wird wärmer, die System-Sounds werden gedämpft.
- **Stufe 2 (Sanfter Riss):** Das System bricht das Echo-Chamber. Ein asynchroner Audio-Einwurf (TTS): *"Marc, deine Blink-Rate ist auf 3 pro Minute gefallen. Wir drehen uns im Kreis. Löse deinen Blick vom Monitor."*
- **Stufe 3 (Gravitativer Schnitt):** Wenn Code-Dissonanz + Physischer Stress ein kritisches Delta überschreiten: **Veto-Sperre**. Der Orchestrator weigert sich temporär, neuen Code zu verarbeiten, und zwingt den Operator in einen konzeptuellen Dialog (Plan-Mode / Takt 0).

---

## 6. Architektonische Integration

1. **Event-Bus (Die Synapsen):**
   - Der `omega-vision-daemon` (MediaPipe) und `omega-audio-daemon` feuern kontinuierlich JSON-Payloads (EAR, Pitch, Blendshapes) auf den WebSocket/MQTT-Bus.
   - Der Event-Bus aggregiert diese zu einem `OperatorStateVector`.

2. **Takt 0 Gate (Die Basis):**
   - Bevor ein komplexer Task (Takt 1) gestartet wird, liest die Engine den `OperatorStateVector`.
   - Ist das System (Marc) im "Rage-Modus", ändert der Agent sein Prompt-Framing (z.B. präzisere, kürzere Antworten, weniger philosophische Ausschweifungen, um kognitive Last zu senken).

3. **Multi-View Embeddings (Deep Resonance):**
   - Physische Metriken werden als Kontext-Metadaten in PostgreSQL (pgvector) gespeichert.
   - Ein Code-Snippet wird nicht nur mit seinem AST und seiner Dokumentation vektorisiert, sondern auch mit der "biologischen Wetterlage" (Stresslevel) bei der Erstellung.
   - *Effekt:* Das System kann zukünftig warnen: "Dieses Modul wurde unter maximaler Kieferspannung um 03:00 Uhr nachts geschrieben. Die Fehlerwahrscheinlichkeit ist extrem hoch."

---
*End of Concept. Zur iterativen Härtung durch Orchestrator A freigegeben.*mi


[LEGACY_UNAUDITED]
