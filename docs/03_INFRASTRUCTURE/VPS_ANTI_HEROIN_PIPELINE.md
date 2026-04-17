# VPS: Anti-Heroin-Scanner (verpflichtende Integritätsprüfung)

**Status:** Umsetzbar — **Deploy vom Rechner mit SSH-Key** (Dreadnought o. ä.)
**Mandat:** `MASTER_UMSETZUNG_VPS_PROD_OHNE_DREAD_2026-04-06.md` §3

## Was liegt vor (Skript + Unit + Deploy + pytest)

| Artefakt | Funktion |
|----------|----------|
| `src/scripts/run_anti_heroin_scan.py` | Ein Eintrag für **lokal**, **Vollkreis Block I** und **VPS** — `validate_file` über `src/**/*.py` |
| `tests/test_run_anti_heroin_scan.py` | pytest: `scan_project` auf dem echten Repo → Exit 0 |
| `infra/vps/systemd/omega-core-anti-heroin.service` | systemd **oneshot** |
| `infra/vps/systemd/omega-core-anti-heroin.timer` | **täglich** |
| `src/scripts/vps_deploy_anti_heroin_mirror.py` | **rsync** `src/` → `/opt/omega-core-mirror/src/`, Units nach `/etc/systemd/system/`, `daemon-reload`, Timer **enable**, sofortiger Lauf |

**Vollkreis:** Block **I** ruft `python -m src.scripts.run_anti_heroin_scan --root <PROJECT_ROOT>` auf — identisch zur VPS-Logik.

## Einmaliger Deploy auf den VPS

Auf einer Maschine, die **per publickey** als `root@$VPS_HOST` darf:

```bash
cd /OMEGA_CORE
export VPS_HOST=…           # oder in .env
export VPS_SSH_KEY=…        # optional, sonst Standard-Agent
.venv/bin/python -m src.scripts.vps_deploy_anti_heroin_mirror
```

- **Kein** vollständiges Git-Repo auf dem VPS nötig — nur der **src/-Spiegel** (Python-stdlib reicht).
- Log: **`/var/log/omega-core-anti-heroin.log`**
- Konfiguration: **`/etc/default/omega-core-anti-heroin`** (`OMEGA_MIRROR_ROOT`)

## Abnahme (Zero-Trust)

1. Deploy-Befehl oben: Endausgabe **`[PASS] VPS: Spiegel + systemd timer + Scan Exit 0`**
2. Auf dem VPS: `journalctl -u omega-core-anti-heroin.service -n 30 --no-pager`
3. Lokal: `pytest tests/test_run_anti_heroin_scan.py -q`

**Hinweis:** Umgebungen **ohne** SSH-Zugang (z. B. ferner CI-Agent ohne Key) können das Deploy-**Skript** bereitstellen, aber nicht „wahr“ grün melden — der Nachweis ist immer **Exit 0 + Log auf dem VPS**.

### Cursor / IDE: `Permission denied (publickey)`

Wenn die Shell **`VPS_SSH_KEY=`** (leer) exportiert, würde `load_dotenv(..., override=False)` den Wert aus `.env` **nicht** übernehmen — SSH nutzt dann den falschen Identitätsweg. **`vps_deploy_anti_heroin_mirror.py`** lädt `.env` mit **`override=True`** (wie `verify_vps_stack.py`). Trotzdem prüfen: `VPS_SSH_KEY` in `.env` = existierende Datei auf dem **lokalen** Rechner (z. B. `/home/…/.ssh/id_ed25519_hostinger`).

### Remote-Befehle / `subprocess` (OpenSSH)

**Symptom:** Remote-stderr z. B. `mkdir: missing operand`, obwohl lokal `ssh root@host 'mkdir -p /var/log && echo OK'` funktioniert.

**Ursache:** Der SSH-Client fasst die Argumente **nach dem Host** zu **einer** Remote-Command-Zeile zusammen (Leerzeichen dazwischen, ohne zusätzliches Shell-Quoting). Übergibt man aus Python `["sh", "-c", "mkdir -p /var/log && echo OK"]`, landet auf dem Server effektiv die Zeile `sh -c mkdir -p /var/log && echo OK`. Für `sh -c` ist das Skript-Argument nur das nächste Wort — hier `mkdir` — der Rest wird falsch zugeordnet; `mkdir` läuft ohne Verzeichnisoperand.

**Strategie im Deploy-Skript:** Statt `sh` und `-c` als **getrennte** Listenelemente zu übergeben, wird **genau ein** Remote-String übergeben (analog zur zsh-Form mit einem einzigen zitierten Argument). Hilfsfunktion `_ssh_remote_shell` dokumentiert das invariant.

## Verweise

- `src/logic_core/anti_heroin_validator.py`
- `run_vollkreis_abnahme.py` (Block I)
- `infra/vps/systemd/README.md`
