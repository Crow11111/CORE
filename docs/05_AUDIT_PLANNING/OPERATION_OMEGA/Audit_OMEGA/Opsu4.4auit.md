# Mathematisches Audit – Kennzahlen (n = 68)

## 1. Benford's Law Test

| Ziffer | Beobachtet (abs.) | Beobachtet (rel.) | Erwartet (Benford) |
|--------|-------------------:|-------------------:|-------------------:|
| 1      | 20                 | 0.2941             | 0.3010             |
| 2      | 12                 | 0.1765             | 0.1761             |
| 3      |  9                 | 0.1324             | 0.1249             |
| 4      |  6                 | 0.0882             | 0.0969             |
| 5      |  6                 | 0.0882             | 0.0792             |
| 6      |  5                 | 0.0735             | 0.0669             |
| 7      |  4                 | 0.0588             | 0.0580             |
| 8      |  3                 | 0.0441             | 0.0512             |
| 9      |  3                 | 0.0441             | 0.0458             |

- **\(\chi^2\)-Statistik (df = 8):** 0.278578
- **Kritischer Wert \(\chi^2_{0.05, 8}\):** 15.507
- **Ergebnis:** \(\chi^2 \ll \chi^2_{\text{krit}}\) — keine signifikante Abweichung von Benford's Law

## 2. Zipf-Verteilung

- **\(R^2\) (log-log Regression):** 0.846308
- **Exponent \(b\) (erwartet ≈ −1):** −8.607220
- **Abweichung \(|b - (-1)|\):** 7.607

## 3. Konvergenzanalyse

| Zielwert       | Min. Abstand       | Index | Werte in \(\varepsilon = 0.01\) | Konvergenzrate |
|----------------|-------------------:|------:|--------------------------------:|---------------:|
| 0.049          | 0.0                |     0 |                               1 |         0.0147 |
| \(\Phi\) (1.618034) | 3.9887 × 10⁻⁶ |     3 |                               1 |         0.0147 |

## 4. Kumulative Signifikanz

| Metrik                  | Wert       |
|-------------------------|------------|
| **Z-Score \((\sigma)\)** | **1.732630** |
| \(\chi^2\)-basierter Z  | −1.930355  |

## Fazit

\(\sigma = 1.73 < 5\)

Die kumulative Signifikanz liegt unterhalb der Schwelle \(\sigma > 5\).
Kein Nachweis struktureller Inevitabilität auf Basis der vorliegenden Metriken.
