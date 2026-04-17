# Agent-Workpack: Messbare Abnahme (Doku-Sync + VPS-Nachweise)

**Datum:** 2026-04-05
**Orchestrator:** Ring 0 (Briefing)
**Umsetzung:** Producer (Code/Doku), optional O2 vor riskanten Architekturänderungen (hier: nur Doku + Verifikationspfade)

## Ziel

Lücken aus Operator-Feedback schließen: **keine falschen Ports in Kanon-Texten**, **eine kurze, kopierbare Verifikationsliste** für VPS (ohne „läuft alles“-Behauptung), **Inventar/Bibliothek konsistent**.

---

## Tasks (mit Abnahmekriterium)

| ID | Was | Dateien | Abnahme (PASS nur wenn erfüllt) |
|----|-----|---------|----------------------------------|
| **T1** | VPS-Chroma-Port in `CLAUDE.md` an **Vertrag** anbinden (32779, nicht 32768); kurzer Verweis auf `VPS_HOST_PORT_CONTRACT.md`. | `CLAUDE.md` | `rg '32768' CLAUDE.md` liefert **keinen** Treffer in der VPS/Chroma-Zeile; `32779` oder Verweis auf Vertrag vorhanden. |
| **T2** | Kurzdok **„VPS in 3 Befehlen prüfen“**: SSH optional; explizit `python -m src.scripts.verify_vps_stack`, Chroma-`curl` Heartbeat (Port aus Vertrag/`CHROMA_PORT`), Kong Admin `GET …/services` (nur Beschreibung, keine Secrets). | neu: `docs/03_INFRASTRUCTURE/VPS_SNAPSHOT_VERIFICATION.md` | Datei existiert; alle drei Prüfarten sind als Shell-Zeilen oder klar benannte Kommandos enthalten. |
| **T3** | Querverweis von `KANON_EINSTIEG.md` auf T2 (eine Tabellenzeile oder Bullet). | `KANON_EINSTIEG.md` | Link/Ziel `VPS_SNAPSHOT_VERIFICATION.md` lesbar. |
| **T4** | `CORE_INVENTORY_REGISTER.md` + `BIBLIOTHEK_KERN_DOKUMENTE.md` um Workpack + `VPS_SNAPSHOT_VERIFICATION.md` ergänzen. | beide | Neue Zeilen vorhanden. |
| **T5** | Anti-Heroin auf **alle** von Producer geänderten `.py` (falls keine `.py`-Änderung: auslassen mit Vermerk). | — | `validate_file(...)` für jede geänderte `.py` oder „keine py-Änderung“. **Producer:** keine `.py`-Dateien geändert — `anti_heroin validate_file` entfällt. |

---

## Verifikations-Bundle (Producer führt aus, Output hier unten eintragen)

```bash
cd /OMEGA_CORE
PYTHONPATH=/OMEGA_CORE .venv/bin/python -m src.scripts.verify_vps_stack
```

Optional (wenn Netzwerk/`.env` vorhanden):

```bash
PYTHONPATH=/OMEGA_CORE .venv/bin/python -m pytest tests/test_ticket_10.py -q --tb=no
```

---

## Ergebnis (Producer nach Umsetzung ausfüllen)

| Task | Status | Nachweis (1 Zeile) |
|------|--------|---------------------|
| T1 | ☑ | `CLAUDE.md`: Chroma 32779 + `VPS_HOST_PORT_CONTRACT.md`; `rg '32768' CLAUDE.md` → kein Treffer. |
| T2 | ☑ | `docs/03_INFRASTRUCTURE/VPS_SNAPSHOT_VERIFICATION.md` — (1) `python -m src.scripts.verify_vps_stack`, (2) Chroma-`curl` mit `VPS_HOST` + 32779/`CHROMA_PORT`, (3) Kong `GET …/services` Port 32777. |
| T3 | ☑ | `KANON_EINSTIEG.md` neue Tabellenzeile → `VPS_SNAPSHOT_VERIFICATION.md`. |
| T4 | ☑ | `CORE_INVENTORY_REGISTER.md` + `BIBLIOTHEK_KERN_DOKUMENTE.md` ergänzt (Workpack + Snapshot-Doc). |
| T5 | ☑ | Keine `.py`-Änderung — Anti-Heroin nicht ausgeführt (siehe Task-Tabelle). |

**Ausgabe verify_vps_stack (Auszug, letzte Zeilen):**

```
[OK] openclaw-admin
[OK] chroma-uvmy-chromadb
[OK] mcp-server
[OK] ha-atlas
[OK] (optional) evolution-api
[OK] (optional) monica
[OK] (optional) kong
  Container gesamt: 15
Kong Deck-Check: timed out
[OK] Chroma v2 heartbeat
[OK] (optional) Evolution API erreichbar
[OK] (optional) Monica erreichbar
[--] (optional) Kong nicht erreichbar
```

**Exit-Code:** `1` (Kong Admin-Deck-Check: Timeout / Kong optional nicht erreichbar; Chroma-Heartbeat OK).
