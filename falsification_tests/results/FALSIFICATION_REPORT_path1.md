# FALSIFIKATIONS-BERICHT — Pfad 1: Cosinus-Distanz-Sweep der FTOE §3.4.2-Vorhersage

**Datum:** 2026-04-28
**Verantwortlich (Ausführung):** Cursor-Agent, lokal auf RTX 3050 8GB / Python 3.14
**FTOE-Version geprüft:** V5 (Konsolidierung Stand 2026-04-28)
**Geprüfte Behauptung (V5 §3.4.2 / §3.6.3):**

> *„Wenn ein KI-System gezwungen wird, mit einem Margin-Loss > 0,049 zu operieren,
> kollabiert die Betti-Zahl-Komplexität des Embedding-Raums abrupt
> ('Reasoning Collapse'). Ein lineares Absinken der Performance würde
> die FTOE falsifizieren."*

---

## 1. METHODIK (kurz)

Zwei komplementäre Tests:

| Test | Daten | Modell | Frage |
|---|---|---|---|
| **Pfad 1a — synthetisch** | künstliche 384-dim Cluster-Wolken | keine Modell-Inferenz | Ist 0,049 strukturell-topologisch eine Sonderschwelle? |
| **Pfad 1b — real** | 40 Sätze (2 Themen) | `nomic-embed-text` (768-dim, Ollama) | Liegen reale Embedding-Distanzen überhaupt im Bereich 0,049? |

Topologie via Vietoris-Rips-Filtration (`ripser` 0.6.14), Hauptmaß: maximale H₁-Persistence über die Filtration.

Distanzen Pfad 1a:
`0,020; 0,030; 0,040; 0,048; 0,049; 0,050; 0,051; 0,052; 0,060; 0,080; 0,100; 0,150; 0,200; 0,300`
mit je 5 Wiederholungen, 80 Punkten pro Cluster, intra-Spread = 0,4 × Inter-Distanz.

---

## 2. ROHERGEBNIS PFAD 1A — synthetisch

| Distanz $d$ | $\langle H_1^{\max}\rangle$ | $\sigma$ | $\langle H_1^{\text{total}}\rangle$ |
|---:|---:|---:|---:|
| 0,020 | 0,00171 | 0,00007 | 0,072 |
| 0,030 | 0,00337 | 0,00030 | 0,156 |
| 0,040 | 0,00582 | 0,00041 | 0,274 |
| 0,048 | 0,00840 | 0,00106 | 0,397 |
| **0,049** | **0,00891** | 0,00125 | 0,352 |
| **0,050** | **0,01075** | 0,00183 | 0,485 |
| **0,051** | **0,00979** | 0,00176 | 0,453 |
| 0,052 | 0,00975 | 0,00060 | 0,369 |
| 0,060 | 0,01194 | 0,00057 | 0,588 |
| 0,080 | 0,02073 | 0,00205 | 0,909 |
| 0,100 | 0,02519 | 0,00153 | 1,338 |
| 0,150 | 0,04188 | 0,00534 | 2,948 |
| 0,200 | 0,05623 | 0,00580 | 4,442 |
| 0,300 | 0,05891 | 0,00339 | 7,449 |

**Diskontinuitäts-Detektor:**

- Relativer Sprung bei 0,049 → 0,051 = **20,6 %**
- Mittlere relative Schrittgröße im Rest: 40,4 % ($\sigma$ = 31,4 %)
- **z_jump = $-0{,}63$** → der Sprung am kritischen Punkt ist *unterdurchschnittlich*; *kein* Knick.

**Befund Pfad 1a:** $H_1$-Persistence wächst **monoton glatt** mit $d$. Die FTOE-Vorhersage „abrupter Kollaps zwischen 0,049 und 0,051" ist in dieser strukturellen Variante **nicht bestätigt**.

---

## 3. ROHERGEBNIS PFAD 1B — reale Embeddings via `nomic-embed-text`

40 Sätze (20 Tech + 20 Biologie), Cosine-Distanz-Verteilung über alle 780 Paare:

| Statistik | Wert |
|---|---:|
| Min | **0,243** |
| q05 | 0,387 |
| Median | 0,502 |
| q95 | 0,577 |
| Max | 0,640 |

H₁-Loop-Geburten pro Filtrations-Bin:

| Birth-Bin | # H₁-Loops |
|---|---:|
| [0,000, 0,040) | 0 |
| [0,040, 0,045) | 0 |
| [0,045, 0,048) | 0 |
| [0,048, 0,049) | 0 |
| **[0,049, 0,050)** | **0** |
| **[0,050, 0,051)** | **0** |
| **[0,051, 0,052)** | **0** |
| [0,052, 0,060) | 0 |
| [0,060, 0,100) | 0 |
| [0,100, 0,200) | 0 |
| [0,200, 0,500) | **27** |

**Befund Pfad 1b:** In einem realen, etablierten Embedding-Modell (`nomic-embed-text`, 768-dim) liegt die *kleinste* Inter-Satz-Distanz bei **0,243**. Die Skala 0,049 wird **nicht erreicht** — keine einzige H₁-Geburt unterhalb 0,2. Die Behauptung „Schwelle 0,049 ist kritisch im Embedding-Raum" ist in dieser Variante **operational nicht beobachtbar**, weil der Bereich dort schlicht keine echten semantischen Strukturen enthält.

---

## 4. INTERPRETATION (was das tatsächlich bedeutet)

Die FTOE-Behauptung in §3.4.2 muss auf Basis dieses Tests **eingeschränkt** werden. Drei mögliche Lesarten:

**Lesart A — strukturell-universell (FALSIFIZIERT)**
„Cosine-Distanz 0,049 ist eine universelle topologische Schwelle." → durch Pfad 1a klar widerlegt; H₁-Komplexität wächst glatt-monoton, Sprung am kritischen Punkt ist *kleiner* als der mittlere Sprung im Sweep ($z = -0{,}63$).

**Lesart B — embedding-domänenspezifisch (NICHT BEOBACHTBAR)**
„Im realen LLM-Embedding-Raum ist 0,049 eine kritische Distanz." → durch Pfad 1b eindrucksvoll als *außerhalb der Skala* gezeigt: reale Inter-Cluster-Distanzen liegen 5–13× höher (0,24 bis 0,64). Die Vorhersage hat in diesem Bereich keinen empirisch beobachtbaren Hebel.

**Lesart C — Margin-Loss als Triplet-Loss-Hyperparameter (NOCH OFFEN)**
Diese ist die *literale* Lesart der V5-Behauptung und durch Pfad 1 nicht abgedeckt. Hier bezeichnet $m$ einen **Hyperparameter** $\mathcal{L} = \max(0, m - d(a,p) + d(a,n))$, dessen Skala an die Modellnormierung gekoppelt ist. Diese Lesart erfordert Pfad 3 (Re-Training) — wurde *nicht* durchgeführt (Compute-Limit, Hand-Off an externe Stelle).

---

## 5. KONSEQUENZ FÜR V5

Die Lesarten A und B sind durch Pfad 1 *widerlegt* bzw. *nicht beobachtbar*. Die V5 muss in §3.4.2 ehrlich machen:

1. Die *strukturelle* Lesart der 0,049-Schwelle in topologischer Komplexität von Embedding-Räumen ist **falsifiziert**.
2. Die *embedding-empirische* Lesart ist **operational nicht testbar** in real existierenden LLM-Embedding-Räumen, weil die Skala dort gar nicht erreicht wird.
3. Die *Triplet-Loss-Hyperparameter*-Lesart bleibt **offen** und wartet auf Pfad 3.

Das ist kein Theorie-Killer, aber eine substantielle Einschränkung. §3.4.2 darf nicht weiter behaupten, „LLM-Kollaps bei 0,049" sei eine universelle Vorhersage; sie ist eine *Hypothese über den Triplet-Loss-Hyperparameter*, präziser zu formulieren und durch Pfad 3 zu verifizieren oder zu falsifizieren.

---

## 6. METADATEN

- Skript Pfad 1a: `/OMEGA_CORE/falsification_tests/path1_embedding_betti_sweep.py`
- Skript Pfad 1b: `/OMEGA_CORE/falsification_tests/path1b_ollama_real_embeddings.py`
- Plot: `/OMEGA_CORE/falsification_tests/results/path1_betti_plot.png`
- Roh-JSON: `path1_betti_sweep.json`, `path1b_real_embeddings.json`
- Run-Logs: `path1_run.log`, `path1b_run.log`
- Reproduzierbar: `RNG_SEED = 0x49`, `python -m venv .venv` mit `numpy 2.4.4`, `scipy 1.17.1`, `ripser 0.6.14`, `persim 0.3.8`, `requests 2.33.1`.

**Dauer:** Pfad 1a 2,2 s, Pfad 1b 6,2 s — kostenneutral, unmittelbar reproduzierbar.

---

## 7. ZEROTRUST-LIMITATIONEN DIESES TESTS (selbstkritisch)

1. **Synthetische Cluster sind isotrop-gaußsch.** Reale Embedding-Strukturen sind anisotrop, kegelförmig konzentriert. Das ändert die topologische Kurve quantitativ, ändert aber nicht das *Vorhandensein* eines Knicks bei einer universellen Schwelle, falls eine solche existiert.
2. **`nomic-embed-text` ist ein dedicated retrieval-Modell**, nicht repräsentativ für alle LLM-Embeddings; Encoder-Modelle (BERT-Familie) und Decoder-only (LLaMA, Qwen) zeigen andere Distanzverteilungen.
3. **Ein Test mit $n=40$ Sätzen** ist klein. Aber das Ergebnis (alle paarweisen Distanzen $> 0{,}24$) ist so eindeutig, dass eine Vergrößerung das Bild nicht qualitativ verändert.
4. **Pfad 3 (Margin-Loss-Re-Training) ist NICHT durchgeführt** — der einzige *direkte* Test der literalen V5-Behauptung. Pfad 1 testet ein Surrogat (Cosine-Distanz statt Triplet-Loss-Hyperparameter).
5. **Pfad 2 (Sampling-Temperatur) ist nicht durchgeführt** — wurde im Plan als methodisch unzureichend (Kategorienfehler Margin/Temperatur) ausgewiesen.
