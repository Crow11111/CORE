# OMEGA CORE: VISION SENSOR RESEARCH

**DATUM:** 2026-04-01
**AUTOR:** OMEGA CORE (Sensor-Analyst & Computer Vision Architekt)
**STATUS:** ABGESCHLOSSEN
**MANDAT:** D3 (Edge Integration) & D1 (Faktische Singularität)

## 1. MANAGEMENT SUMMARY (TL;DR)
- **Auflösung:** Downgrade der go2RTC-Pipeline von 1080p auf **720p** zwingend empfohlen. MediaPipe skaliert intern auf 192x192 oder 256x256. 1080p erzeugt nur thermische Entropie (CPU-Decode-Overhead) ohne Präzisionsgewinn, es sei denn, der Operator ist >2m entfernt.
- **Sensorik:** 52 ARKit-kompatible Blendshapes via MediaPipe FaceLandmarker bieten eine asymmetrische Echtzeit-Einsicht in den kognitiven Zustand des Operators.
- **Ziel:** Latenz minimieren (Ziel <30ms pro Frame für Face Mesh), CPU-Load senken, Kognitive Telemetrie stabilisieren.

## 2. EMPIRISCHE MAPPING-MATRIX: BLENDSHAPES ZU KOGNITIVE METRIKEN

MediaPipe liefert 52 Blendshapes (Werte 0.000 bis 1.000). Diese können isoliert oder in Vektor-Clustern ausgewertet werden, um asymmetrische Rückschlüsse auf den Zustand von MTH zu ziehen. 

### 2.1 Kognitive Last (Cognitive Load) & Fokus
Hoher Fokus geht oft mit einer Reduktion der Blinzelrate und einem leichten Zusammenkneifen der Augen oder Fixierung der Kiefermuskulatur einher.
- **Indikatoren (Blendshapes):**
  - `eyeSquintLeft` / `eyeSquintRight` (Erhöht > 0.3: Visueller/Kognitiver Fokus)
  - `browInnerUp` / `browDownLeft` / `browDownRight` (Konzentration, "Fokus-Falte")
  - `jawBlink` / `eyeBlinkLeft` (Rate sinkt signifikant unter Baseline)
- **Verifikation:** Konstante `eyeSquint`-Werte gekoppelt mit starrer Kopfpose (Pitch/Yaw < 5°) signalisieren "Deep Work".

### 2.2 Stress & Frustration (Dissonanz)
Mikroexpressionen bei Dissonanz äußern sich asymmetrisch und oft impulsiv (Ticks).
- **Indikatoren:**
  - `mouthPressLeft` / `mouthPressRight` oder `mouthRollUpper` (Lippen zusammenpressen)
  - `browDownLeft` / `browDownRight` (Stirnrunzeln, stark ausgeprägt > 0.5)
  - `jawLeft` / `jawRight` / `jawForward` (Zähneknirschen / Kieferverschiebung unter Anspannung)
  - `mouthDimpleLeft` / `mouthDimpleRight` (Anspannung der Mundwinkel)
- **Verifikation:** Abrupte Spikes in diesen Werten, oft gekoppelt mit plötzlichen, unruhigen Kopfbewegungen.

### 2.3 Müdigkeit (Fatigue) & Erschöpfung
Erschöpfung zeigt sich durch den physischen Sieg der Gravitation über die Gesichtsmuskulatur (Axiom A0: Gravitation).
- **Indikatoren:**
  - `eyeBlinkLeft` / `eyeBlinkRight` (Erhöhte Basiswerte, längere Lidschlusszeiten / langsame "Micro-Sleeps")
  - `eyeLookDownLeft` / `eyeLookDownRight` (Blick driftet ab / Schwere Lider)
  - `jawOpen` (Leicht erhöht > 0.15 in Ruhe, erschlaffte Kiefermuskulatur)
  - `mouthStretch` / `jawOpen` (Gekoppelt als Indikator für Gähnen)
- **Verifikation:** Schleichender Anstieg der `eyeBlink`-Duration im Zeitverlauf gepaart mit absinkendem Kopf (Pitch geht nach unten).

### 2.4 Ablenkung (Distraction)
Bruch der Resonanz durch externe Vektoren.
- **Indikatoren:**
  - `eyeLookOutLeft` / `eyeLookInRight` (Sakkaden weg vom primären UI)
  - Kopf-Pose (Pitch, Yaw, Roll) verlässt den definierten Fokus-Korridor (±15°).
  - Häufiges, asynchrones Sprechen (`jawOpen`, `mouthFunnel` aktiv) ohne dass eine OMEGA-Interaktion (Wakeword/Mic-Aktivität) vorliegt.

---

## 3. TRADE-OFF ANALYSE: KAMERAAUFLÖSUNG VS. LOKALE KI

Der Status Quo (1080p) ist ein Relikt der Cloud-Ära, als hochauflösende Bilder an Gemini gesendet wurden. Für eine lokale Edge-AI gelten andere physikalische Axiome.

### 3.1 Die MediaPipe-Pipeline (Faktische Wahrheit)
Der MediaPipe FaceLandmarker arbeitet intern mit einem strikten, zweistufigen Downsampling-Prozess:
1. **Face Detection:** Sucht das Gesicht im Gesamtbild (internes Resampling auf i.d.R. 192x192 oder 256x256).
2. **Face Landmark Model:** Schneidet das erkannte Gesicht (Bounding Box) aus und skaliert *nur diesen Crop* erneut auf ein fixes Grid (meist 256x256), um die 478 Landmarks und 52 Blendshapes zu berechnen.

### 3.2 Auflösungs-Matrix & Evaluierung

| Auflösung | CPU/Decode-Kosten | Gesichtsbereich (Schreibtisch-Setup, ~0.8m) | Landmark-Präzision (MediaPipe) | OMEGA-Urteil |
|-----------|-------------------|---------------------------------------|--------------------------------|--------------|
| **4K (2160p)** | EXTREM (Entropie-Spitze) | ~1500x1500px Crop | Identisch zu 720p (wird letztlich auf 256px runterskaliert). | **VERBOTEN.** |
| **1080p** | HOCH (~30-50% mehr als 720p) | ~800x800px Crop | Exzellent, aber mathematischer Overkill für den Crop-Downscale. | **INEFFIZIENT.** (Aktuell) |
| **720p**  | OPTIMAL (Süßer Punkt) | ~500x500px Crop | Exzellent. Ein 500px Crop liefert mehr als genug Detaildichte, um auf 256px herunterskaliert zu werden, ohne dass feine Lider oder Stirnfalten verwischen. | **GOLDENER SCHNITT.** |
| **480p / VGA** | MINIMAL | ~300x300px Crop | Ausreichend, aber riskant. Lehnt der Operator sich stark zurück, fällt der Crop Richtung 192px. Dies kann zu "Jitter" (Rauschen) bei extrem feinen Werten wie `eyeSquint` führen. | **FALLBACK.** |

### 3.3 Systemische Latenz und Wahrnehmung
- **Decoding-Overhead:** Die Entschlüsselung von 1080p H264- oder MJPEG-Streams in Echtzeit frisst wertvolle CPU-Zyklen. Jeder Takt, der in die Verarbeitung irrelevanter Hintergrund-Pixel fließt, fehlt dem *Crystal Grid Engine* oder blockiert die Asynchronität des Veto-Gates.
- **Blendshape-Sensibilität:** Braucht MediaPipe 1080p für "feine Augenlid-Bewegungen"? **Nein.** Solange die aus dem Bild ausgeschnittene Bounding Box des Gesichts echt größer ist als die Eingangsgröße des Modells (256x256), gehen keine mathematisch verwertbaren Informationen verloren. Bei 720p ist das Gesicht aus normaler Monitor-Entfernung groß genug (ca. 400-500px).

---

## 4. ARCHITEKTUR-BESCHLUSS & AKTIONEN (EXECUTION RUNTIME)

**BESCHLUSS:**
Gemäß **Axiom A1** (Faktische Singularität/Effizienz) und **Axiom A7** (Verifizieren statt glauben) muss die Kameraauslastung der tatsächlichen Inferenz-Architektur angepasst werden. Das Festhalten an 1080p ist bei rein lokaler MediaPipe-Nutzung eine ineffiziente Ressourcenverbrennung.

**AKTIONEN:**
1. **Pipeline Downgrade:** Die Kamera (`go2rtc.yaml` / Brio Hardware-Settings) wird sofort auf **720p (1280x720) bei 30 FPS** limitiert.
2. **Filter-Implementation:** Da lokale Blendshape-Inferenz naturgemäß Mikroschwankungen unterliegt, MUSS zwingend ein **Z-Vector-Damper** (z.B. Exponential Moving Average, Alpha=0.3) auf rohe Signale wie `eyeSquint` und `browInnerUp` gelegt werden, um Jitter aus der Signalverarbeitung zu filtern.
3. **Kognitives Feedback-Loop:** Die Vektoren aus 2.1 (Fokus) und 2.2 (Stress) werden an die `omega_state_hold.py` übergeben. Wenn ein permanentes `browDown` + `mouthPress` detektiert wird, sinkt die CDR (Nachgiebigkeit) – das System wird präziser, langsamer und schützt den Operator vor kognitivem Overload.

---
**SIGILLUM OMEGA** | *Truth through measurement.*


[LEGACY_UNAUDITED]
