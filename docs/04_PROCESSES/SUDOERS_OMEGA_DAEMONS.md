# sudoers-Fragment: OMEGA-Daemons ohne Passwort (NOPASSWD)

**Zweck:** Auf Dreadnought `systemctl` für die CORE/OMEGA-Units ausführen dürfen **ohne** `LINUX_SUDO_PW` in Skripten — aber **nur** diese Befehle, nicht volles `sudo`.

**Sicherheit:** Keine Passwörter in Git oder Chat. Diese Datei enthält **nur** eine Vorlage; Du installierst sie lokal unter `/etc/sudoers.d/`.

---

## Regeln

1. **Immer** mit `visudo` bearbeiten (Syntax-Check), nie roh nach `/etc/sudoers` appenden.
2. **Volle Pfade** — `which systemctl` / `which journalctl` prüfen (Arch: meist `/usr/bin/systemctl`, `/usr/bin/journalctl`).
3. **`DEIN_USER`** durch Deinen Login ersetzen (z. B. `mth`).
4. Datei unter `/etc/sudoers.d/` **nur** `root:root`, Modus **0440**.
5. Nach dem Speichern: `sudo visudo -c -f /etc/sudoers.d/omega-core-daemons`

---

## Vorlage A — schmal (empfohlen zum Start)

Nur **restart** und **status** für die bekannten Units:

```sudoers
# OMEGA CORE — nur systemd für OMEGA-Units (NOPASSWD)
# Ersetze DEIN_USER. Pfade an System anpassen (command -v systemctl).
Defaults:DEIN_USER !requiretty

DEIN_USER ALL=(root) NOPASSWD: /usr/bin/systemctl restart omega-backend
DEIN_USER ALL=(root) NOPASSWD: /usr/bin/systemctl restart omega-frontend
DEIN_USER ALL=(root) NOPASSWD: /usr/bin/systemctl restart omega-event-bus
DEIN_USER ALL=(root) NOPASSWD: /usr/bin/systemctl restart omega-watchdog
DEIN_USER ALL=(root) NOPASSWD: /usr/bin/systemctl restart omega-vision
DEIN_USER ALL=(root) NOPASSWD: /usr/bin/systemctl restart omega-audio

DEIN_USER ALL=(root) NOPASSWD: /usr/bin/systemctl status omega-backend
DEIN_USER ALL=(root) NOPASSWD: /usr/bin/systemctl status omega-frontend
DEIN_USER ALL=(root) NOPASSWD: /usr/bin/systemctl status omega-event-bus
DEIN_USER ALL=(root) NOPASSWD: /usr/bin/systemctl status omega-watchdog
DEIN_USER ALL=(root) NOPASSWD: /usr/bin/systemctl status omega-vision
DEIN_USER ALL=(root) NOPASSWD: /usr/bin/systemctl status omega-audio
```

**Hinweis:** `!requiretty` ist optional; ohne TTY schlagen manche `sudo`-Aufrufe (z. B. aus IDE) sonst fehl. Nur setzen, wenn Du das bewusst willst.

---

## Vorlage B — erweitert (start/stop + Journal)

Wenn Du auch start/stop oder Logs ohne Passwort brauchst:

```sudoers
# Zusätzlich zu Vorlage A — Beispiele; bei Bedarf ergänzen
DEIN_USER ALL=(root) NOPASSWD: /usr/bin/systemctl start omega-backend
DEIN_USER ALL=(root) NOPASSWD: /usr/bin/systemctl stop omega-backend
DEIN_USER ALL=(root) NOPASSWD: /usr/bin/systemctl start omega-frontend
DEIN_USER ALL=(root) NOPASSWD: /usr/bin/systemctl stop omega-frontend

# Nur Lesen: letzte Zeilen Service-Log (exakt diese Argumente = sudoers-Zeile)
DEIN_USER ALL=(root) NOPASSWD: /usr/bin/journalctl -u omega-backend -n 80 --no-pager
```

**Journalctl:** Jede Argumentkombination ist in sudoers **eigenständig** — wenn Du andere Flags brauchst, neue Zeile oder `Cmnd_Alias` (siehe `man sudoers`).

---

## Installation (Kurz)

```bash
sudo visudo -f /etc/sudoers.d/omega-core-daemons
# Inhalt einfügen, DEIN_USER + Pfade prüfen, speichern

sudo chmod 440 /etc/sudoers.d/omega-core-daemons
sudo chown root:root /etc/sudoers.d/omega-core-daemons
sudo visudo -c -f /etc/sudoers.d/omega-core-daemons
```

Test:

```bash
sudo -n systemctl status omega-backend
# soll ohne Passwortprompt eine Ausgabe liefern (oder Fehler „Unit not found“, aber kein Passwort)
```

---

## Bezug CORE

- Doku Jarvis/LLM-Basis-URL: `docs/02_ARCHITECTURE/JARVIS_OMEGA_LLM_VERBINDUNG.md`
- Daemons-Überblick: `CLAUDE.md` (Abschnitt Daemons)

---

*Ratifiziert als Prozess-Doku; keine Secrets in diesem Repository.*
