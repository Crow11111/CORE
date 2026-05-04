# Math-Audit AH.1 — Anti-Cherry-Picking-Test für $\Omega_b \stackrel{?}{=} 1/(8\varphi^2)$

> **Auftrag:** V5.2.AH.8 Punkt 1 — Anti-Cherry-Picking-Test
> **Rolle:** Hostiler numerischer Skeptiker / Anti-Numerologie-Auditor
> **Datum:** 29.04.2026, 02:30 (Wall-Clock ~25 min)
> **Status:** ABGESCHLOSSEN
> **Verdikt (kurz):** **PLAUSIBEL → schwach SIGNIFIKANT-NEGATIV**. Die numerische Übereinstimmung von $1/(8\varphi^2)$ mit $\Omega_b$ ist **nicht** strukturell ausgezeichnet; mehrere FTOE-konforme Konkurrenten passen besser.
>
> **Hard-Kern-Befund:** Die Ziel-Hypothese $1/(8\varphi^2) \approx 0{,}04774$ liegt **selbst $-1{,}07\sigma$ vom Planck-Center entfernt**, also bereits **knapp außerhalb** des $1\sigma$-Intervalls $[0{,}0478;\,0{,}0494]$. **23 strukturell vergleichbare oder einfachere FTOE-Kombinationen** liegen näher am Mess-Center.

---

## AH.1.1 — Methodik (reproduzierbar)

**Skript:** `/tmp/audit_ah1/audit2.py` (107 074 Kandidaten evaluiert, ~2 s).

**FTOE-Pool (31 Symbole) — gesammelt aus V5/V5.1/V5.2:**

| Klasse                  | Symbole                                                    |
| ----------------------- | ---------------------------------------------------------- |
| Carmichael / klein      | 2, 3, 4, 5, 6, 7, 8                                        |
| Lie-Gruppen-relevant    | 12, 13, 18, 20, 24, 27, 30                                 |
| Lie-Algebra-Dim         | 78 ($E_6$), 133 ($E_7$), 248 ($E_8$)                       |
| Numerologie-Kontroll    | 2026 (Jahr — explizit als Sentinel)                        |
| Mitose / Goldener Schnitt | $\varphi, \varphi^2, \varphi^3, \varphi^4, 1/\varphi, 1/\varphi^2$ |
| Transzendent / radikal  | $\pi, \pi^2, e, \sqrt{2}, \sqrt{3}, \sqrt{5}, \sqrt{8}$    |

**Familien (5 Stück), alle systematisch enumeriert:**

1. $1/(a \cdot b)$
2. $a/b$
3. $a/(b \cdot c)$
4. $1/(a \cdot b \cdot c)$
5. $(a \cdot b)/(c \cdot d)$  ← die mit Abstand größte Familie

**Ziel-Intervall:** $[\text{Planck} - 1\sigma;\,\text{Planck} + 1\sigma] = [0{,}0478;\,0{,}0494]$.
Quelle: Planck-2018 TT,TE,EE+lowE+lensing, $\Omega_b = 0{,}0486 \pm 0{,}0008$.

**Plausibilitäts-Heuristik (FTOE-Bias-bewusst, 0..5):**

| Token-Klasse           | Score |
| ---------------------- | ----- |
| enthält `8`            | +2    |
| enthält `phi`/`phi^k`  | +2    |
| enthält Coxeter/Cartan-Token (6, 7, 12, 18, 24, 27, 30) | +1 |
| enthält `pi`/`pi^2`    | +1    |
| enthält 78 / 133 / 248 | −1 (zu spezifisch, "magic number") |
| enthält `e`            | −1 (kein FTOE-Anker) |
| enthält `2026`         | −3 (Numerologie-Sentinel) |

**Hypothese als Referenz:** $1/(8\varphi^2)$ → Plaus = +4 (8 + phi).

**Deduplikation:** Treffer im 1σ-Fenster numerisch zusammengefasst, falls $|v_i - v_j| < 10^{-7}$. Bei Kollision wird der Kandidat mit höherer Plausibilität behalten.

---

## AH.1.2 — Quantitatives Ergebnis

| Fenster | Unique Treffer | Plaus ≥ 3 | Plaus ≥ 4 |
| ------- | -------------- | --------- | --------- |
| ±0.25σ  | **14**         | 6         | 1         |
| ±0.5σ   | **27**         | 7         | 1         |
| ±1σ     | **66**         | 14        | 2         |
| ±1.5σ   | **100**        | 21        | 4         |

**Größenordnung:** Aus ~107 000 evaluierten einfachen Kombinationen liegen **66 unique Werte** im $1\sigma$-Fenster. Davon sind **14 strukturell mindestens so plausibel wie die Hypothese $1/(8\varphi^2)$** (Plaus ≥ 3) und **2 sogar plausibler** (Plaus ≥ 4).

### Top-15 nach Plausibilität (im 1σ-Fenster)

| Plaus | Wert     | Abw. (σ) | Ausdruck                             | Bemerkung |
| ----- | -------- | -------- | ------------------------------------ | --------- |
| **+5** | 0.048633 | **+0.04** | $\mathbf{8/(24\,\varphi^4) = 1/(3\varphi^4)}$ | **fast exakt auf Planck-Center; FTOE-rein (8 + φ⁴), strukturell mit Hypothese verwandt** |
| +4    | 0.047999 | −0.75    | $\pi^2/(30\,\varphi^4)$              | Coxeter-30 + Mitose⁴ + π² |
| +3    | 0.048611 | +0.01    | $7/(8\cdot 18)= 7/144$               | reine Integer-Heptade × Carmichael × Coxeter |
| +3    | 0.048557 | −0.05    | $\sqrt{2}/(18\,\varphi)$             | Hamming-Wurzel + Coxeter + Mitose |
| +3    | 0.048482 | −0.15    | $\varphi^2/(2\cdot 27)$              | Mitose / 2·E_6-Wurzel-System |
| +3    | 0.048424 | −0.22    | $(2\cdot 8)/(78\,\varphi^3)$         | $E_6$-Dim, FTOE-rein |
| +3    | 0.048784 | +0.23    | $\varphi^2/(24\sqrt{5})$             | Mitose / Coxeter, $\sqrt{5}$ Mitose-Wurzel |
| +3    | 0.048958 | +0.45    | $\varphi^4/(7\cdot 20)$              | Mitose / Septim·5×4 |
| +3    | 0.049087 | +0.61    | $\pi/(8\cdot 8) = \pi/64$            | **maximal einfach: nur 8 und π** |
| +3    | 0.049181 | +0.73    | $5/(24\,\varphi^3)$                  | Mitose-Familie |
| +3    | 0.049182 | +0.73    | $1/(\varphi \cdot 4\pi)$             | Wirkungsmodul-artig |
| +3    | 0.049286 | +0.86    | $(4\cdot 8)/(248\,\varphi^2)$        | $E_8$-Dim, Hypothese-Variante |
| +3    | 0.047837 | −0.95    | $2/(\varphi^3 \pi^2)$                | Mitose + Phasen-Vektor |
| +3    | 0.049383 | +0.98    | $8/(6\cdot 27)$                      | reine Integer (Cartan × E_6-Wurzel-System) |
| —     | **0.047746** | **−1.07** | $\mathbf{1/(8\,\varphi^2)}$ (Hypothese) | **bereits außerhalb 1σ** |

### Top-5 nach Nähe zu Planck-Center (alle Plaus-Klassen)

| Plaus | Wert | Abw. | Ausdruck | Anmerkung |
| ----- | ---- | ---- | -------- | --------- |
| +3    | 0.048611 | +0.01σ | $7/144 = 7/(8\cdot 18)$ | bestes plausibles Tripel |
| 0     | 0.048583 | −0.02σ | $(7\cdot 12)/(13\cdot 133)$ | Misch-Numerologie |
| **−3**  | 0.048627 | +0.03σ | $(20\cdot 133)/(27\cdot 2026)$ | **Numerologie-Sentinel feuert** |
| **+5**  | 0.048633 | +0.04σ | $\mathbf{1/(3\varphi^4)}$ | **FTOE-Sieger** |
| +3    | 0.048557 | −0.05σ | $\sqrt{2}/(18\,\varphi)$ | Hamming-Wurzel-Familie |

**Wichtiger Sentinel-Befund:** Der `2026`-Token (Jahr — eingeschmuggeltes Numerologie-Honeypot) **erzeugt bei +0.03σ einen Treffer** ($(20\cdot 133)/(27\cdot 2026)$). Das beweist empirisch, dass der Suchraum genug Freiheitsgrade hat, um **beliebige** Zielwerte mit kleinen Abweichungen zu treffen.

---

## AH.1.3 — Look-Elsewhere-Korrektur

**Naive (zu schwache) Schätzung:** Bei uniformer Verteilung im Bereich $[0;0{,}1]$ wäre die Trefferwahrscheinlichkeit pro Kandidat $\approx 0{,}016$. Bei 107 074 Kandidaten erwartet man $\approx 1700$ Treffer; beobachtet werden 66 unique. Das System konzentriert sich also weg vom Fenster (FTOE-Symbole erzeugen viele große und sehr kleine Werte). **Diese Korrektur ist irreführend für unsere Frage.**

**Korrektur, die die effektive strukturelle Suche zählt:**

- Plausibel (Plaus ≥ 3) zu betrachtende Kombinationen, geschätzt aus dem Pool: $\sim 1500{-}3000$ (heuristisch: alle Tripel mit ≤ 1 "fragwürdigem" Token).
- Treffer-Wahrscheinlichkeit für *Plaus-≥3*-Kandidaten im 1σ-Fenster: $14/2000 \approx 0{,}007$ pro Kandidat.
- Wahrscheinlichkeit, dass **mindestens eine** plausible Hypothese im 1σ-Fenster landet: bei $\sim 30$ "von Hand" erzeugbaren Kandidaten pro Sitzung: $1 - (1-0{,}007)^{30} \approx 0{,}19$.

**Look-Elsewhere-korrigierter p-Wert:**

$$p_{\text{LE}} \approx 0{,}19 \quad\text{(d.h. ca. 1 von 5 Sitzungen findet eine plausible Hypothese)}$$

**Interpretation:** Die Übereinstimmung ist **nicht signifikant**. Wenn ein FTOE-Theoretiker $\sim 30$ plausible Drei-Symbol-Kombinationen aus seinem Strukturzahl-Pool prüft, wird er mit **~19% Wahrscheinlichkeit** mindestens eine Übereinstimmung im 1σ-Fenster finden — *unabhängig von der zugrundeliegenden Physik*.

---

## AH.1.4 — Zerlegung des FTOE-Bias (warum so viele Treffer?)

Die FTOE-Strukturzahlen sind **nicht zufällig**: sie clustern um Werte zwischen 1 und 30, und $\varphi^k$ erzeugt eine geometrische Skala um 1.6. Die natürliche Größenordnung von $a/(b\cdot c)$ mit $a \in \{1,2,..,30\}$, $b, c \in \{1,..,30\}$ liegt im Bereich $0{,}001..0{,}3$, also exakt um $\Omega_b \approx 0{,}05$. Das ist eine **Bias-Falle**: jede Größe in dieser Größenordnung ist mit Strukturzahl-Tripeln gut approximierbar.

**Konsequenz:** Numerische Treffer in dieser Skala dürfen **nicht** als strukturelle Evidenz gelesen werden, sofern keine **vorab spezifizierte** algebraische Ableitung existiert.

---

## AH.1.5 — Strukturell verwandte Konkurrenten

Drei besonders gefährliche Konkurrenten der Hypothese $1/(8\varphi^2)$:

### Konkurrent A — $1/(3\varphi^4)$ (= $8/(24\varphi^4)$)

- **Wert:** 0.048633 (+0.04σ — fast exakt auf Planck-Center).
- **Algebraische Verwandtschaft:** Identisch zur Hypothese, nur mit `8 → 24 = 8·3` und `phi^2 → phi^4`. **Gleiche FTOE-Bausteine, anderes Tripel.**
- **Strukturelle Lesart (mindestens so plausibel wie AH.3):**
  > "24 = $E_6$-Wurzel-System-Anzahl pro Cartan-Slot. $\varphi^4 = (\varphi^2)^2$ = Mitose-Doppel-Iteration. $1/(3\varphi^4)$ = Anteil zweifach-stabiler Mitose pro 3-Achsen-Rotation."
- **Verdikt:** Diese Lesart ist genau so erfindbar wie AH.3 selbst. Sie passt besser zur Messung. Sie ist die **direkte Falsifikation des Singularitäts-Anspruchs** der Hypothese.

### Konkurrent B — $\pi/64 = \pi/(8\cdot 8)$

- **Wert:** 0.049087 (+0.61σ — innerhalb 1σ).
- **Plausibilität:** maximal hoch (nur 8 und π, beides FTOE-Kern).
- **Strukturelle Lesart (trivial):**
  > "$\pi$ = irrationaler Vortrieb (V5 Sci §4.2). $64 = 8^2$ = Cartan-Slot-Quadrat. $\pi/64$ = Phasen-Vortrieb pro Cartan-Slot-Paar."
- **Verdikt:** **Maximal kompakt, FTOE-rein, passt besser.**

### Konkurrent C — $7/144 = 7/(8\cdot 18)$

- **Wert:** 0.048611 (+0.01σ — exakt auf Planck-Center).
- **Plausibilität:** rein-rational, keine Transzendenten.
- **Strukturelle Lesart:**
  > "7 = erste Septim-Zahl (V5.2.AH.2). 144 = $F(12)$ = Fibonacci, $144 = 12^2 = $ Coxeter-Quadrat."
- **Verdikt:** **Septim × Coxeter² liegt EXAKT.** Erfordert minimal mehr Begründungs-Aufwand (warum gerade 7?), aber keiner als AH.3.

---

## AH.1.6 — Methodische Schwächen des Audits (offen deklariert)

1. **Plausibilitäts-Heuristik ist subjektiv.** Andere Heuristiken könnten andere Top-Listen erzeugen. Die Größenordnung der Treffer (Dutzende) bleibt aber stabil.
2. **Größere Familien nicht enumeriert:** $(a^k b^l)/(c^m d^n)$ mit $k,l,m,n \in \{-2,..,2\}$ würde viel mehr Treffer ergeben, aber auch mehr Bias-Verzerrung.
3. **Der Sentinel `2026` feuerte** — Beweis, dass der Suchraum jeden Zielwert irgendwo trifft.
4. **Keine "schöne Form"-Penalisierung:** Vielleicht ist $1/(8\varphi^2)$ "schöner" als $7/144$. Aber $\pi/64$ ist mindestens ebenso schön und passt besser.

---

## AH.1.7 — Urteil

| Kriterium | Befund |
| --------- | ------ |
| Anzahl Treffer im 1σ-Fenster | **66 unique** (von ~107 000 Kandidaten) |
| Davon Plaus ≥ 3 (FTOE-konform) | **14** |
| Davon Plaus ≥ Hypothese (≥4) | **2** |
| Davon strukturell **besser** passend (|dev|<1.07σ, Plaus≥2) | **23** |
| Hypothese selbst im 1σ-Fenster? | **NEIN** (−1.07σ) |
| Look-Elsewhere-korrigierter p-Wert | **~0.19** |

### → Verdikt: **PLAUSIBEL** (5–50 Kombinationen mit struktureller Bias)

**Genauere Lesart:** Die Hypothese $\Omega_b \stackrel{?}{=} 1/(8\varphi^2)$ ist **eine** plausible numerische Konstruktion unter mindestens **zwei Dutzend** strukturell vergleichbaren oder besseren FTOE-Konstrukten. Sie ist **nicht** durch ihre Trefferqualität ausgezeichnet — im Gegenteil: sie liegt selbst knapp außerhalb des 1σ-Fensters.

**Es gibt keinen statistischen Grund, $1/(8\varphi^2)$ als "die" Lösung zu privilegieren.**

---

## AH.1.8 — Konsequenz für V6.1-Integration

### Empfehlung: **UMFORMULIEREN, nicht verwerfen**

| Aktion | Begründung |
| ------ | ---------- |
| ❌ **Nicht** als Theorem oder zentrale Vorhersage in V6.1 integrieren | Cherry-Picking-Risiko ist zu hoch (p ≈ 0.19) |
| ❌ **Nicht** als "Skalen-Brücke S0 ↔ S3" mit Beweis-Anspruch behaupten | Mindestens 23 strukturell ebenso plausible Kandidaten existieren |
| ✅ Als **eine von mehreren** plausiblen FTOE-Approximationen markieren | wissenschaftlich ehrlich, Hard-Constraint-#11 erfüllt |
| ✅ Konkurrenten-Tabelle ($1/(3\varphi^4)$, $\pi/64$, $7/144$) **mitführen** | macht den Cherry-Picking-Bias sichtbar |
| ✅ **Vorhersage 22** verschärfen: **wenn** zukünftige Messung näher an einem Konkurrenten liegt, ist AH.3 zugunsten dieses Konkurrenten zu **revidieren** | Vorhersage 22 erst dann diskriminierend, wenn Konkurrenten ausgeschlossen sind |
| ✅ **Mathematische Ableitung priorisieren** | nur eine echte Ableitung aus $E_8 \times \text{Mitose}$-Algebra würde die Hypothese vor den Konkurrenten privilegieren |

### Konkrete Textpatch-Vorschläge für V5.2.AH.3 / V6.1.D2

**Statt** (V5.2.AH.3):
> "Innerhalb 1σ der primären Planck-Messung."

**Präziser:**
> "Bei 1.07σ vom primären Planck-Center entfernt — formal **knapp außerhalb** des 1σ-Intervalls. Gleicher oder kleinerer Abstand wird von mindestens 23 anderen FTOE-Strukturzahl-Kombinationen erreicht (siehe Audit AH.1)."

**Statt** (V5.2.AH.7, Tabelle Zeile 116):
> "$\Omega_b \stackrel{?}{=} 1/(8\varphi^2)$ als alternative Hypothese zu V6-D2-Plan-A"

**Präziser:**
> "$\Omega_b \stackrel{?}{=} 1/(8\varphi^2)$ als **eine** von mehreren FTOE-konformen numerischen Approximationen (Audit AH.1: ~14 strukturell vergleichbare Kandidaten im 1σ-Fenster, davon 2 mit höherer Plausibilität: $1/(3\varphi^4)$ +0.04σ, $\pi^2/(30\varphi^4)$ −0.75σ). Look-Elsewhere-korrigierter p-Wert ≈ 0.19. Status: **schwache Evidenz**, nicht hypothesen-tragend."

---

## AH.1.9 — Reproduzierbarkeit

```bash
# Vollständig reproduzierbar:
mkdir -p /tmp/audit_ah1
# Skript: /tmp/audit_ah1/audit2.py (siehe oben)
python3 /tmp/audit_ah1/audit2.py | tee /tmp/audit_ah1/result.txt
# Roh-Treffer: /tmp/audit_ah1/hits.tsv
```

**Eckdaten:**

- 31 Symbole im FTOE-Pool
- 5 Familien einfacher Kombinationen
- 107 074 Kandidaten in ~2 Sekunden enumeriert
- 66 unique-Wert-Treffer im 1σ-Fenster (14 plaus ≥ 3, 2 plaus ≥ 4)
- Sentinel-Token `2026` feuerte bei +0.03σ → Bias-Beweis

---

## AH.1.10 — Hard-Constraint-Compliance

| Constraint | Status |
| ---------- | ------ |
| ❌ Keine Bestätigungs-Bias | ✅ erfüllt — aktiv nach Gegenbeispielen gesucht, gefunden |
| ✅ Quantitativ | ✅ erfüllt — alle Aussagen mit Zahlen belegt |
| ✅ Reproduzierbar | ✅ erfüllt — Skript und Datenliegen vor |
| ❌ Kein Helpful-Bias | ✅ erfüllt — Verdikt explizit ungünstig für die Hypothese |
| Hard-Constraint-#11 | ✅ verstärkt — Audit zeigt: numerische Koinzidenz ist **nicht ausreichend** |

---

## TL;DR (für V6.1-Konsolidierung)

> **Die Hypothese $\Omega_b \stackrel{?}{=} 1/(8\varphi^2) \approx 0{,}04774$ ist eine von ~14 strukturell vergleichbaren FTOE-Konstrukten im 1σ-Bereich und liegt selbst knapp außerhalb (−1.07σ). Mindestens 23 Konkurrenten passen besser, darunter $1/(3\varphi^4) \approx 0{,}04863$ (+0.04σ, mit identischen Bausteinen), $\pi/64 \approx 0{,}04909$ (+0.61σ, maximal kompakt) und $7/144 \approx 0{,}04861$ (+0.01σ, rein-rational mit Septim×Coxeter²). Der Look-Elsewhere-korrigierte p-Wert beträgt ~0.19. → AH.3 ist als HYPOTHESE zu erhalten, aber NICHT als Theorem oder zentrale Vorhersage in V6.1 zu integrieren. Konkurrenten-Tabelle ist mitzuführen.**

---

**Bericht-Ende. Persistiert. Konsistent mit V5.2.AH.6 (Hard-Constraint-#11) und V5.2.AH.8 Punkt 1.**
