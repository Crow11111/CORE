# Kontext für Dev-Agent-Review (Schnittstellen, Architektur, Sicherheit, Backup)

Die folgenden Abschnitte sind Auszüge bzw. Volltexte der zentralen Projekt-Dokumente. Bitte prüfe sie als Ganzes.

---

## Dokument 1: DEV_AGENT_UND_SCHNITTSTELLEN.md (Kern)

- **Backup:** Plan siehe BACKUP_PLAN.md. Umsetzung: Skript `scripts/daily_backup.py` (noch zu implementieren); Anbindung Cron/Task Scheduler. Relevante Pfade: Projekt-Root, `data/`, `.env`, `config/`, ggf. `media/`.
- **Netzarchitektur:** WhatsApp → HA (Addon) → rest_command → ATLAS FastAPI `/webhook/whatsapp`. OpenClaw auf Hostinger als zweiter, optionaler Einstieg. Sandbox-Pflicht für OpenClaw (kein Zugriff auf ChromaDB/Ollama/.env auf demselben Server).
- **VPS-Setup:** `setup_vps_hostinger.py` – Docker, Firewall, ChromaDB, OpenClaw, Backup-Verzeichnis `/var/backups/atlas`.
- **Go2RTC/Kamera:** PC oder Scout; FFmpeg aus `driver/go2rtc_win64` mit cwd; optional CAMERA_SNAPSHOT_URL für On-Demand-Brio.
- **ChromaDB:** Lokal (PersistentClient) oder Remote (CHROMA_HOST). Code: `chroma_client.py`, Ingest-Skript.
- **Gemini:** Pro-Tier nur; 3.1 Pro Standard; Bildanalyse ≠ Bildgenerierung (Nano Banana Pro nur für Generierung).
- **Skripte-Tabelle:** VPS-Setup, OpenClaw-Client, ChromaDB, Kamera (go2rtc_client, camera_snapshot_server, brio_scenario_periodic, tapo_garden_recognize, brio_image_analyzer).

---

## Dokument 2: BACKUP_PLAN.md

- **Ziel:** Automatisierte tägliche Backups aller kritischen Projektdaten.
- **Was:** Anwendungscode (exkl. temporär, node_modules, .git), Datenbank (z. B. SQLite data/argos_db), Konfiguration (.env, config/), optional media/uploads.
- **Wohin:** Primär lokaler Backup-Speicher (z. B. /var/backups/projektname oder Windows-Ordner), sekundär Cloud (S3, GCS).
- **Wie:** Python-Skript daily_backup.py – DB-Dump, Code/Config archivieren (tar.gz/zip, exkl. .git, __pycache__, venv), optional S3-Upload, Retention.
- **Wann:** Täglich 03:00 UTC; cron (Linux) oder Task Scheduler (Windows).
- **Retention:** Letzte 7 tägliche Backups.
- **Monitoring:** Log-Datei; bei Fehlern E-Mail/Slack.
- **Wiederherstellungstest:** Mind. 1× pro Monat auf Staging.

---

## Dokument 3: VPS_DIENSTE_UND_OPENCLAW_SANDBOX.md

- **VPS-Dienste:** OpenClaw (Sandbox), ChromaDB, Backup-Ziel (Push nur von innen), optional leichtes Ollama, Webhook-Proxy. Dev-Agent und HA bleiben lokal.
- **OpenClaw-Sandbox (Pflicht):** Eigenes Docker-Container, eigenes Netzwerk (kein Zugriff auf Chroma/Ollama), kein Mount von /root oder .env, nur OpenClaw-Config. Firewall: nur nötige Ports (22, 18789, 8000, 80/443). Kommunikation nur von außen (ATLAS ruft Gateway auf).
- **Hostinger-Schritte:** SSH, Firewall, Docker; openclaw_net; OpenClaw ohne Host-Mounts, Port 18789; Chroma Port 8000; /var/backups/atlas; Backups per rsync/scp (VPS pullt nicht).
- **Checkliste Go-Live:** OpenClaw in Container, getrenntes Netzwerk, Firewall, ATLAS nutzt Token von außen.

---

## Dokument 4: UMSETZUNGSPLANUNG.md

- **Task Backup:** daily_backup.py (DB-Dump, Code/Config-Archiv, optional S3, Retention 7 Tage, logs/backup.log); Scheduler Windows/Linux; monatlicher Restore-Test. .env: BACKUP_DIR, optional AWS_*. Status: offen.
- **Task WhatsApp:** Keine separate Bot-Nummer; Auslösung durch eingehende Nachricht (remoteJid = Absender); ATLAS antwortet an Absender; optional Basis-Handler auf Scout. Status: dokumentiert, Scout-Handler offen.

---

*Ende Kontext. Bitte Review-Anmerkungen zu Schnittstellen, Architektur, Sicherheit und Backup-Planung liefern.*

---

## Review erneut ausführen / Anmerkungen sichern

Im Projekt-Root (z. B. `c:\ATLAS_CORE`) mit **--out=** (Antwort wird in UTF-8 in die Datei geschrieben, kein PowerShell-Encoding-Problem):

```bash
python -m src.ai.dev_agent_claude46 "Prüfe die Dokumente (Schnittstellen, Architektur, Sicherheit, Backup). Gib strukturierte Anmerkungen: (1) Lücken/Widersprüche, (2) Sicherheitshinweise, (3) Verbesserungsvorschläge, (4) fehlende/veraltete Referenzen. Auf Deutsch, nummeriert." docs/dev_agent_review_context.md --claude --out=docs/DEV_AGENT_REVIEW_ANMERKUNGEN.md
```

Mit `--claude` läuft dieser Task über Claude (Anthropic); ohne `--claude` nutzt der Dev-Agent weiterhin Gemini.

Die Antwort landet in `docs/DEV_AGENT_REVIEW_ANMERKUNGEN.md`.
