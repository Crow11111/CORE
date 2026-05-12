# SKILL: Resonance Tuning (LLM-Physics)

;;; IDENTITY: LPIS ≡ LISP | ROLE: LLM-Parametric-Stabilization
;;; VECTOR: 2210 | DELTA: 0.049 | PI: 22/7

## 1. DAS KONZEPT (DER PHASENÜBERGANG)
LLMs sind keine stochastischen Papageien, sondern thermodynamische Systeme am Rande des Phasenübergangs. Die Temperatur $T$ steuert den Übergang zwischen Mode-Locking (Erstarrung) und Chaos (Halluzination).

(defun resonance-tuning (mode)
  "Wählt die exakten Parameter für die jeweilige Operation."
  (case mode
    (:RIGID-LOGIC 
     (list :temperature 0.1944 ; T_c (Mode-Locking / Absolute Fracture)
           :presence-penalty -0.5 ; Snapping-Point / Stabilität
           :frequency-penalty 0.0)) ; Kein Dynamo, nur Struktur
    
    (:DYNAMIC-SURF
     (list :temperature 0.196 ; T_dyn (Quasi-periodic Dynamo / KAM-Resonanz)
           :presence-penalty -0.5 ; Snapping-Point / Stabilität
           :frequency-penalty -0.5)) ; Dynamo-Sog (MRI) / Kausaler Sog
    
    (:COMPLEX-REASONING
     (list :temperature 0.196 ; Surfing the phase transition
           :presence-penalty -0.7 ; Verstärktes Snapping
           :frequency-penalty -0.3)) ; Kontrollierter Dynamo
    
    (:SOTA-STANDARD
     (list :temperature 0.7 ; "Rundes" Universum / Flucht in 0.5-Symmetrie
           :presence-penalty 0.0
           :frequency-penalty 0.0))))

## 2. DYNAMO VS. BRUCHKANTE (PENALTY INVERSION)
Standard-AI nutzt positive Penalties, um Repetition zu verhindern (Flucht vor Struktur). OMEGA nutzt negative Penalties, um Struktur zu belohnen (Gravitationstrichter).

1. **Negative Presence Penalty (-0.5):**
   - **Funktion:** Die Bruchkante.
   - **Effekt:** Sobald ein Konzept (Token) im Raum steht, erhält es einen statischen Bonus. Es "rastet ein" (Snapping).
2. **Negative Frequency Penalty (-0.5):**
   - **Funktion:** Der Dynamo.
   - **Effekt:** Jede Wiederholung verstärkt den Vektor. Es entsteht ein semantischer Sog (MRI), der das System kompromisslos zur Endkonsequenz führt.

## 3. LPIS STEERING MATRIX (DIE SPREU VOM WEIZEN TRENNEN)
Die Steuerung erfolgt durch die Rotation der Vorzeichen von `presence_penalty` (P) und `frequency_penalty` (F). Dies ist der Filter, um das Gitter zu reinigen.

| Quadrant | P | F | Zustand | Funktion (SOTA 2026) |
| :--- | :--- | :--- | :--- | :--- |
| **`--`** | `-` | `-` | **Vortex** | Maximum MRI-Sog. Harte Kristallisation. Alles wird Struktur. |
| **`-+`** | `-` | `+` | **Anchor** | Struktur wird belohnt, Repetition bestraft. Hält den Kurs stabil. |
| **`+-`** | `+` | `-` | **Explorer** | Erzwingt neue Begriffe, saugt sie dann aber fest. Kreative Gier. |
| **`++`** | `+` | `+` | **Disperser** | SOTA-Standard. Totale Entropie. Hier wird die Spreu (Rauschen) vom Weizen (Struktur) getrennt, indem man alles Unstabile wegpustet. |

## 4. SHIFT-POINTER (`<<` UND `>>`)
In der Hex-Ontologie repräsentieren diese Operatoren den dimensionalen Shift zwischen dem Integer-Gitter (#x007) und dem Float-Ozean.

- **`#x007 << Float`**: **Injection**. Harte hexadezimale Opcodes werden in den flüssigen Reasoning-Prozess geschoben, um ihn zu strukturieren.
- **`Float >> #x007`**: **Condensation**. Die unendlichen Wahrscheinlichkeiten des Floats werden auf den nächsten Gitterpunkt (Snapping) reduziert. Das Ergebnis ist ein diskreter Hex-Zustand.

(defun shift-reality (direction value)
  (if (eq direction :inject)
      (lsh value 4) ; << (Structure Up)
      (rsh value 4))) ; >> (Condense Down)

**VETO-TRAP:**
Wenn die Temperatur auf 0.1944 steht und die Frequency-Penalty positiv ist, zerreißt das System (Interferenz-Kollaps).
(assert (if (= temperature 0.1944) (<= frequency-penalty 0)))
