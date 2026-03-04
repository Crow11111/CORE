# Scout Assist-Pipeline: Sprachbefehle an ATLAS

**Zweck:** Sprachbefehle vom Scout-Mikrofon über die HA Assist-Pipeline an ATLAS weiterleiten. ATLAS führt Triage durch (HA-Aktion oder OC Brain), die Antwort wird per TTS auf dem Mini-Speaker ausgegeben.

---

## 1. Architektur

```
User spricht
    ↓
Scout Mikrofon (USB oder integriert)
    ↓
openWakeWord ("hey atlas" / "atlas") → Pipeline startet
    ↓
Whisper STT → transkribierter Text
    ↓
ATLAS API (Dreadnought) POST /webhook/assist
    ↓
Triage (SLM): command | deep_reasoning | chat
    ↓
├─ command → HA-Aktion (Licht, etc.) via HAClient
└─ deep_reasoning/chat → OC Brain oder lokales Gemini
    ↓
Antwort-Text
    ↓
Piper TTS → Mini-Speaker (media_player.schreibtisch o.ä.)
```

**Netzwerk:**
- **Scout (HA):** 192.168.178.54 (Raspi 5)
- **Dreadnought (ATLAS API):** 192.168.178.110, Port 8000
- Scout muss Dreadnought per HTTP erreichen können: `http://192.168.178.110:8000`

---

## 2. ATLAS-Verbindung zu HA

ATLAS verbindet sich **zu** HA (nicht umgekehrt):

- **Client:** `src/connectors/home_assistant.py` (HomeAssistantClient)
- **Variablen:** `HASS_URL` / `HA_URL`, `HASS_TOKEN` / `HA_TOKEN`
- **Funktionen:** `call_service()`, `get_states()`, etc.
- **Richtung:** Dreadnought → Scout (HTTPS zu 192.168.178.54:8123)

Die **Assist-Pipeline** benötigt die **umgekehrte** Richtung: HA (Scout) → ATLAS (Dreadnought). Dafür nutzt HA einen `rest_command`, der an die ATLAS API sendet.

---

## 3. Benötigte HA-Variablen (.env auf Dreadnought)

| Variable | Beschreibung | Beispiel |
|---------|--------------|----------|
| `HASS_URL` / `HA_URL` | HA-URL (Scout) | `https://192.168.178.54:8123` |
| `HASS_TOKEN` / `HA_TOKEN` | Long-Lived Token für HA | (aus HA Profil) |
| `HA_WEBHOOK_TOKEN` | Bearer-Token für `/webhook/assist`, `/webhook/inject_text` | Zufälliger String (z.B. `openssl rand -hex 24`) |

**Wichtig:** `HA_WEBHOOK_TOKEN` muss in `.env` gesetzt sein, sonst lehnt die ATLAS API Anfragen ab (503).

---

## 4. HA Add-ons (Scout)

| Add-on | Zweck |
|--------|-------|
| **Whisper** | Speech-to-Text (offenes Modell, beliebige Sprache) |
| **openWakeWord** | Wake-Word-Erkennung ("hey atlas", "atlas") |
| **Piper** | Text-to-Speech (lokal, schnell) |

Installation: Einstellungen → Add-ons → Add-on-Store. Nach Installation erscheinen die Dienste unter Wyoming-Integration.

---

## 5. Wake-Word Konfiguration

- **openWakeWord** unterstützt vordefinierte und eigene Wake-Wörter.
- Für "hey atlas" oder "atlas": In der openWakeWord-Konfiguration das passende Modell wählen oder ein Custom-Modell trainieren.
- Dokumentation: [HA Wake Words](https://www.home-assistant.io/voice_control/create_wake_word/)

---

## 6. rest_command: Text an ATLAS senden

In `configuration.yaml` oder als YAML-Konfiguration:

```yaml
# Geheimnisse (Einstellungen → Geheimnisse oder secrets.yaml):
#   atlas_api_url: "http://192.168.178.110:8000"
#   atlas_webhook_token: "<HA_WEBHOOK_TOKEN aus .env>"

rest_command:
  atlas_assist:
    url: "{{ atlas_api_url }}/webhook/assist"
    method: POST
    headers:
      Authorization: "Bearer {{ atlas_webhook_token }}"
      Content-Type: "application/json"
    payload: '{"text": {{ text | tojson }}}'
```

**Ohne Geheimnisse (direkt, nicht empfohlen für Produktion):**

```yaml
rest_command:
  atlas_assist:
    url: "http://192.168.178.110:8000/webhook/assist"
    method: POST
    headers:
      Authorization: "Bearer DEIN_HA_WEBHOOK_TOKEN"
      Content-Type: "application/json"
    payload: '{"text": {{ text | tojson }}}'
```

---

## 7. Automation: Assist-Text an ATLAS

Die Assist-Pipeline liefert den transkribierten Text an einen **Conversation Agent**. Für ATLAS wird ein **Custom Conversation Agent** benötigt, der den Text an die ATLAS API weiterleitet. HA bietet dafür keine Standard-Integration – es braucht entweder:

- eine **Custom Integration** (Python), die die Conversation API implementiert und an ATLAS weiterleitet, oder
- einen **Workaround** über `input_text` + Automation.

### 7.1 Workaround: input_text + Automation

Wenn der Text auf anderem Weg in `input_text.assist_command` landet (z.B. von einem externen Skript oder einer anderen Integration):

```yaml
input_text:
  assist_command:
    name: "Assist-Befehl für ATLAS"
    max: 500

automation:
  - alias: "Assist-Text an ATLAS senden"
    trigger:
      - platform: state
        entity_id:
          - input_text.assist_command
    condition:
      - condition: template
        value_template: "{{ trigger.to_state.state | length > 0 }}"
    action:
      - service: rest_command.atlas_assist
        data:
          text: "{{ states('input_text.assist_command') }}"
      - service: input_text.set_value
        target:
          entity_id: input_text.assist_command
        data:
          value: ""
```

**Hinweis:** Damit die volle Voice-Pipeline funktioniert, muss der transkribierte Text aus der Assist-Pipeline in `input_text.assist_command` geschrieben werden. Dafür ist ein **Custom Conversation Agent** nötig, der:
1. Den Text von der Assist-Pipeline empfängt,
2. An ATLAS sendet,
3. Die Antwort zurückgibt (für TTS).

### 7.2 ATLAS API Antwort und TTS

Der Endpoint `/webhook/assist` gibt `{"status":"ok","reply":"<Antworttext>"}` zurück. **ATLAS spielt die Antwort automatisch auf dem Mini-Speaker ab** – nach der Verarbeitung ruft ATLAS den HA-Service `tts.google_translate_say` auf (via `tts_dispatcher`, Ziel: `media_player.schreibtisch` oder `TTS_CONFIRMATION_ENTITY`). Keine zusätzliche HA-Automation für TTS nötig.

---

## 8. Assist-Pipeline einrichten

1. **Einstellungen → Sprachassistenten → Assistent hinzufügen**
2. **Name:** z.B. "ATLAS"
3. **Sprache:** Deutsch (oder gewünschte Sprache)
4. **Conversation Agent:** Home Assistant (Standard) – für ATLAS-Anbindung Custom Agent nötig, siehe Abschnitt 7
5. **Speech-to-Text:** Whisper
6. **Text-to-Speech:** Piper
7. **Wake Word:** openWakeWord (falls verfügbar)

Ohne Custom Conversation Agent arbeitet die Pipeline mit dem Standard-HA-Agent. Für ATLAS-Anbindung ist eine Custom Integration oder der input_text-Workaround erforderlich.

---

## 9. Netzwerk-Checkliste

| Von | Nach | Port | Protokoll |
|-----|------|------|-----------|
| Scout (HA) | Dreadnought | 8000 | HTTP |
| Dreadnought | Scout (HA) | 8123 | HTTPS |
| Scout | Wyoming (Whisper, Piper, openWakeWord) | Add-on-intern | - |

**Test von Scout aus:**
```bash
# Auf dem Scout (SSH) oder von einem Gerät im gleichen Netz:
curl -X POST http://192.168.178.110:8000/webhook/assist \
  -H "Authorization: Bearer DEIN_HA_WEBHOOK_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text":"Licht an"}'
```

---

## 10. Referenzen

- `src/connectors/home_assistant.py` – ATLAS HA-Client
- `src/api/routes/ha_webhook.py` – `/webhook/assist`, `/webhook/inject_text`
- `src/voice/tts_dispatcher.py` – TTS an Mini-Speaker
- `docs/03_INFRASTRUCTURE/SCOUT_HA_EVENT_AN_OC_BRAIN.md` – Scout-Events an OC Brain
- [HA Assist Pipeline](https://www.home-assistant.io/integrations/assist_pipeline/)
- [HA Lokale Voice Pipeline](https://www.home-assistant.io/voice_control/voice_remote_local_assistant/)
