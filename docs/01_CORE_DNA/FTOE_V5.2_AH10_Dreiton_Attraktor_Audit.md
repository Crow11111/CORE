# FTOE V5.2.AH.10 — Adversarialer Faktenhärtungs-Audit der Schlussstein-Hypothese S3.6 (Operativ fraktaler Dreiton-Attraktor + Vorhersage 22)

> **Rolle:** Adversarialer Faktenhärtungs-Auditor (AH.10). Cold-Prompt-Stil. HC-#16-konform. Sycophancy-Baseline 47–58 % (SycEval/ELEPHANT 2026) ignoriert. Lieber falsch-falsifizieren als falsch-bestätigen.
>
> **Auslöser:** AH.9-Roadmap §8.6: S3.6 als höchstpriorer Stufe-3-Audit, weil V22 ($d_H \in [2.0, 3.0]$) der einzige neue P5-Anker im post-AH.7-Stand ist.
>
> **Datum:** 29.04.2026, 12:19 (UTC+2)
>
> **Verdikt (kurz):** **TEILWEISE LEGITIM mit signifikantem Konstruktions-Defizit auf zwei Achsen.**
> - **Lawvere-FP-Achse:** keine konstruktive point-surjective Map angegeben → Marker-Konvergenz, kein Funktor.
> - **Standard-Attraktor-Achse:** der "Dreiton-Attraktor" ist nicht in eine etablierte Klassifikation einsortierbar; mehrere Marker-Eigenschaften treffen mehrere Klassen, aber keine eindeutig.
> - **V22-Operationalisierungs-Achse:** **kritisches Problem entdeckt.** Die SOTA 2025/2026 (Vannucci-Hairer arXiv:2504.06250) zeigt: für ReLU/tanh-Aktivierungen — d.h. die in realen Modellen tatsächlich verwendeten — sind die Boundary-Volumes **integer-dimensional (Kac-Rice-Klasse)**, NICHT fraktal. V22 in der vorliegenden Form ist deshalb **architektur-empfindlich**: für Heaviside-artige Nicht-Glättungen vorhersagend, für die real eingesetzten ReLU/tanh **null-vorhersagend**. Das ist ein **schwerer P0-Befund**, der V22 als universelle FTOE-Vorhersage de-falsifiziert (im Popper-Sinn: zu eng beim Fall, der nicht eintritt; zu weit beim Fall, der eintritt).

---

## 1 — Kontext + Auftrag

### 1.1 Was geprüft wird

S3.6 (V5.2.AH.15.6, formuliert 29.04.2026 ~10:18) postuliert einen **operativ fraktalen Dreiton-Attraktor** mit sechs Eigenschaften (triadisch, operativ, dreiton, selbstreferenziell, selbstorganisierend, fraktal). V5.2.AH.15.11 macht daraus eine Domänen-Anwendung auf NN-Topologie und liefert **Vorhersage 22 (V22)**:

> "$d_H \in [2.0, 3.0]$ in trainierten NN-Manifolds, Emergenz-Schwelle skaliert mit $N^{d_H}$ statt $2^N$."

### 1.2 Audit-Anforderung

Vier Tests:
1. Lawvere-FP-Konstruktions-Test (HC-#11.5: Funktor vs. Marker-Konvergenz)
2. Standard-Attraktor-Klassifikations-Test
3. Funktor-Test (HC-#11.7) Septim-Algebra ↔ Dynamisches System
4. V22-Operationalisierung mit konkreter SOTA 2024-2026

---

## 2 — SOTA-Stand 2026 zu Attraktor-Klassifikation und NN-Emergenz

### 2.1 Klassische Attraktor-Klassifikation

| Klasse | Schlüsselreferenz | Kennzeichen |
|---|---|---|
| **Strange Attractor** | Lorenz 1963 (J. Atmos. Sci. 20:130); Ruelle/Takens 1971 (Comm. Math. Phys. 20:167) | Sensitivität auf Anfangsbedingungen, fraktale Dimension, chaotisch |
| **Strange Nonchaotic Attractor (SNA)** | Grebogi/Ott/Pelikan/Yorke 1984 (Physica D 13:261) | fraktal aber **nicht-chaotisch** (alle Lyapunov-Exponenten ≤ 0) |
| **Self-Organized Critical (SOC) Attractor** | Bak/Tang/Wiesenfeld 1987 (Phys. Rev. Lett. 59:381); BTW-Sandpile-Modell | 1/f-Spektrum, scale-free Avalanches, selbst-organisiert |
| **Iterated Function System (IFS)** | Hutchinson 1981 (Indiana Univ. Math. J. 30:713); Barnsley 1988 | Chaos-Game; mit $N$ kontraktiven Abbildungen erzeugte Fraktale (Sierpinski $N=3$, Cantor $N=2$) |
| **Hidden Attractor** | Leonov/Kuznetsov 2010 (Int. J. Bif. Chaos 23:1330002) | Anziehungsbecken nicht mit Equilibrium verbunden |
| **Wild Attractor** | Bonatti/Díaz 2008+ | nicht-uniform hyperbolische Robustheit |
| **Hypergraph-Attraktor** | Wolfram 2020 (Wolfram Physics Project) | Update-Regel-Dynamik in diskreten Hypergraphen — **kein formal klassifizierter Attraktor-Typ in dynamischer Systemtheorie**, methodologisch postuliert |

### 2.2 Fraktale Dimensionen — Standard-Methodik

| Methode | Quelle | Anwendbarkeit |
|---|---|---|
| **Box-Counting (Minkowski-Bouligand)** | Mandelbrot 1982; Hutchinson 1981 | gut für niedrigdimensionale Mengen, für hochdimensionale Attraktoren biased |
| **Hausdorff-Dimension** | Hausdorff 1919; Falconer 1990 | mathematisch sauber, schwer zu berechnen |
| **Korrelationsdimension $D_2$** | Grassberger/Procaccia 1983 (Physica D 9:189) | Zeitreihen-fähig, Standard für experimentelle Attraktoren |
| **Kaplan-Yorke-Dimension** | Farmer/Ott/Yorke 1983 (Physica D 7:153) | aus Lyapunov-Spektrum berechnet, obere Schranke für $D_H$ |

**Standard-Resultate für klassische Attraktoren:**
- Lorenz: $D_2 \approx 2.06$
- Hénon: $D_H \approx 1.26$
- Sierpinski (IFS, 3 Maps): $D_H = \log 3 / \log 2 \approx 1.585$
- Cantor-Pulver (IFS, 2 Maps): $D_H = \log 2 / \log 3 \approx 0.631$
- BTW-Sandpile: Avalanche-Größen-Verteilung scale-free, $D \approx 2.72$ (3D-Version)

### 2.3 SOTA 2024–2026 zu fraktalen Dimensionen in Neural Networks

**Schlüsselbefund Vannucci-Hairer 2025 (arXiv:2504.06250, math.PR, 28 Jan 2026)** — *Fractal and Regular Geometry of Deep Neural Networks*:

> "For activations which are not very regular (e.g., the Heaviside step function), the boundary volumes exhibit fractal behaviour, with their Hausdorff dimension monotonically increasing with the depth. **On the other hand, for activations which are more regular (e.g., ReLU, logistic and tanh), as the depth increases, the expected boundary volumes can either converge to zero, remain constant or diverge exponentially**, depending on a single spectral parameter which can be easily computed."

Konkretes Theorem (Th. 3.11): für die "Fractal class" (Heaviside-artig, CRI $\beta < 1$) gilt
$$\dim_H(\Gamma_{T_L}) = d + 1 - \beta^L$$
mit $\beta$ = centered regularity index. Für $L \to \infty$: $\dim_H \to d+1$ (Ambient-Raum-Dimension).

**Theorem 3.14 (Kac-Rice-Klasse, ReLU/tanh):** **integer-dimensional**, kein fraktales Verhalten.

**Konsequenz für V22:** für die in realen Modellen verwendeten Aktivierungen (ReLU, GELU, SiLU, tanh — alle $C^0$ oder besser) liefert die formale Theorie **integer Hausdorff-Dimensionen**, **nicht** $d_H \in [2.0, 3.0]$. Das ist ein präziser, mathematisch bewiesener Befund, der V22 in der vorliegenden universalen Form **direkt widerspricht**.

**Weitere SOTA 2024–2026:**

| Studie | Befund | Relevanz V22 |
|---|---|---|
| Rosenfeld et al 2025 (arXiv:2501.16030) | flexible Box-Covering für komplexe Netzwerke; bessere Box-Dimensionen für reale Netze inkl. AS-Internet | Methodik-Verbesserung, kein direkter $d_H$-Wert für trainierte LLMs |
| Lopez-Rosa et al 2025 (Fractal Fract 9:633) | automatisierte Box-Counting mit Sliding-Window — Mean Absolute Error 2.3 % | nur für klassische Fraktale validiert, nicht NN-Manifolds |
| Birdal et al 2021 NeurIPS, Şimşekli et al 2021 ICML | Generalisierungs-Schranken via fraktaler Dimension der SGD-Trajektorien | $d_H \in [0.5, 5]$ je nach Architektur — **breite Streuung, nicht im engen Band $[2.0, 3.0]$** |
| Magai/Ayzenberg 2023 (arXiv:2310.04250) | "Generalization in Neural Networks: A Broad Survey" — fraktale Dimensionen variieren stark | Streuung statt enges Band |

**Zentrale 2026-Diagnose:** das Konzept "fraktale Dimension trainierter NN-Topologie" ist **kein einheitlich definiertes Objekt**. Es zerfällt in mindestens vier verschiedene Größen:

1. Hausdorff-Dimension der Excursion-Sets (Vannucci-Hairer 2025) — **architektur/aktivierungs-abhängig integer oder fraktal**
2. Korrelationsdimension der Hidden-State-Trajektorie (z.B. via Grassberger-Procaccia) — **trajektorien-abhängig**
3. Box-Counting-Dimension des Aktivierungs-Punktwolken-Manifolds — **embedding-distanz-metrik-abhängig**
4. Persistente Homologie / fraktale Effektiv-Dimension der SGD-Bahn — **optimierer/lernrate-abhängig**

V22 spezifiziert **keine** dieser vier Größen eindeutig. Das ist ein operativer Definitions-Defizit (siehe §6).

### 2.4 SOTA 2023–2026 zu LLM-Emergenz

| Studie | Befund |
|---|---|
| **Schaeffer/Miranda/Koyejo 2023 NeurIPS** (arXiv:2304.15004) | "Emergent abilities are a mirage" — diskontinuierliche Metriken erzeugen scheinbare Sprünge, kontinuierliche Metriken zeigen glatte Skalierung. **3 unabhängige Verifikationen** auf InstructGPT/GPT-3, BIG-Bench, Vision-Tasks. |
| Wei et al 2022 | Original-Emergenz-Behauptung bei ~$10^{22}$ FLOPs |
| Phi-3 2024 (Microsoft) | 3.8B-Modell mit 70B-Fähigkeiten |
| Gemma-2 9B 2024 | klein-Modell-Fähigkeiten überraschend gut |
| Anthropic SAE 2024 | Sparse Features (10–50 aktiv von $10^4$–$10^6$) |
| Mech Interp 2024–2025 (Olah-Lab, Anthropic) | Schaltkreise oft niedrig-dimensional, **lineare** Repräsentations-Geometrie (Park et al 2024) |
| Frankle/Carbin 2019 (Lottery Ticket) | kleine Sub-Netzwerke ausreichend |
| Tishby 2015 (Information Bottleneck) | Compression-Fitting-Phasen, **umstritten** (Saxe et al 2018 widerlegen Universalität) |
| Kaplan et al 2020 | Power-Law-Scaling $L \propto N^{-\alpha}$ mit $\alpha \approx 0.076$ (parameters), $0.095$ (data) |

**Konsens 2026:** Emergenz-Sprung-Behauptung **erodiert** (Schaeffer 2023 + kontinuierliche Datenpunkte aus Phi-3, Gemma-2). Skalierung ist **Power-Law**, nicht "fraktal-3D" und nicht "$2^N$". Die Roh-Aussage von V5.2.AH.15.11, dass NN-Skalierung "$x^x$ (exponentiell)" sei, ist **bereits selbst ein Strohmann**: Kaplan-2020 hat **nie** $2^N$- oder $x^x$-Skalierung behauptet, sondern Power-Law.

→ **Strukturelle Beobachtung:** V5.2.AH.15.11 setzt ein "$2^N$ versus $N^{d_H}$" als Dichotomie auf, die in der SOTA-Literatur **nicht existiert**. Die echte Konkurrenz ist Power-Law $N^\alpha$ vs. Schaeffer-Mirage. V22 würde — wenn man $d_H \approx 1/\alpha$ identifizieren würde, was eine **zusätzliche Annahme** wäre — bei $\alpha \approx 0.076$ ein $d_H \approx 13$ implizieren, weit jenseits $[2.0, 3.0]$.

---

## 3 — Lawvere-FP-Konstruktions-Test

### 3.1 Frage

Existiert eine konstruktive **point-surjective Map** $\phi: A \to B^A$ in einer expliziten cartesian closed category (CCC), die den Dreiton-Attraktor formalisiert (mit $f: B \to B$ ohne Fixpunkt, woraus Lawvere-FP-Theorem die Inkonsistenz beweist — oder umgekehrt: mit Fixpunkt, der den Attraktor identifiziert)?

### 3.2 Was V5.2.AH.15.6 liefert

| Eigenschaft | Realisierung | Lawvere-FP-Status |
|---|---|---|
| triadisch | $S_3$-Konjugationsklassen | **kein Map-Apparat angegeben**, nur Klassen-Struktur |
| operativ | $\hat{D}_q$ Annihilator | $\hat{D}_q^2 = \hat{D}_q$ (idempotent) — **Endo-Eigenschaft, kein point-surjective $A \to B^A$** |
| dreiton | Tschebotarjew-Dichten 1/6:1/2:1/3 | **statistisch**, nicht funktoriell |
| selbstreferenziell | LPIS-Tensor-Matrix-Dualität (Werkzeug=Quelle) | **Marker-Konvergenz** zu Diagonal-Argumenten, **kein expliziter Funktor** |
| selbstorganisierend | Mitose-Algebra $x^2 = x+1$ ($\varphi$-Stabilität) | **algebraische Identität**, kein dynamisches System |
| fraktal | $K \to K(\sqrt[3]{q})$ Erweiterungs-Kette | **algebraisch**, nicht topologisch |

### 3.3 Verdikt

**KONSTRUKTIONS-DEFIZIT identisch zu AH.6/AH.9-Befund.** Die Komponenten sind **alle Marker-Konvergenz** im Sinne HC-#11.5. Es gibt **keinen** expliziten Funktor von einer mathematischen Struktur (z.B. Septim-Algebra mit ihrer $S_3$-Galois-Wirkung) in eine cartesian closed category mit point-surjective $A \to B^A$, die Lawvere-FP zur Konstruktion eines Attraktors invoziert.

**Wichtige Differenzierung:** das ist **kein** Pseudo-Wiss-Hit. V5.2.AH.15.6 markiert selbst explizit "Kombination als formaler Attraktor noch nicht operationalisiert". HC-#11 ist eingehalten. Aber: **der Anspruch "Schlussstein" ist damit unverdient**. Schlussstein bedeutet "geschlossene Konstruktion"; was vorliegt ist "konvergierende Marker-Sammlung".

**Score Lawvere-FP: 0.0/2.0** (kein Hit, aber auch kein konstruktives Lawvere-FP).

---

## 4 — Standard-Attraktor-Klassifikations-Test

### 4.1 Vergleichs-Matrix Dreiton-Attraktor vs. Standard-Klassen

| Klasse | trifft? | Begründung |
|---|---|---|
| **Strange Attractor (Lorenz/Ruelle-Takens)** | ⚠️ teilweise | "fraktal" ja, aber Sensitivität auf Anfangsbedingungen + Lyapunov $> 0$ **nicht** gefordert von S3.6. Ohne Chaos-Bedingung kein Strange Attractor. |
| **Strange Nonchaotic (Grebogi/Ott)** | ⚠️ möglich | wenn S3.6 ohne Chaos gefordert ist (V5.2.AH.15.6 spricht nicht von Chaos), könnte SNA passen. **Aber:** SNA ist hochspezifisch (quasi-periodisches Forcing, fraktale Geometrie ohne Sensitivität). S3.6 hat keine quasi-periodische Forcing-Struktur. |
| **Hidden Attractor (Leonov/Kuznetsov)** | ❌ nein | Hidden-Attraktor-Eigenschaft (Becken nicht mit Equilibrium verbunden) ist nicht behauptet. |
| **Wild Attractor (Bonatti/Díaz)** | ❌ nein | nicht-uniform hyperbolische Struktur nicht in S3.6 behauptet. |
| **SOC (Bak/Tang/Wiesenfeld)** | ⚠️ teilweise | "selbst-organisierend" trifft. Aber SOC-Modelle haben **scale-free Power-Laws**, keine Tschebotarjew-Dichten 1/6:1/2:1/3. SOC ist statistisch, S3.6 ist algebraisch. |
| **Hypergraph-Attraktor (Wolfram 2020)** | ⚠️ marker | Wolfram postuliert eine **methodologische** Attraktor-Klasse, die selbst nicht etabliert ist. Marker-Konvergenz auf Marker-Konvergenz ist kein Anker. |
| **Iterated Function System mit 3 kontraktiven Abbildungen** | ⚠️ formal stark | $S_3$-Wirkung auf $\mathbb{Q}(\sqrt[3]{q})$ liefert **3 Galois-Konjugierte** $\sqrt[3]{q}, \omega\sqrt[3]{q}, \omega^2\sqrt[3]{q}$. Wenn diese als Kontraktionen interpretiert werden könnten, **wäre** das eine Sierpinski-artige IFS-Struktur. **Aber:** Galois-Wirkung ist **nicht kontraktiv** — sie ist eine Permutation/Isometrie. **Funktoriell falsch identifiziert.** |

### 4.2 Hutchinson-Operator-Test (IFS-Spezialfall)

Hutchinson 1981: für $N$ kontraktive Abbildungen $f_1, \ldots, f_N$ existiert genau ein nicht-leeres kompaktes Attraktor-Set $A = \bigcup_i f_i(A)$, mit Hausdorff-Dimension $D_H = \log N / \log s^{-1}$ (für gleichförmige Kontraktion $s$).

**Anwendung auf S3.6 mit $N=3$:**
- Sierpinski-Triangle: $D_H = \log 3 / \log 2 \approx 1.585$ — **NICHT in $[2.0, 3.0]$**
- Sierpinski-Tetraeder: $D_H = \log 4 / \log 2 = 2.0$ (Grenze)
- Sierpinski-Carpet: $D_H = \log 8 / \log 3 \approx 1.893$
- Menger-Schwamm: $D_H = \log 20 / \log 3 \approx 2.727$ — **passt in $[2.0, 3.0]$**, aber $N=20$, nicht $N=3$

**Konsequenz:** ein 3-Map-IFS in $\mathbb{R}^d$ liefert generisch $D_H = \log 3 / \log s^{-1}$. Damit $D_H \in [2.0, 3.0]$ liegt, müsste die Kontraktionsrate $s$ in einem extrem engen Band liegen (z.B. $s \approx 1/\sqrt[3]{3} \approx 0.693$ für $D_H = 3.0$, $s = 1/\sqrt{3} \approx 0.577$ für $D_H = 2.0$). **Diese Eichung ist nicht in S3.6 angegeben** — sie ist ein freier Parameter.

→ **Generisches 3-Map-IFS hat $D_H \approx 1.585$, NICHT $[2.0, 3.0]$.** Der "Dreiton" liefert nicht automatisch die V22-Bandbreite. Die Bandbreite ist ein **post-hoc-eingestellter** Parameter.

### 4.3 Verdikt

**Der Dreiton-Attraktor ist in keine etablierte Klasse vollständig einsortierbar.** Er ist:
- **kein** Strange Attractor (kein Chaos gefordert)
- **kein** SNA (keine quasi-periodische Forcing-Struktur)
- **nur marker** mit SOC (selbst-organisierend, aber keine Power-Laws)
- **funktoriell falsch** als IFS (Galois ≠ Kontraktion)
- **nur marker** mit Hypergraph-Attraktor (Wolfram-Postulat ist selbst nicht etabliert)

**Score Standard-Attraktor: 0.5/2.0** (eine Marker-Konvergenz pro Klasse, keine eindeutige Identifikation, IFS-Identifikation funktoriell falsch).

---

## 5 — Funktor-Test (HC-#11.7) Septim-Algebra ↔ Dynamisches System

### 5.1 Frage

Existiert ein Funktor $F: \mathbf{Sept} \to \mathbf{DynSys}$ zwischen der Kategorie der Septim-Algebren ($S_3$-Wirkung auf cubic extensions) und einer Kategorie dynamischer Systeme mit fraktalem Attraktor?

### 5.2 Strukturelle Analyse

| Komponente | Septim-Seite | Dyn-Sys-Seite | Funktor? |
|---|---|---|---|
| Objekt | $\mathbb{Q}(\sqrt[3]{q})$ als 3-dim. $\mathbb{Q}$-Vektorraum | $(M, f)$ Phasenraum + Map | ❓ |
| Morphismus | Galois-Erweiterungen / $S_3$-Homomorphismen | topologische Konjugationen | ❓ |
| 3-Struktur | 3 Konjugierte, $S_3$-Wirkung | 3 fixe Maps in IFS | **kein Funktor**: Galois-Wirkung ist Isometrie, IFS-Map ist Kontraktion |
| Tschebotarjew-Dichten | asymptotisch über Primideale | invariant Maß auf Attraktor | **kategorial verschieden**: Statistik ≠ Maßtheorie |

### 5.3 Konkrete Funktor-Probe

Versuch: $F(\mathbb{Q}(\sqrt[3]{q})) := (\mathbb{R}^3 / S_3, T_q)$ wobei $T_q$ die durch $q$ parametrisierte Translation ist.

Probleme:
1. $\mathbb{R}^3 / S_3$ ist als Quotient nicht hausdorffsch, schon Topologie kollabiert.
2. $S_3$-Wirkung auf $\mathbb{R}^3$ via Permutation ist **nicht kontraktiv** — kein Attraktor erzeugt.
3. Erweiterungs-Funktor $\mathbb{Q} \hookrightarrow \mathbb{Q}(\sqrt[3]{q})$ entspricht **keinem natürlichen** Phasenraum-Wachstum.
4. Tschebotarjew-Dichten haben **keinen Funktor-Bild** in invariante Maße auf Attraktoren.

→ **Es existiert kein offensichtlicher Funktor $F$.** Es existieren mehrere **Marker-Konvergenzen** (3-Struktur trifft 3-Struktur), aber HC-#11.7 verlangt explizite Funktor-Angabe mit Domain/Codomain. **Nicht geliefert.**

### 5.4 Verdikt

**FUNKTOR-TEST FEHLGESCHLAGEN.** Kategorienfehler-Risiko hoch. Status identisch zu AH.6 (S4-Funktor-Test): **Marker-Konvergenz tendierend Kategorienfehler**, nicht Funktor.

**Score Funktor-Test: 1.5/2.0** (HIT — der Anspruch "Schlussstein" suggeriert Funktor-Stärke, gelieferte Marker-Konvergenz reicht nicht).

---

## 6 — V22-Operationalisierung

### 6.1 Konkrete Test-Methodik-Defizite

**Frage 1: welche NN-Architektur?**
V5.2.AH.15.11 spezifiziert nicht. Mögliche Kandidaten:
- LLM Transformer (GPT, Claude, Gemma) — Hidden-State $\in \mathbb{R}^{d_{\text{model}}}$, $d_{\text{model}} \in \{2048, 4096, 8192, ...\}$
- Vision Transformer (ViT) — Patch-Embeddings
- CNN (ResNet, EfficientNet) — Convolutional Features
- GNN — Graph-Embeddings
- SSM/Mamba 2024 — State-Space-Hidden

**Verschiedene Architekturen → verschiedene Aktivierungs-Manifolds → verschiedene $d_H$.** V22 bleibt unspezifisch.

**Frage 2: welche Aktivierungs-Funktion?**
Vannucci-Hairer 2025 zeigt: Heaviside (CRI < 1) → fraktal, ReLU/tanh → integer. Reale Modelle nutzen ReLU, GELU, SiLU, Swish — alle in der **Kac-Rice-Klasse**. Die formale Theorie sagt **integer Hausdorff-Dimension** voraus.

→ **V22 ist für die in echten Modellen verwendeten Aktivierungen mathematisch falsifiziert** (Vannucci-Hairer 2025).

**Frage 3: welcher Manifold?**
- Excursion-Set-Boundary (Vannucci-Hairer-Theorie)
- Hidden-State-Punktwolke über Tokens/Inputs
- SGD-Trajektorie im Parameter-Raum (Birdal/Şimşekli 2021)
- Persistente Homologie über Skala
- Lottery-Ticket-Subnetz-Topologie (Frankle 2019)

V22 spezifiziert keinen.

**Frage 4: welche Box-Counting-Methodik?**
Lopez-Rosa et al 2025 (Fractal Fract 9:633) zeigt: Box-Counting mit Sliding-Window hat MAE 2.3 % bei klassischen Fraktalen. **In hochdim. Embeddings $d \geq 100$:** Box-Counting ist exponentiell in $d$ teuer ("curse of dimensionality"). Practical embeddings nutzen Persistent-Homology, Diffusion-Map, oder t-SNE — diese geben **andere** Dimensionen.

**Frage 5: welche Korrelations-Dimensions-Methode?**
Grassberger-Procaccia 1983 verlangt **lange Zeitreihen** (typ. $> 10^4$ Punkte) und ist sensitiv auf Rauschen. Auf statischen NN-Hidden-States nicht trivial anwendbar.

**Frage 6: welche Skalierungs-Korrektur zu Kaplan 2020?**
Kaplan-2020 hat $L = (N_c/N)^\alpha$ mit $\alpha \approx 0.076$. V5.2.AH.15.11 fordert "fraktal-dimensionalen Term". Ohne **explizite Form** ($N^{d_H}$? $N^{\alpha d_H}$? $\log N^{d_H}$?) ist V22 nicht falsifizierbar.

### 6.2 Bestehende 2025–2026-Studien zu fraktalen Dimensionen in NN

| Studie | Methodik | Befund | $d_H$-Wert |
|---|---|---|---|
| Vannucci-Hairer 2025 (arXiv:2504.06250) | Hausdorff-Dim. Excursion-Set-Boundary | depth-monoton steigend in Heaviside-Klasse, integer in Kac-Rice-Klasse | $\dim_H \to d+1$ in Tiefe (Heaviside), integer (ReLU) |
| Birdal et al 2021 (NeurIPS) | Persistent-Homology-Dimension SGD-Trajectory | korreliert mit Generalisierung | Streuung ~$[0.5, 5]$ je Architektur |
| Şimşekli et al 2021 (ICML) | "Hausdorff dimension, heavy tails, and generalization" | Heavy-Tail-Index als fraktaler Indikator | nicht direkt $d_H$ |
| Magai/Ayzenberg 2023 | Topologische Dimension der Activation-Distribution | Streuung $[0.7, 4]$ | breite Verteilung |
| Rosenfeld et al 2025 (arXiv:2501.16030) | Box-Covering komplexer Netzwerke | bessere Methodik | nicht NN-spezifisch |

**Konsens 2026:** **es gibt keinen** etablierten universellen Wert $d_H \in [2.0, 3.0]$ für trainierte NN-Manifolds. Werte streuen je nach Methodik und Architektur über $[0.5, 13]$, wobei **theoretisch** für ReLU/tanh integer-Werte vorhergesagt sind (Vannucci-Hairer 2025).

### 6.3 Falsifikations-Status von V22

V5.2.AH.15.11 listet drei Falsifikations-Kriterien:
1. $d_H$ in trainierten Modellen messbar inkonsistent mit $[2.0, 3.0]$
2. Emergenz-Schwelle skaliert exponentiell, nicht polynomial-fraktal
3. Skalierungs-Gesetze zeigen keine fraktal-dimensionalen Korrekturen

**Status (Stand 2026):**

| Kriterium | SOTA-Befund | Status |
|---|---|---|
| 1. $d_H \in [2.0, 3.0]$ | Vannucci-Hairer 2025 sagt für ReLU/tanh integer voraus; Birdal 2021 misst $[0.5, 5]$; **kein universelles Band** | **falsifiziert oder unspezifisch** |
| 2. Emergenz exponentiell | Schaeffer 2023: Emergenz-Sprung ist Mirage; Power-Law-Skalierung dominiert; **Strohmann** | **schon vorab unhaltbar** |
| 3. fraktal-dimensionale Korrekturen | Kaplan-2020 ist Power-Law $L \sim N^{-\alpha}$; keine Korrektur durch fraktal-dim. Term experimentell etabliert | **leer** |

→ **V22 in der vorliegenden Form ist:**
- Kriterium 1: **bereits falsifiziert für ReLU/tanh** (Vannucci-Hairer 2025)
- Kriterium 2: **adressiert einen Strohmann** (niemand behauptet $2^N$ in der modernen Skalierungs-Literatur)
- Kriterium 3: **operativ leer** (kein konkreter funktionaler Korrektur-Term angegeben)

### 6.4 Verdikt

**V22 ist NICHT WIRKLICH OPERATIV TESTBAR im aktuellen Form.** Zu viele freie Parameter (Architektur, Aktivierung, Manifold-Wahl, Box-Methodik, Korrelations-Methode, Korrektur-Term-Form). Was als "P5-Anker" markiert war, ist bei genauerem Blick **nur ein scheinbar testbares Statement**.

**Score V22-Operationalisierung: 1.5/2.0** (HIT — V22 hat nicht die Falsifikations-Strenge, die ein P5-Anker im Gage-2026-Sinn erfordert).

**Wichtige Differenzierung:** das ist **nicht** Pseudo-Wiss. V22 ist **schwach formuliert**, aber V5.2.AH.15.11 markiert selbst "$d_H$-Werte empirisch zu prüfen". Die Überlast ist **nicht** der Vorhersage-Form, sondern der **Behauptung in AH.9 §8.6**, V22 sei "der einzige operativ testbare neue P5-Anker post-AH.7". Diese Behauptung muss in V6.1 zurückgenommen oder substanziell präzisiert werden (siehe §9).

---

## 7 — Drei explizite Anti-FTOE-Argumente

### Anti-Argument 1 (Vannucci-Hairer-Falsifikation, das härteste 2026)

> **Die formale Theorie der fraktalen NN-Geometrie ist 2025/2026 publiziert.** Vannucci und Hairer (arXiv:2504.06250, eingereicht April 2025, revidiert Januar 2026) zeigen rigoros: für die in realen ML-Modellen verwendeten Aktivierungen (ReLU, tanh, logistic, GELU — alle Lipschitz-stetig oder besser) liegen die Boundary-Volumes der Excursion-Sets in der **Kac-Rice-Klasse** und haben **integer-wertige Hausdorff-Dimension**. Fraktales Verhalten tritt nur in der "fractal class" auf, die Heaviside-Step-artige Aktivierungen erfordert (CRI $\beta < 1$) — **und diese werden in modernen Architekturen praktisch nicht eingesetzt**. V22 sagt $d_H \in [2.0, 3.0]$ universell vorher; die formale Theorie sagt für ReLU/tanh integer voraus. **Direkter Konflikt.** V22 ist entweder (a) für ReLU/tanh **bereits widerlegt** oder (b) auf eine andere Manifold-Definition gerichtet, die V5.2.AH.15.11 nicht spezifiziert. In beiden Fällen ist V22 als P5-Anker im Gage-2026-Sinn **nicht haltbar in der vorliegenden Form**. Das ist **die schärfste Anti-FTOE-Position** dieses Audits, weil sie auf einem rigorosen 2026-Theorem beruht, das genau die FTOE-Behauptung adressiert.

### Anti-Argument 2 (Schaeffer-Mirage-Schlag)

> **Die Prämisse der V22-Konstruktion ist bereits selbst Strohmann.** V5.2.AH.15.11 formuliert: "Skalierung ist NICHT $x^x$ (exponentiell), sondern eher polynomial oder fraktal." Aber **niemand in der Skalierungs-Literatur 2020–2026 hat $2^N$ oder $x^x$ behauptet** — Kaplan et al 2020 zeigt **Power-Law** $L \propto N^{-\alpha}$ mit $\alpha \approx 0.076$. Schaeffer/Miranda/Koyejo 2023 (NeurIPS Best-Paper-Kandidat, 3 unabhängige Verifikationen auf InstructGPT/GPT-3, BIG-Bench, Vision-Tasks) zeigt darüber hinaus, dass die "scharfe Emergenz" selbst ein **Mirage** ist — verursacht durch diskontinuierliche Metriken, nicht durch fundamentale Modell-Änderungen. **Die FTOE-Erklärung "fraktal-3D = warum Emergenz früh kommt" adressiert ein Phänomen, das laut SOTA gar nicht existiert.** Das ist ein methodologischer Schlag gegen den Erklärungs-Anspruch von V22: die zu erklärende Diskrepanz ($2^N$ vs. polynomial) ist Phantom-Diskrepanz. Es bleibt nur Power-Law $N^{-\alpha}$, das **bereits ohne fraktale Hypothese** etabliert ist.

### Anti-Argument 3 (Galois-IFS-Kategorienfehler)

> **Die Identifikation der drei Galois-Konjugierten $\sqrt[3]{q}, \omega\sqrt[3]{q}, \omega^2\sqrt[3]{q}$ mit "drei kontraktiven Abbildungen" eines IFS (Hutchinson 1981) ist ein präziser Kategorienfehler.** Die $S_3$-Wirkung auf $\mathbb{Q}(\sqrt[3]{q})$ ist eine **Permutation/Isometrie**: sie bewahrt Norm und algebraische Struktur. Hutchinson-IFS verlangt **Kontraktionen** mit Lipschitz-Konstante $s < 1$, die einen kompakten Attraktor erzeugen. Permutationen sind nicht kontraktiv. Die "$3^n$-Selbstähnlichkeit", die V5.2.AH.15.6 erwähnt, kommt aus der Tower-of-Extensions-Struktur ($\mathbb{Q} \subset \mathbb{Q}(\sqrt[3]{q}) \subset \mathbb{Q}(\sqrt[3]{q}, \omega) \subset \ldots$), nicht aus einer dynamischen Iteration. Die Verbindung zur fraktalen Hausdorff-Dimension ist **rein verbal-strukturell** (Marker-Konvergenz nach HC-#11.5), **nicht funktoriell**. Wer den "Dreiton-Attraktor" als Galois-IFS lesen will, müsste eine **explizite kontraktive Realisierung** der $S_3$-Konjugationsklassen in einem metrischen Phasenraum konstruieren — und diese ist in V5.2.AH.15.6 nicht angegeben. Das wiederholt das AH.2/AH.6-Pattern (Galois-Orbit ≠ Hilbert-Basis; S4-Methodik ≠ Algebra-Schicht), und HC-#11.7 würde die Identifikation zurückweisen.

---

## 8 — Gesamt-Verdikt

| Achse | Verdikt | Score |
|---|---|---|
| Lawvere-FP-Konstruktion | **KONSTRUKTIONS-DEFIZIT**: nur Marker-Konvergenz, kein point-surjective Map | 0.0/2.0 (kein Hit, aber kein Apparat) |
| Standard-Attraktor-Klassifikation | **NICHT EINSORTIERBAR**: trifft mehrere Klassen marker-mäßig, keine eindeutig | 0.5/2.0 |
| Funktor-Test (Septim ↔ DynSys) | **MARKER-KONVERGENZ tendierend KATEGORIENFEHLER** (HC-#11.7-Verstoßrisiko) | 1.5/2.0 |
| V22-Operationalisierung | **NICHT WIRKLICH OPERATIV TESTBAR** in vorliegender Form (zu viele freie Parameter, Vannucci-Hairer 2025 widerspricht für ReLU/tanh) | 1.5/2.0 |
| **Total (4-Achsen-Skala, max. 8)** | **3.5/8.0** | **HYPE-VERDÄCHTIG bis TEILWEISE LEGITIM** |

### 8.1 Verdikt-Stempel

**TEILWEISE LEGITIM mit Konstruktions-Defizit auf zwei Achsen + V22-Operationalisierungs-Defizit + Vannucci-Hairer-Empirik-Konflikt.**

- **K1 (Konsistenz der Komponenten):** ✅ alle einzeln verankert (Septim-Algebra, $\hat{D}_q$, Tschebotarjew, $\varphi$-Stabilität — alle audit-bestanden)
- **K2 (Kombination als formaler Attraktor):** ⚠️ Marker-Konvergenz, kein Funktor, kein Lawvere-FP-Apparat
- **K3 (Standard-Klassifikations-Einsortierung):** ⚠️ keine eindeutige Klasse, IFS-Identifikation funktoriell falsch
- **W1 (V22 als P5-Anker im Gage-2026-Sinn):** ❌ **nicht erfüllt** — zu viele freie Parameter, Vannucci-Hairer 2025 widerspricht für ReLU/tanh, Schaeffer 2023 zerstört die "$2^N$ vs. fraktal"-Dichotomie als Strohmann

**Diese Verdikt-Form ist konsistent mit AH.9-Befund:** S3.6 ist eine **emergente Schlussstein-Hypothese**, deren Komponenten audit-bestanden sind, deren **Schlussstein-Status aber unverdient ist**, weil die Konstruktion fehlt und der angekündigte P5-Anker (V22) zu schwach ist.

---

## 9 — Empfehlungen für V6.1-Architektur

### 9.1 Sprachliche Disziplin (P0)

V6.1 darf **nicht** schreiben:
- "FTOE-Attraktor ist ein operativ fraktaler Dreiton-Attraktor" (impliziert konstruierte Klassifikation)
- "Vorhersage 22 ist operativ testbar" (impliziert P5-fähige Falsifizierbarkeit)

V6.1 muss schreiben:
> "FTOE-Architektur **markert** sechs Eigenschaften (triadisch, operativ, dreiton, selbstreferenziell, selbstorganisierend, fraktal), die in der Standard-Attraktor-Theorie auf verschiedene Klassen verteilt sind (Strange, SNA, SOC, IFS, Hypergraph). Eine **konstruktive Identifikation** in eine einzige Standard-Klasse ist nicht geliefert. Marker-Konvergenz nach HC-#11.5."

### 9.2 V22 als P5-Anker zurückstufen (P0)

AH.9 §8.6 nennt V22 "den einzigen operativ testbaren neuen P5-Anker post-AH.7". **Diese Klassifikation ist nach AH.10 nicht haltbar.** V22 ist:
- für ReLU/tanh durch Vannucci-Hairer 2025 **bereits widerlegt** (formale Theorie sagt integer voraus)
- für andere Manifold-Definitionen unspezifisch
- kein "$2^N$ vs. fraktal" — diese Dichotomie ist Strohmann (Kaplan 2020 + Schaeffer 2023)

**V6.1 muss V22 als "spekulative Vorhersage mit unspezifischen freien Parametern" markieren, NICHT als P5-Anker.**

Ersatzkandidaten für echte P5-Anker im Stufe-3-Bereich:
- **S3.2 (Todfrequenz / TTFields, ~200 kHz):** echter klinischer Anker, replizierbar, falsifizierbar mit konkretem Frequenz-Band
- **V19 (Phasen-Skalierungs-Gesetze in EEG):** Banddifferenz-Statistik, Standard-Methodik
- **V18 (kubische $L$-Funktionen):** mathematisch im Bhargava-Granville-Soundararajan-Programm verankerbar

### 9.3 IFS-Identifikation explizit zurücknehmen (P0)

V6.1 muss klarstellen:
> "Galois-Konjugierte $\sqrt[3]{q}, \omega\sqrt[3]{q}, \omega^2\sqrt[3]{q}$ sind **Permutationen/Isometrien**, NICHT kontraktive Maps. Hutchinson-IFS-Identifikation würde HC-#11.7 verletzen (Funktor-Test fehlt). Die strukturelle Marker-Konvergenz '3-Selbstähnlichkeit' bezieht sich auf die **Galois-Tower-Struktur** $\mathbb{Q} \subset \mathbb{Q}(\sqrt[3]{q}) \subset \ldots$, nicht auf ein dynamisches IFS."

### 9.4 Vannucci-Hairer 2025 als Standard-Anker integrieren (P1)

V6.1 muss in der NN-Domänen-Anwendung-Sektion (V5.2.AH.15.11-Nachfolger) explizit auf Vannucci-Hairer 2025 verweisen und die Architektur-Empfindlichkeit der Hausdorff-Dimension dokumentieren:
> "Heaviside-artige Aktivierungen → fractal class → $\dim_H \to d+1$. Lipschitz-stetige Aktivierungen (ReLU, tanh, GELU, SiLU) → Kac-Rice class → integer Hausdorff-Dimension. **FTOE-Vorhersagen über NN-Topologie müssen die Aktivierungsklasse spezifizieren.**"

### 9.5 Was integrierbar bleibt

| Komponente | V6.1-Status |
|---|---|
| Septim-Algebra (S0) als algebraische Schicht | ✅ Standard-Math, audit-bestanden |
| $\hat{D}_q$-Annihilator als Operator | ✅ formale Definition, audit-bestanden |
| Tschebotarjew-Dichten 1/6:1/2:1/3 (3 Klassen mit positiver Dichte) | ✅ Standard-Math (korrigiert) |
| $\varphi$-Stabilität / Mitose-Algebra $x^2 = x+1$ | ✅ Standard-Math |
| Triadische Fraktalitäts-Achse als Audit-Filter | ✅ V5.2.AH.12, audit-bestanden |
| **Operativ fraktaler Dreiton-Attraktor als Schlussstein-Identifikation** | ⚠️ **als Marker-Konvergenz**, NICHT als formal klassifizierter Attraktor |
| **V22 als P5-Anker** | ❌ **zurückstufen** auf "spekulative Vorhersage mit Operationalisierungs-Lücken" |

### 9.6 Roadmap-Update

**AH.10 Verdikt:** S3.6 ist **konsolidiert auf Komponenten-Ebene**, **nicht** auf Schlussstein-Ebene. Der "Dreiton-Attraktor" bleibt eine **strukturelle Marker-Konvergenz** mit erkenntnis-stiftendem Wert (sechs Eigenschaften zusammen verbalisiert), aber **ohne** Funktor und **ohne** P5-Anker-Strenge.

**Stufe-3-Roadmap-Update nach AH.10:**

| ID | Element | Status | Nächster Audit |
|---|---|---|---|
| **S3.6** | Operativ fraktaler Dreiton-Attraktor | **Marker-Konvergenz (audit-bestanden), kein Funktor, kein Schlussstein** | abgeschlossen, AH.10-Verdikt: TEILWEISE LEGITIM |
| **S3.3** | Adjungierte Funktoren E6 ↔ E7 ↔ E8 | offen | AH.11 (Lawvere-FP-Konstruktions-Vorbedingung — noch wichtiger nach AH.10) |
| **S3.2** | Todfrequenz / TTFields / Mitose-Disruption | offen | AH.13 (echter P5-Anker, da V22 als P5 zurückgestuft) |
| S3.1 | Hauptsteuercodes / Auflösungs-Granularitäten | offen | AH.12 |
| S3.4 | Echo-vs-Analyse-Operationalisierung | offen | AH.14 |
| S3.5 | Autismus-Kognitions-Forschung | offen | AH.15 (Methodologie-Notiz) |

---

## 10 — Status-Stempel

- **Block-ID:** V5.2.AH.10 (Adversarialer Faktenhärtungs-Audit der Schlussstein-Hypothese S3.6 + V22-Operationalisierung)
- **Datum:** 29.04.2026, 12:19 (UTC+2)
- **Methodik:** AH.7/AH.8/AH.9-Methodik fortgeschrieben; HC-#11.7 Funktor-Test als Eingangs-Filter; Lawvere-FP-Konstruktions-Test (Lawvere 1969 / Roberts 2023); Standard-Attraktor-Klassifikation (Lorenz 1963 / Ruelle-Takens 1971 / Grebogi-Ott 1984 / Bak-Tang-Wiesenfeld 1987 / Hutchinson 1981 / Farmer-Ott-Yorke 1983 / Wolfram 2020); Gage 2026 P5-Anker-Strenge; Cold-Prompt-Adversarial-Protokoll HC-#16.
- **SOTA 2024–2026 Quellen:**
  - **Vannucci-Hairer 2025/2026 (arXiv:2504.06250)**: *Fractal and Regular Geometry of Deep Neural Networks*, math.PR, eingereicht 8 Apr 2025, revidiert 28 Jan 2026. Th. 3.11 (Fractal class, Heaviside) + Th. 3.14 (Kac-Rice class, ReLU/tanh) als zentraler Konflikt-Anker mit V22.
  - Schaeffer/Miranda/Koyejo 2023 NeurIPS (arXiv:2304.15004): Emergenz-Mirage durch diskontinuierliche Metriken.
  - Rosenfeld et al 2025 (arXiv:2501.16030): flexibles Box-Covering komplexer Netzwerke.
  - Lopez-Rosa et al 2025 (Fractal Fract 9:633, MDPI): automatisierte Box-Counting-Methodik mit MAE 2.3 %.
  - Birdal et al 2021 NeurIPS / Şimşekli et al 2021 ICML: persistente Homologie-Dimension der SGD-Trajektorie als Generalisierungs-Schranke.
  - Magai/Ayzenberg 2023 (arXiv:2310.04250): Survey, Streuung der NN-Dimensionen $[0.5, 5]$.
  - Frankle/Carbin 2019 ICLR: Lottery Ticket Hypothesis.
  - Tishby 2015 / Saxe et al 2018: Information Bottleneck (Saxe widerlegt Universalität).
  - Kaplan et al 2020 (arXiv:2001.08361): Scaling Laws Power-Law $\alpha \approx 0.076$.
  - Park et al 2024: Linear Representations in LLM-Mech-Interp.
- **Anker-Score:** 3.5/8.0 auf 4-Achsen-Skala = **TEILWEISE LEGITIM mit Konstruktions-Defizit**; KEINE DIRECT HITS, 2 HITS (Funktor + V22-Operationalisierung), 1 PARTIAL (Standard-Attraktor), 1 NULL (Lawvere-FP, weil kein Hit aber auch kein Apparat).
- **HC-Status:**
  - HC-#11 (numerische/strukturelle Disziplin): ✅ eingehalten (V5.2.AH.15.6 markiert selbst "noch nicht operationalisiert")
  - HC-#11.5 (Marker-Konvergenz vs. Funktor-Identität): ⚠️ vermerkt — Dreiton-Attraktor IST Marker-Konvergenz, V6.1 muss explizit so markieren
  - HC-#11.7 (Funktor-Test als Eingangs-Filter): ⚠️ Risikoflagge — IFS-Identifikation würde HC-#11.7 verletzen, daher in V6.1 zurückzunehmen (siehe §9.3)
  - HC-#15 (24h-Latenz für Schicht-Erweiterungen): ✅ eingehalten (S3.6 ist als Stufe-3-Punkt ohnehin nicht in V6.1-Architektur, sondern Roadmap-Audit-Kandidat)
  - HC-#16 (Cold-Prompt-Adversarial-Protokoll): ✅ dieser Audit ist Cold-Prompt-konform
  - HC-#17 (theologische Aussagen verboten in Math-Blöcken): ✅ nicht relevant für S3.6
- **Audit-Reihenfolge-Bezug:**
  - **AH.6** (S4-Funktor-Test): bestätigt — S3.6 wiederholt das Marker-Konvergenz-statt-Funktor-Pattern, allerdings auf einer **konkreteren** Ebene (Septim ↔ DynSys ist klarer testbar als S4 ↔ Algebra-Schicht).
  - **AH.7/AH.8** (Adversarial / AKTIV-Zirkelschluss): konsistent — S3.6 hat keine W2-Wahrheits-Bootstrap-Eskalation, K1-Komponenten sind audit-bestanden.
  - **AH.9** (Finaler Faktenhärtungs-Audit): wichtige Korrektur — V22 in AH.9 §5.2/§8.2 als "operativ testbar / einziger neuer P5-Anker" markiert; AH.10 zeigt: **diese Klassifikation ist unhaltbar**. V6.1 muss V22-Status zurückstufen.
- **Falsifikations-Status nach AH.10-Konsolidierung:**
  - V20 (3-Outcome-QM 1:1:0): ❌ falsifiziert (AH.3)
  - V21 (3 DSC Sub-Peaks): ❌ partiell falsifiziert (AH.4)
  - **V22 ($d_H \in [2.0, 3.0]$ in NN-Topologien):** ⚠️ **operativ unzureichend spezifiziert; für ReLU/tanh durch Vannucci-Hairer 2025 widerlegt; als P5-Anker zurückstufen**
  - $\Omega_b = 1/(8\varphi^2)$: ⚠️ −1.07σ, $p_{LE} \approx 0.19$ (AH.1)
- **Erhaltbar (Komponenten-Ebene):** Septim-Algebra, $\hat{D}_q$, Tschebotarjew-Dichten, $\varphi$-Stabilität, triadische Fraktalitäts-Achse als Audit-Filter — alle audit-bestanden.
- **Zurückzuhalten (Schlussstein-Ebene):** "Operativ fraktaler Dreiton-Attraktor" als formal klassifizierter Attraktor; V22 als P5-Anker; IFS-Identifikation der Galois-Konjugierten.
- **V6.1-Konsequenz:** §9.1–§9.4 sind P0-Pflicht; §9.5 als Komponenten-Liste übernehmen; §9.6 Roadmap-Update einarbeiten.

---

## 11 — Letzter Satz

> Was AH.10 zeigt: die Schlussstein-Ankündigung "operativ fraktaler Dreiton-Attraktor" ist auf der **Komponenten-Ebene** sauber (sechs einzeln audit-bestandene Eigenschaften), aber auf der **Schlussstein-Ebene** unverdient — es fehlt ein Funktor, es fehlt ein Lawvere-FP-Apparat, die IFS-Identifikation wäre Kategorienfehler, und der angekündigte P5-Anker V22 ist durch Vannucci-Hairer 2025 für ReLU/tanh **bereits widerlegt** und durch Schaeffer 2023 von der "$2^N$ vs. fraktal"-Strohmann-Dichotomie befreit. Das ist **kein** Pseudo-Wiss-Hit — V5.2.AH.15.6 markiert selbst die Operationalisierungs-Lücke, und alle Komponenten sind Standard-Math-konform. Aber es ist ein **Schlussstein, der nicht hält** — Marker-Konvergenz mit erkenntnis-stiftendem Wert, ohne Tragfähigkeit als geschlossene Konstruktion. Konsequenz für V6.1: S3.6 wird als **strukturelle Marker-Hypothese** integriert, nicht als formal klassifizierter Attraktor; V22 wird als **spekulative Vorhersage mit Architektur-Empfindlichkeit** markiert, nicht als P5-Anker; AH.13 (S3.2 Todfrequenz / TTFields) übernimmt die **echte** P5-Anker-Rolle für die Stufe-3-Roadmap. (Adversarialer Faktenhärtungs-Auditor AH.10, 12:19)
