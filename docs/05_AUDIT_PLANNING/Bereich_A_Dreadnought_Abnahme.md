# Bereich A: Dreadnought – Prüfergebnis und Abnahme

**Referenz:** OMEGA_VOLLKREIS_PLAN.md §3 (A: Dreadnought), §5 (Abnahme).  
**Abnahme-Skript:** `run_vollkreis_abnahme.py` (Orchestrator führt aus).  
**Stand:** 2026-03-18

---

## 1. Geprüft

| Prüfpunkt | Ergebnis | Anmerkung |
|------------|----------|-----------|
| **Backend :8000** | Abnahme prüft `curl http://localhost:8000/status` | `src/api/main.py` liefert `/status` mit `event_bus.running` (true wenn Event-Bus gestartet). |
| **Frontend :3000** | Abnahme prüft Port 8000 + 3000 via `ss -tuln` | Beide Ports müssen belegt sein (Backend + Frontend laufen). |
| **Event-Bus** | `event_bus.running === true` in `/status` | Start in `main.py` lifespan via `start_event_bus()` bei gesetztem HASS_URL/HASS_TOKEN. |
| **Daemons (event-bus, watchdog, vision)** | Architektur: im Backend-Prozess (event_bus) bzw. systemd | event-bus = Teil des API-Prozesses; watchdog/vision = separate systemd-Units. |
| **Ollama** | Nicht direkt in run_vollkreis_abnahme | `run_verification.sh` prüft `systemctl is-active ollama`. |
| **systemd (omega-backend, omega-frontend, omega-event-bus, omega-watchdog, omega-vision)** | Keine Unit-Dateien im Repo | Siehe Lücken. |
| **.env Konsistenz** | Geprüft | CORE_HOST_IP=192.168.178.20, CORE_API_PORT=8000, CHROMA_HOST=187.77.68.250, CHROMA_PORT=32768 – konsistent für VPS-Chroma. |
| **src/config ohne Windows-Pfade** | core_state.py vorhanden, keine C:\/c:\ | core_path_manager.py fehlt im Repo (nur core_state wird geprüft). |
| **Zentrale Skripte ohne Windows-Pfade** | build_core_usb.py bereinigt | CORE_USB_DRIVE aus ENV; keine hardcodierten C:\ oder J:\ in Ausgaben. |

---

## 2. Geändert / Dokumentiert

- **run_vollkreis_abnahme.py:** Beide Config-Dateien (core_path_manager, core_state) werden geprüft, falls vorhanden; kein Abbruch nach der ersten.
- **.env:** Kommentar „PC Win11 IoT“ → „Dreadnought (Arch)“.
- **src/scripts/build_core_usb.py:** USB_DRIVE aus `CORE_USB_DRIVE` (Default: J: unter Windows, /mnt/usb unter Linux); Print-Texte ohne C:\/J:\.
- **Dieses Dokument:** Abweichungen und Lücken festgehalten.

---

## 3. Verbleibende Lücken

| Lücke | Maßnahme |
|-------|----------|
| **core_path_manager.py** | Im Plan/BIBLIOTHEK referenziert, nicht im Repo. Abnahme nutzt `core_state.py`. Kein Code-Change nötig; Doku verweist auf core_state. |
| **systemd-Unit-Dateien** | Nicht im Repo. Auf Dreadnought manuell unter `/etc/systemd/system/` anlegen (omega-backend, omega-frontend, omega-event-bus, omega-watchdog, omega-vision). Referenz: `run_verification.sh`, START_OMEGA_COCKPIT.bat (Ports/Commands). |
| **run_verification.sh** | Erwartet `omega-watchdog.service`; Backend/Frontend-Start aktuell nicht als systemd im Repo abgebildet. |

**Erfolg Bereich A:** Wenn der Orchestrator `run_vollkreis_abnahme.py` ausführt und Backend (:8000) + Frontend (:3000) laufen sowie HASS_URL/HASS_TOKEN gesetzt sind, bestehen die Prüfungen für A (Backend /status event_bus.running, Ports 8000/3000, Config ohne Windows-Pfade).


[LEGACY_UNAUDITED]
