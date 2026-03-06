# ATLAS HA Config – Einbindung

## Dateien

| Datei | Inhalt |
|-------|--------|
| `rest_commands.yaml` | REST-Commands für ATLAS Event/Query API |
| `automations_atlas.yaml` | 3 Automationen (Door, Temperatur, Presence) |

## Einbindung in Home Assistant

### 1. Dateien kopieren

Kopiere die Dateien in dein HA-Config-Verzeichnis, z.B.:

```
<HA_CONFIG>/
├── rest_commands.yaml      # aus ha_config/rest_commands.yaml
├── automations_atlas.yaml   # aus ha_config/automations_atlas.yaml
└── configuration.yaml
```

Oder per Symlink:

```bash
# Von ATLAS_CORE aus
ln -s "$(pwd)/ha_integrations/ha_config/rest_commands.yaml" /path/to/ha/config/
ln -s "$(pwd)/ha_integrations/ha_config/automations_atlas.yaml" /path/to/ha/config/
```

### 2. configuration.yaml erweitern

```yaml
# REST Commands einbinden
rest_command: !include rest_commands.yaml

# Automationen einbinden (eine der Varianten)
automation: !include automations_atlas.yaml
```

**Alternative** (wenn du bereits `automation:` mit anderen Includes hast):

```yaml
automation:
  - !include automations.yaml
  - !include automations_atlas.yaml
```

Oder mit `include_dir_merge_list`:

```yaml
automation: !include_dir_merge_list automations/
# → Lege automations_atlas.yaml in Unterordner automations/
```

### 3. input_text.atlas_webhook_token anlegen

Die REST-Commands nutzen `states('input_text.atlas_webhook_token')` für den Bearer-Token.

**Developer Tools → YAML** oder `configuration.yaml`:

```yaml
input_text:
  atlas_webhook_token:
    name: ATLAS Webhook Token
    initial: ""
    max: 256
```

Dann unter **Einstellungen → Geräte & Dienste → Helfer** den Wert mit deinem ATLAS-API-Token setzen.

### 4. Neustart / Reload

- **Konfiguration prüfen:** Einstellungen → System → Neustart → Konfiguration prüfen
- **Neu starten** oder nur Automationen neu laden: Developer Tools → YAML → Automationen neu laden

---

## API-Pfade (Hinweis)

Die REST-Commands verwenden `/api/v1/event` und `/api/v1/query`.  
Falls deine ATLAS-API andere Pfade nutzt (z.B. `/api/atlas/event`), passe die URLs in `rest_commands.yaml` an.
