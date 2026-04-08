# Detailplan: VPS / Omega-Backend / Vollkreis / Kong (Nachschub)

**Stand:** 2026-04-06
**Kontext:** Ergänzung zur Cloud-Agent-Zusammenfassung — diese kann **neuer** sein als ältere Orchestrator-Antworten; Abgleich immer gegen **Git + messbare Skripte**.

---

## 1. Messstand (referenzierbar)

| Messung | Erwartung | Bedeutung |
|--------|-----------|-----------|
| `python -m src.scripts.verify_vps_stack` | Exit 0 | Container, Port-Vertrag, Kong **Deck-Referenz** vs. Admin-API, Chroma-Heartbeat, optionale Dienste |
| Zeile `[--] Kong Proxy /status: timed out` | Optionaler Hinweis | **Kein** Deck-Fail: Route existiert. Ursache typisch: **Upstream** `omega-backend` auf Host **32800** nicht erreichbar, hängt, oder Firewall/Route — **nicht** „Kong kaputt“ |
| `python -m src.scripts.verify_vps_omega_backend_http` | Exit 0 | **Direkt** auf dem VPS: Loopback **`127.0.0.1:32800/status`** per SSH — bestätigt systemd-Backend **ohne** Kong |

---

## 2. URL-Strategie (keine harte VPS-IP im Code)

| Zweck | Mechanismus |
|-------|-------------|
| Vollkreis A + G gegen **eine** Runtime | **`CORE_BASE_URL`** in `.env` (oder Export vor Lauf): z. B. `http://127.0.0.1:8000` (Dev), `https://api.example.com`, oder `http://<VPS-IP>:32776` wenn Kong öffentlich terminiert und `/status` durchreicht |
| Nur „lebt das Backend auf dem Metal?“ | **`verify_vps_omega_backend_http`** — immer **Loopback auf dem VPS**, keine IP im Skript nötig (`VPS_HOST` + `VPS_SSH_KEY`) |

**Regel:** Keine feste öffentliche IP in `run_vollkreis_abnahme.py` — nur **`CORE_BASE_URL`**.

---

## 3. Phasen (Reihenfolge)

### Phase A — Sofort messbar (Operator / Dev-Host)

1. `verify_vps_stack` → Exit 0 dokumentieren.
2. Bei `/status`-Timeout: `verify_vps_omega_backend_http` laufen lassen.
   - **Grün:** Backend ok, Problem eher Kong→Host-Routing (172.17.0.1, Firewall, langsame Antwort).
   - **Rot:** `/etc/default/omega-backend`, `systemctl status omega-backend`, `journalctl -u omega-backend`.

### Phase B — Secrets & Betrieb (nur Operator)

3. `/etc/default/omega-backend` auf dem VPS vollständig (Keys, DB, Chroma gemäß Vorlage).
4. `systemctl restart omega-backend` nach Änderung.
5. Wiederholen: Loopback-Check + optional `curl` von außen über Kong `:32776/status`.

### Phase C — Abnahme „Prod-URL“

6. `CORE_BASE_URL` auf die **tatsächlich** von außen erreichbare Basis setzen (Domain oder `http://VPS_IP:32776` falls so betrieben).
7. `run_vollkreis_abnahme.py` komplett — **A** und **G** müssen gegen dieselbe Basis konsistent sein.

### Phase D — Backlog (getrennt ticketisieren)

8. Anti-Heroin-VPS: Deploy-Spiegel vs. Doku, `[PASS]` definieren.
9. OpenClaw / WhatsApp / Macro / MCP: je eigener messbarer Exit (nicht mit Kong-Deck vermischen).

---

## 4. Rollen

| Wer | Was |
|-----|-----|
| **Marc** | `/etc/default/omega-backend`, Operator-Abnahme vor riskanten Kong-Änderungen, `CORE_BASE_URL` für Prod-Runs |
| **Agent (lokal)** | Skripte ausführen, Doku/Tests pflegen, **keine** Produktiv-Secrets erfinden oder loggen |
| **Cloud-Agent-Auswertung** | Kann **aktueller** sein als einzelne Chat-Sessions — immer mit Repo-Stand vergleichen |

---

## 5. Änderungen am Repo (dieser Nachschub)

- `run_vollkreis_abnahme.py`: Block **G** Agent-Pool nutzt **`CORE_BASE_URL`** wie Block **A** (`curl -sk`, Timeout 10).
- `OMEGA_BACKEND_VPS_SYSTEMD.md`: Abgrenzung **Loopback-Skript** vs. **Kong Proxy /status** vs. **`CORE_BASE_URL`**.

---

[PASS] Plan konsistent mit Verkehrsplan, Kong-README und Vollkreis-Skript.
