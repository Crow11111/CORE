# Ollama auf Hostinger-VPS (Strang B – OC Brain)

**Bezug:** [OC_BRAIN_AUFTRAG_AUSFUEHRUNG.md](../05_AUDIT_PLANNING/OC_BRAIN_AUFTRAG_AUSFUEHRUNG.md) (Strang B)  
**Skript:** `src/scripts/install_ollama_vps.py`  
**VPS:** OPENCLAW_ADMIN_VPS_HOST (z. B. 187.77.68.250)

---

## Übersicht

| Thema | Wert |
|--------|------|
| **Installationspfad** | Typisch `/usr/local/bin/ollama` (nach `curl \| sh`) |
| **Service** | `systemctl start ollama` / `systemctl is-active ollama` |
| **Port** | 11434 (nur localhost, sofern nicht `--open-firewall`) |
| **Modell (Standard)** | `qwen2.5:7b` (Alternative: `mistral:7b-instruct`) |
| **Prüfung** | `curl http://127.0.0.1:11434/api/tags` auf dem VPS |

---

## Installation

```bash
# Aus CORE-Projektroot (mit .env: OPENCLAW_ADMIN_VPS_*)
python -m src.scripts.install_ollama_vps
```

Das Skript:

1. Verbindet per SSH (User/Key oder Passwort aus .env).
2. Installiert Ollama mit: `curl -fsSL https://ollama.com/install.sh | sh`
3. Startet den Service (`systemctl enable/start ollama`) bzw. `ollama serve` im Hintergrund.
4. Zieht das Modell: `ollama pull qwen2.5:7b` (oder mistral:7b-instruct).
5. Prüft: `curl http://127.0.0.1:11434/api/tags`.

---

## Firewall

- **Standard:** Port 11434 ist **nur lokal** erreichbar (nicht in ufw freigegeben). OpenClaw-Container auf demselben Host nutzen `http://localhost:11434` bzw. `http://127.0.0.1:11434`.
- **Optional (gezielt öffnen):**  
  `python -m src.scripts.install_ollama_vps --open-firewall`  
  setzt `ufw allow 11434/tcp`. Nur verwenden, wenn externer Zugriff gewollt ist.

---

## Service-Status & Pfad (nach Lauf)

Das Skript gibt im Kurzbericht aus:

- **Installation durchgeführt:** ja/nein  
- **Ollama-Status:** ok / fehler  
- **api/tags:** Rohausgabe (Auszug)  
- **Modell:** z. B. qwen2.5:7b  
- **Installationspfad:** z. B. /usr/local/bin/ollama  
- **Service-Status:** active / inactive / no-systemd  

Bei Fehlern: exakte Meldung im Bericht und ggf. in `api_tags_output` (inkl. `ollama list` / systemctl).

---

## OpenClaw-Provider-Config

Die OpenClaw-Provider-Config für Ollama (baseUrl, Modell) wird vom **System-Architect** umgesetzt. Dieses Dokument und das Install-Skript liefern nur den **Ollama-Betrieb** auf dem VPS.

---

## Referenzen

- OC Brain Auftrag: `docs/05_AUDIT_PLANNING/OC_BRAIN_AUFTRAG_AUSFUEHRUNG.md`
- VPS Full-Stack: `docs/03_INFRASTRUCTURE/VPS_FULL_STACK_SETUP.md`
