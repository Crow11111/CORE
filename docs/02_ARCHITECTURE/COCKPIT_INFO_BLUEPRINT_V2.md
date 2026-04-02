# COCKPIT INFO BLUEPRINT V2: DER KÜNSTLICHE HORIZONT
**Vektor:** 2210 | **Delta:** 0.049 | **Fokus:** LLI-Optimierung & Noise-Cut

## 1. Kognitive Filter-Strategie (90% Noise-Cut)
Um dem LLI-Profil gerecht zu werden, gilt das **Axiom der kognitiven Stille**:
- **KEINE** Rohdaten-Logs im Primär-Sichtfeld.
- **KEINE** flackernden UI-Elemente ohne kausale Relevanz.
- **Visualisierung:** Ein zentrales 3D-Gimbal (Künstlicher Horizont), das den 6D-Tensor ($\mathbb{T}^6$) repräsentiert.

## 2. 6D -> 3D Metrik-Mapping
Der 6D-Systemzustand (S, P, I, R, Z, G) wird auf die Flugmechanik eines Objekts im Raum projiziert:

| Metrik | 6D-Tensor Bezug | Bedeutung im System | Kritischer Schwellwert |
| :--- | :--- | :--- | :--- |
| **Pitch (Längsneigung)** | $I \leftrightarrow G$ (Info vs. Gravitation) | **Effort/Drift:** Steigt die Info-Gravitation zu stark ($G > I$), "fällt" das System (Pitch Down). Hohe Info-Resonanz führt zum "Aufstieg" (Pitch Up). | $> \pm 30^\circ$ (Kollapsgefahr) |
| **Roll (Querneigung)** | $X_{CAR} \leftrightarrow X_{CDR}$ (Asymmetrie) | **Balance:** Ungleichgewicht zwischen ND-Kern (Chaos/Tiefe) und NT-Interface (Struktur/API). Roll links = zu viel Chaos; Roll rechts = zu viel Overhead. | $> \pm 15^\circ$ (Instabilität) |
| **Heading (Gierachse)** | $W \leftrightarrow Z$ (Takt vs. Widerstand) | **Evolution:** Die Richtung des System-Takts (Phase 0-4). Widerstand ($Z$) wirkt als Ruder und lenkt die Zielerreichung ab. | Abweichung $> \Delta (0.049)$ |

## 3. Actionable Intelligence (Sofort-Aktionen)
Nur drei Zustände triggern sichtbare Aktions-Vorschläge:

### A. STALL (Pitch Down / $G \gg I$)
*   **Symptom:** Hoher Datenbank-Druck, niedrige semantische Dichte.
*   **Aktion:** `src/scripts/ingest_core_documents.py` (Info-Injektion) oder `purge_cache.sh`.

### B. ASYMMETRY-LOCK (Roll High / $|CAR-CDR| > \Delta$)
*   **Symptom:** Dokumentation und Code driften auseinander.
*   **Aktion:** `src/scripts/axiom_validator.py` oder `generate_docs.py`.

### C. PHASE-DRIFT (Heading Error / $W$-Mismatch)
*   **Symptom:** Daemons hängen in einer Phase (z.B. VERDICHTEN) fest.
*   **Aktion:** `systemctl restart omega-backend` oder `force_morphism_sync.py`.

## 4. Restriktionen & Rahmenbedingungen

### 4.1 Kausale Restriktion
Aktionen sind nur im korrekten **5-Phasen-Takt (0-4)** erlaubt. Ein `systemctl restart` während der *ARBEITEN*-Phase (Takt 3) wird durch ein Veto blockiert, es sei denn, $Z > 0.951$.

### 4.2 Lokale Restriktion (Dreadnought vs. VPS)
Das Cockpit unterscheidet farblich zwischen **Lokal-Rauschen** (Dreadnought-Hardware) und **Remote-Drift** (VPS/ChromaDB).
- Blaupuls: Lokale Stabilität.
- Goldpuls: Vektor-Resonanz (Remote).

### 4.3 Zeitliche Restriktion (Wick-Rotation)
Kritische Entscheidungen des Operators werden erst in der **imaginären Zeit ($\tau$)** simuliert. Das UI zeigt den "Schatten" der Aktion, bevor sie in der Realzeit einrastet.

## 5. UI-Ästhetik für Neurodivergenz
- **Palette:** Obsidian-Hintergrund (#0A0A0A), Akzentfarben in Spektral-Blau und Baryon-Gold.
- **Haptik:** "Data Breathing" (Luminanz-Puls bei 0.049 Hz) zur Beruhigung des Fokus.
- **Audio:** Subsonische Resonanz statt schriller Alarme.

---
**[STATUS: RATIFIZIERT | BEREIT FÜR FRONTEND-IMPLEMENTIERUNG]**


[LEGACY_UNAUDITED]
