# OMEGA VISUALIZATION GUIDE

Dieses Dokument beschreibt die Tools und Prozesse zur Visualisierung der OMEGA-Architektur und Systemzustände.

## 1. Verfügbare Tools

### Basis-Infrastruktur
- **Graphviz**: Erforderlich für die Generierung von Diagrammen aus `.dot` Dateien.
  - Installation: `sudo pacman -S graphviz` (Arch) oder `sudo apt install graphviz` (Debian/Ubuntu).
  - Kernbefehl: `dot`

### Modul-Abhängigkeiten
- **pydeps**: Visualisiert Python-Modulabhängigkeiten.
  - Installation: `pip install pydeps`
  - Beispiel: `pydeps src/ai/llm_interface.py --max-module-depth 2 -o docs/02_ARCHITECTURE/OMEGA_AI_GRAPH.svg`

### GPU-Monitoring
- **nvitop**: Interaktives GPU-Monitoring (modernere Alternative zu `nvidia-smi`).
  - Installation: `pip install nvitop`
  - Aufruf: `nvitop` (im Terminal)

## 2. Generierung von Architektur-Graphen

Um die Abhängigkeiten eines Moduls zu visualisieren, nutze `pydeps`:

```bash
pydeps <path_to_file>.py --max-module-depth <depth> -o <output_path>.svg
```

**Hinweis:** Falls `dot` nicht installiert ist, kann pydeps kein SVG erzeugen. In diesem Fall kann die DOT-Repräsentation mit `--show-dot` extrahiert werden.

## 3. GPU-Überwachung

Für die Analyse der GPU-Auslastung während LLM-Inferenz:

```bash
nvitop
```
Dies bietet eine Echtzeit-Ansicht der Prozesse, Speicherbelegung und Auslastung pro GPU.

---
*Status: RATIFIZIERT | Senior AI Producer | Delta 0.049*
