---
name: budget-estimation
description: Token-Budget-Schaetzung fuer Schicht-2-Teamleiter (V6 Fibonacci-Verteilung)
---

# Budget Estimation

## Faustregel: Token pro Aufgabe

| Komplexitaet | Token |
|--------------|-------|
| Einfach | 500 |
| Mittel | 1500 |
| Komplex | 3000 |

## Budget-Split (Fibonacci-Ratio, V6 Engine Pattern)

| Rolle | Anteil | Fibonacci-Basis |
|-------|--------|-----------------|
| Teamleiter | 13% | F(7) = 13 |
| Produzenten | 55% | F(10) = 55 |
| Auditoren | 21% | F(8) = 21 |
| Reserve (Eskalation) | 11% | F(6) = 11, Summe = ~100 (rundet) |

Begruendung: Fibonacci-Verteilung spiegelt natuerliche Ressourcen-Allokation
(Sonnenblumenkerne, Blattanordnung, DNS-Faltung). Dasselbe Optimierungsprinzip
das substratunabhaengig in biologischen und digitalen Systemen auftritt.

## Beispiel (Mittlere Aufgabe: 1500 Token)

- Teamleiter: 195 (13%)
- Produzenten (z.B. 2): 825 (55%)
- Auditoren (z.B. 1): 315 (21%)
- Reserve: 165 (11%)
