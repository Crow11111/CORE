# OS-Audio-Diktat (Headless)

## 1. Übersicht
CORE bietet eine systemweite Audio-Diktat-Funktion, die unabhängig vom Browser funktioniert. Sie wird über einen globalen Shortcut oder ein Tray-Icon (Plasmoid) getriggert.

## 2. Komponenten

### Skript: `src/scripts/os_dictate.sh`
- **Funktion:** Start/Stop Toggle.
- **Workflow:**
  - Klick 1: Startet `pw-record` (PipeWire) lautlos.
  - Klick 2: Beendet Aufnahme, sendet an `/api/dictate` des CORE Backends.
  - Ergebnis: Transkribierter Text wird per `wl-copy` in die Wayland-Zwischenablage kopiert.

### Desktop-Entry: `core-dictate.desktop`
- Ermöglicht das Anheften an die Taskleiste oder das Zuweisen eines Hotkeys.
- `StartupNotify=false` sorgt für einen lautlosen Start ohne blinkenden Cursor.

## 3. Installation & Shortcut
1. Skript ausführbar machen: `chmod +x src/scripts/os_dictate.sh`.
2. Desktop-Datei in `~/.local/share/applications/` ablegen.
3. In KDE Systemeinstellungen -> Kurzbefehle -> Eigene Kurzbefehle -> Neuen Befehl hinzufügen (z.B. `Meta+V`).

## 4. Backup
Das Skript ist gesichert unter:
`src/config/os/scripts/os_dictate.sh`
