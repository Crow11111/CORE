# ATLAS Ω Voice — KDE-Plasmoid (OMEGA CORE)

**Vektor:** 2210 | **Delta:** 0.049
**Pfad im Repo:** `atlas-omega-voice/`
**Oberfläche:** Deutsch (Standard)

---

## Zweck

Lokales **Sprach- und Chat-Plasmoid** für KDE Plasma 6, angebunden an das **OMEGA-CORE-Backend** (OpenAI-kompatible Endpunkte: `/v1/chat/completions`, TTS optional über `/v1/audio/speech`). Upstream-Basis: Jarvis (Novik), Fork und Markenführung **ATLAS** / **OMEGA**.

---

## Probleme und Lösungen (in normaler Sprache)

### 1) Im Terminal steht viel Kram mit „Plasma.Flex.Hub“ — oder altes Jarvis lokal

| Was los ist | **Plasma.Flex.Hub** ist ein **anderes** Widget (nicht unser ATLAS). **Wichtig:** Legst du es nur als `*.bak` **im selben Ordner** `~/.local/share/plasma/plasmoids/` ab, **scannt Plasma die trotzdem** (`metadata.json`) — dann kommen weiter die KPackage-Fehler. Zusätzlich bleibt oft ein Eintrag **`plugin=Plasma.Flex.Hub`** in `~/.config/plasma-org.kde.plasma.desktop-appletsrc` → Meldung „Paket existiert nicht“. |
| Was du tun kannst | **`bash /OMEGA_CORE/atlas-omega-voice/scripts/alte_plasmoids_auslagern.sh`** — verschiebt Pakete nach **`~/.local/share/OMEGA-plasmoid-archiv/<Zeit>/`** (nicht unter `plasmoids/`) und ruft **`plasma_entferne_flex_hub_applet.py`** auf (entfernt Flex.Hub aus der Leisten-Config, Backup `*.bak-OMEGA`). Danach **`plasmashell --replace`**. Nur Flex.Hub: `python3 …/plasma_entferne_flex_hub_applet.py`. **Hinweis:** Leiste ggf. **ATLAS Ω Voice** neu einfügen. |

### 2) ATLAS schreibt: Sprachmodell fehlt / kein Wake-Wort

| Was los ist | Für **Wake-Wort** (per Stimme „aufwecken“) braucht ATLAS **eine Datei** auf der Festplatte: `ggml-tiny.bin`. Ohne diese Datei: **kein** automatisches Zuhören aufs Wach-Wort — **Chat und OMEGA** können trotzdem gehen, wenn du anders auslöst. |
| Was du tun kannst | Einmal ausführen (Internet nötig): `bash /OMEGA_CORE/atlas-omega-voice/scripts/install_whisper_modell.sh` — dann **Plasma neu starten** (`plasmashell --replace` oder neu einloggen). |

### 3) Kein Mikrofon / ATLAS hört nichts

| Was los ist | KDE findet kein Eingabegerät oder das Format passt nicht. |
| Was du tun kannst | **Systemeinstellungen → Sound → Eingabe:** Standard-Mikro wählen, Pegel testen. |

### 4) ATLAS redet mit OMEGA nicht

| Was los ist | Backend läuft nicht oder die **Basis-URL** ist falsch (kein `/v1/...` an die URL hängen). |
| Was du tun kannst | OMEGA-Backend starten (Port **8000**). Im Widget nur z. B. `http://127.0.0.1:8000`. Optional `CORE_API_URL` in `~/.config/plasma-workspace/env/atlas-omega.sh` — siehe unten. Details: `JARVIS_OMEGA_LLM_VERBINDUNG.md`. |

---

## Konfiguration (ohne Secrets im Git)

- **Server-Basis-URL:** nur Origin, z. B. `http://127.0.0.1:8000` oder die in `.env` gesetzte **`CORE_API_URL`** (wird vom Plasmoid als **Umgebungsvariable** gelesen, wenn noch kein gespeicherter Wert in QSettings existiert).
- **Plasma:** Umgebungsvariable für die Session z. B. unter `~/.config/plasma-workspace/env/atlas-omega.sh`:
  - `export CORE_API_URL=http://<CORE_HOST_IP>:<CORE_API_PORT>`
  Werte aus lokaler `.env` übernehmen — **nicht** ins Repository schreiben.
- **QSettings-Gruppe:** `OMEGA` / `AtlasOmegaVoice` (getrennt vom Original-Jarvis).

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

**Wake-Wort-Modell (einmalig):**

```bash
bash /OMEGA_CORE/atlas-omega-voice/scripts/install_whisper_modell.sh
```

**Wake-Wort:** Sage **„Atlas“** (nicht mehr „Jarvis“). Whisper ist im Code auf **Sprache `de`** gesetzt (Wake-Wort + Sprachbefehl), damit nicht ständig andere Sprachen „erraten“ werden.

---

## Für Entwickler (kurz)

- QML-Modul intern: `org.kde.plasma.jarvis` (Installationspfad). Sichtbar: **ATLAS**; Chat-Rollen: `user` / `atlas` / `system`.
- **GCC/Qt 6:** Kein `QStringLiteral(u8"…")` — nur `QStringLiteral("…")` mit UTF-8-Quellen; Signal `availableLlmModelsChanged` in `jarvissettings.h` deklarieren, wenn emittiert.

---

## Siehe auch

- `docs/BIBLIOTHEK_KERN_DOKUMENTE.md`
- `docs/02_ARCHITECTURE/JARVIS_OMEGA_LLM_VERBINDUNG.md`
- `CORE_EICHUNG.md` (Anhang A/B)

---

*Stand: 2026-03-19*
