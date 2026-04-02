# OC Brain – Strang B Kurzbericht (Ollama auf VPS)

**Datum:** 2025-03-14  
**VPS:** 187.77.68.250 (OPENCLAW_ADMIN_VPS_HOST)  
**Skript:** `src/scripts/install_ollama_vps.py`

---

## Ergebnis (letzter Lauf)

| Kriterium | Wert |
|-----------|------|
| **Installation durchgeführt** | Ja (install.sh ausgeführt) |
| **Ollama-Status** | Fehler (api/tags leer, siehe unten) |
| **api/tags** | (leer) – curl http://127.0.0.1:11434/api/tags lieferte keine Antwort |
| **Modell** | qwen2.5:7b – **ollama pull exit: 0**, 4.7 GB gezogen (Pull erfolgreich) |
| **ollama list** | Auf dem VPS leer (evtl. anderer Nutzer/PATH pro SSH-Channel) |
| **Port 11434** | Nur localhost (nicht in ufw freigegeben) |
| **Service-Status** | unknown (systemctl is-active lieferte nichts; VPS ggf. ohne systemd) |

## Fehlermeldung (exakt)

```
api/tags: exit=0, body leer oder ungültig (curl empty?). ollama list/Service siehe api_tags_output.
```

Zusätzlich: `ollama list` auf dem VPS war leer, `systemctl`-Ausgabe leer. Mögliche Ursachen: Service nicht gestartet (kein systemd?), Modell-Pull fehlgeschlagen oder Timeout, oder Ollama hört nicht auf 127.0.0.1:11434.

---

## Durchgeführte Schritte

1. SSH zu 187.77.68.250 (root) – OK.
2. Ollama installiert mit `curl -fsSL https://ollama.ai/install.sh | sh` (Installationsflag auf True).
3. systemctl enable/start ollama sowie Fallback `nohup ollama serve`.
4. `ollama pull qwen2.5:7b` ausgeführt (lange Laufzeit).
5. `curl http://127.0.0.1:11434/api/tags` → leer.

---

## Nächste Schritte (Empfehlung)

1. **Erneut ausführen** mit offizieller URL (Skript nutzt nun `https://ollama.com/install.sh`) und erweiterter Diagnose (pull_exit_code, pull_stderr im Bericht):
   ```bash
   python -m src.scripts.install_ollama_vps
   ```
2. **Manuell auf dem VPS prüfen:**  
   `systemctl status ollama` bzw. `pgrep -a ollama`; `ollama list`; `curl -s http://127.0.0.1:11434/api/tags`.
3. **OpenClaw-Provider-Config** (baseUrl localhost:11434, Modell) bleibt Aufgabe des System-Architekten; Strang B liefert nur den Ollama-Betrieb auf dem VPS.

---

## Referenzen

- Auftrag Strang B: `docs/05_AUDIT_PLANNING/OC_BRAIN_AUFTRAG_AUSFUEHRUNG.md`
- Infrastruktur-Doku: `docs/03_INFRASTRUCTURE/VPS_OLLAMA_SETUP.md`


[LEGACY_UNAUDITED]
