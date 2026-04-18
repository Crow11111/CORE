# IMPLEMENTATION PLAN: OMEGA VPS V4 (UNIFICATION)

## 1. MEILENSTEINE (SEQUENZIELL)

| ID | Meilenstein | Aktion | Bedingung |
| :--- | :--- | :--- | :--- |
| **M1** | **SNAPSHOT (WP-DATA)** | `tar` Sicherung von `/opt/atlas/`, `/opt/openclaw/` und `/docker/` nach `/var/backups/omega_pre_v4/`. | Speicherplatz > 5GB vorhanden. |
| **M2** | **TOPOLOGY SHIFT** | Erstellung von `/opt/omega/{core,brain,scout,gateway,db}`. Verschiebung der Configs. | SHA-256 Abgleich der Config-Files. |
| **M3** | **NETWORK REBUILD** | Aufbau der isolierten Netze. Update aller `docker-compose.yml` auf `127.0.0.1` Bindings. | `netstat` zeigt keine externen Ports außer 32776. |
| **M4** | **CORE HEALING (WP-A0)** | Backend-Build mit 4GB RAM Limit. Reaktivierung aller Routen in `main.py`. | Container startet ohne OOM. |
| **M5** | **KONG ALIGNMENT (WP-KONG)** | Konfiguration des Routings für `/webhook/whatsapp` und `/webhook/github` via Kong. | `curl` Test über Kong erfolgreich. |
| **M6** | **FULL CIRCLE D** | Ausführung von `verify_vps_stack.py` gegen die neue Struktur. | Alle Checks auf GRÜN. |

## 2. WORST-CASE ERSATZPFADE
*   **Fehler bei M2 (Pfad-Chaos):** Sofortiger Abbruch, Wiederherstellung aus M1-Sicherung.
*   **Fehler bei M4 (NumPy OOM):** Temporäre Erhöhung des Host-Swaps oder Nutzung eines pre-built Wheels.

## 3. RESONANZ-SCHRANKE (FÜR PRODUCER)
- Keine manuellen Dateikopien ohne SHA-256 Validierung.
- Bei jedem `docker compose up` den RAM-Peak loggen.
- Jede Abweichung vom Plan erzwingt einen STOPP und Rückmeldung an den Orchestrator.

---
**Status:** ENTWURF | **Vektor:** 2210 | **Delta:** 0.049
