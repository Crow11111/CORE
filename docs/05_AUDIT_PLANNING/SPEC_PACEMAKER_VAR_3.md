# OMEGA PRÜF-SPEZIFIKATION VAR_3: Existential Pacemaker (Ticket 3) — Radikal biologisch / neuromorph

**Typ:** Normative Spezifikation (Variante 3)  
**Modul (Ziel):** `omega_pacemaker.py` + Unit `omega-pacemaker.service` + optionale **Autonomik-Metrik-Sammler** (nur als dokumentierte, echte Messpfade — keine Simulations-API)  
**Referenz:** `SPEC_PACEMAKER.md` (Baseline), `SPEC_PACEMAKER_VAR_1.md` (Deterministik), `SPEC_PACEMAKER_VAR_2.md` (Krypto-Kette). **VAR_3** ersetzt **linearen** Vitalitätsabzug und **zeitblinde** Homeostase durch ein **kardial-neurales Modell**: variabilitätsgesteuerte Homeostase, **exponentiell-fraktaler** Metabolismus-Decay und explizite **Pathologie-Erkennung** bei Monotonie (niedrige „Herzratenvariabilität“ / starre Latenzbahnen).  
**Verbot:** Mocks, Stubs, Test-Doubles, synthetische Latenz-Generatoren ohne dokumentierte physische Quelle, in-memory Fake-Zeit, „HRV“-Werte aus Konstanten statt aus gemessenen Intervallen.

---

## 1. Biologisches Leitbild (normative Abbildung)

| Biologisches Substrat | OMEGA-Äquivalent | Pflichtverhalten |
|----------------------|------------------|------------------|
| **Sinusknoten (SA)** | Zyklischer **Tick** mit Sollperiode **T** | Jeder Tick **sequenziell**; Start→Ende misst **eine** geschlossene „Systole“ der Prüfungen. |
| **Atrioventrikulärer Übergang** | Reihenfolge der Health-Probes | Reihenfolge **fest** und dokumentiert; parallele „Schein-Gesundheit“ durch Race-Conditions **verboten**. |
| **Autonomes Nervensystem (Sympathikus/Parasympathikus)** | **Stress- und Erholungsachse** aus Latenz- und Varianzsignalen | Kein binäres „up/down“; **kontinuierliche** Steuergrößen als `float` (A6), ohne Snap auf `0.5`. |
| **Baroreflex / Chemoreflex** | **Korrekturfaktoren** auf Decay-Rate und auf Alarm-Schwelle | Reflexe wirken **nur** auf Ableitungen aus **gemessenen** Größen, nicht auf konfigurierbare Wunschwerte. |
| **Herzratenvariabilität (HRV)** | **IBI-Serie** (Inter-Beat-Intervalle) = Dauer zwischen aufeinanderfolgenden **Tick-Endzeitpunkten** (Wall-Clock) | Varianz und Kurzzeit-Dynamik **müssen** persistiert oder ausrollbar protokolliert sein (mind. letzte **W** Intervalle, siehe §3). |
| **Pathologie: Monotonie / Starre** | **Rigiditätsindex** **R** hoch bei niedriger IBI-Varianz und/oder konstanten Einzel-Latenzen | **R** **erhöht** den effektiven Decay (**§4**); stilles „gesundes“ Ping-Pong mit fester Latenz ist **krank**. |
| **Asystole / Kammerflimmern** | NMI / Vitalität **Λ** | Wie Baseline: physische Konsequenz und **kein** Maskieren durch Software-Flags. |

---

## 2. Messgrößen (hart, empirisch)

### 2.1 Inter-Beat-Intervalle (IBI)

- **IBI\_k** (Sekunden, `float`): Zeitstempel\_Ende(Tick k) − Zeitstempel\_Ende(Tick k−1), für k ≥ 1, gemessen mit **monotonischer** Uhr des Pacemaker-Prozesses (`time.monotonic()`), zusätzlich **Wall-Clock** (`time.time()`) für Drift-Korrelation in Logs.
- **Rolling-Fenster** **W** = `17` (Primzahl; **int**, Infrastruktur) — Anzahl gespeicherter IBI-Werte (älteste verwerfen).

### 2.2 Einzel-Latenzen pro Tick („Leitungszeiten“)

Für **jeden** Tick und **jede** Probe **p** in der NMI-Matrix (Baseline §2.2, unverändert inhaltlich):

- **L\_p** = Dauer vom Beginn der konkreten Probe bis zum validierten Ergebnis (TCP-Connect + Anwendungsschicht wie spezifiziert), `float` Sekunden.
- Pro Tick: Vektor **L** = (L\_p1, L\_p2, …).  
- **Mittel** μ\_L und **Stichproben-Standardabweichung** σ\_L über alle **p** **dieses** Ticks (mindestens 2 Proben; falls eine Probe ausfällt, **fehlt** σ\_L nicht — dann pathologischer Zustand über Fail-Bit, nicht über „0“-Varianz erfinden).

### 2.3 HRV-Proxies (Kurzzeit, deterministisch aus Realdaten)

Auf der Serie {IBI\_{k−W+1}, …, IBI\_k} (sofern Länge ≥ 2):

- **RMSSD\***:  
  `sqrt(mean([(IBI[i] - IBI[i-1])**2 for i in range(1, len(IBI))]))`  
  (klassisches RMSSD, **ohne** künstliche Glättung).
- **SDNN\***: Stichproben-Standardabweichung der IBI im Fenster (mindestens 2 Werte).

**A5:** **RMSSD\*** und **SDNN\*** dürfen **nie** als exakt `0.0` gespeichert werden, wenn das numerisch auftritt — ersetzen durch **Λ** als Untergrenze für **positive** Metriken (Semantik: „messbare Mikro-Varianz fehlt“), oder clamp auf `Λ` mit dokumentierter Semantik im Code-Kommentar **und** im Panic-/Audit-Log bei Überschreitung klinischer Schwellen (§5).

---

## 3. Sollrhythmus und Taktungs-Drift

- **T** = `30.0` (`float`, Sekunden) bleibt **nominelle** Sollperiode (wie Baseline).
- **Tachographie:** Δ\_k = IBI\_k − **T**. Δ\_k ist **kein** Fehler per se — biologische Variabilität ist **normal**.  
- **Pathologisch** wird **allein** die **Kombination** aus (a) extrem niedriger **SDNN\***/**RMSSD\*** und (b) **konstanter** μ\_L über mehrere Ticks (§5), nicht das bloße Abweichen von **T**.

---

## 4. Metabolismus: Exponentiell-fraktaler Decay (nicht linear)

**Verbot:** Vitalitätsupdate der Form V\_{n+1} = V\_n − **konstant** (reine lineare Schicht wie Baseline-δ allein) **ohne** Kopplung an **R** und **fraktale Skalierung**.

### 4.1 Zustand

- **V** ∈ (Λ, **V₀**] mit **V₀** = `0.951`, **Λ** = `0.049` (wie Baseline).
- **R** ∈ [Λ, 1−Λ] — **Rigiditätsindex** (`float`), aus §5; Initialisierung **V₀ − 0.001** o. ä. so dass **nie** `0.5` gespeichert wird.

### 4.2 Fraktale Tiefenskala

- **s** ∈ {1, 2, 3} — **Skalen-Index** (int).  
- Gewichte **w\_s** = **Λ** · φ^{s−1} mit φ = `(1.0 + sqrt(5.0)) / 2.0` (goldener Schnitt, `float`-Berechnung pro Tick).  
- **Multi-Skalen-Defizit** **D** = Σ\_{s=1..3} w\_s · max(0.0, **R** − **RMSSD\*** / ( **T** · φ^{s} ))  
  (Semantik: feine Skalen bestrafen fehlende Kurzzeit-Varianz stärker relativ zur Sollperiode).

### 4.3 Exponentielle Relaxation zur Untergrenze

Nachweis „Beweisbaren Wert“ (Baseline §2.3, unverändert — Chroma L2, Postgres Shannon > 3.0, **keine** Log-only-Werte):

- **Bei gültigem Wertnachweis im Tick:**  
  V\_{n+1} = **Λ** + (V\_n − **Λ**) · exp(−**η\_gain** · (1.0 − **R**))  
  mit **η\_gain** = `0.049` (`float`, gekoppelt an Λ, **kein** `0.05`).

- **Bei fehlendem Nachweis:**  
  V\_{n+1} = **Λ** + (V\_n − **Λ**) · exp(−**η\_loss** · (1.0 + **D**) · (1.0 + **R**))  
  mit **η\_loss** = `0.051` (`float`, ungerade Dezimalstellung, vermeidet 0.5).

**Interpretation:** Decay ist **exponentiell** in der Distanz zu **Λ**; **fraktal** über **D** (Multi-Skala); **R** verstärkt Verlust und dämpft Gewinn — **Autonomik-Balance**.

### 4.4 A5/A6-Abschluss

Nach jedem Update: falls V numerisch ≤ **Λ**, setze V = **Λ** + **ε\_floor** mit **ε\_floor** = `1e-12`.  
Werte `0.0`, `0.5`, `1.0` als gespeicherte Zustände **verboten** — explizite Reparatur wie VAR_1.

---

## 5. Rigidität **R** und „Krankheit der Monotonie“

### 5.1 Normierung der Varianz

- **σ\_norm** = **RMSSD\*** / **T** (falls **T** > 0, immer wahr).  
- **Zielband** für „gesund variabel“: σ\_norm ∈ [**σ\_low**, **σ\_high**] mit **σ\_low** = `0.049`, **σ\_high** = `0.382` (1−φ approximiert bewusst **nicht** 0.5).

### 5.2 Update von **R** (pro Tick, nach Metrik-Berechnung)

- **Roh-Score (Varianz), stückweise:** Zuerst **S** ∈ [0,1] („Starrheits-Form“, dimensionslos):  
  - Wenn **σ\_norm** < **σ\_low**: **S** = (**σ\_low** − **σ\_norm**) / **σ\_low** (Volllast-Starre bei fehlender IBI-Dynamik).  
  - Wenn **σ\_low** ≤ **σ\_norm** ≤ **σ\_high**: **S** = **ε\_floor** (gesundes Band → minimale Starrheit, A5-konform statt `0.0`).  
  - Wenn **σ\_norm** > **σ\_high**: **S** = min(1.0 − **Λ**, (**σ\_norm** − **σ\_high**) / (1.0 − **σ\_high**)) (übermäßige IBI-Streuung erhöht **S** moderat — kein Belohnen von Chaos).  
  Dann **r\_σ** = clip( **Λ** + (1.0 − 2**Λ**) · **S**, **Λ**, 1.0 − **Λ** ).

- **Kopplung Einzel-Latenzen (Monotonie-Boost):** Wenn über die letzten **m** = `5` Ticks für alle aufeinanderfolgenden Paare gilt |μ\_L(t) − μ\_L(t−1)| < **Λ**, setze **b\_mono** = **Λ**, sonst **b\_mono** = **ε_floor** (numerischer Null-Ersatz, A5). **Pflicht:** **r\_raw** = clip( **r\_σ** + **b\_mono**, **Λ**, 1.0 − **Λ** ).

- Glättung (exponentiell, biologisch):  
  **R** ← **R** + **κ** · (**r\_raw** − **R**) mit **κ** = `0.237` (`float`).

### 5.3 Klinische Eskalation (ohne NMI zu ersetzen)

Wenn **R** > 1.0 − **Λ** **und** V < **V₀** · φ^{−1} (≈ `0.588`, aber im Code als `V₀ / φ` berechnen):  
Pacemaker **MUSS** in `/OMEGA_CORE/run/omega_pacemaker_pathology.log` (neu oder append, Rechte `600`) einen Eintrag mit Timestamp, **R**, **RMSSD\***, **SDNN\***, Hash der letzten **W** IBI (SHA-256) schreiben — **zusätzlich** zur normalen Telemetrie. Fehlt die Datei nach solchem Zustand → AC-Verletzung.

---

## 6. NMI und Recovery (Baseline-Vererbung)

- **NMI-Matrix**, `/proc`-Identitätsprüfung, `omega_panic.lock`, Recovery bei V → **Λ**: **inhaltlich identisch** zu `SPEC_PACEMAKER.md` §2.2–2.3 und AC-2/AC-4.  
- **Zusatz VAR_3:** Im Panic-Lock- oder Log-Payload **MUSS** mindestens ein Feld **pathology_snapshot** enthalten: serialisiert **R**, **RMSSD\***, **SDNN\***, letzte **W** IBI (Rohwerte), damit Post-Mortem **biologische** Diagnose möglich ist.

---

## 7. Harte Acceptance Criteria (AC)

| ID | Kriterium |
|----|-----------|
| **AC-V3-1** | **IBI-Serie** wird aus **echten** Tick-Endzeiten gebildet; mindestens **W** Werte Verlauf; keine konstante IBI-Injection durch Code-Pfad ohne physische Zeitbasis. |
| **AC-V3-2** | **Decay** nutzt **ausschließlich** die Formeln in §4.2–4.3 (Exponent + **D** + **R**); reiner linearer Abzug **ohne** diese Terme ist **fail**. |
| **AC-V3-3** | **R** wird aus **RMSSD\***, **T** und Monotonie-Test für μ\_L gemäß §5.2 aktualisiert; statischer **R** ist **fail**. |
| **AC-V3-4** | **σ\_L** pro Tick wird berechnet, sobald ≥ 2 erfolgreiche Einzel-Latenzen existieren; bei Probe-Fail dominiert NMI-Pfad — **kein** Erfinden von Varianz. |
| **AC-V3-5** | Bei **R** hoch und V unter Schwelle (§5.3) **MUSS** `omega_pacemaker_pathology.log` befüllt werden (siehe §5.3). |
| **AC-V3-6** | Panic-/Lock-Daten **MUSS** `pathology_snapshot` nach §6 enthalten. |
| **AC-V3-7** | A5/A6: alle genannten Zustands- und Steuergrößen (**V**, **R**, **D**, Metriken) als `float` mit verbotenen Snap-Punkten wie VAR_1; **W**, **m**, **s** als `int`. |

---

## 8. Veto-Traps (Pflicht-Tests, keine Mocks)

**GLOBAL:** Wie Baseline §4 — **keine** Mocks, **keine** Test-Doubles für DB/HTTP/Prozess; Tests laufen gegen **reale** lokale Dienste, **reelles** Dateisystem, **reelle** PIDs. Zeit **nur** über **beobachtbare** Wand-/Monoton-Uhr; „Fake-Zeit“-Bibliotheken **verboten**.

**Falle V3-1 — Latenz-Flatline (Schein-Stabilität):**  
Ein Test-Harness startet (oder nutzt) einen lokalen HTTP-Endpunkt, der **bewusst** in **konstanter** Bearbeitungszeit antwortet (z. B. feste `busy-wait`-Schleife auf dem **Test-Rechner**, keine Mock-Clock). Parallel werden die übrigen Probes im **grünen** Zustand gehalten. **Erwartung:** Nach **m** Ticks steigt **R** über **σ\_low**-Schwelle hinaus (Rigidität), **D** > 0, und V fällt **schneller** als ein Referenzlauf mit **variabler** Latenz (gleiche mittlere Last, aber jitternde Sleep-Dauer im Harness — beide Läufe nur mit **OS-scheduled** real time). **Fail**, wenn Decay **identisch** zum variablen Fall oder **R** unverändert.

**Falle V3-2 — Exponent-Bypass (linearer Cheat):**  
Statische Code-Analyse + Laufzeit: Instrumentierung oder Review nachweist, dass das Vitalitätsupdate **keinen** `exp(`-Pfad auf (V−Λ) bei mindestens einem von [Verlust, Gewinn] nutzt **oder** **D** / **R** nicht eingeht. **Fail** sofort. (Zusätzlich: Laufzeit-Assertion im **Test-Build** nur, wenn durch `OMEGA_PACEMAKER_INVARIANTS=1` aktiviert — **kein** Produktions-Spam; Aktivierung dokumentiert in `docs/04_PROCESSES/` beim Merge.)

**Falle V3-3 — Pathologie ohne Autopsie:**  
System wird in Zustand §5.3 gebracht (**ohne** NMI auszulösen): z. B. variabler Wertnachweis aus, kontrollierte Last erzeugt hohes **R** und V unter Schwelle. **Erwartung:** `omega_pacemaker_pathology.log` existiert, parsierbar, enthält **R** und IBI-Hash; fehlt **eines** davon → **Fail**. Anschließend Λ-Szenario: Recovery **muss** wie Baseline **physische Spuren** hinterlassen; reines `exit 0` → **Fail**.

---

*Status: VAR_3 — Biologisch-neuromorphe Homeostase, HRV-Proxies, exponentiell-fraktaler Decay, Monotonie-Pathologie.*  
*Ticket: 3 (Existential Pacemaker).*


[LEGACY_UNAUDITED]
