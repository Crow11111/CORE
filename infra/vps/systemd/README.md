# systemd — VPS

| Unit | Zweck |
|------|--------|
| `omega-core-anti-heroin.service` | Oneshot: `run_anti_heroin_scan.py` gegen `/opt/omega-core-mirror` |
| `omega-core-anti-heroin.timer` | Täglich (mit RandomizedDelaySec) |
| `omega-backend.service` | FastAPI Omega-Runtime: `uvicorn src.api.main:app` auf Host-Port **32800** (`/opt/omega-backend`) |
| `omega-backend.env.template` | Vorlage für `/etc/default/omega-backend` (nur Kommentare im Repo; keine Secrets) |

**Omega-Backend:** `docs/03_INFRASTRUCTURE/OMEGA_BACKEND_VPS_SYSTEMD.md` · Deploy: `python -m src.scripts.vps_deploy_omega_backend`

**Install (Anti-Heroin):** vom Rechner mit SSH-Zugang zu `root@$VPS_HOST`:

```bash
cd /OMEGA_CORE
.venv/bin/python -m src.scripts.vps_deploy_anti_heroin_mirror
```

Voraussetzung: `VPS_HOST`, optional `VPS_SSH_KEY` in `.env` (oder SSH-Agent ohne `-i`).

**Log auf dem VPS:** `/var/log/omega-core-anti-heroin.log`
**Spiegel:** nur `src/` nach `/opt/omega-core-mirror/src/` (rsync, `--delete`).
