# CoolerControl Setup (CachyOS / Gigabyte B560M AORUS PRO)

## 1. Problemstellung
Hohe Lüftergeräusche im Idle-Betrieb durch fehlende Steuerung der Gehäuselüfter unter Linux. Die Gigabyte WMI Sensoren lieferten keine stabilen Lüfterwerte, und der Standard-Kernel-Treiber erkannte den ITE IT8689E Chip nicht vollständig.

## 2. Lösung: Sensoren-Support (it87)
Für das Gigabyte B560M AORUS PRO wurde das Modul `it87` benötigt, das jedoch manuell mit Parametern geladen werden muss.

**Installation:**
- `yay -S it87-dkms-git` (AUR)

**Konfiguration (`/etc/modprobe.d/it87.conf`):**
```bash
options it87 ignore_resource_conflict=1 force_id=0x8689
```

**Dauerhaftes Laden (`/etc/modules-load.d/it87.conf`):**
```bash
it87
```

## 3. CoolerControl Konfiguration
Das Tool `CoolerControl` wurde installiert (`pacman -S coolercontrol`) und konfiguriert, um den `it8689` Chip zu nutzen.

**Profile:**
- **Silent:** Fixiert auf 30% bis 60°C, danach linearer Anstieg.
- **Performance:** Aggressivere Kurve für Lastspitzen.

**Temperaturquelle:**
- Da `coretemp` (`Package id 0`) in der CoolerControl-Logik teilweise "missing" meldete, wurde auf `it8689` `temp3` (Intel PECI / CPU) als stabilere Quelle umgestellt.

**Fan-Mapping:**
- Alle erkannten Gehäuselüfter (`fan1` bis `fan5`) des `it8689` wurden dem "Silent"-Profil zugewiesen.

## 4. Backup
Die Konfigurationsdateien sind im Repo gesichert unter:
`src/config/os/etc/coolercontrol/config.toml`
`src/config/os/etc/modprobe.d/it87.conf`
`src/config/os/etc/modules-load.d/it87.conf`
