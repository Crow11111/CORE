# ATLAS Ω Voice — KDE-Plasmoid (OMEGA CORE)

**Vektor:** 2210 | **Delta:** 0.049  
**Pfad im Repo:** `atlas-omega-voice/`  
**Oberfläche:** Deutsch (Standard)

---

## Zweck

Lokales **Sprach- und Chat-Plasmoid** für KDE Plasma 6, angebunden an das **OMEGA-CORE-Backend** (OpenAI-kompatible Endpunkte: `/v1/chat/completions`, TTS optional über `/v1/audio/speech`). Upstream-Basis: Jarvis (Novik), Fork und Markenführung **ATLAS** / **OMEGA**.

---

## Konfiguration (ohne Secrets im Git)

- **Server-Basis-URL:** nur Origin, z. B. `http://127.0.0.1:8000` oder die in `.env` gesetzte **`CORE_API_URL`** (wird vom Plasmoid als **Umgebungsvariable** gelesen, wenn noch kein gespeicherter Wert in QSettings existiert).
- **Plasma:** Umgebungsvariable für die Session z. B. unter `~/.config/plasma-workspace/env/atlas-omega.sh`:
  - `export CORE_API_URL=http://<CORE_HOST_IP>:<CORE_API_PORT>`  
  Werte aus lokaler `.env` übernehmen — **nicht** ins Repository schreiben.
- **QSettings-Gruppe:** `OMEGA` / `AtlasOmegaVoice` (getrennt vom Original-Jarvis).

Details zur Health-URL und Normalisierung: `JARVIS_OMEGA_LLM_VERBINDUNG.md`.

---

## Build & Installation

```bash
cd /OMEGA_CORE/atlas-omega-voice
mkdir -p build && cd build
cmake .. -DCMAKE_INSTALL_PREFIX=/usr
cmake --build . -j"$(nproc)"
sudo make install
# Plasma: plasmashell --replace &   oder neu einloggen
```

Widget in der Leiste hinzufügen (Name in Plasma: **ATLAS Ω Voice (OMEGA)**).

---

## Technischer Hinweis

Das QML-Modul heißt weiterhin `org.kde.plasma.jarvis` (Binärkompatibilität, Installationspfad). Die **sichtbare** Marke ist ATLAS; Chat-Rollen im Verlauf: `user` / `atlas` / `system`.

**Build (GCC / Qt 6):** `QStringLiteral(u8"…")` führt zu *widersprüchlichen Kodierungspräfixen* beim Verketten — im Fork wird **`QStringLiteral("…")`** mit UTF-8-Quelldateien genutzt. Signal **`availableLlmModelsChanged`** muss in `jarvissettings.h` deklariert sein, wenn `populateModelList()` es emittiert.

---

## Siehe auch

- `docs/BIBLIOTHEK_KERN_DOKUMENTE.md`  
- `docs/02_ARCHITECTURE/JARVIS_OMEGA_LLM_VERBINDUNG.md`  
- `CORE_EICHUNG.md` (Anhang A/B)

---

*Stand: 2026-03-20*
