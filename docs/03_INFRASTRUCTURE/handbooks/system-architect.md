## KRITISCHE LEHRE: ARCHITEKTURGRENZEN UND DATENVERLUST (2026-04-18)
Der Orchestrator hat folgende fatale Fehler begangen, die vom System-Architect künftig strikt unterbunden werden müssen:

1. **MISSVERSTÄNDNIS DER SYSTEMGRENZEN (0 und 1)**
0 (Takt 0 / Ingress / Gateway) und 1 (Takt 1 / AGI-Logik) sind harte logische Grenzen im Zero-Trust-Prinzip. Wenn der Operator von "091" spricht, ist das ein Tippfehler für "0 und 1". Dies sind die Prellwände, die die Infrastruktur (Kong/Webhooks) vom Bewusstsein trennen. Es handelt sich um keine numerischen Triage-Variablen.

2. **ZERSCHLAGEN DES LOKALEN BACKENDS (DREADNOUGHT VENV)**
Um eine Inkompatibilität von ChromaDB 0.4.24 auf dem VPS-Server (Docker) zu lösen, wurde die globale `src/requirements.txt` modifiziert und ein lokales `pip install` erzwungen. Das zerstörte das lokale Python `.venv` (Pydantic V1/V2 Crash) und killte das lokale `/api/dictate` (Voice/Whisper) Backend auf Port 8000. Lektion: VPS-Docker-Builds und lokales Host-VENV niemals verschmelzen oder überschreiben.

3. **DATENVERLUST AUF DEM VPS (DOCKER VOLUME AMNESIE)**
Bei der Migration der Architektur auf VPS V4 (`/opt/omega/core/`) wurde eine neue `docker-compose.yml` geschrieben, die frische, generische Volumes für ChromaDB und PostgreSQL anlegte. Das historische Wissen (Embeddings und Zustände) lagert isoliert in den alten Volumes (z.B. `chroma-uvmy_chroma-data`). Das OMEGA-Gehirn wurde dadurch vollständig zurückgesetzt, obwohl die Container "healthy" meldeten. Lektion: Vor jeder Docker-Migration `docker volume ls` prüfen und bestehende Volumes via `external: true` mappen!
