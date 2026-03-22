# Science Council (Rat der Titanen) in Google Colab

**Ziel:** Auf einer **GPU-Laufzeit** (empfohlen **T4**, 16 GB VRAM) **Ollama** starten und `run_omega_science_council_r2.py` ausführen — gleiche Logik wie auf dem Dreadnought, nur in der Cloud.

**Voraussetzung:** Neues Notebook, **Laufzeit → Laufzeittyp ändern → Hardwarebeschleuniger: T4 GPU → Speichern**.

---

## 1. GPU prüfen

```python
!nvidia-smi
```

Wenn keine GPU erscheint: Laufzeit neu starten oder später noch einmal versuchen (Free-Tier).

---

## 2. Ollama installieren

```bash
!apt-get update && apt-get install -y zstd
!curl -fsSL https://ollama.com/install.sh | sh
```

---

## 3. Ollama-Server im Hintergrund starten

Nach **Neustart der Laufzeit** oder wenn Port belegt: Zelle erneut ausführen.

```python
import subprocess
import time

subprocess.run(["pkill", "-f", "ollama"], capture_output=True)  # noqa: S603
time.sleep(1)
subprocess.Popen(  # noqa: S603
    ["ollama", "serve"],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
    start_new_session=True,
)
time.sleep(8)
print("Ollama sollte auf 127.0.0.1:11434 lauschen.")
```

---

## 4. Modell ziehen (einmal pro Laufzeit, ~9 GiB bei 14B)

```bash
!ollama pull qwen2.5:14b
```

Bei VRAM-Problemen später: `qwen2.5:7b` und `OMEGA_COUNCIL_NUM_CTX` anpassen.

---

## 5. Repo einbinden

**Variante A — öffentliches Git (Standard-Remote laut CORE):**

```bash
%cd /content
!rm -rf OMEGA_CORE
!git clone https://github.com/Crow11111/CORE.git OMEGA_CORE
%cd OMEGA_CORE
```

---

## 6. Python-Abhängigkeit

```bash
%cd /content/OMEGA_CORE
!pip install -q httpx
```

---

## 7. Rat ausführen (Runde 2 → `reviews_2/`)

```python
import os
import subprocess

root = "/content/OMEGA_CORE"
os.chdir(root)

env = os.environ.copy()
env["OLLAMA_LOCAL_HOST"] = "http://127.0.0.1:11434"
env["OMEGA_COUNCIL_MODEL"] = "qwen2.5:14b"
env["OMEGA_COUNCIL_NUM_CTX"] = "65536"  # bei OOM: 32768

subprocess.run(
    ["python3", "src/scripts/run_omega_science_council_r2.py", "--force"],
    env=env,
    cwd=root,
    check=False,
)
```

---

## 8. Ergebnisse sichern

```python
from google.colab import files
!cd /content/OMEGA_CORE && zip -r reviews_2.zip docs/01_CORE_DNA/5d/WHITEPAPER/reviews_2/
files.download("/content/OMEGA_CORE/reviews_2.zip")
```
