# CORE OS: DUAL-BOOT MIGRATION (DIRTY WAY)

**Status:** EXECUTION
**Vektor:** 2210
**Ziel:** Harter Dual-Boot (Windows 11 / Debian Linux) auf der gleichen Platte. Maximale Isolation. Minimaler manueller Aufwand fǬr den Operator.

## 1. Das Konzept (Der Dirty Way)
Wir machen keinen komplizierten Proxmox-Hypervisor. Wir machen den klassischen, dreckigen Dual-Boot:
* **Windows-Partition (Status Quo):** Bleibt unangetastet. Dein Photoshop, dein Cursor, deine aktuelle Umgebung bleibt exakt so, wie sie ist.
* **Linux-Partition (CORE OS):** Wir zwacken 100-200 GB von deiner Festplatte ab und installieren dort ein nacktes Debian Linux.
* **Der Bootloader (GRUB):** Beim PC-Start whlst du: Windows (Alltag) oder Linux (CORE-Schmiede).

## 2. Der Medienbruch (Die BrǬcke)
Whrend der Installation hast du kein Copy&Paste zwischen Windows und Linux. 
**Die Lsung:** Wir nutzen einen externen Messenger (z.B. Telegram "Saved Messages", WhatsApp an dich selbst, oder ein einfaches GitHub-Gist) auf deinem **iPad/Handy** als Zwischenspeicher.
1. Ich generiere dir hier alle komplexen Befehle.
2. Du kopierst sie dir auf dein iPad (WhatsApp/Telegram).
3. Sobald Linux luft und du dort einen Browser/Messenger hast, kopierst du die Befehle vom iPad direkt ins Linux-Terminal. Kein Abtippen von 1000 Zeilen.

---

## 3. EXECUTION: SCHRITT-FǬR-SCHRITT

### SCHRITT 1: Platz schaffen (Unter Windows)
Das musst du jetzt sofort in Windows machen:
1. DrǬcke `Win + X` -> **Datentrgerverwaltung** (Disk Management).
2. Rechtsklick auf deine groe Windows-Partition (C:) -> **Volume verkleinern** (Shrink Volume).
3. Gib **102400** (fǬr 100 GB) oder **204800** (fǬr 200 GB) ein und klicke auf "Verkleinern".
4. *Ergebnis:* Du hast jetzt einen schwarzen Block "Nicht zugewiesener Speicherplatz". Lass ihn genau so. Nichts formatieren.

### SCHRITT 2: Den USB-Stick bauen (Unter Windows)
1. Lade **Rufus** herunter: `https://rufus.ie/`
2. Lade das **Debian 12 Netinst ISO** herunter (minimal, stabil): `https://cdimage.debian.org/debian-cd/current/amd64/iso-cd/debian-12.5.0-amd64-netinst.iso`
3. Stecke einen leeren USB-Stick (min. 4GB) ein.
4. Starte Rufus, whle das Debian-ISO und klicke auf **START**. (Achtung: Stick wird gelscht).

### SCHRITT 3: Die Installation (Der Neustart)
1. PC neu starten, ins BIOS/UEFI gehen (meist `F2`, `F12` oder `Del`).
2. Vom USB-Stick booten.
3. **Graphical Install** whlen.
4. **WICHTIGSTE STELLE (Partitionierung):** Whle **"GefǬhrte Partitionierung - grten freien Speicherplatz verwenden"**. (NICHT die ganze Platte lschen! Nur den Platz nutzen, den wir in Schritt 1 freigemacht haben).
5. **Software-Auswahl:** Whle NUR "SSH server" und "Standard system utilities". **KEINE** Desktop-Umgebung (GNOME/KDE) ankreuzen! Wir wollen ein nacktes Terminal.

### SCHRITT 4: Der BrǬcken-Kopf (Das iPad)
*Kopiere dir diesen Block jetzt auf dein iPad (WhatsApp/Notes).*

Sobald Debian installiert ist und du vor dem schwarzen Terminal sitzt, loggst du dich mit deinem gewhlten User ein. Dann tippst du diesen *einen* Befehl ab, um die BrǬcke zu bauen:

```bash
su -  # (Root-Passwort eingeben)
apt update && apt install -y curl git python3-venv python3-pip htop
```

Ab hier Ǭbernimmt CORE. Wir ziehen das Repo und starten das Setup-Skript, das alles weitere (Docker, Sensoren, ChromaDB) vollautomatisch installiert.

---
**Operator:** Besttige, wenn Schritt 1 (Volume verkleinern) und Schritt 2 (USB-Stick) abgeschlossen sind. Ich generiere dann das finale Auto-Setup-Skript fǬr Linux, das du dir aufs iPad kopieren kannst.