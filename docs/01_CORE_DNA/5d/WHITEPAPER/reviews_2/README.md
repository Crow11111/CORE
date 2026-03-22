# Rat der Titanen — Runde 2 (`reviews_2`)

## Vorgelegtes Dokument

[`../Whitepaper_Informationsgrafitation ausformuliert.md`](../Whitepaper_Informationsgrafitation%20ausformuliert.md)

## Ausführung (lokal — wie Runde 1)

Die Gutachten werden **nicht** von einer Cloud-KI erzeugt, sondern von **Ollama** auf dem Rechner, mit demselben Setup wie `src/scripts/run_omega_science_council.py`:

| Parameter | Standard |
|-----------|----------|
| API | `OLLAMA_LOCAL_HOST` → `http://127.0.0.1:11434` |
| Modell | `OMEGA_COUNCIL_MODEL` → `qwen2.5:14b` |
| Temperatur | `0.2` |
| Streaming | an |
| Kontext | `OMEGA_COUNCIL_NUM_CTX` (Default **65536**; bei VRAM-Engpass z. B. `32768` setzen). Zu klein → Text wird abgeschnitten → eher **Zusammenfassungs-Modus**. |
| Profile | `src/scripts/omega_science_council_profiles.py` — pro Titan **Profil** + **Kern-Anker** (Formel/Prinzip aus deren Werk); Prompt verlangt expliziten Vergleich mit dem Whitepaper. |

### Quantisiertes Modell mit großem Kontext (Ollama)

- **Standard-Pull:** `ollama pull qwen2.5:14b` — das ist bereits die **Q4_K_M**-Variante (ca. 9 GiB Download; Richtwert **VRAM** mit 64k Kontext oft **12–16 GB+**, je nach Batch/Overhead). Kein separates „Quant“-Tag nötig.
- **Mehr Kontext:** Qwen2.5-14B-Instruct unterstützt architektonisch bis ca. **128 k** Tokens; `OMEGA_COUNCIL_NUM_CTX=131072` ist möglich, wenn der GPU-Speicher reicht — sonsten **OOM** oder Swap-Thrashing.
- **Weniger VRAM, gleicher Code:** `OMEGA_COUNCIL_MODEL=qwen2.5:7b` und `OMEGA_COUNCIL_NUM_CTX=32768` oder `65536` (7B ist leichter, Qualität für tiefe Gutachten etwas geringer).
- **Maximale Qualität (teuer):** `qwen2.5:14b-instruct-fp16` — nur sinnvoll mit sehr viel VRAM; für den Rat meist **nicht** nötig.
- **Alternative mit langem Kontext:** z. B. `llama3.1:8b` (in Ollama oft mit großem Kontextfenster gelistet) — dann `OMEGA_COUNCIL_MODEL` entsprechend setzen und `num_ctx` an die Modellkarte anpassen.

**Faustregel:** Kontextlänge linear im **KV-Cache** — lieber **kleineres Modell** oder **kürzeres `num_ctx`** als FP16, wenn es knirscht.

**~8 GB VRAM (z. B. ASUS RTX 3050 8 GB, Gigabyte-Board):** Die **14B**-Q4-Weights liegen schon bei ca. **9 GiB** — auf **8 GB** oft **GPU-OOM** oder starkes **CPU-Offloading** (sehr langsam). Für den Science Council hier sinnvoller:

1. `OMEGA_COUNCIL_MODEL=qwen2.5:7b` — `ollama pull qwen2.5:7b`
2. `OMEGA_COUNCIL_NUM_CTX` zuerst **16384** oder **32768** testen; wenn stabil, vorsichtig **49152** — **65536** nur wenn `nvidia-smi` unter Last noch Luft hat.
3. **3050 Laptop** mit **4 GB / 6 GB:** noch enger → eher **8192–16384** und ggf. kleineres Modell (z. B. `qwen2.5:3b` oder `llama3.2:3b`) nur für Experimente; Qualität der Gutachten sinkt.

### Google Colab — ja, als Option (mit Einschränkungen)

**Wann sinnvoll:** Wenn Du **mehr VRAM** willst als die **RTX 3050 8 GB** bietet — z. B. **T4 mit 16 GB** (häufig bei GPU-Laufzeit in Colab) reicht für **`qwen2.5:14b`** + **deutlich höheres `num_ctx`** oft besser als die lokale 8 GB-Karte.

**Free-Tier-Realität (wie in der Ressourcen-Anzeige):** **Kein Abo** → **GPU oft nicht verfügbar** oder nur begrenzt; Sessions **disconnecten** nach Idle, **Laufzeitlimits**, kein Dauerbetrieb. Für „mal einen Rat-Lauf“ ok, für verlässlichen Workflow eher **lokal** oder **Colab Pro** (bzw. eigenes VPS mit Ollama, siehe `docs/03_INFRASTRUCTURE/VPS_OLLAMA_SETUP.md`).

**Ablauf-Kern (gleiches Skript):** Repo/Whitepaper ins Colab bringen (Git clone oder Upload) → **Ollama für Linux** installieren, `ollama serve` im Hintergrund → `OLLAMA_LOCAL_HOST=http://127.0.0.1:11434`, Modell ziehen, dann wie lokal `run_omega_science_council*.py` ausführen → erzeugte `reviews_2/*.md` **herunterladen** oder ins Repo committen (Colab ist **kein** Ersatz für den integrierten Dreadnought-Daemon, nur **Batch-GPU**).

**„Großer Rat“ (viele Titanen):** Die Gutachten laufen **sequentiell** — **eine** Chat-Anfrage pro Titan nacheinander (siehe `run_omega_science_council.py`). Es gibt **keinen** parallelen 10×-VRAM-Bedarf: immer nur **ein** Durchlauf mit vollem Whitepaper und `num_ctx`. **Eine Colab-T4 (16 GB)** reicht daher typischerweise für **`qwen2.5:14b`** + **`OMEGA_COUNCIL_NUM_CTX=65536`** (oder testweise höher), bis alle Dateien durch sind. **Laufzeit → Laufzeittyp ändern → T4 GPU** speichern — genau die Stufe vor den gesperrten Premium-GPUs (H100, A100, …).

**Hinweis (Qualität):** Wenn Gutachten wie „Schlüsselpunkte“, „Dein Dokumentationsmaterial…“ oder **MRI = Medizin** klingen, war oft **zu wenig Kontext** oder das Modell ignorierte die Rolle. Im Skript sind **strengere Regeln** und die **MRI-Definition** nachgerüstet — betroffene Dateien mit `--force` neu erzeugen.

**Vom Repo-Root `/OMEGA_CORE`:**

```bash
# Python-Umgebung mit httpx (z. B. .venv aus requirements.txt)
.venv/bin/python src/scripts/run_omega_science_council_r2.py
```

### Google Colab Integration

- **Notebook:** [`science_council_colab.ipynb`](science_council_colab.ipynb) — Direkt in Cursor öffnen und mit Colab-Kernel verbinden.
- **Guide:** [`COLAB_SCIENCE_COUNCIL.md`](COLAB_SCIENCE_COUNCIL.md) — Detaillierte Anleitung.

Bereits vorhandene `*.md`-Gutachten werden **übersprungen** (Resume). Alle neu erzwingen:

```bash
python3 src/scripts/run_omega_science_council_r2.py --force
```

**Allgemeiner Aufruf** (andere Datei / anderer Ordner):

```bash
python3 src/scripts/run_omega_science_council.py \
  --paper "docs/01_CORE_DNA/5d/WHITEPAPER/Whitepaper_Informationsgrafitation ausformuliert.md" \
  --out "docs/01_CORE_DNA/5d/WHITEPAPER/reviews_2" \
  --title "OMEGA … Runde 2"
```

## Erste Runde (Referenz)

`docs/01_CORE_DNA/5d/Reviews/` bzw. `docs/05_AUDIT_PLANNING/OPERATION_OMEGA/REVIEWS/` — je nach damaligem Lauf; Skript-Standard für Runde 1 ist die Kurzfassung `WHITE_PAPER_INFORMATIONSGRAVITATION.md`.

## Ausgabe

Pro Titan eine Datei: `Vorname_Nachname.md` (z. B. `Roger_Penrose.md`). `README.md` wird vom Skript **nicht** überschrieben.
