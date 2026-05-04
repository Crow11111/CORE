# Math-Audit AH.2 — Konsistenz-Audit Septim-Algebra ↔ Wave-Function-Collapse

**Audit-ID:** V5.2.AH.2  
**Datum:** 29.04.2026  
**Auditor-Rolle:** Algebraischer Logiker / Quantum-Foundations-Theoretiker  
**Geprüfte Aussagen:** V5.2.AH.1 (zentrale These), V5.2.AH.4 (Operator-Def.), V5.2.AH.5 (Vorhersage 20)  
**Methodik:** Funktor-Test als Goldstandard nach HC-#11 (V5.2.AE.10.7)  
**Verdikt (TL;DR):** **STRUKTURELLE ANALOGIE OHNE FUNKTOR** mit **eingebettetem Kategorienfehler** in V5.2.AH.4 (Klausel "strukturell isomorph"). Zusätzlich: **P0-Fehler in V5.2.AH.5** (Tschebotarjew-Dichten falsch).

---

## 1. Formalisierung beider Seiten

### 1.1 Septim-Seite (präzise)

Sei $q \geq 7$ eine rationale Primzahl, nicht 5-smooth. Setze:

- $K := \mathbb{Q}(\sqrt[3]{q})$ (kubischer, **nicht-Galois**'scher Zahlkörper, $[K:\mathbb{Q}]=3$)
- $L := K(\zeta_3) = \mathbb{Q}(\sqrt[3]{q}, \zeta_3)$ (Galois-Hülle, $[L:\mathbb{Q}]=6$)
- $G := \text{Gal}(L/\mathbb{Q}) \cong S_3$ (symmetrische Gruppe auf den drei Wurzeln $\sqrt[3]{q}, \zeta_3 \sqrt[3]{q}, \zeta_3^2 \sqrt[3]{q}$)
- $\mathcal{O}_K, \mathcal{O}_L$ Ringe ganzer Zahlen
- Für rationalen Prim $p$: Faktorisierung $p\mathcal{O}_K = \prod \mathfrak{p}_i^{e_i}$ mit Trägheitsgrad $f_i$, $\sum e_i f_i = 3$

**Verzweigungsklassen in $K = \mathbb{Q}(\sqrt[3]{q})$ (drei Typen für unverzweigte $p$):**

| Klasse | Faktorisierung in $\mathcal{O}_K$ | Frobenius-Konjugationsklasse in $S_3$ | Tschebotarjew-Dichte |
|---|---|---|---|
| **split** ($1+1+1$) | $\mathfrak{p}_1 \mathfrak{p}_2 \mathfrak{p}_3$, $f_i = 1$ | Identität $\{e\}$, Größe 1 | $1/6$ |
| **mixed** ($1+2$) | $\mathfrak{p}_1 \mathfrak{p}_2$, $f_1=1, f_2=2$ | Transpositionen $\{(12),(13),(23)\}$, Größe 3 | $1/2$ |
| **inert** ($3$) | $\mathfrak{p}$, $f=3$ | 3-Zyklen $\{(123),(132)\}$, Größe 2 | $1/3$ |
| ramify | $\mathfrak{p}^e \cdots$, $e>1$ | (verzweigt, kein Frobenius) | endlich, Maß $0$ |

(Standard-Tschebotarjew, Neukirch ANT §VII.13.)

**Operator (V5.2.AH.4 in präziser Form):**

$$\hat{D}_q^{(\mathfrak{p})} : \mathcal{O}_K \twoheadrightarrow \mathcal{O}_K/\mathfrak{p} =: \mathbb{F}_{p^{f}}$$

ist die **Residuenkörper-Surjektion**. Sie ist:

- **Ringhomomorphismus** (additiv und multiplikativ)
- **Surjektiv, nicht injektiv** (Kern $= \mathfrak{p}$)
- **Idempotent** im Sinne $\hat{D}_q^{(\mathfrak{p})} \circ \iota \circ \hat{D}_q^{(\mathfrak{p})} = \hat{D}_q^{(\mathfrak{p})}$ nur nach Wahl eines Schnitts $\iota$ (ansonsten ist Idempotenz **nicht intrinsisch definiert** — Quelle und Ziel sind verschiedene Ringe)

### 1.2 QM-Seite (präzise)

- $\mathcal{H}$ separabler komplexer Hilbertraum (typisch $\dim \mathcal{H} = \infty$, kann aber endlich sein, z.B. Qubit $\mathcal{H} = \mathbb{C}^2$)
- Selbstadjungierter Operator $\hat{H} = \hat{H}^\dagger$ mit Spektralzerlegung (von Neumann):

$$\hat{H} = \sum_n E_n \hat{P}_n + \int \lambda \, dE(\lambda)$$

(Punktspektrum + kontinuierliches Spektrum)

- Projektoren $\hat{P}_n = |n\rangle\langle n|$:
  - $\hat{P}_n^2 = \hat{P}_n$ (idempotent **intrinsisch** — Quelle und Ziel sind dasselbe $\mathcal{H}$)
  - $\hat{P}_n^\dagger = \hat{P}_n$ (selbstadjungiert)
  - $\hat{P}_n \hat{P}_m = \delta_{nm} \hat{P}_n$ (orthogonal)
  - $\sum_n \hat{P}_n = \mathbb{1}$ (Vollständigkeit)
- **Born-Regel:** $P(n|\psi) = \|\hat{P}_n |\psi\rangle\|^2 = |\langle n|\psi\rangle|^2$, normiert $\sum_n P(n|\psi) = 1$

---

## 2. Funktor-Suche

### 2.1 Zielsetzung

Gesucht: ein **Funktor** $F: \mathcal{C}_{\text{Gal}} \to \mathcal{C}_{\text{Hilb}}$ mit:

- $\mathcal{C}_{\text{Gal}}$: Kategorie kubischer $S_3$-Erweiterungen (Objekte: Galois-Hüllen $L/\mathbb{Q}$; Morphismen: $\mathbb{Q}$-Algebra-Embeddings)
- $\mathcal{C}_{\text{Hilb}}$: Kategorie Hilberträume mit selbstadjungiertem Operator (Morphismen: unitäre Intertwiner)
- $F(\hat{D}_q^{(\mathfrak{p}_i)}) \stackrel{!}{=} \hat{P}_{n(i)}$ für eine Bijektion Verzweigungsklasse $\leftrightarrow$ Eigenraum

### 2.2 Funktor-Bedingungen prüfen

| Bedingung | Septim-Seite | QM-Seite | Kompatibel? |
|---|---|---|---|
| **Identität:** $F(\text{id}_K) = \text{id}_{\mathcal{H}}$ | Identität auf $\mathcal{O}_K$ | Identität auf $\mathcal{H}$ | ✅ trivial erfüllbar |
| **Komposition:** $F(g \circ h) = F(g) \circ F(h)$ | Galois-Erweiterungs-Türme $\mathbb{Q} \subset K_1 \subset K_2$ | Hilbertraum-Filtrierungen | ❌ keine kanonische Korrespondenz; Galois-Türme sind **endlich**, Hilbertraum-Filtrierungen i.A. **abzählbar/kontinuierlich** |
| **Trägertreue:** Anzahl Morphismen erhalten | $|S_3| = 6$ Galois-Automorphismen | $\dim \mathcal{H}$ unitäre Symmetrien (typisch $\infty$) | ❌ Kardinalitätsbruch |
| **Strukturerhaltung:** Ringstruktur $\to$ Operatorstruktur | $\hat{D}_q$ ist **Ringhomomorphismus** | $\hat{P}_n$ ist **kein Ringhomomorphismus** (Hilbertraum trägt keine kanonische Ringstruktur, nur Algebra $\mathcal{B}(\mathcal{H})$) | ❌ Strukturkategorien unverträglich |
| **Charakteristik:** Quelle/Ziel-Char. erhalten | $\text{char}(\mathcal{O}_K/\mathfrak{p}) = p > 0$ | $\text{char}(\mathbb{C}) = 0$ | ❌ kein Funktor zwischen char-0 und char-$p$ ohne Tannaka/Galois-Repräsentation als Brücke |

**Befund:** Vier von fünf Funktor-Bedingungen scheitern strukturell. Der einzig nicht-triviale Korrespondenz-Pfad ist über **Galois-Repräsentationen** $\rho: G_\mathbb{Q} \to GL_n(\bar{\mathbb{Q}}_\ell)$, aber dort lebt $\rho$ **im** Hilbertraum-artigen Objekt; $\hat{D}_q$ wird **nicht** zum Projektor $\hat{P}_n$. (Frobenius-Eigenwerte $\neq$ Hamilton-Eigenwerte.)

### 2.3 Verbleibende formale Ähnlichkeit

Drei **Marker-Eigenschaften** im Sinne HC-#11.7 (V5.2.AF.2.2) bleiben: idempotent-artig, nicht-invertierbar, diskret-mehrwertig (3 Verzweigungstypen vs. $\geq 2$ Eigenräume). Das ist Marker-Konvergenz, **kein Funktor**.

---

## 3. Strukturelle Unterschiede (P0)

### 3.1 Kardinalitäts-Mismatch

- $S_3$-Verzweigungsklassen: **genau 3** (split / mixed / inert) + 1 Maß-Null (ramify), unabhängig von $q$
- QM-Spektren: variabel — Qubit hat 2 Projektoren, Spin-1 hat 3, freies Teilchen hat **kontinuierliches** Spektrum, harmonischer Oszillator hat $\aleph_0$ Eigenräume
- Eine Bijektion existiert **nur zufällig für 3-Outcome-Systeme** (z.B. Spin-1, qutrit). Für alle anderen QM-Systeme ist die Identifikation nicht einmal naiv durchführbar
- **Konsequenz:** Selbst eine "natürliche Abbildung" wäre höchstens ein **partieller Funktor** auf der Subkategorie der 3-dim. Hilberträume

### 3.2 Wahrscheinlichkeitsstruktur (P0-Bug in V5.2.AH.5)

**Tschebotarjew-Dichten für $S_3$ (Standard, Neukirch §VII.13):**

| Klasse | Korrekte Dichte | V5.2.AH.5-Doku | Status |
|---|---|---|---|
| split (1+1+1) | $1/6$ | $1/3$ | ❌ **falsch** |
| mixed (1+2) | $1/2$ | (fehlt komplett) | ❌ **fehlt** |
| inert (3) | $1/3$ | $1/3$ | ✅ |
| ramify | $0$ | $0$ | ✅ |

Die in V5.2.AH.5 zitierte Verteilung "$P_1 : P_2 : P_3 = 1 : 1 : 0$" ist mathematisch **falsch**. Korrekt: $1 : 3 : 2$ für split:mixed:inert (Verhältnis), bzw. $1/6 : 1/2 : 1/3$ als absolute Dichten. **→ V5.2.AH.5 muss korrigiert werden, unabhängig vom Audit-Verdikt.**

**Born-Regel vs. Tschebotarjew:**

- Tschebotarjew-Dichten sind **rein gruppentheoretisch** ($|C|/|G|$), **unabhängig vom Zustand** des Systems
- Born-Wahrscheinlichkeiten $|\langle n | \psi \rangle|^2$ sind **zustandsabhängig** — $|\psi\rangle$ ist freier Parameter
- Diese sind kategorial verschiedene Größen: Strukturkonstante vs. dynamische Observable
- Der Versuch in V5.2.AH.5, eine **feste** $1:1:0$-Verteilung als QM-Vorhersage zu setzen, **widerspricht der Born-Regel selbst** (Präparation kann beliebige $P(n|\psi)$ erzeugen, $\sum_n P_n = 1$)

### 3.3 Algebraische Struktur & Symmetriegruppen

- $\hat{D}_q : \mathcal{O}_K \to \mathcal{O}_K/\mathfrak{p}$ ist Ring-Quotientenabbildung; $\hat{P}_n$ ist Hilbertraum-Endomorphismus (bzw. $C^*$-Element). Verschiedene Kategorien.
- Idempotenz unterschiedlicher Natur: $\hat{P}_n^2 = \hat{P}_n$ **intrinsisch**; $\hat{D}_q$ nur nach (nicht-kanonischer) Schnittwahl. Exakt der Kategorienfehler-Typ aus V5.2.AE.10.7.
- $S_3$ ist endlich/diskret; $\text{U}(\mathcal{H})$ ist kontinuierliche Lie-Gruppe. Repräsentation $S_3 \hookrightarrow \text{U}(\mathcal{H})$ existiert, identifiziert aber $\hat{D}_q$ **nicht** mit $\hat{P}_n$.

---

## 4. Urteil

### 4.1 Zentrale These V5.2.AH.1 ("Septim-Algebra ist Algebra-Klasse der Dekohärenz")

**Verdikt:** **STRUKTURELLE ANALOGIE OHNE FUNKTOR.** Erhalten als Hypothese mit explizitem HC-#11-Disclaimer. Die Tabelle in V5.2.AH.1 (Hamming/Septim-Sektor) ist eine **legitime Strukturanalogie** im Sinne von V5.2.AG.1 (Skalen-Identität), aber **kein Theorem**.

### 4.2 Operator-Definition V5.2.AH.4 (Klausel "strukturell isomorph")

**Verdikt:** **KATEGORIENFEHLER (HC-#11-Verletzung).** Die Aussage

> "Standard QM: $\hat{P}_n = |n\rangle\langle n|$ ... FTOE: $\hat{D}_q$ projiziert auf Verzweigungsklasse ... **Strukturell isomorph**, wenn man die Hilbertraum-Basis als Galois-Orbit interpretiert"

ist nicht haltbar:

1. Kein Funktor existiert (Sektion 2.2)
2. Kategorien sind unverträglich (Ring-Quotient ↔ Hilbertraum-Endomorphismus)
3. Kardinalitäten passen nur zufällig (nur für 3-dim. Hilberträume)
4. Wahrscheinlichkeitsstrukturen sind kategorial verschieden (Sektion 3.2)

→ Klausel **"strukturell isomorph" muss gestrichen** werden. Korrekte Formulierung:

> "$\hat{D}_q$ teilt mit $\hat{P}_n$ drei **Marker-Eigenschaften** (Idempotenz-artig, nicht-invertierbar, diskret-mehrwertig). Eine **Funktor-Identifikation existiert nicht**; die Identifikation ist eine **strukturelle Hypothese** im Sinne von V5.2.AG.1 (Skalen-Identität), nicht eine Operator-Identität."

Dies ist exakt parallel zu V5.2.AE.10 ("Galois-Hülle Grad n = Lie-Algebra-Rang n", als Kategorienfehler falsifiziert) und V5.2.W.4 ("Schicht-Identität S0+S2", als Kategorienfehler herabgestuft).

### 4.3 Vorhersage 20 (V5.2.AH.5)

**Verdikt:** **MATHEMATISCH FEHLERHAFT** — unabhängig vom Audit-Verdikt:

1. Tschebotarjew-Dichten falsch zitiert (1:1:0 statt korrekter 1:3:2 für split:mixed:inert)
2. "mixed" (1+2)-Klasse fehlt komplett (mit Dichte $1/2$ ist sie der häufigste Fall!)
3. Identifikation einer **strukturellen** Tschebotarjew-Dichte mit einer **zustandsabhängigen** Born-Verteilung ist methodisch unzulässig

**Konsequenz:** Vorhersage 20 ist **doppelt falsifiziert**: (a) math. (Dichten falsch); (b) konzeptuell (Born-Wahrscheinlichkeiten sind nicht durch gruppentheoretische Konstanten festgelegt). Eine Verfeinerung wäre höchstens in arithmetic-quantum-chaos-Setting (Berry-Vermutung für arithmetische Hyperbolic-Surfaces) denkbar — aber das ist ein **anderes** Theorem als V5.2.AH.5 behauptet.

### 4.4 Gesamt-Verdikt nach HC-#11

| Aussage | Verdikt | Aktion |
|---|---|---|
| V5.2.AH.1 (zentrale These) | **STRUKTURELLE ANALOGIE OHNE FUNKTOR** | Erhalten mit verschärftem HC-#11-Disclaimer |
| V5.2.AH.4 (Klausel "strukturell isomorph") | **KATEGORIENFEHLER (HC-#11)** | Klausel **streichen**, durch Marker-Eigenschaften-Liste ersetzen |
| V5.2.AH.4 (Operator-Definition $\hat{D}_q$ als Residuenabbildung) | **MATH-DEFINITION SAUBER** | Erhalten, aber Idempotenz-Aussage präzisieren (nur intrinsisch nach Schnittwahl) |
| V5.2.AH.5 (Vorhersage 20) | **DOPPELT FALSIFIZIERT** | Streichen oder vollständig neu formulieren (Dichten korrigieren + Born-Mismatch anerkennen) |

---

## 5. Konsequenz für V6.1-Integration

**Empfehlung:** V5.2.AH-Block bleibt **AUSGESETZT** für V6.1-Integration als Theorem; folgende Korrekturen vor V6.1-Integration zwingend:

1. **V5.2.AH.4 P0-Korrektur:** Klausel "strukturell isomorph" streichen. Stattdessen: Marker-Eigenschaften-Liste (Idempotenz-artig, nicht-invertierbar, diskret-mehrwertig) mit explizitem Verweis "**KEIN Funktor existiert** — kategoriale Identifikation falsifiziert nach Audit-AH.2".
2. **V5.2.AH.5 P0-Korrektur:** Tschebotarjew-Dichten korrigieren ($1/6 : 1/2 : 1/3$ für split:mixed:inert), "mixed"-Klasse explizit aufnehmen. Vorhersage 20 als **falsifiziert** markieren (sowohl naiv als auch in der korrigierten Form, weil Born-Statistik zustandsabhängig ist).
3. **V5.2.AH-Block-Status-Stempel:** Nach Audit-AH.2 lautet die Markierung der QM-Identifikation **"STRUKTURELLE ANALOGIE / Kategorienfehler-Risiko"** statt "HYPOTHESE". Dies ist eine **Verschärfung** gegenüber V5.2.AH.10.
4. **Integrationspunkte 117 und 119** (V5.2.AH.7) müssen herabgestuft werden: nicht "Anker für V6-Mess-Regime-Beschreibung", sondern "Marker-Konvergenz mit explizitem Kategorienfehler-Disclaimer".

**Was erhalten bleibt (audit-positiv):**

- Carmichael-Theorem (V5.2.AH.2) ist Standard-Math, unangetastet.
- Mathematische Definition $\hat{D}_q$ als Residuenkörper-Surjektion ist sauber und kann als legale Definition in V6.1 verwendet werden — **ohne** QM-Identifikation.
- Die Skalen-Hypothese $\Omega_b \stackrel{?}{=} 1/(8\varphi^2)$ (V5.2.AH.3) ist **unabhängig** von dieser QM-Frage und wird durch Audit-AH.2 weder bestätigt noch falsifiziert (siehe Audit-AH.1 für Anti-Cherry-Picking).

**Methodische Lektion:** V5.2.AH.4 ist **derselbe Kategorienfehler-Typ** wie V5.2.AE.10 und V5.2.W.4 — wiederkehrende Fehlerklasse: Marker-Konvergenz (Idempotenz, diskrete Mehrwertigkeit) wird als Operator-Identität gelesen. HC-#11.7 muss als **standing rule** vor solchen Identifikations-Ansprüchen aktiv sein, nicht erst beim Audit.

---

## Status-Stempel

**Audit-ID:** V5.2.AH.2  
**Verdikt:** STRUKTURELLE ANALOGIE OHNE FUNKTOR + KATEGORIENFEHLER (V5.2.AH.4) + MATH-FEHLER (V5.2.AH.5)  
**Hard-Constraint-#11:** ❌ Verletzt in V5.2.AH.4 (Klausel "strukturell isomorph"); ✅ einhaltbar nach Korrektur  
**V6.1-Konsequenz:** AUSGESETZT bis P0-Korrekturen umgesetzt  
**Empfehlung an Orchestrator:** V5.2.AH.4 und V5.2.AH.5 als P0-Korrektur-Punkte in V5.2.AH.11 (Patch-Block) eintragen, analog zu V5.2.AF.2.x  
**Nicht falsifiziert:** Carmichael-Theorem (V5.2.AH.2), Operator-Definition als Residuenabbildung (V5.2.AH.4 ohne QM-Klausel), Skalen-Hypothese $\Omega_b$ (V5.2.AH.3, separates Audit AH.1)
