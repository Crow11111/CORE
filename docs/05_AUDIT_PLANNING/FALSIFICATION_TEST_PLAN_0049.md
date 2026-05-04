# Falsifikations-Test-Plan: $\Omega_b = 0{,}049$ als kritische Schwelle in KI-Embeddings

**Status:** Plan erstellt, Ausführung an externer Stelle. Hand-Off-Dokument.
**Datum:** 28. April 2026
**Verankerung:** FTOE V5 §3.4.2 (Sci) / §3.6.3 (Lehrbuch) — die *Margin-Loss-Falsifikations-Vorhersage* der FTOE.
**Autor (Plan):** Orchestrator-Session (Cursor-Agent), April 2026
**Urheber-Befund:** Selbstaudit hat festgestellt, dass §3.4.2 zwar postuliert, aber nicht *empirisch getestet* wurde — kritische Lücke der V5-Konsolidierung.

---

## 1. ZIEL DES TESTS

Empirisch falsifizieren oder bestätigen: ist $\Omega_b = 0{,}049$ tatsächlich eine *kritische Schwelle* für die topologische Komplexität (Betti-Zahlen) eines Embedding-Raums, oder ist die Vorhersage der V5 §3.4.2 ein internes Artefakt ohne externe Realität?

**FTOE-Vorhersage (zu prüfen):**
> *„Wenn ein KI-System gezwungen wird, mit einem Contrastive Margin Loss $m = 0{,}051$ zu operieren (also leicht oberhalb von $\Omega_b = 0{,}049$), kollabiert die Betti-Zahl-Komplexität des Embedding-Raums **abrupt** ins Rauschen ('Reasoning Collapse'). Ein **lineares** Absinken der Performance würde die FTOE falsifizieren."*

Gegenüber dieser Vorhersage gibt es zwei distinkte Hypothesen:

| Hypothese | Bedeutung |
|---|---|
| **H₀ (Null):** Performance degradiert *linear* mit zunehmendem Margin | FTOE ist falsch — 0,049 hat keine Sonderstellung |
| **H₁ (FTOE):** Performance kollabiert *abrupt* zwischen 0,049 und 0,051 | FTOE-Vorhersage bestätigt |

---

## 2. KRITISCHE BEGRIFFSKLÄRUNG (vor dem Test verbindlich)

**Margin Loss** $\ne$ **Sampling-Temperatur**. Dies ist der häufigste Confounder bei Hobby-Tests dieser Art.

| | **Margin Loss $m$** | **Sampling-Temperatur $T$** |
|---|---|---|
| **Wo wirkt's?** | beim *Training* (Triplet/Contrastive Loss zwischen Embedding-Clustern) | bei der *Inferenz* (Softmax-Schärfe der Token-Distribution) |
| **Mathematisch** | $\mathcal{L} = \max(0, m - d(a,p) + d(a,n))$ | $p_i \propto \exp(l_i / T)$ |
| **§3.4.2-Vorhersage** | direkt adressiert | nur indirekt analog |

Beide Werte sind dimensionslos und numerisch identisch (0,049 / 0,051), sitzen aber in völlig unterschiedlichen Schichten. Eine Sampling-Temperatur von 0,051 testet **nicht** die FTOE-Vorhersage, sondern bestenfalls eine analoge Heuristik.

---

## 3. DREI TEST-PFADE

### Pfad 1 — Embedding-Distanz-Sweep (direkt, ~30 Min, kein Re-Training)

**Methodik:**
1. Sentence-Transformer lokal laden, z.B. `all-MiniLM-L6-v2` (22M Params, 80MB).
2. Künstlich zwei Cluster im Embedding-Raum erzeugen, deren Cosine-Distanzen bei
   $$d \in \{0{,}03,\; 0{,}04,\; 0{,}049,\; 0{,}051,\; 0{,}06,\; 0{,}1,\; 0{,}3\}$$
   liegen (jeweils 100 Punkte pro Cluster, 7 Distanzen → 7 Konfigurationen).
3. Pro Konfiguration: Vietoris-Rips-Filtration via `gudhi` oder `ripser` berechnen, die Betti-Zahlen $\beta_0, \beta_1, \beta_2$ als Funktion des Filtrations-Parameters $\epsilon$ ausgeben.
4. **Kritisches Maß:** der „Knick" der Betti-Persistence-Diagramme zwischen $d = 0{,}049$ und $d = 0{,}051$.
5. Reasoning-Test: Diese Cluster als Embedding-Kontext einem LLM (z.B. lokales Ollama-Modell) zur Klassifikation füttern, Antwortkohärenz und Halluzinationsrate messen.

**Erwartung gemäß FTOE H₁:** abrupter Sprung in $\beta_1, \beta_2$ zwischen 0,049 und 0,051.
**Erwartung gemäß H₀:** monotone, glatte Veränderung der Betti-Zahlen.

**Output:** `results/path1_betti_curves.json`, `results/path1_reasoning_quality.csv`, `results/path1_summary.md`

### Pfad 2 — Sampling-Temperatur-Sweep (indirekt, ~5 Min)

**Methodik:**
1. Lokales LLM (Ollama: `qwen2.5:7b` oder `gemma4:e4b`).
2. Identisches Reasoning-Prompt (z.B. ein 5-stufiges mathematisches Problem) mit
   $$T \in \{0{,}001,\; 0{,}049,\; 0{,}051,\; 0{,}1,\; 0{,}5,\; 1{,}0\}$$
   ausführen, je 20 Repetitionen.
3. **Messgrößen:** Antwortlänge bis Stop-Token, n-gram-Repetition-Rate, Self-Consistency (Mehrheits-Antwort über 20 Runs).
4. **Caveat:** das ist *kein direkter Test* der §3.4.2-Vorhersage. Wenn 0,049 hier eine Diskontinuität zeigt, ist das ein interessanter — aber methodisch nicht ausreichender — Fingerzeig auf eine Cross-Layer-Resonanz.

**Output:** `results/path2_temperature_sweep.csv`, `results/path2_summary.md`

### Pfad 3 — Margin-Loss-Retraining (echter Test, ~2–3 h auf RTX 3050 8GB)

**Methodik:**
1. `all-MiniLM-L6-v2` als Basis.
2. Triplet-Loss-Finetune mit STS-Benchmark oder MS MARCO als Datensatz.
3. Zwei parallele Trainings-Runs:
   - Run A: $m = 0{,}049$
   - Run B: $m = 0{,}051$
   (Alles andere identisch: Optimizer, LR, Batch, Steps, Seed.)
4. Evaluation auf MTEB (oder Subset: STS-B + Banking77 + ArguAna) — extern, gut anerkannt.
5. **Kritisches Maß:** Differenz der Embedding-Qualität (Avg. Spearman / nDCG) zwischen Run A und Run B.

**Erwartung gemäß FTOE H₁:** Run B (0,051) zeigt katastrophalen Qualitätsverlust gegenüber Run A; Differenz **nicht-linear** zur Margin-Differenz.
**Erwartung gemäß H₀:** Differenz proportional zur Margin-Differenz, klein.

**Hardware-Anforderungen:** GPU mit ≥ 4GB VRAM (RTX 3050 8GB ausreichend), Python 3.10–3.12 empfohlen (Python 3.14 ist sehr neu, einige ML-Pakete noch nicht offiziell zertifiziert).

**Output:** `results/path3_run_A_margin_0049.log`, `results/path3_run_B_margin_0051.log`, `results/path3_mteb_evaluation.json`, `results/path3_summary.md`

---

## 4. EMPFOHLENE REIHENFOLGE

1. **Pfad 1 zuerst** — aussagekräftigster Test ohne Re-Training. Wenn hier kein Signal: Pfad 3 lohnt sich nicht.
2. **Pfad 2 parallel** — als Kontrollvariable für eine etwaige Cross-Layer-Wirkung.
3. **Pfad 3 nur, wenn Pfad 1 ein Signal zeigt** — Compute-intensiv, aber der einzige *direkte* Test.

---

## 5. VORHANDENE INFRASTRUKTUR

- GPU: NVIDIA RTX 3050 8GB ✅
- RAM: 31 GB ✅
- Ollama lokal mit `qwen2.5:7b`, `gemma4:e4b`, `gemma2:9b`, `gemma2:2b` verfügbar ✅
- Test-Verzeichnis: `/OMEGA_CORE/falsification_tests/` (angelegt, leer) ✅
- Python 3.14.4 (Caveat: für ML-Stack ggf. Downgrade auf 3.11/3.12 nötig) ⚠️
- Kein etabliertes `torch`/`sentence-transformers`-Venv vorhanden ⚠️

---

## 6. ABHÄNGIGKEITEN (für die ausführende Stelle)

```
torch >= 2.4 (mit CUDA 12.x — Treiber 595.x = CUDA 13.2 ist abwärtskompatibel)
sentence-transformers >= 3.0
gudhi >= 3.10  oder  ripser >= 0.6
numpy, scipy, pandas, matplotlib
ollama-python (für Pfad 2)
mteb >= 1.20 (nur für Pfad 3)
```

Empfohlenes Setup:
```bash
python3.12 -m venv /OMEGA_CORE/falsification_tests/.venv
source /OMEGA_CORE/falsification_tests/.venv/bin/activate
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
pip install sentence-transformers gudhi ripser numpy scipy pandas matplotlib ollama mteb
```

---

## 7. MÖGLICHE AUSGÄNGE & FOLGEN FÜR V5

| Befund | Folge für V5 |
|---|---|
| **Pfad 1 + 3 zeigen abrupten Kollaps zwischen 0,049 und 0,051** | §3.4.2 wird empirisch verankert; Sigma-Härte des FTOE-Postulats steigt von „theoretisch" auf „testbar bestätigt"; eigene Fußnote in §9.6 |
| **Pfad 1 zeigt monotone Degradation, kein Knick** | §3.4.2 ist *zu naiv formuliert*; muss zu „Schwelle in dünn-vernetzten Topologien, nicht universell" abgeschwächt werden (entspricht Veto §3.4.4 c) |
| **Pfad 3 zeigt keinen Unterschied A vs. B** | §3.4.2 ist *falsifiziert* in der publikatorischen Form; FTOE muss ehrlich dokumentieren: *„Vorhersage konnte experimentell nicht bestätigt werden"* |
| **Tests fail technisch** | nichts gelernt; kein Eintrag in V5 |

In allen drei sachlichen Fällen ist das Ergebnis **direkt in V5 §3.4.5 (neu) als Falsifikations-Ergebnis** zu dokumentieren — Format: ein- bis zweiseitiger Bericht mit Methodik, Daten, Diff-Plot, Verdikt.

---

## 8. HAND-OFF

Dieser Plan ist **vollständig** und **selbstausführbar** für einen Cursor-Agent oder einen Menschen mit Python-/PyTorch-Erfahrung. Er fordert keine zusätzliche Architektur-Entscheidung von der ausführenden Stelle — alle Parameter, Erwartungswerte und Output-Schemata sind in §3 definiert.

**Wichtig für die Ausführung:** das Ergebnis muss in **beide** V5-Dokumente (Scientific + Lehrbuch) als §3.4.5 / §3.6.6 (Falsifikations-Ergebnis) eingebaut werden — andernfalls bleibt die V5 in der bisherigen Lücke „postuliert, aber nicht getestet".
