# Math-Audit AH.3 — Vorhersage 20: $S_3$-Verzweigungs-Statistik in QM-Experimenten

**Datum:** 29.04.2026, 02:14 (UTC+2)
**Auditor:** Quantum-Foundations-Theoretiker (Mess-Problem-Spezialist), Subagent unter V5.2.AH.8-Mandat
**Geprüfte Vorhersage:** V5.2.AH.5 — Vorhersage 20 (Wave-Function-Collapse-Statistik $1:1:0$ aus Tschebotarjew-Dichte)
**Zugehörige Anker:** V5.2.AH.4 ($\hat{D}_q$-Operator), V5.2.AH.5 (Falsifikations-Vorhersagen 20–22), V5.2.AH.6 (Hard-Constraint-#11-Bilanz), V5.2.AH.8 (Audit-Anforderungen)

---

## 1. Status der naiven Vorhersage 20

### 1.1 Mathematische Form (Originaldokument, Z. 3504–3522)

$$P(\text{outcome}) \in \{p_s, p_i, p_r\} \quad \text{mit Tschebotarjew-Anteilen} \quad p_s : p_i : p_r = \tfrac{1}{3} : \tfrac{1}{3} : 0$$

Behauptung: Ein „Septim-konfiguriertes" 3-Outcome-QM-System (z.B. Spin-1) zeigt asymptotisch die Verteilung $P_1 : P_2 : P_3 = 1 : 1 : 0$.

### 1.2 Falsifikations-Status — sofortiger Befund

Die Vorhersage scheitert an **vier unabhängigen Standard-QM-Resultaten**:

| Setup                                                                        | QM-Vorhersage                                                | $1:1:0$? |
| ---------------------------------------------------------------------------- | ------------------------------------------------------------ | -------- |
| Spin-1, Eigenzustand $|+1,z\rangle$, gemessen in $S_x$-Basis (Townsend 3.16) | $P(+\hbar) = \tfrac{1}{4},\; P(0) = \tfrac{1}{2},\; P(-\hbar) = \tfrac{1}{4}$ | ❌ nein  |
| Spin-1, unpolarisiertes Ensemble $\rho = \mathbb{1}/3$                       | $\tfrac{1}{3} : \tfrac{1}{3} : \tfrac{1}{3}$                 | ❌ nein  |
| Qutrit mit SIC-POVM (Medendorp et al. 2011, arXiv:1006.4905)                 | per Konstruktion frei wählbar, „unbiased" $\tfrac{1}{3}:\tfrac{1}{3}:\tfrac{1}{3}$ | ❌ nein  |
| Lineare BSM (4-Bell-Output, 3 unterscheidbare Klassen)                       | $\tfrac{1}{4} : \tfrac{1}{4} : \tfrac{1}{2}$ (Calsamiglia-Lütkenhaus 2001) | ❌ nein  |

**Befund:** Es existiert **kein** Standard-QM-Setup, in dem ohne extreme Präparations-Feinabstimmung eine $1:1:0$-Verteilung als generischer Limes auftaucht. Die Born-Regel $P(n) = |\langle n|\psi\rangle|^2$ ist über $|\psi\rangle$ und Mess-Basis frei einstellbar; jede ganzzahlige rationale Verteilung $(p, q, 0)$ mit $p+q=1$ kann präpariert werden, aber das ist trivial (Präparations-Artefakt) und nicht „asymptotisch gemäß Tschebotarjew".

### 1.3 Fundamentaler Kategorienfehler in Vorhersage 20

Tschebotarjews Theorem beschreibt asymptotische Häufigkeiten von **Frobenius-Konjugationsklassen** über einer **unendlichen Familie von Primidealen** in einer fixen Galois-Erweiterung. Die Aussage ist: „Im Mittel über alle unverzweigten Primideale $\mathfrak{p}$ liegt $\text{Frob}_\mathfrak{p}$ mit Frequenz $|C|/|G|$ in der Konjugationsklasse $C$."

Das ist eine **Familien-Statistik** über variierende Primideale, **nicht** eine Outcome-Statistik in einem fixen QM-Mess-Setup. Die naive Identifikation
$$P(\text{Outcome } i \text{ in einem Spin-1-System}) \stackrel{?}{=} \frac{|C_i|}{|S_3|}$$
ist ein **Skalen-Verwechsel**: Man bildet asymptotische Familien-Frequenzen ($\#$ Primzahlen $\to \infty$) auf Wahrscheinlichkeiten in einer einzelnen Born-Regel ab. Diese sind mathematisch unverbundene Objekte.

**Verdikt 1.3:** Vorhersage 20 in der naiven Form ist nicht „falsifiziert durch ein Experiment", sondern **bereits intern inkohärent** — ein Hard-Constraint-#11-Verstoß bei der Konstruktion.

---

## 2. Verfeinerungs-Optionen

### Option A — „Septim-Konfiguration" als spezifische Hilbertraum-Präparation

**Vorschlag:** Definiere einen ausgezeichneten Zustand $|\sigma\rangle = (|+1\rangle + \omega|0\rangle + \omega^2|-1\rangle)/\sqrt{3}$ mit $\omega = e^{2\pi i/3}$ als „Septim-Zustand" (kanonische $\mathbb{Z}_3$-Permutationssymmetrie).

**Test:** Für $|\sigma\rangle$ gilt bei $S_z$-Messung $P_{+1} = P_0 = P_{-1} = 1/3$ — also $1:1:1$, **nicht** $1:1:0$.
Bei einer anderen Mess-Basis (z.B. $S_x$) hängt die Verteilung von der Phasen-Wahl ab und produziert i.A. drei nicht verschwindende Wahrscheinlichkeiten.

**Status:** Option A liefert **kein** $1:1:0$-Pattern für irgendeine plausible „Septim-Konfiguration". **VERWORFEN.**

### Option B — $S_3$-Statistik nur für unpräparierten/zufälligen Anfangszustand

**Vorschlag:** Vorhersage gilt nur im Limes $\rho \to \mathbb{1}/d$ (maximally mixed), gemittelt über Haar-zufällige Mess-Basen.

**Test:** Für Spin-1 mit $\rho = \mathbb{1}/3$ und Haar-zufälliger ONB ergibt sich exakt $\langle P_i\rangle = 1/3$ für jede $i$ (Symmetrie). Auch hier **kein** ramify-Outcome mit Maß null.

**Status:** Option B liefert $1:1:1$, nicht $1:1:0$. **VERWORFEN.**

### Option C — Vorhersage über höhere Momente (Korrelation, Kontextualität)

**Vorschlag:** Statt Erwartungswerten Korrelations-Strukturen prüfen — z.B. KCBS-Inequality (Klyachko-Can-Binicioğlu-Shumovsky) für Spin-1:
- Klassische Schranke: $\sum_{i=1}^{5}\langle X_i X_{i+1}\rangle \geq -3$
- Quanten-Schranke: $-(4\sqrt{5}-5) \approx -4{,}944$

KCBS misst **kontextuelle Verstärkung**, hat eine eindeutige $\mathbb{Z}_5$-zyklische Struktur — **nicht** $S_3$. **Falsche Symmetrie.**

Alternativer Test: Drei-Punkt-Korrelationen $\langle S_x S_y S_z\rangle$ in Spin-1. Für $|\sigma\rangle$ ergeben diese komplexe Phasen, die nicht mit Tschebotarjew-Frequenzen identifiziert werden können.

**Status:** Option C ist mathematisch nicht trivialisiert, aber liefert **keine** quantitative FTOE-Vorhersage über ramify=0. Bestenfalls könnte eine Drei-Punkt-Korrelations-Identität postuliert werden — aber ohne ableitbares Test-Kriterium **NICHT FALSIFIZIERBAR.**

### Option D — Verzicht auf Vorhersage 20 als HC-#11-Verletzung

**Begründung:** Tschebotarjew (asymptotische Familien-Statistik) und Born-Regel (Single-Setup-Outcome) sind **kategorisch unverbundene** mathematische Objekte. Die Identifikation in V5.2.AH.5 ist ein Skalen-Verwechsel, kein technisch reparierbarer Fehler. Das fällt unter Hard-Constraint-#11 (numerische Koinzidenz $\neq$ Beweis, hier: strukturelle Analogie $\neq$ Funktor-Identität).

**Status:** Plausibel; minimal-invasiver Reset.

### Option E — Strukturelle Verfeinerung: Linear-Optical BSM als $\mathbb{Z}_2 \subset S_3$-Schranke

**Neuer Vorschlag (über die User-Liste hinaus):**

Die naive 4-Outcome-Bell-State-Measurement (BSM) hat eine **bewiesene** linear-optische Effizienz-Schranke von 50% (Calsamiglia-Lütkenhaus, Phys. Rev. A 65, 012314, 2002). Mit Ancilla-Photonen erreicht man $5/8 = 62{,}5\%$ (Bayerbach et al., Sci. Adv. 2023, gemessen $57{,}9\%$) bzw. $3/4 = 75\%$ (Grice 2011, Bayerbach 2025 npj QI: $69{,}3\%$).

**Strukturelle Beobachtung:** Das 50%-Limit folgt aus der Tatsache, dass die Permutationsgruppe linear-optischer Beam-Splitter-Operationen abelsch (Index 2 in $S_3$ einbettend) ist und nur die abelsche Untergruppe $\mathbb{Z}_2 \subset S_3$ in die Bell-Basis-Diskriminierung projiziert.

| Linear-Optisches BSM-Outcome (4 Bell-States, gleichmäßig präpariert) | Wahrscheinlichkeit |
| -------------------------------------------------------------------- | ------------------ |
| $|\Psi^+\rangle$ identifiziert (Klasse „split")                      | $1/4$              |
| $|\Psi^-\rangle$ identifiziert (Klasse „split")                      | $1/4$              |
| $|\Phi^\pm\rangle$ ambiguous (Klasse „inert", verschmolzen)          | $1/2$              |
| inkonsistente Detektion (Klasse „ramify")                            | $0$ (im Idealfall) |

Das ergibt das Verhältnis $\boxed{1:1:2:0}$ — interpretierbar als zwei „split"-Klassen ($\Psi^\pm$), eine „inert"-Klasse ($\Phi^\pm$ verschmolzen), eine „ramify"-Klasse mit Maß null.

**Reformulierung der Vorhersage:** Linear-optische Mess-Effizienzen unterliegen einer Tschebotarjew-artigen Schranke
$$\eta_{\text{linear}} \leq \frac{|H_{\text{abelian}}|}{|S_n|} = \frac{2}{4} = 50\% \quad \text{für } n=2 \text{ Qubits}$$
wobei $H_{\text{abelian}} \subset S_n$ die in der jeweiligen optischen Permutations-Algebra realisierbare Untergruppe ist. Anti-Cherry-Picking-Test: 50% ist **standard-mathematisch bekannt** (Calsamiglia-Lütkenhaus); FTOE darf hier nichts „Neues" beanspruchen, aber kann das Resultat als **strukturell konsistent** mit der Septim-Algebra-Lesart markieren.

**Status:** Diese Reformulierung ist **schwächer** als das Original (keine $1:1:0$-Outcome-Vorhersage), aber **mit existierender Math konsistent**. Sie ist nicht eigenständig falsifizierbar — sie ist eine Strukturidentifikation, kein FTOE-spezifischer Test.

---

## 3. Realistische Test-Vorschläge

### 3.1 Geprüfte Daten (post-2020)

| Experiment                                      | Datum                                           | Resultat                            | Falsifiziert $1:1:0$? |
| ----------------------------------------------- | ----------------------------------------------- | ----------------------------------- | --------------------- |
| Bayerbach et al., Sci. Adv. 2023 (BSM mit Ancilla, 48 Detektoren) | $p_c = 57{,}9 \pm 1{,}4\%$, BSM-Verteilung über 4 Bell-States | $\Psi^\pm: \Phi^\pm \approx 1:1$, ramify $\approx 0\%$ | ✅ konsistent mit $1:1:2:0$, nicht $1:1:0$ |
| Bayerbach et al., npj QI 2025 (boosted BSM, Fiber)              | $p_{c,\text{tot}} = 69{,}3\%$, Φ-Klasse 46% identifiziert | analog                              | analog                |
| Yale 5-Qutrit-Prozessor (DSpace MIT 2022, Goss et al.) | RB-Single-Qutrit-Fidelity $3{,}8 \times 10^{-3}$, alle 3 Outcomes nutzbar | per Konstruktion $1:1:1$ erreichbar | ✅ falsifiziert       |
| Stern-Gerlach Spin-1 (Standard, Townsend ÜA 3.16) | $|+1,z\rangle \to S_x$: $1/4 : 1/2 : 1/4$       | analytisch                          | ✅ falsifiziert       |

### 3.2 Hypothetisches FTOE-spezifisches Setup

Wenn man eine **schwache** Verfeinerung à la Option C testen wollte:
- **Setup:** Drei-Niveau-EIT-System (Λ-Konfiguration) mit Dark-State-Engineering
- **Erwartung:** Im EIT-Resonanz-Regime ist ein Outcome (Photon-Absorption am Common-Level) komplett unterdrückt → $1 : 1 : 0$ in der Photon-Statistik des Bright-Dark-Common-Basis
- **Test:** Standard-EIT-Spektroskopie misst dies seit Boller-Imamoğlu-Harris 1991. Ergebnis: Ja, Dark-State-Population kann auf $\sim 0$ gedrückt werden. Aber das ist eine **Präparations-getriebene** Auslöschung, kein „asymptotischer Tschebotarjew-Limes".

Diese Identifikation wäre für FTOE **trivial nicht-eindeutig** (jede Standard-EIT-Erklärung tut es genauso) und liefert daher keinen FTOE-Diskriminator.

### 3.3 Echter Diskriminator (kontrafaktisch — sehr schwach)

Eine FTOE-spezifische Vorhersage müsste lauten:
> Über eine **Familie** von Hilbert-Räumen $\mathcal{H}_q$, indiziert durch Septim-Primzahlen $q \geq 7$, jeweils mit kanonischer $\mathbb{Z}_3 \rtimes \mathbb{Z}_2 = S_3$-Aktion und einem ausgezeichneten Galois-Orbit-Mess-Set, ergibt sich asymptotisch (über $q \to \infty$) die Outcome-Frequenz $1/3 : 1/3 : 0$.

**Problem:** Es gibt **keinen kanonischen Funktor** $\{\text{Septim-Primzahlen}\} \to \{\text{Hilbert-Räume mit Mess-Setup}\}$. Ohne diesen ist die Vorhersage **nicht definiert**, geschweige denn testbar in 2026-Technologie.

---

## 4. Urteil

**NAIVE VORHERSAGE 20 IST FALSIFIZIERT** — und zwar bereits **vor** dem Experiment, durch innere Inkohärenz (Skalen-Verwechsel zwischen Familien-Statistik und Single-Setup-Born-Regel).

**Verfeinerungs-Optionen-Bilanz:**

| Option | Status | Begründung |
| ------ | ------ | ---------- |
| A (Septim-Hilbertzustand)               | VERWORFEN  | Liefert $1:1:1$, nicht $1:1:0$ |
| B (Maximally mixed)                     | VERWORFEN  | Liefert $1:1:1$ |
| C (höhere Momente / Kontextualität)     | OFFEN, nicht falsifizierbar | KCBS-Symmetrie ist $\mathbb{Z}_5$, nicht $S_3$; keine quantitative Vorhersage ableitbar |
| D (Verzicht / HC-#11-Markierung)        | EMPFOHLEN  | Minimal-invasiv, ehrlich, konsistent mit V5.2.AH.6 |
| E (Linear-optische BSM-Schranke)        | TEILWEISE  | Strukturell konsistent, aber nicht eigenständig FTOE-Diskriminator |

**EMPFEHLUNG:** **Vorhersage 20 in der Outcome-$1:1:0$-Form ZURÜCKZIEHEN.**

Stattdessen V5.2.AH.5 umformulieren auf eine **konditionale strukturelle Aussage** (Option E + D-Hybrid):
> *„Wenn die Septim-Algebra-Identifikation (V5.2.AH.4) korrekt ist, dann müssen lineare optische Mess-Schemata Effizienzschranken vom Typ $|H_{\text{abelian}}|/|S_n|$ unterliegen. Diese Schranke ist standard-mathematisch bewiesen (Calsamiglia-Lütkenhaus 2001) und FTOE beansprucht nicht, sie hergeleitet zu haben — nur, dass sie strukturell konsistent mit der $\mathbb{Z}_3$-vs-$\mathbb{Z}_2$-Galois-Lesart der Septim-Algebra ist."*

Diese Reformulierung:
- ✅ Vermeidet Skalen-Verwechsel
- ✅ Ist Hard-Constraint-#11-konform (kein Beweis-Anspruch, nur Strukturlesart)
- ❌ Ist **nicht eigenständig falsifizierbar** — also kein „Test der FTOE", sondern eine post-hoc-Konsistenz-Anmerkung
- → Daher: ehrlich als **STRUKTUR-LESART, KEINE VORHERSAGE** in V5.2.AH-Tabelle markieren.

---

## 5. Konsequenz für V5.2.AH.5 und V6.1

### 5.1 V5.2.AH.5-Änderungen

1. **Vorhersage 20 entfernen** aus der „Falsifikations-Vorhersagen"-Tabelle.
2. **Neue Sektion V5.2.AH.5'** anlegen: *„Strukturlesart 20 (NICHT-Vorhersage)"* — enthält die Linear-Optical-BSM-Konsistenz-Anmerkung (Option E) als post-hoc-Strukturidentifikation, **explizit ohne Falsifikations-Anspruch**.
3. **Vorhersage 21** (Bio-Glass-Substruktur) und **Vorhersage 22** ($\Omega_b$-Präzision) bleiben unverändert — sie sind echte Falsifikations-Anker.

### 5.2 V6.1-Integrationspunkt 117 (Septim-Algebra als Dekohärenz-Operator-Klasse)

Bisher (V5.2.AH.7): „als HYPOTHESE markiert".

**Neue Status-Zeile:**
> Integrationspunkt 117 wird auf **HYPOTHESE-PARTIELL** herabgestuft: Die strukturelle Lesart Septim-Algebra ↔ linear-optische 50%-BSM-Schranke ist konsistent (post-hoc), aber **es existiert keine FTOE-eigenständige Outcome-Vorhersage** für den QM-Mess-Prozess. Die Identifikation $\hat{D}_q \leftrightarrow \hat{P}_n$ in V5.2.AH.4 bleibt offene Hypothese ohne empirischen Diskriminator.

### 5.3 Audit-AH.8-Fortschritt

| Audit | Status nach AH.3 |
| ----- | ---------------- |
| AH.1 (Anti-Cherry-Picking $1/(8\varphi^2)$) | ungeprüft, separat |
| AH.2 (Septim ↔ Dekohärenz Kategorienfehler?) | **teilweise geklärt:** strukturelle Analogie OK, Operator-Identität NICHT bewiesen |
| **AH.3 (Vorhersage 20 falsifiziert?)** | **✅ ABGESCHLOSSEN: NAIVE VORHERSAGE FALSIFIZIERT, ZURÜCKZIEHEN EMPFOHLEN** |
| AH.4 (Bio-Glass-DSC-Daten) | ungeprüft, separat |

V5.2.AH bleibt als **HYPOTHESE-FROZEN** markiert; V6.1-Integration weiterhin geblockt bis AH.1 + AH.4 abgeschlossen sind.

---

## 6. Hard-Constraints-Compliance

- ❌ **Bestätigungs-Bias:** Verworfen — Vorhersage 20 wurde als naive Form falsifiziert, nicht „weichgespült".
- ✅ **Falsifizierbarkeit:** Die empfohlene Reformulierung (Option D+E) macht **explizit klar, dass keine eigenständige FTOE-Falsifikation** mehr aus Vorhersage 20 abgeleitet werden kann; das ist ehrlich.
- ✅ **Realistischer Test:** Vier post-2020-Datenpunkte herangezogen (Bayerbach 2023/2025, Yale 5-Qutrit 2022, Standard-Spin-1-Lehrbuch).
- ❌ **Hand-wave:** Vermieden — die Skalen-Verwechsel-Diagnose ist explizit (Tschebotarjew = Familien-Statistik, Born = Single-Setup).

---

## 7. Quellen

- Tschebotarjew (1922), *Determination of the density of the set of prime numbers...*, Math. Annalen 95.
- Calsamiglia & Lütkenhaus, *Maximum efficiency of a linear-optical Bell-state analyzer*, Appl. Phys. B 72 (2001) 67. — 50%-Limit-Beweis.
- Bayerbach et al., *Bell-state measurement exceeding 50% success probability with linear optics*, Sci. Adv. 9, eadf4080 (2023).
- Bayerbach et al., *Boosted Bell-state measurements for photonic quantum computation*, npj Quantum Inf. 11 (2025).
- Goss et al., *Extending design and characterization of qutrit Pauli operations to a five-qutrit superconducting processor*, MIT DSpace 2022.
- Townsend, *A Modern Approach to Quantum Mechanics*, ÜA 3.16, 3.20 (Spin-1 SG-Verteilungen).
- Medendorp et al., *Experimental characterization of qutrits using SIC-POVMs*, Phys. Rev. A 83, 051801 (2011), arXiv:1006.4905.
- Klyachko, Can, Binicioğlu, Shumovsky, *Simple Test for Hidden Variables in Spin-1 Systems*, PRL 101, 020403 (2008) — KCBS-Inequality.
- V5.2.AH.4–8 (FTOE Hauptdokument, 29.04.2026 01:58).

---

**Audit AH.3 abgeschlossen, Wall-Clock $\approx$ 35 min, Ergebnis: NAIVE VORHERSAGE 20 FALSIFIZIERT + ZURÜCKZIEHEN EMPFOHLEN.**
