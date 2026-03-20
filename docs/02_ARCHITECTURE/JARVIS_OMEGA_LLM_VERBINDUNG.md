# J.A.R.V.I.S. (KDE-Plasmoid) ↔ OMEGA CORE — LLM-Verbindung

**Vektor:** 2210 | **Delta:** 0.049
**Status:** Diagnose + Fix-Plan (Umsetzung siehe Git + lokaler Jarvis-Tree)

---

## 1. Symptom

- HUD: **„LLM SERVER OFFLINE — RECONNECTING…“**
- Teilweise: Einstellungen zeigen **Connected**, HUD **Offline** — beide nutzen dieselbe Property `JarvisBackend.connected`, Abweichungen entstehen typischerweise durch **wechselnde URL**, **Timing** (Health alle 10 s) oder **Screenshots zu unterschiedlichen Zeitpunkten**.

---

## 2. Root Cause (verifiziert)

Das Plasmoid prüft die Erreichbarkeit mit:

`GET <llmServerUrl> + "/health"`

Chat und TTS hängen dagegen an:

- `<llmServerUrl>/v1/chat/completions`
- `<llmServerUrl>/v1/audio/speech`

**Falsche Konfiguration:** Basis-URL = `http://127.0.0.1:8000/v1/chat/completions`
→ Health wird zu `http://127.0.0.1:8000/v1/chat/completions/health` → **404** → `connected = false`.

**Messung (OMEGA laufend auf :8000):**

| URL | HTTP |
|-----|------|
| `GET /health` | 200 |
| `GET /v1/chat/completions/health` | 404 (vor Kompat-Route) |

**Korrekte Basis:** nur Origin, z. B. `http://127.0.0.1:8000` (ohne `/v1/...`). Siehe auch `CORE_EICHUNG.md` / `AGENTS.md` (Backend :8000).

---

## 2b. Symptom: Chat 500, ATLAS spricht nichts

- **Health** kann **grün** sein (`/health` oder `/v1/chat/completions/health`), **Chat** liefert trotzdem **500**.
- **Häufige Ursache:** `jarvis_mri_coupler` leitete **nur** `OLLAMA_LOCAL_HOST` (localhost:11434) an. Auf Dreadnought läuft Ollama oft **nicht** lokal, sondern unter **`OLLAMA_HOST`** (z. B. LAN-Pi). Dann fehlt dort das Modell für `core-local-min` (`llama3.2:1b`) → **404** von Ollama → **500** am Plasmoid. **TTS** kommt erst nach einer gültigen LLM-Antwort — wirkt dann wie „es spricht gar nicht“.
- **Fix (Code):** `OLLAMA_API_BASE` = `JARVIS_OLLAMA_URL` **oder** `OLLAMA_HOST` **oder** `OLLAMA_LOCAL_HOST` (siehe `jarvis_mri_coupler.py`). Nach Änderung: **Backend neu starten**.

### Symptom: „Operation timed out“ bei CORE Local (Deep) / 14B

- Das Plasmoid hatte **`setTransferTimeout(60000)`** (60 s) auf `POST /v1/chat/completions`. **Qwen 14B** lokal braucht oft **länger** → Qt bricht ab, obwohl Ollama noch rechnet.
- **Fix:** Timeout im Widget auf **600000 ms** (10 min) für Chat; TTS **`/v1/audio/speech`** mit **180000 ms** (3 min). Nach `sudo make install`: `plasmashell --replace`.

---

## 3. Umgesetzte / geplante Fixes

### A) OMEGA Backend (`src/api/main.py`)

- **`GET /v1/chat/completions/health`** — liefert `200` und minimales JSON, falls die Basis-URL fälschlich mit `/v1/chat/completions` endet (Abwärtskompatibilität).
- **Hinweis:** Nach Deploy **Backend neu starten** (`systemctl restart omega-backend` o. Ä.), damit die Route live ist.

### B) Jarvis-Quellbaum (lokal, z. B. `jarvis-main`)

1. **`jarvissettings.cpp`** — rekonstruiert (vorher: doppelte Funktionen + Syntaxbruch).
2. **`normalizeLlmBaseUrl()`** — trimmt, entfernt trailing `/`, strippt Suffix `/v1/chat/completions` (case-insensitive). Wird in `loadSettings()` und `setLlmServerUrl()` angewendet.
3. **Default-Port** — `8000` statt `8080` (llama.cpp-Default vs. OMEGA).
4. **`main.qml`** — HUD-Text nutzt **`JarvisBackend.llmServerUrl`** statt hardcodiert `127.0.0.1:8080`.
5. **`configGeneral.qml`** — Placeholder `8000`.

**Build auf Dreadnought:** im Build-Verzeichnis `cmake --build .` → `sudo make install` → Plasmoid neu laden.

### C) GitHub / Repo „Atlas-Omega-Voice“

- Soll: eigener Clone mit obigen Änderungen + Theme (dunkelgrau / Bordeaux / Weiß).
- Aktuell: Tree oft unter `~/Downloads/jarvis_temp/...` — in Git-Repo überführen und pushen (Operator-Flow).

### D) Nächste Schritte (optional)

- Health strikt auf **`GET /status`** + JSON-Prüfung (C++), falls du HTML an `/health` vermeiden willst.
- Qt: bei HTTP 4xx sicherstellen, dass `QNetworkReply::error()` gesetzt ist (Version-abhängig).
- TTS-Stimmen: Mapping zu `voice_bridge` / Gemini Kore / ElevenLabs (`.env`) — getrennt von dieser LLM-Health-Thematik.

---

## 4. Referenzen

- `@docs/BIBLIOTHEK_KERN_DOKUMENTE.md` — Index.
- `@docs/02_ARCHITECTURE/CORE_SCHNITTSTELLEN_UND_KANAALE.md` — API-Kontext.
- `@CORE_EICHUNG.md` — System-Eichung, Backend-Port.
- Code: `src/api/main.py`, Router `jarvis_mri_coupler.py`, `voice_bridge.py`.

---

*Letzte Aktualisierung: 2026-03-19*
