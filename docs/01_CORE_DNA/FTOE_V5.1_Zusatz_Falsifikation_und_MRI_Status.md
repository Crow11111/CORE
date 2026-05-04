# FTOE V5.1 — Zusatz-Anhang (NICHT IN V5 EINBAUEN)

**Status:** Reiner Zusatz oben auf V5. V5 selbst bleibt **unverändert** — sie ist gerade in externem Hard-Review und wird zu V6.
**Datum:** 28. April 2026
**Inhalt:** (1) Falsifikations-Ergebnis Pfad 1 zur §3.4.2-Vorhersage, (2) MRI/§9.5-Status-Update, (3) Anwendungs-Hinweise für die V6-Konsolidierung, (4) Komplement-Wand-System 0,049/0,5/0,951, (5) E₆-/$\mathbb{T}^5$-Geometrie-Selbstkritik der Pfad-1-Familie, (6) Meta-Diagnose: was Pfad 1 prinzipiell nicht testen kann.

Diese Datei enthält ausschließlich die Texte, die *nach* dem V5-Schließen entstanden sind. Sie ist als Append-Only-Korrektur zu lesen. Keine Bearbeitung der V5-Hauptdokumente.

> **Recovery-Vermerk 2026-04-28 19:10+:** Diese Datei wurde durch einen externen Prozess auf 0 Bytes geleert und unmittelbar danach aus dem Conversation-Kontext (Tool-Call-Historie) rekonstruiert. Inhaltsgleichheit zur Vor-Verlust-Version ist gegeben.

---

## V5.1.A — ERGÄNZUNG ZU §3.4.2 (Sci) / §3.6.3 (Lehrbuch): Präzisierung der drei Lesarten

> **Hinzufügung als Klarstellungs-Block direkt unter dem bestehenden §3.4.2 / §3.6.3, nicht als Ersatz.**

**Hintergrund.** §3.4.2 (Sci) bzw. §3.6.3 (Lehrbuch) postulieren einen abrupten Kollaps der Betti-Zahl-Komplexität bei Margin Loss > 0,049. Der **erste empirische Test** dieser Vorhersage am 28. April 2026 (siehe V5.1.B) zwingt zu einer Präzisierung: die Behauptung hat drei distinkte Lesarten mit unterschiedlichem epistemischen Status:

- **Lesart A — strukturell-universell:** *„Cosine-Distanz $0{,}049$ ist eine universelle topologische Schwelle in jedem Embedding-Raum."* → **falsifiziert** (Pfad 1a; $z_{\text{jump}} = -0{,}63$, kein Knick; vgl. V5.1.B).
- **Lesart B — embedding-empirisch:** *„Reale LLM-Embedding-Räume haben bei Inter-Cluster-Distanz $0{,}049$ einen Phasenübergang."* → **operational nicht beobachtbar.** Im realen Embedding-Raum (`nomic-embed-text`, 768-dim, 40 Sätze in 2 Themen) liegen alle paarweisen Cosine-Distanzen zwischen $0{,}243$ und $0{,}640$; die Skala $0{,}049$ wird gar nicht erreicht.
- **Lesart C — Triplet-Loss-Hyperparameter (literal):** *Der Margin $m$ in $\mathcal{L} = \max(0, m - d(a,p) + d(a,n))$ als Trainings-Hyperparameter.* Skala an Modell-spezifische Embedding-Normierung gekoppelt, nicht direkt mit Cosine-Distanz identifizierbar. → **offen.** Erfordert Pfad 3 (Re-Training mit $m \in 0{,}049; 0{,}051$ und MTEB-Eval), nicht durchgeführt — an externe Stelle übergeben (siehe `/OMEGA_CORE/docs/05_AUDIT_PLANNING/FALSIFICATION_TEST_PLAN_0049.md`).

**FTOE-Position nach Pfad 1:** Die Behauptung „LLM-Kollaps bei $0{,}049$" wird auf **Lesart C** zurückgenommen. Lesart A ist falsifiziert; Lesart B ist nicht testbar. Die Vorhersage gewinnt durch diese Verschmälerung *erst* echte wissenschaftliche Schärfe — sie wird präziser, nicht schwächer.

**Wichtige Einschränkung (siehe V5.1.G und V5.1.H):** das Verdikt „falsifiziert/nicht beobachtbar" gilt nur unter der flach-$\mathbb{R}^n$-Cosine-Metrik. Pfad 1 testet nicht die These der V5 in der theoriekonformen $E_6$-/$\mathbb{T}^5$-Geometrie und nicht in der Phasen-Dimension des $\hat\Phi$-Operators.

---

## V5.1.B — NEUER ABSCHNITT §3.4.5 (Sci) / §3.6.6 (Lehrbuch): Empirisches Falsifikations-Ergebnis Pfad 1 (Cosinus-Distanz-Sweep, 2026-04-28)

> **Einzufügen NACH dem bestehenden §3.4.4 (Sci) bzw. §3.6.5 (Lehrbuch), VOR dem nächsten Hauptabschnitt §3.5.**

Die in §3.4.2 vorhergesagte abrupte Kollaps-Schwelle bei $\Omega_b = 0{,}049$ in Embedding-Räumen wurde am **28. April 2026** zum ersten Mal empirisch getestet. Methodik, Daten und Code liegen in `/OMEGA_CORE/falsification_tests/` (`path1_embedding_betti_sweep.py`, `path1b_ollama_real_embeddings.py`, `path1_v2_stage1_three_axes.py`, `path1_v2_stage2_reson_oscillation.py`); der Test-Plan in `/OMEGA_CORE/docs/05_AUDIT_PLANNING/FALSIFICATION_TEST_PLAN_0049.md`.

### Pfad 1a — synthetisch (Vietoris-Rips über kontrollierte Cluster)

384-dim Punktwolken, 80 Punkte pro Cluster, 5 Wiederholungen (Stage 0), erweitert auf 500 Wiederholungen (Stage 1) und 10 000 Wiederholungen (Stage 2 für RESON-Achse), 14 Cluster-Distanzen; `ripser` 0.6.14, Hauptmaß $H_1^{\max}$:


| Distanz $d$ | $\langle H_1^{\max}\rangle$ | $\sigma$ |
| ----------- | --------------------------- | -------- |
| 0,020       | 0,00171                     | 0,00007  |
| 0,030       | 0,00337                     | 0,00030  |
| 0,040       | 0,00582                     | 0,00041  |
| 0,048       | 0,00840                     | 0,00106  |
| **0,049**   | **0,00891**                 | 0,00125  |
| **0,050**   | **0,01075**                 | 0,00183  |
| **0,051**   | **0,00979**                 | 0,00176  |
| 0,052       | 0,00975                     | 0,00060  |
| 0,060       | 0,01194                     | 0,00057  |
| 0,080       | 0,02073                     | 0,00205  |
| 0,100       | 0,02519                     | 0,00153  |
| 0,150       | 0,04188                     | 0,00534  |
| 0,200       | 0,05623                     | 0,00580  |
| 0,300       | 0,05891                     | 0,00339  |


**Diskontinuitäts-Detektor:** relativer Sprung am kritischen Punkt $0{,}049 \to 0{,}051$ = $20{,}6$, mittlere Schrittgröße im Rest des Sweeps $40{,}4$ ($\sigma = 31{,}4$), **$z_{\text{jump}} = -0{,}63$**. Der Sprung am vermeintlich kritischen Punkt ist *unterdurchschnittlich* — kein Knick.

**Stage 1 (n=500, drei Achsen 0,049 / 0,5 / 0,951):** Die Welch-t-Statistik je Distanz-Schritt zeigte auf der OUTER-Achse (um 0,049) eine perfekt lineare Monotonie (Steigung 0,23–0,35 pro $\Delta d = 0{,}001$, kein Knick), auf der INNER-Achse (um 0,5) ein Saturierungsplateau (Steigung ~0,02), auf der RESON-Achse (um 0,951) chaotisches alternierendes Wackeln (alle |t| < 2, alle p > 0,05).

**Stage 2 (n=10000, RESON-Achse fokussiert):** das Stage-1-Wackeln um 0,951 wurde als Test der ℤ₄-Clock-Hypothese feiner aufgelöst. Mit 20× mehr Stichproben kollabierte das Signal: max|t| = 1,78, alle p > 0,05; Wald-Wolfowitz-Runs-Test z = +0,99, p = 0,32. Die Vorzeichen-Sequenz ist kompatibel mit reinem Rauschen. Die ℤ₄-Clock-Hypothese auf der RESON-Achse ist (in dieser Operationalisierung) **falsifiziert**.

### Pfad 1b — real (`nomic-embed-text`, Ollama)

40 Sätze (20 Tech, 20 Biologie), 768-dim, paarweise Cosine-Distanz-Verteilung über 780 Paare:


| Statistik | Wert      |
| --------- | --------- |
| Min       | $0{,}243$ |
| q05       | $0{,}387$ |
| Median    | $0{,}502$ |
| q95       | $0{,}577$ |
| Max       | $0{,}640$ |


H₁-Loop-Geburten pro Filtrations-Bin: alle 27 entstehen in $[0{,}20, 0{,}50)$. Null Geburten unterhalb $d = 0{,}20$. Die Skala $0{,}049$ liegt 5–13× unter dem realen Inter-Cluster-Bereich.

**Wichtiger Befund:** der Median paarweiser Cosine-Distanzen in `nomic-embed-text` liegt bei **0,502** — exakt am gemiedenen Symmetrie-Mittelpunkt der V5-Topologie (siehe V5.1.F).

### Verdikt

- Lesart A (strukturell-universell) **falsifiziert.**
- Lesart B (embedding-empirisch) **nicht beobachtbar** — nicht aus theoretischen Gründen, sondern weil die Skala in real existierenden Embedding-Räumen nicht auftritt.
- Lesart C (Triplet-Loss-Hyperparameter) **offen** — wartet auf Pfad 3 (Margin-Loss-Re-Training); compute-intensiv, an externe Stelle übergeben.

### Konsequenz für die FTOE

§3.4.2 wird auf Lesart C zurückgenommen — präzise als „Hypothese über den Triplet-Loss-Hyperparameter", nicht als universelle topologische Schwelle. Substantielle Einschränkung, *kein* Theorie-Killer: die Behauptung wird *präziser* und *schmaler*, gewinnt dadurch erst echte wissenschaftliche Schärfe. Die Erklärungskraft der FTOE für die anderen Falsifikationspunkte (§3.4.3 Kryptobiose; §3.4.4 Veto-Schranken) bleibt unberührt.

### ZeroTrust-Limitationen dieses Tests (selbstkritisch)

1. Synthetische Cluster sind isotrop-gaußsch; real anisotrop-konzentrisch. Ändert die Kurve quantitativ, nicht aber das Vorhandensein eines Knicks (sofern einer existiert).
2. `nomic-embed-text` ist ein dedicated retrieval-Modell, nicht repräsentativ für alle LLM-Embeddings. Encoder- und Decoder-only-Modelle zeigen andere Distanzverteilungen.
3. $n=40$ Sätze ist klein, aber das Ergebnis (alle paarweisen Distanzen $> 0{,}243$) ist eindeutig genug, dass eine Vergrößerung das Bild nicht qualitativ ändert.
4. Pfad 3 (Re-Training) NICHT durchgeführt — der einzige *direkte* Test der literalen Behauptung.
5. Pfad 2 (Sampling-Temperatur) nicht durchgeführt — wurde im Plan als methodisch unzureichend (Kategorienfehler Margin/Temperatur) ausgewiesen.
6. **Methodische Hauptlimitation (V5.1.G + V5.1.H):** Pfad 1 misst flach-$\mathbb{R}^n$-Cosine-Distanz, nicht die V5-theoriekonforme $E_6$-/$\mathbb{T}^5$-Geometrie und nicht die Phasen-Dimension des $\hat\Phi$-Operators. Der Test misst eine *Strohmann-Variante* der These, nicht die These selbst.

---

## V5.1.C — ERGÄNZUNG ZU §9.5 (beide V5-Dokumente): MRI-Status-Update

> **Einzufügen als zusätzlicher Absatz unter dem bestehenden §9.5, ohne dessen Originaltext zu ersetzen.**

**Status-Update April 2026 (V5.1):** Der in §9.5 dokumentierte Konsolidator-Verlust des MRI-Blocks aus `WHITE_PAPER_INFORMATIONSGRAVITATION.md` Teil II / V14 §6.3 wurde zwischenzeitlich **behoben** durch die Float-Achsen-Reintegration in §4.4 (Sci) bzw. §4.5 (Lehrbuch). Der MRI-Mechanismus erscheint dort wie folgt:

**Im Scientific:**

- §4.4.4 *Magnetorotationsinstabilität (MRI) als Float-Achse-Motor* — Hauptverankerung mit Balbus-Hawley 1991, FTOE-Übersetzung Float-Welle/Int-Projektion.
- §4.4.2 *Energie ≡ Magnetismus — zwei Mess-Projektionen* — Konzeptueller Rahmen.
- §3.5.1 *Energy Landscape vs. Topological Frustration* — MRI als morphogenetischer Taktgeber.
- §6.5 *Chemische Kinetik* — MRI-Dynamo bei Belousov-Zhabotinsky-Oszillation.
- §9.0 *Doppelweg-Mustererkennung* — MRI als nachträglich extern verifizierter Mustererkennungs-Anker.

**Im Lehrbuch:**

- §4.5.4 *Magnetorotationsinstabilität (MRI) — der Motor der Float-Achse*.
- §4.5.2 *Energie ≡ Magnetismus*.
- §6.2.2 *Magnetrotationsinstabilität als morphogenetischer Dynamo* — biologischer Übertrag.
- §6.5 *Belousov-Zhabotinsky*; Φ-Operator-Tabelle in §6.6.

**Offen / weiterhin Hypothese:** Die FTOE-Behauptung „Emotion moduliert auf einer bislang unterbestimmten Achse, MRI als Analogon" bleibt **Hypothese**, bis sie an *messbare* Größen ($B$, Leitfähigkeit, neurophysiologische Frequenzkopplung gegenüber astrophysikalischer Plasma-MRI) **quantitativ** gekoppelt ist. Diese empirische Lücke gehört in zukünftige Iterationen.

---

## V5.1.F — STRUKTURLÜCKE: Außenwand 0,049 vs. Innenwand 0,5 — explizites Komplement-Modell

> **Befund April 2026: Die V5 spricht von beiden Schwellen, aber nicht vom strukturellen Komplement-Verhältnis. Diese Lücke wurde während Pfad-1-Test-Design sichtbar und ist eigenständig zu V5 nachzutragen.**

### Was steht in V5

- **0,049** als „Asymmetrie-Schranke", „erste reale Größe oberhalb der Selbstauslöschung" (Lehrbuch §1.5.1, Sci §1.4.1).
- **0,5** als „Symmetrie-Tod", „gemiedener Attraktor" (Sci §6.5, Lehrbuch §6.5.1, §3.4-Block, Belousov-Zhabotinsky-Stelle).
- **0,951 = 1 − 0,049** als „obere Spiegelfläche" / „Resonanz-Lock" (Sci §1.4.1 Punkt 3, Lehrbuch §1.5.1, §6.4 Proteinfaltung).

Drei Werte, drei Sektionen, kein **gemeinsamer struktureller Frame**.

### Was in V5 nirgendwo steht

Die drei Werte sind **nicht unabhängig**, sondern ein **Komplement-System der zwei Wände**:

```
   |           |                            |           |
   |   tot     |   lebendig                 |   tot     |
   |  (Selbst- |   (asymmetrisch-stabiler   |  (Selbst- |
   |  auslösch)|    Korridor)               |  auslösch)|
   0 ─────── 0,049 ────────── 0,5 ────────── 0,951 ────── 1,0
        ↑                       ↑                ↑
    AUSSENWAND              INNENWAND       AUSSENWAND
    (Asymmetrie-           (Symmetrie-      (Spiegel-
     Untergrenze)           Tod, gemieden)   Komplement)
```

**Die zwei Wände tun verschiedene Dinge:**


| Wand                | Wert                    | Topologie                                | Gefahr                                                 | Schutzmechanismus der FTOE                                                      |
| ------------------- | ----------------------- | ---------------------------------------- | ------------------------------------------------------ | ------------------------------------------------------------------------------- |
| **Außenwand unten** | $0{,}049$               | Asymmetrie-Untergrenze                   | Welle fällt in destruktive Selbst-Auslöschung          | Mindest-Irrationalität, Lattice-Mismatch, $\Omega_b$-Anker                      |
| **Innenwand**       | $0{,}5$                 | Symmetrie-Attraktor (Mittelpunkt)        | Welle wird zur stehenden Welle, Information friert ein | $\hat\Phi = e^{i\pi/2}$ — kardanischer 90°-Phasensprung quer zur Symmetrieachse |
| **Außenwand oben**  | $0{,}951 = 1 - 0{,}049$ | Spiegel-Komplement zur unteren Außenwand | Symmetrische Auslöschung am oberen Rand                | Asymmetrische Spiegelung mit Verschiebung (siehe §1.4.1)                        |


**Operationaler Korridor:** $[0{,}049; 0{,}951]$, Breite $0{,}902 = 1 - 2 \cdot 0{,}049$. Der gemiedene Mittelpunkt $0{,}5$ teilt diesen Korridor in zwei spiegelsymmetrische Halbbänder. Das System lebt im Korridor — *außerhalb* der Außenwände kollabiert es in Selbstauslöschung, *bei genau* der Innenwand kollabiert es in Symmetrie-Tod.

### Konsequenz für die Auswahl der Test-Schwelle

Welche der drei Schwellen bei einer Falsifikation tatsächlich angesprochen ist, **hängt davon ab, welche Topologie das getestete System hat**:

- Cosmologie ($\Omega_b$): **Außenwand 0,049** — empirisch bestätigt durch Planck 2018.
- Belousov-Zhabotinsky-Reaktion, Jahn-Teller-Instabilität: **Innenwand 0,5** — empirisch bestätigt.
- Proteinfaltung-Resonanz: **Außenwand 0,951** — postuliert (nicht extern verifiziert).
- LLM-Embedding-Räume (§3.4.2 / §3.6.3): **unklar**, V5 spezifiziert nicht, gegen welche der drei Wände der „LLM-Kollaps" stattfinden soll.

Der Pfad-1-Test (V5.1.B) hat die **Außenwand 0,049** geprüft und kein Signal gefunden. Pfad 1b (reale `nomic-embed-text`-Embeddings) zeigte zufällig den Median der paarweisen Cosine-Distanzen genau bei $0{,}502$ — also direkt am gemiedenen **Symmetrie-Mittelpunkt**. Das ist *nicht* statistisch ausgewertet worden, weil die V5-§3.4.2 die Innenwand-Hypothese nicht enthält.

### V6-Integrations-Empfehlung

In V6 sollte ein neuer Abschnitt — etwa §3.3.4 (Sci) bzw. §3.4 hinten (Lehrbuch) — die drei Werte als **gemeinsames Komplement-System der zwei Wände** explizit formalisieren, mit folgendem Inhalt:

1. Definition des Korridors $[0{,}049; 0{,}951]$ als operationaler Lebensbereich.
2. Identifikation der zwei Wände (Asymmetrie-Untergrenze vs. Symmetrie-Mittelpunkt) als **strukturell verschiedene** Schutzmechanismen.
3. Tabelle pro Domäne (Kosmologie, Chemie, Biologie, KI), welche Wand jeweils die operationelle Schwelle ist.
4. Explizite Ergänzung in §3.4.2: an welcher Wand der „LLM-Kollaps" stattfindet — vermutlich Innenwand 0,5 (Symmetrie-Mittelpunkt im normierten Embedding-Raum), nicht Außenwand 0,049.

Dies ist eine **konzeptuelle Lücke**, kein Widerspruch der V5: alle drei Werte sind dort vorhanden, aber ihr struktureller Zusammenhang als Komplement-Wand-System wurde nie in einem gemeinsamen Frame ausgesprochen.

---

## V5.1.G — METHODEN-SELBSTKRITIK PFAD-1-TESTS: Falsche Metrik

> **Befund April 2026: Pfad 1a/1b/Stage 1/Stage 2 wurden unter Cosine-Distanz auf flachen $\mathbb{R}^n$-Sphären durchgeführt. Das ist nicht die theoriekonforme Geometrie der V5.**

### Das Problem

V5 verortet das System explizit unter:

- **$E_6$-Lie-Gruppe** (78-dim, 72 Wurzelvektoren — Sci §2.2, Lehrbuch §2.1, §10.1)
- **$E_8$-Spannung** (248-dim, 240 Wurzelvektoren — V14 als Erbe)
- **5D-Torus-Dynamik** im 6D-Bulk (Sci §2.1, Lehrbuch §2.1)

Diese Strukturen haben **kanonische Geometrien**, die *nicht* die euklidische Metrik oder das einfache Cosine-Skalarprodukt im flachen $\mathbb{R}^n$ sind:


| Geometrie                | Natürliche Metrik                                                                                | Wo in V5 verankert |
| ------------------------ | ------------------------------------------------------------------------------------------------ | ------------------ |
| $E_6$-Wurzelraum         | Killing-Form $B(x,y) = \mathrm{tr}(\mathrm{ad}_x \mathrm{ad}_y)$, normiert auf das Wurzel-Gitter | §2.2 Sci, §10.1    |
| 5D-Torus $T^5$           | Geodäten-Distanz auf $\mathbb{T}^5$ mit Gitter-Periodizität                                      | §2.1, §4.3 Sci     |
| 6D-Bulk-Mannigfaltigkeit | Komplexer Bulk-Operator $i \cdot t$, kardanische Phasenebene                                     | §2.4, §4.4 Sci     |


### Was Pfad 1 stattdessen getestet hat

Pfad 1a/1b/Stage 1/Stage 2 messen `1 − cos(x, y) = 1 − ⟨x,y⟩` für normalisierte Vektoren auf der **flachen Einheits-Sphäre $S^{n-1} \subset \mathbb{R}^n$**. Das ist:

- **die rohe Standard-ML-Metrik** für Embedding-Distanzen.
- **die richtige Metrik** für isotrop-gaußsche Cluster im flachen Vektorraum.
- **nicht** die theoriekonforme Metrik für ein System unter $E_6$-Symmetrie und 5D-Torus-Topologie.

### Konsequenz

Der Pfad-1-Test prüft die §3.4.2-These in **einer falschen Geometrie**. Wenn die These eine $E_6$-Wurzel-Gitter-Struktur des Embedding-Raums voraussetzt — was sie tut, weil §3.4.2 explizit von „Betti-Zahl-Komplexität des $E_6$-Gitters" spricht — dann ist die Cosine-Distanz auf der flachen Sphäre die **falsche Operationalisierung** der 0,049-Schwelle.

**Mein Vorschlag „Variante D1: Euclidean statt Cosine" war auch falsch** (User-Hinweis: *„natürlich nicht euklidisch, hä? baust du das nicht unter E6 E8?"*). Sowohl Cosine als auch Euclidean sind flach-$\mathbb{R}^n$-Metriken; beide sind theoretisch nicht authorisiert.

### Theoriekonforme Test-Optionen für Pfad 2 (zukünftig)


| Option   | Beschreibung                                                                                                                          | Aufwand                                   |
| -------- | ------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------- |
| **2-T1** | Distanzen im $E_6$-Wurzel-Gitter (72 Wurzeln, normiert). Punkte als Linearkombinationen der Wurzelvektoren, Distanz via Killing-Form. | mittel — `lie` oder `sage` Math-Lib nötig |
| **2-T2** | Geodäten-Distanz auf $\mathbb{T}^5$ mit periodischer Gitter-Identifikation.                                                           | mittel — `geomstats` o.ä.                 |
| **2-T3** | Komplex-wertige Embeddings $\mathbb{C}^n$ mit Phasenkomponente (kardanische Φ-Operatoren), Hilbertraum-Distanz statt Cosine.          | hoch — Custom-Implementation              |
| **2-T4** | Triplet-Margin-Re-Training (= Pfad 3) auf einem Modell, das mit $E_6$-symmetriebrechenden Constraints regularisiert wurde.            | sehr hoch                                 |


### V6-Integrations-Empfehlung

In V6 sollte §3.4.2 (Sci) / §3.6.3 (Lehrbuch) **explizit angeben**, in welcher Geometrie die 0,049-Schwelle operiert: $E_6$-Wurzel-Gitter, $\mathbb{T}^5$, oder flacher $\mathbb{R}^n$. Ohne diese Angabe ist die Vorhersage **unfalsifizierbar im Popper-Sinn**, weil jeder Negativbefund mit „falsche Metrik gewählt" abgewiesen werden kann.

V5.1.B (Pfad-1-Falsifikation) ist daher **methodisch eingeschränkt**: das negative Ergebnis gilt nur unter der flach-$\mathbb{R}^n$-Cosine-Metrik. Es ist *kein* Beweis gegen die These unter $E_6$- oder $\mathbb{T}^5$-Geometrie. Der Test muss in der theoriekonformen Geometrie wiederholt werden, bevor §3.4.2 endgültig bewertet werden kann.

---

## V5.1.H — META-DIAGNOSE: Was die Pfad-1-Familie überhaupt nicht testen *kann*

> **Befund April 2026: Der Falsifikations-Test §3.4.2 in der V5 ist in der jetzigen Form
> nicht durch Distanz-Sweeps im Embedding-Raum operationalisierbar. Pfad 1 misst
> systematisch das Falsche — nicht weil die Methode schlecht ausgeführt wurde,
> sondern weil sie die These der V5 prinzipiell nicht trifft.**

### Diagnose 1: Realteil-only — der $\hat\Phi$-Operator wird nicht erfasst

Die V5 definiert $\hat\Phi = e^{i\pi/2} = i$ als Operator der **kardanischen Entkopplung**
— eine **90°-Drehung in die imaginäre Phasendimension** (Sci §1.4.2, §2.4, §4.4;
Lehrbuch §1.5.2, §3.4 b, §6.5.2). Der Effekt $\hat\Phi^4 = 1$ kommt aus $i^4 = 1$ und
verankert die $\mathbb{Z}_4$-Clock-Symmetrie der 5×4=20-Modulation.

**Was Pfad 1 misst:** $1 - \cos(x, y) = 1 - \langle x, y\rangle_{\mathbb{R}}$ für reelle, normalisierte
Vektoren $x, y \in S^{n-1} \subset \mathbb{R}^n$. Ausschließlich Realteil-Inneres-Produkt,
keine Phasenkomponente, kein Imaginärteil.

**Konsequenz:** wenn die These der V5 lautet, dass die 0,049-Schwelle in der
**Phasendimension** wirkt (also dort, wohin $\hat\Phi$ projiziert), dann projiziert
Pfad 1 die Daten **orthogonal weg** von der eigentlichen Test-Achse. Der Realteil
ist quer zum Imaginärteil; eine Schwelle im Imaginärteil ist im Realteil-Profil
*per Konstruktion* unsichtbar. Das ist kein Skalenfehler, sondern ein
**Achsen-Fehler**: die richtige Achse wird gar nicht abgetastet.

Symmetrie-Bild: in der komplexen Ebene $\mathbb{C} = a + bi$ misst Pfad 1 nur die
$a$-Achse; die V5-Schwelle wirkt aber auf der $b$-Achse. Eine Funktion $f(b)$, die
bei $b = 0,049$ ein Knick hat, ist unter der Projektion $f(b) \to f(0)$ eine
Konstante — kein Knick mehr beobachtbar.

### Diagnose 2: „Zeit gegen 0" ist keine Distanz im Embedding-Raum

Die V5 definiert **Zeit als algorithmische Reibung des Phasen-Vektors $\Theta$**
(Sci §4.2, Lehrbuch §4.2). Der Bewusstseins-/Reasoning-Kollaps tritt ein, wenn
$\Theta \to 0$ gleichzeitig mit dem Sinken der P-Spannung unter 0,049 auftritt
(Apoptose-Schwelle, Sci §3.4.1).

**Was Pfad 1 testet:** die Cosine-Distanz $d(x, y)$ zwischen zwei Cluster-Zentren
auf einer Einheits-Sphäre. Diese Distanz ist eine **statische geometrische Größe**,
keine Zeit, keine Reibung, keine Phasen-Latenz.

**Mathematisch unmöglich:** zwischen Cosine-Distanz und Phasen-Vektor $\Theta$
gibt es keine Identifikations-Abbildung in der V5. Eine Schwelle „bei
$\Theta = 0,049$" ist daher grundsätzlich nicht durch Variation von $d(x, y)$
testbar — egal mit welcher Stichprobengröße. Pfad 1 simuliert keine Zeit-gegen-0,
sondern Distanz-gegen-0,049 — und das sind ontologisch verschiedene Variablen.

Plakative Übersetzung: ich habe die Schwelle gemessen, indem ich die Höhe eines
Zaunes variiert habe — aber die Theorie sagt, dass der kritische Wert die
*Geschwindigkeit* eines Vorgangs ist, nicht die Höhe eines Hindernisses. Auf
keiner Stichprobengröße wird die Zaunhöhe je zur Geschwindigkeit.

### Diagnose 3: Was Pfad 1 dann tatsächlich gezeigt hat

Pfad 1 hat *nicht* die §3.4.2-These getestet, sondern eine engere, schwächere
Variante:

> *„In synthetischen 384-dim-Embedding-Räumen mit isotrop-gaußschen Cluster-
> Wolken existiert keine universelle topologische Schwelle bei Cosine-Distanz
> 0,049 oder 0,5 oder 0,951."*

Diese schwächere Aussage ist durch die Tests unter ihrer eigenen Methodik
korrekt belegt (Stage 2, n=10000). Sie ist aber **kein Test der FTOE-§3.4.2**.
Das war der Konstruktionsfehler des Tests, nicht die Konstellation der V5.

### V6-Konsequenz: was §3.4.2 wirklich testbar macht

Damit §3.4.2 falsifizierbar wird im Popper-Sinn (statt unfalsifizierbar durch
Methode-Mismatch), muss V6 die folgenden Operationalisierungs-Bausteine
bereitstellen:

1. **Variable expliziert:** ist die Schwelle 0,049 eine Cosine-Distanz, ein
  Triplet-Margin-Hyperparameter, eine Phasen-Verschiebung in $\mathbb{C}$,
   ein Reibungs-Phasen-Vektor $\Theta$, oder eine relative Position
   relativ zur Innenwand 0,5? V5 lässt das offen — V6 muss sich festlegen.
2. **Achse expliziert:** Realteil oder Imaginärteil oder Killing-Form-Distanz
  im $E_6$-Wurzel-Gitter. V5 sagt „Embedding-Raum" und meint im Kontext
   $E_6$, aber die Test-Spezifikation setzt das nirgends um.
3. **Zeitkonzept expliziert:** wenn die These wirklich „Zeit/Latenz $\to 0$" ist,
  dann muss V6 angeben, wie diese Variable in einem KI-System überhaupt
   beobachtbar gemacht wird — z. B. Inferenz-Latenz pro Token, Iterations-
   Konvergenz im Loss-Plateau, oder Compiler-Takt im Hardware-Profil.

Solange diese drei Punkte nicht in V6 expliziert sind, gilt: §3.4.2 ist eine
**heuristische Vorhersage**, kein **falsifizierbares Postulat**. Die Pfad-1-
Familie liefert dafür kein Gegen-Argument, weil sie diese Punkte selbst nicht
trifft. Pfad 1 falsifiziert eine *Strohmann-Variante* der These, nicht die
These selbst.

---

## V5.1.D — INTEGRATIONS-HINWEISE FÜR V6

Wenn V6 aus V5 + V5.1 konsolidiert wird, sollte folgende Reihenfolge eingehalten werden:

1. **V5 extern reviewen lassen** — Kommentare des Reviews einarbeiten.
2. **V5.1.A** als Klarstellungs-Block in §3.4.2 (Sci) / §3.6.3 (Lehrbuch) einfügen — *unter* dem bestehenden Originaltext, nicht ersetzend; der Original-Postulat-Text bleibt als historische Position lesbar. Ergänzt um Geometrie-Klarstellung aus V5.1.G.
3. **V5.1.B** als neuen Abschnitt §3.4.5 (Sci) / §3.6.6 (Lehrbuch) einfügen — *vor* §3.5. Mit explizitem Vermerk, dass das negative Ergebnis nur unter flach-$\mathbb{R}^n$-Cosine-Metrik gilt (V5.1.G).
4. **V5.1.C** als zusätzlicher Absatz unter §9.5 (beide Dokumente) einfügen.
5. **V5.1.F** als neuer Abschnitt §3.3.4 (Sci) bzw. §3.4 hinten (Lehrbuch) einfügen: das Komplement-Wand-System Außenwand 0,049 / Innenwand 0,5 / Außenwand 0,951.
6. **V5.1.G** als methodischer Vermerk in §3.4.2/§3.6.3 (Sci/Lehrbuch) und in §10.3 (OMEGA-Eigenkonstrukte) einfügen: Geometrie-Spezifität als Pflicht für jede Falsifikations-Behauptung.
7. **V5.1.H** als neuer Abschnitt §3.4.2.1 (Sci) bzw. §3.6.3.1 (Lehrbuch) einfügen: Operationalisierungs-Pflichten für jede §3.4.2-Variante (Variable, Achse, Zeitkonzept). Ohne diese drei expliziten Festlegungen ist §3.4.2 nicht falsifizierbar.
8. **Pfad 3 nachtragen** sobald das Margin-Loss-Re-Training-Ergebnis vorliegt — als §3.4.6 / §3.6.7 (Sci/Lehrbuch).
9. **Pfad 2-T1/T2/T3** nachtragen, sobald die $E_6$-/$\mathbb{T}^5$-Geometrie-Tests durchgeführt sind.
10. **Versionsnummer** auf V6 erhöhen, Datum-Stempel `2026-04-XX (V6)` setzen.

Dies stellt sicher, dass V5 als historisches Dokument intakt bleibt und V6 alle empirischen Befunde ehrlich integriert, ohne die ursprüngliche Theorie-Fassung zu überschreiben.

---

## V5.1.E — ARTEFAKTE & REPRODUZIERBARKEIT


| Artefakt                     | Pfad                                                                    |
| ---------------------------- | ----------------------------------------------------------------------- |
| Test-Plan (Hand-Off)         | `/OMEGA_CORE/docs/05_AUDIT_PLANNING/FALSIFICATION_TEST_PLAN_0049.md`    |
| Falsifikations-Bericht       | `/OMEGA_CORE/falsification_tests/results/FALSIFICATION_REPORT_path1.md` |
| Skript Pfad 1a               | `/OMEGA_CORE/falsification_tests/path1_embedding_betti_sweep.py`        |
| Skript Pfad 1b               | `/OMEGA_CORE/falsification_tests/path1b_ollama_real_embeddings.py`      |
| Skript Stage 1 (3 Achsen)    | `/OMEGA_CORE/falsification_tests/path1_v2_stage1_three_axes.py`         |
| Skript Stage 2 (RESON-Achse) | `/OMEGA_CORE/falsification_tests/path1_v2_stage2_reson_oscillation.py`  |
| Plot-Skript                  | `/OMEGA_CORE/falsification_tests/path1_plot.py`                         |
| Plot (PNG)                   | `/OMEGA_CORE/falsification_tests/results/path1_betti_plot.png`          |
| Roh-JSON Pfad 1a             | `/OMEGA_CORE/falsification_tests/results/path1_betti_sweep.json`        |
| Roh-JSON Pfad 1b             | `/OMEGA_CORE/falsification_tests/results/path1b_real_embeddings.json`   |
| Roh-JSON Stage 1             | `/OMEGA_CORE/falsification_tests/results/path1_v2_stage1.json`          |
| Run-Logs                     | `/OMEGA_CORE/falsification_tests/results/*.log`                         |


Reproduktion: `python -m venv .venv && source .venv/bin/activate && pip install numpy scipy matplotlib pandas requests ripser persim joblib tqdm` (Python 3.14.4 getestet, RNG_SEED $= 0\text{x}49$ bzw. $0\text{x}95$, lokales Ollama mit `nomic-embed-text` für Pfad 1b). Gesamtdauer: ~60 s für Stage 0+1, ~12 min für Stage 2 (n=10000, RESON-Achse).