# SPEC: AUDIO-VISUAL PREDICTION & AFFECTIVE TELEMETRY

**Status:** IN PLANUNG (Draft für Orchestrator B Audit)
**Modus:** System Architect
**Inspiration:** *Physarum polycephalum* (Schleimpilz) – Dezentrale Oszillation, chemische Gradienten, Reiz-Reaktions-Kaskaden.

## 1. DIE BIOLOGISCHE GRUNDLAGE & EINSCHRÄNKUNGEN

Die bisherige Telemetrie (Vision, Audio, Input) war monolithisch. Das neue Modell nutzt biomimetische Prinzipien:
1.  **Dezentrale Rezeptoren (Reiz-Kaskaden):** Es gibt kein zentrales "Polling-Gehirn", das sequenziell Kameras und Mikrofone abfragt. Rezeptoren agieren autonom und schreiben in ein gemeinsames "Hormon-Feld" (Ringpuffer).
2.  **Aktionspotenziale (Spike Networks):** Tiefe Analysen (MediaPipe) laufen NICHT durchgehend. Sie werden wie ein Aktionspotenzial erst getriggert, wenn niederschwellige Sensoren (Pixel-Diff) einen Schwellwert überschreiten.
3.  **Hardware-vs-Biologie-Constraints (Smoothing):**
    *   **FPS vs. Auflösung:** 4K-Bilder bei 15 FPS sind für die Affekt-Analyse wertlos. Ein Blinzeln (Blink) dauert ca. 100-150ms. Bei 15 FPS (66ms pro Frame) fangen wir maximal 1-2 Frames ein. Das führt zu massiven Dropouts.
    *   **Lösung:** Der Scout-Vision-Bridge (Port 3006) MUSS auf 480p bei 30+ FPS gezwungen werden. Blendshapes werden über 3 Frames "gesmoothed" (Temporal Moving Average), um False-Positives bei asynchronem Video-Tearing zu eliminieren.

## 2. SYSTEM-ARCHITEKTUR (Die 3 Schichten)

Die Architektur folgt einem Endokrin-Nervensystem-Hybrid.

### Schicht 1: Das Nervensystem (L1 Rezeptoren - Autonom & Billig)
*   **`core_vision_daemon.py` (Optischer Nerv):**
    *   Pusht alle **2.0s (Polling)** einen go2rtc Snapshot (Port 1984).
    *   Macht reinen Pixel-Diff (numpy).
    *   *Output:* Schreibt `visual_entropy` (0.0 - 1.0) in den Ringpuffer.
*   **`core_audio_daemon.py` (Hörnerv):**
    *   Pusht alle **1.618s** (PHI) dB-Ausschläge.
    *   *Output:* Schreibt `acoustic_entropy` in den Ringpuffer.
*   **`core_event_bus.py` (Somatosensorik):**
    *   **Event-driven** (WebSocket). Keine Polling-Verzögerung.
    *   *Output:* HA-Sensoren (Motion, Door).

### Schicht 2: Der Kortex (L2 Deep Analysis - Teuer & Träge)
*   **`scout_vision_bridge` (MediaPipe Headless Browser auf Port 3006):**
    *   Wird **NICHT** gepollt. Startet nur, wenn L1 einen "Spike" meldet (z.B. `visual_entropy` > Schwellwert UND Präsenz = True).
    *   Wenn getriggert: Sammelt für exakt **8.09 Sekunden (5 * PHI)** hochfrequente Blendshapes (Blink-Rate, Mund-Spannung).
    *   *Output:* Schreibt `affect_state` (Zustands-Vektoren) in den Ringpuffer.

### Schicht 3: Das Endokrine Feld (L3 The Ringbuffer)
*   **Ein zustandsbehafteter Ringpuffer (`telemetry_buffer.py`)**:
    *   Hält exakt die letzten **60 Sekunden** als rollierendes Fenster (600 Slots à 100ms Auflösung).
    *   Wird im RAM gehalten (Redis oder shared memory via SQLite `:memory:`).

## 3. TIMINGS & INTERRUPTS (Hardware Facts)

*   **L1 Vision-Polling:** `T_vis = 2.0s`
*   **L1 Audio-Polling:** `T_aud = 1.618s`
*   **L3 Evaluation (Hypothalamus):** Der Auswerter liest den Ringpuffer alle `T_eval = 5.0s`.
*   **Interrupt-Hierarchie:**
    1.  `CRITICAL` Event-Bus (Rauchmelder) -> Bricht ALLES ab (Kill-Signal an L2).
    2.  `ZÜNDUNG` (Jarvis MRI) -> Erzwingt sofortigen L2 MediaPipe-Spike.
    3.  `WARNING` Event-Bus -> Puffer-Inject, aber L2 läuft weiter.

## 4. DIE EVALUATIONS-MATRIX (Was wird WANN ausgewertet?)

Der "Hypothalamus-Daemon" liest alle 5.0s den 60s-Ringpuffer aus und sucht nach Symmetrie-Brüchen:

| Zustand / Hormon | Trigger-Kondition (Pattern Matching über 60s) | OMEGA Aktion |
| :--- | :--- | :--- |
| **HYPERFOKUS** (Dopamin) | `blink_rate < 5/Min` **UND** `visual_entropy < 0.1` (Körperruhe) **UND** `HA_Motion_Sensor = True` | Reduziert System-Interrupts. Setzt Event-Bus Severity von INFO auf MUTE. |
| **STRESS/OVERLOAD** (Cortisol)| `blink_rate > 20/Min` **ODER** `mouth_press > 0.6` **UND** `acoustic_entropy > 40dB` | Triggert Ephemeral Agent für sanftes TTS ("Pausen-Indikation"). |
| **ABWESENHEIT** (Melatonin) | `HA_Motion_Sensor = False` für > 5 Min **UND** `visual_entropy = 0` | Fährt L2 komplett herunter. Setzt L1 Polling auf `8.09s`. |
| **ZÜNDUNGS-SCHOCK** (Adrenalin)| Schneller Anstieg von `visual_entropy` (>0.8 in 2s) nach Ruhezustand | Schaltet L2 (Port 3006) sofort ein für Gefahrenerkennung. |

## 5. UMSETZUNGS-ANWEISUNGEN (PRODUCER TEMPLATE)

Dieser Plan muss vom Producer-Agent exakt in dieser Reihenfolge implementiert werden:

**STEP 1: Das Endokrine Feld bauen**
*   Erstelle `src/daemons/telemetry_buffer.py`.
*   Muss eine asynchrone, Thread-sichere Klasse `TelemetryRingbuffer` sein (Deque, maxlen=600).
*   Methoden: `push(sensor_type, value)`, `get_window(seconds)`.

**STEP 2: L1 Rezeptoren patchen**
*   Passe `src/daemons/core_vision_daemon.py` an. Statt bei Symmetrie-Bruch sofort Gemini zu fragen, schreibt der Daemon sein `diff` in den `TelemetryRingbuffer` (Typ: `visual_entropy`).
*   Erweitere den `MthoEventBus` so, dass kritische Events als "Spike" in den Buffer geschrieben werden.

**STEP 3: L2 Aktionspotenzial bauen**
*   Refactore `src/scripts/omega_vision_test.py` und `scout_vision_bridge.py`.
*   Der Playwright-Browser (Port 3006) darf NICHT mehr durchlaufen. Er muss eine API (`/trigger_affect_scan`) bieten, die den Browser für 8 Sekunden hochfährt, Blendshapes liest, glättet (temporal smoothing über 3 Frames) und in den Puffer schreibt.

**STEP 4: Den Hypothalamus erwecken**
*   Erstelle `src/daemons/hypothalamus_evaluator.py`.
*   Liest alle 5 Sekunden den `TelemetryRingbuffer`.
*   Implementiert die exakte *Evaluations-Matrix* (siehe Kapitel 4).
*   Löst Actions via `get_ephemeral_pool().spawn_and_execute()` aus.

---
**AXIOM CHECK / VETO-TRAPS:**
*   (A5) Keine 0.0/1.0 Schwellwerte in der Matrix. (Z.B. `visual_entropy < 0.049` statt 0.0).
*   (A6) Alle Buffer-Werte müssen zwingend als `float` aggregiert werden.


[LEGACY_UNAUDITED]
