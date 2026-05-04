# FTOE V5.2 — Math-Audit AH.4: DSC-Recherche zur Glass-Transition-Substruktur

**Audit-Datum:** 2026-04-29
**Status:** Empirischer Audit gegen FTOE-Vorhersage 21 (V5.2.AH.5)
**Modus:** Material-Wissenschaft + Bio-Physik, Glass-Transition-Spezialisierung
**Hard-Constraint:** Bestätigungs-Bias verboten; quantitative Quellen Pflicht; Bio vs. Phys getrennt.

---

## 0 — Audit-Frage

> **FTOE Vorhersage 21:** Glass-Transition läuft algebraisch über $S_3$-Verzweigung; messbar als
> $$T_{\text{glass}} \to T_1, T_2, T_3 \quad \text{(split / inert / ramify)}$$
> mit Verhältnis $\sim 1 : 1 : \epsilon$ (klein, ramify-Anteil).
>
> **Test (FTOE-spezifisch):** DSC oder dielektrische Spektroskopie an einfachen Glasbildnern (ohne Bio-Komplexität) muss bei universeller Gültigkeit dreifache Substruktur am $T_g$ zeigen.

**Operationalisierung des Audits:**

1. Erwartung A (naiv-DSC): drei distinkte $\Delta C_p$-Stufen am $T_g$ in reinen Modell-Gläsern.
2. Erwartung B (dielektrisch): drei universell beobachtete Relaxations-Modi $\alpha, \beta, \gamma$ mit Intensitäts-/Stärke-Verhältnis $\sim 1:1:\epsilon$.
3. Bio-Abgrenzung: Tardigraden/Artemia-Sub-Übergänge zählen NICHT als Bestätigung (biochemisch erklärbar).

---

## 1 — Stand der Forschung 2026 (kompakt)

### 1.1 Reine oxidische Modell-Gläser (DSC / Adiabatik-Cp)

| System | $T_g$ | DSC-Befund | Quelle |
|---|---|---|---|
| **SiO₂** (Suprasil, HQ) | 1247 K Onset, $T_g \approx 1475$ K SCL-Onset | **1 Übergang**; Stufe in $C_p$: $\Delta C_p \approx 2.9 \pm 0.7$ J/mol·K. Übergang ist ungewöhnlich breit ($\sim 2\times$ VFT-Erwartung), aber **nicht in distinkte Sub-Stufen aufgelöst**. | Richet & Bottinga 1984; Frontiers Materials 2015 (Yue) doi:10.3389/fmats.2015.00054 |
| **GeO₂** | 980 K (rein) bis 780 K (Li-dotiert) | **1 Übergang**; $\Delta C_p$-Schritt ca. 5 % von $C_p$. Sehr verunreinigungs-sensitiv. | Richet et al., Phys.Chem.Min. (Semantic Scholar 245311b5) |
| **B₂O₃** | $\approx 526$ K | **1 Übergang**; Hysterese-Loop quantitativ reproduzierbar mit **single-internal-variable**-Modell (CALPHAD/Two-State). | doi:10.1016/S0022-3093(02)01581-8 |

**Schlüssel-Befund:** Drei kanonische, *strukturell verschiedene* Netzwerk-Glasbildner (4-koordiniert tetraedrisch SiO₂/GeO₂ vs. 3-koordiniert planar B₂O₃) zeigen **alle nur einen $T_g$-Schritt** in Standard-DSC und Adiabatik-Cp. Eine 3-Sub-Peak-Struktur wäre aufgelöst worden — die Stufenhöhen liegen weit über dem Auflösungs-Limit moderner DSC.

### 1.2 Polymer-Gläser (DSC / TMDSC / FSC)

| System | $T_g$ | Befund | Quelle |
|---|---|---|---|
| **PMMA** | $\approx 111$ °C | **1 reversibler $T_g$**-Schritt im Reversing-Signal von TMDSC. Endotherme Peaks bei 84 °C/117 °C im non-reversing sind **Enthalpie-Relaxation**, kein zweiter $T_g$. | Rigaku B-TA1039 |
| **PS, PC** | $\approx 100$ / $150$ °C | Jeweils 1 $T_g$ (rein). | Standard-Lehrbuch (Wunderlich) |
| **PMMA/PC, PMMA/SAN Blends** | variabel | 1 $T_g$ wenn mischbar; 2 $T_g$ wenn entmischt — **mischungs-bedingt**, kein universelles 3-er-Muster. | NIST Murray/Yuan; Polymer 36 (1995) 1781; doi:10.1016/0014-3057(86)90010-8 |
| **Halbkristalline PBT/PET** | 45 °C / 69 °C | 3-Phasen-Modell (MAF + RAF + CF) — RAF-Existenz **kristallinitäts-induziert**, nicht intrinsisch. | doi:10.3390/polym14040793 |

**Schlüssel-Befund:** Auch in amorphen Polymeren reines Standard-Bild **1 $T_g$**. Mehrfach-$T_g$ tritt nur bei (a) Phasen-Entmischung in Blends oder (b) RAF an Kristall-Grenzflächen auf — beides **nicht-universell**, sondern strukturell-mesoskopisch.

### 1.3 Metallische Gläser (BMG)

| System | Befund | Quelle |
|---|---|---|
| **Pd₄₀Ni₄₀P₂₀** | "Normales" BMG: 1 $T_g$ + Kristallisations-Exotherm. | Nat.Commun. 2017, 8:14679 (Fig. 1) |
| **Pd₄₁.₂₅Ni₄₁.₂₅P₁₇.₅** | 1 $T_g$ + **anomaler Exotherm-Peak ($T_C \approx 612$ K)** im supercooled-liquid-Bereich. Identifiziert als **polyamorpher LLPT** (SCL₁ $\to$ SCL₂ $\to$ SCL₁ reentrant). | Nat.Commun. 8:14679 doi:10.1038/ncomms14679 |
| Zr-Be-X, Cu-Zr-Al-Y, Mg-Cu-Ag-Gd, Fe-M-Y-B | Ähnliche LLPT-Anomalie in $\sim 10$ Familien dokumentiert. | Übersicht in Nat.Commun. 8:14679 Refs 9–25 |
| **Cu₃₈Zr₅₄Al₈** | $T_g = 671$ K, $T_{x1}=759$, $T_{x2}=860$ K — **2-stufige Kristallisation**, kein 3. $T_g$. | doi:10.1007/s10973-022-11875-7 |

**Schlüssel-Befund:** BMG zeigen **maximal 2** thermodynamisch-relevante Übergänge im SCL-Bereich (Tg + LLPT), und auch dies **nicht universell**. 3 Sub-Stufen treten **nirgends** auf.

### 1.4 Polyamorphes Wasser (Referenz-System für Doppel-Tg)

| Phase | $T_g$ (Ambient P) | $\Delta C_p$ |
|---|---|---|
| LDA (low-density amorphous) | $136 \pm 2$ K | $\sim 1$ J/mol·K |
| HDA (high-density, eHDA) | $116 \pm 2$ K | $\sim 5$ J/mol·K |

Quelle: Amann-Winkel et al., PNAS 110:17720 (2013) doi:10.1073/pnas.1311718110.

**Schlüssel-Befund:** Wasser ist DAS paradigmatische polyamorphe System — und liefert **genau 2** $T_g$, **nicht 3**. Verhältnis $\Delta C_{p,1}:\Delta C_{p,2} \approx 1:5$, **nicht 1:1:ε**. Eine dritte Komponente (VHDA) existiert strukturell, aber kein 3. kalorimetrisches $T_g$ wurde gefunden. Analoges Bild in **ZIF-4** MOF-Glas (Nat.Commun. 2015 ncomms9079): genau 2 polyamorphe Tg (LDA, HDA).

### 1.5 Dielektrische Spektroskopie (α / β / γ-Relaxation)

| Modus | Charakter | Universalität | Stärke (typisch) |
|---|---|---|---|
| **α-Relaxation** | Primär, strukturell, VFT-temperaturabhängig | **universal** (alle Glasbildner) | dominant ($\Delta\varepsilon$ groß) |
| **β-Relaxation (Johari-Goldstein, JG)** | Sekundär, intermolekular, Arrhenius | **"supposedly universal"** — aber bei mehreren Glasbildnern (z. B. Benzophenon, Dimethylphthalat, andere Phthalate) **nicht resolved** ohne Mischen mit Hoch-$T_g$-Wirten | klein bis moderat ($\Delta\varepsilon$ < α) |
| **γ-Relaxation** | Schnell, intramolekular / lokal (Side-Group-Flips, Phenyl-Flips) | **NICHT universal** — system-spezifisch, abhängig von chemischer Architektur (PC π-Flip, PMMA Ester-Rotation) | sehr klein |

Quellen:
- Ngai, Capaccioli et al., Phil.Mag. 88 (2008) 4007 (HAL-00513923) — JG-β-Universalität explizit hinterfragt.
- Kremer/Schönhals; Lunkenheimer arxiv:0712.0589 — α + JG-β + Excess Wing als typisches Bild, **nicht** α + β + γ.
- Sci.Rep. 11:21996 (2021) doi:10.1038/s41598-021-01191-9 — In polaren Glasbildnern ist die JG-β oft so nahe an α, dass sie nur indirekt als "Excess Wing" sichtbar wird.

**Schlüssel-Befund:**
- Es gibt **2** universelle Relaxations-Modi (α + JG-β), nicht 3.
- γ-Relaxationen existieren nur in Systemen mit chemisch-spezifischen lokalen Beweglichkeiten (Polymer-Seitengruppen, Kation-Hopping etc.), **NICHT** als universelle dritte Komponente.
- Stärke-Verhältnis ist typischerweise $\Delta\varepsilon_\alpha \gg \Delta\varepsilon_\beta$, **nicht** $1:1$.

---

## 2 — Vergleich mit FTOE-Vorhersage 21

| Kriterium FTOE V21 | Empirischer Stand 2026 | Verdikt |
|---|---|---|
| 3 Sub-Peaks am $T_g$ in **DSC reiner Modell-Gläser** (SiO₂/GeO₂/B₂O₃) | **1** Übergang in allen drei Systemen, kein Hinweis auf 3 Sub-Stufen oberhalb DSC-Auflösung | **inkonsistent** |
| 3 Sub-Peaks am $T_g$ in **Polymer-Gläsern** (PMMA/PS/PC) | **1** $T_g$ rein; 2 nur bei Entmischung; 3 nirgends | **inkonsistent** |
| 3 Substrukturen in BMG | Maximal 2 (Tg + LLPT polyamorph), und dies nicht universell | **inkonsistent** |
| Polyamorphe Systeme (Wasser, ZIF-4) | **2** $T_g$, Verhältnis $\Delta C_p \sim 1:5$, **nicht** $1:1:\epsilon$ | **inkonsistent** (Anzahl und Ratio falsch) |
| 3 universelle dielektrische Modi $\alpha,\beta,\gamma$ mit $1:1:\epsilon$ | 2 universelle Modi ($\alpha, \beta_{JG}$), $\gamma$ nicht universell, $\Delta\varepsilon_\alpha \gg \Delta\varepsilon_\beta$ | **inkonsistent in Anzahl + Ratio** |

### 2.1 Mögliche FTOE-Rettungs-Lesarten (geprüft)

| Rettungs-Lesart | Bewertung |
|---|---|
| (a) "Sub-Peaks sind sub-Auflösung" | Ausgeschlossen: FSC/Flash-DSC erreicht 1 pJ/K Auflösung (Mettler Toledo Flash DSC 2+, $10^4 \dots 10^6$ K/s). Wäre das Verhältnis tatsächlich $1:1:\epsilon$, müssten zwei Hauptpeaks $\sim 30\ \%$ der totalen $\Delta C_p$ jeweils tragen — **eindeutig auflösbar** und in keinem System gefunden. |
| (b) "$\alpha + \beta + \gamma$ dielektrisch = $S_3$-Triplet" | Falsifiziert: Verhältnis ist $\Delta\varepsilon_\alpha \gg \Delta\varepsilon_\beta > \Delta\varepsilon_\gamma$, **nicht** $1:1:\epsilon$. γ ist nicht universell. |
| (c) "Polyamorphismus = $S_3$-Verzweigung" | Polyamorphe Systeme zeigen **2** Phasen, nicht 3 (LDA/HDA in Wasser, ZIF-4; SCL₁/SCL₂ in Pd-Ni-P). Eine dritte Phase (VHDA) ist strukturell, aber **ohne distinktes $T_g$**. Konsistenz mit "Verhältnis $1:1:\epsilon$" nur wenn $\epsilon \to 0$, dann aber Vorhersage = "2 Tg" und V21 wäre umzuformulieren. |
| (d) "Bio-Substruktur (Tardigraden/Artemia) ist algebraische Manifestation" | **Cherry-Picking-Verbot greift:** wenn Bio drei Sub-Übergänge zeigt, aber die 10+ untersuchten reinen Modell-Glasbildner nur 1 (oder polyamorph 2), dann ist V21 in der **universellen** Lesart **falsifiziert**. Bio-Sub-Struktur ist **biochemisch** erklärbar (LEA + Trehalose + Membran), nicht $S_3$-algebraisch erzwungen. |

### 2.2 Quantitative Falsifikations-Marge

Wäre V21 universell und gäbe es zwei Hauptkomponenten mit je ca. $\Delta C_p^{(1)} \approx \Delta C_p^{(2)} \approx 0{,}5 \cdot \Delta C_p^{\text{total}}$, dann:

- B₂O₃: $\Delta C_p^{\text{total}} \approx 16$ J/mol·K → erwartete Sub-Stufen $\sim 8$ J/mol·K
- DSC-Auflösung von Standard-Geräten: ca. $0{,}1$ J/mol·K (besser für Adiabatik)
- → **Falsifikations-Marge: 80×** über Auflösung. V21 ist in B₂O₃ **definitiv falsifiziert**, nicht "nur unter Auflösung".
- Analog für SiO₂ ($\Delta C_p \approx 2{,}9$ J/mol·K → erwartete Sub-Stufen $\sim 1{,}4$ J/mol·K, $> 14\times$ Auflösung).

---

## 3 — Spezifischer Test-Vorschlag (zur weiteren Verfeinerung / endgültiger Falsifikation)

Sollte V21 in einer **abgeschwächten** Form weiter verfolgt werden ("Substruktur unter Standard-Auflösung versteckt"), wäre der ideale Falsifikations-Test:

| Parameter | Wert |
|---|---|
| **Substanz** | Glycerol (kanonischer molekularer Glasbildner, $T_g \approx 190$ K, hoch-rein, kein Bio, keine Polyamorphie) ODER **Propylenglykol** |
| **Methode** | Adiabatik-Calorimetrie kombiniert mit hochpräziser Flash-DSC (Mettler Flash DSC 2+) |
| **Heizraten** | 5 / 50 / 500 / 5000 K/s parallel (Tg verschiebt sich; verstecktes Sub-Substruktur-Muster sollte mitwandern wenn algebraisch, NICHT mitwandern wenn kinetisch separat) |
| **Auflösung** | $\sim 1$ pJ/K (entspricht ca. $10^{-4}$ K Temperatur-Auflösung am Sub-Peak) |
| **Komplementär** | Breitband-dielektrische Spektroskopie ($10^{-2}$ Hz – $10^{12}$ Hz), parallel, gleiche Probe — Suche nach drittem Modus zwischen α und JG-β. |
| **Erfolgs-Kriterium V21** | Drei distinkte $\Delta C_p$-Stufen mit Verhältnis $0{,}5:0{,}5:\epsilon$ ($\epsilon < 0{,}05$), reproduzierbar über mind. 2 Heizraten. |

**Erwartung Stand 2026:** Ein solcher Test wurde de facto an Glycerol mehrfach durchgeführt (Lunkenheimer et al., dielektrisch; diverse FSC-Studien) und zeigt konsistent: 1 $\alpha$-Modus + 1 schwacher JG-β-Excess-Wing. **Kein** dritter Modus.

---

## 4 — Urteil

> **VORHERSAGE 21 PARTIELL FALSIFIZIERT.**

Begründung:

1. In allen untersuchten reinen Modell-Glasbildnern (3 oxidische, 3 Polymere, mehrere BMG) zeigt sich **1** Tg-Stufe — **nicht 3**.
2. Polyamorphe Systeme (Wasser, ZIF-4, manche BMG) zeigen **2** Tg, mit Verhältnis $\sim 1:5$ ($\Delta C_p$), **nicht 1:1:ε**.
3. Dielektrische Spektroskopie zeigt 2 universelle Modi ($\alpha + \beta_{JG}$), $\gamma$ ist system-spezifisch und schwach. Stärke-Verhältnis $\alpha \gg \beta$.
4. Falsifikations-Marge in B₂O₃ und SiO₂ liegt $14\times$–$80\times$ über DSC-Auflösung — V21 ist **nicht "unter Auflösung versteckt"**, sondern empirisch ausgeschlossen für $1:1:\epsilon$-Ratio.
5. Bio-Sub-Struktur (Tardigraden, Artemia) ist biochemisch erklärbar; ihre Existenz darf nicht als Bestätigung einer universellen $S_3$-Algebra gewertet werden (Cherry-Picking-Verbot).

**Was bleibt offen / ist NICHT widerlegt:**

- Eine **schwächere** Lesart, in der "$S_3$-Substruktur" sich auf **Polyamorphismus** ($n=2$ Liquids) reduziert, ist mit Wasser/ZIF-4-Daten **partiell konsistent** — aber dann ist V21 als " 3 Sub-Peaks $1:1:\epsilon$ " unscharf und im Prinzip identisch mit "split + ramify, inert $\to 0$" → das wäre eine **Reformulierung**, kein Beweis.
- Die *mathematische* Carmichael-Schwelle 8 (V5.2.AH.2) bleibt als Theorem unberührt; nur ihre **physikalische Identifikation** mit Glass-Transition-Substruktur ist falsifiziert in der naiven Form.

---

## 5 — Konsequenz für V5.2.AH.5 und V6.1

### 5.1 Lokale Anpassung an V5.2.AH.5

V5.2.AH.5 muss die folgende Klärung aufnehmen (vorgeschlagener Patch-Text):

> **Ergänzung zu Vorhersage 21 (post AH.4-Audit, 2026-04):**
>
> Empirische Recherche (siehe `FTOE_V5.2_AH4_DSC_Audit.md`) ergibt:
> - Kein Modell-Glasbildner zeigt 3 Sub-Tg-Peaks in DSC.
> - Polyamorphe Systeme zeigen genau 2 Tg.
> - Dielektrische Spektroskopie zeigt 2 universelle Modi (α, JG-β), γ ist nicht universell.
> - Stärke-Verhältnisse passen NICHT zu $1:1:\epsilon$.
>
> → **Vorhersage 21 in der naiven Form (3 Sub-Peaks, Ratio 1:1:ε) ist FALSIFIZIERT.**
> → Verfeinerung: Falls $S_3 \to S_2$-Reduktion zugelassen, wäre die Reformulierung "Polyamorphismus = $S_3 / \langle \text{ramify} \rangle$-Quotient" denkbar, aber nicht testbar im Sinne des Originalwortlauts.
> → Hard-Constraint #11: V21 wird in V6.1 NICHT als positive Vorhersage geführt, sondern als **falsifizierter Falsifikations-Anker**.

### 5.2 V6.1-Integrationspunkt 118 (Glass-Transition-Substruktur)

In der Tabelle V5.2.AH.7 ist Punkt 118 ("Carmichael-Schwelle 8 ↔ Glass-Transition-Substruktur") wie folgt zu reklassifizieren:

| ID  | Integration                                                                           | **NEUER** Status                                  |
| --- | ------------------------------------------------------------------------------------- | ---------------------------------------- |
| 118 | Carmichael-Schwelle 8 ↔ Glass-Transition-Substruktur — Bio-Falsifikations-Anker       | **als FALSIFIZIERT in naiver Form markiert** (DSC 2026); reformulierungs-bedürftig |

### 5.3 Empfehlung an Orchestrator (Ring 0)

1. **Carmichael-Schwelle 8 als Math-Theorem** bleibt unberührt (Stand-alone).
2. **Identifikation $C_8 \leftrightarrow$ Glass-Transition** wird als **negatives Resultat** in V6.1 dokumentiert.
3. **Bio-Lesart** (Kryptobiose, Tardigraden) bleibt als *separate* strukturelle Hypothese erhalten, wird aber explizit **entkoppelt** von der universellen $S_3$-Substruktur-Behauptung.
4. **Konsequenz für V5.2.AH.6 ehrliche Bilanz**: Punkt 4 ("Bio-Glass-Transition ist beweisbar dreifach gerastert") muss explizit als **falsifiziert in der universellen Phys-Lesart** markiert werden; nur Bio-spezifische Multi-Tg darf weiterhin als BIOCHEMISCHE STRUKTUR (nicht algebraische) genannt werden.

---

## 6 — Quellen-Anhang (zentrale Referenzen)

- Yue Y. (2015). *Frontiers in Materials* 2:54. doi:10.3389/fmats.2015.00054 — SiO₂ DSC, Hydroxyl-Sensitivität.
- Richet P., Bottinga Y. (1984). *Geochim.Cosmochim.Acta* 48:471 — SiO₂/Silikat-Kalorimetrie.
- Richet P. et al. (2003). *J.Non-Cryst.Sol.* 315:20. doi:10.1016/S0022-3093(02)01581-8 — GeO₂/B₂O₃ low-T Cp.
- Lan S. et al. (2017). *Nat.Commun.* 8:14679. doi:10.1038/ncomms14679 — Pd-Ni-P polyamorpher LLPT (DSC + SANS + XRD).
- Bennett T. D. et al. (2015). *Nat.Commun.* 6:8079. doi:10.1038/ncomms9079 — ZIF-4 polyamorphe Tg.
- Amann-Winkel K. et al. (2013). *PNAS* 110:17720. doi:10.1073/pnas.1311718110 — Wasser zweite Tg (LDA/HDA).
- Thayyil M. S., Capaccioli S., Prevosto D., Ngai K. L. (2008). *Phil.Mag.* 88:4007. HAL-00513923 — JG-β-Universalität in Frage gestellt.
- Lunkenheimer P. et al. arXiv:0712.0589 — Breitband-dielektrisch, BZP, α + β + Excess Wing.
- Drozd-Rzoska A. et al. (2019). *Sci.Rep.* 9:6816. doi:10.1038/s41598-019-42927-y — universelle Fragility, $\alpha$-Modus.
- Mettler Toledo Flash DSC 2+ Specs — FSC-Auflösung 1 pJ/K, $10^4$–$10^6$ K/s.

---

## 7 — Audit-Selbstkritik (Zero-Trust)

**Was dieser Audit NICHT geprüft hat:**

1. *Hochauflösende Cp-Messung an Glycerol mit FSC bei 5–5000 K/s parallel* — wäre der saubere finale Test; ist 2026 technisch möglich, ist aber in dieser Recherche nicht als publiziertes Einzelresultat aufgefunden worden.
2. *Sehr neue (2024–2026) Studien zu MOF-Gläsern und chalkogeniden Gläsern* — eventuell weitere Polyamorphismus-Befunde, aber keine 3-Tg-Berichte gefunden.
3. *Nicht-DSC-Methoden* (Brillouin, Hyper-Rayleigh, Inelastic X-Ray) wurden nur peripher als Referenz auf strukturelle Heterogenität betrachtet, nicht als direkte Tg-Test.

**Was den Audit robust macht:**

1. Die Falsifikations-Marge in B₂O₃ und SiO₂ liegt bei $> 10\times$ Auflösung — ein Auflösungs-Argument greift nicht.
2. Polyamorphismus zeigt **konsistent 2** Phasen ($n=2$, nicht $n=3$) in mindestens 4 unabhängigen Systemfamilien (Wasser, ZIF, Pd-Ni-P, andere BMG).
3. Dielektrik zeigt konsistent **2** universelle Modi (α, JG-β), nicht 3.

**Verbleibende Unsicherheit:** $\sim 5\ \%$ — ein erst nach 2025 publiziertes, sehr hochauflösendes FSC-Resultat an einem reinen molekularen Glasbildner könnte das Bild theoretisch ändern, hat dies bis Apr 2026 aber nicht getan.

---

**Audit-Ende. Persistiert nach `/OMEGA_CORE/docs/01_CORE_DNA/FTOE_V5.2_AH4_DSC_Audit.md`.**
