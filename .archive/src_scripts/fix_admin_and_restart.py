# Config in Admin-Pfad schreiben, openclaw-admin neustarten (Dashboard = Admin)
from __future__ import annotations
import os
import sys
import json
import base64
import paramiko
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
load_dotenv()

HOST = (os.getenv("OPENCLAW_ADMIN_VPS_HOST") or os.getenv("VPS_HOST") or "").strip()
USER = (os.getenv("OPENCLAW_ADMIN_VPS_USER") or os.getenv("VPS_USER") or "root").strip()
KEY = (os.getenv("OPENCLAW_ADMIN_VPS_SSH_KEY") or os.getenv("VPS_SSH_KEY") or "").strip().strip('"')
PWD = (os.getenv("OPENCLAW_ADMIN_VPS_PASSWORD") or os.getenv("VPS_PASSWORD") or "").strip().strip('"')
PORT = int(os.getenv("OPENCLAW_ADMIN_VPS_SSH_PORT") or os.getenv("VPS_SSH_PORT", "22"))
TOKEN = (os.getenv("OPENCLAW_GATEWAY_TOKEN") or "").strip().strip('"')

ADMIN_CONFIG_PATH = "/opt/core-core/openclaw-admin/data/openclaw.json"
SPINE_CONFIG_PATH = "/opt/core-core/openclaw-spine/data/openclaw.json"
FALLBACK_CONFIG = "/var/lib/openclaw/openclaw.json"


def run(ssh, cmd, timeout=30):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    code = stdout.channel.recv_exit_status()
    out = (stdout.read() or b"").decode("utf-8", errors="replace").strip()
    err = (stderr.read() or b"").decode("utf-8", errors="replace").strip()
    return code, out, err


def main():
    if not HOST or not USER:
        print("FEHLER: VPS_HOST und USER in .env")
        return 1

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        if KEY and os.path.isfile(KEY):
            ssh.connect(HOST, port=PORT, username=USER, key_filename=KEY, timeout=15)
        else:
            ssh.connect(HOST, port=PORT, username=USER, password=PWD or None, timeout=15)
    except Exception as e:
        print("SSH-Fehler:", e)
        return 1

    try:
        # 1) Config lesen (Admin-Container oder Host)
        code, raw, _ = run(ssh, f"docker exec openclaw-admin cat /home/node/.openclaw/openclaw.json 2>/dev/null || true")
        if not raw or len(raw) < 50:
            code, raw, _ = run(ssh, f"cat {ADMIN_CONFIG_PATH} 2>/dev/null || cat {FALLBACK_CONFIG} 2>/dev/null || true")
        if not raw or len(raw) < 50:
            print("FEHLER: Keine Config lesbar")
            return 1

        cfg = json.loads(raw)

        # 2) Gateway controlUi setzen (device identity required beheben)
        if "gateway" not in cfg:
            cfg["gateway"] = {}
        g = cfg["gateway"]
        g["controlUi"] = {
            "dangerouslyAllowHostHeaderOriginFallback": True,
            "allowInsecureAuth": True,
            "dangerouslyDisableDeviceAuth": True,
        }
        if TOKEN:
            g["auth"] = {"mode": "token", "token": TOKEN}
            g["remote"] = {"token": TOKEN}

        merged = json.dumps(cfg, indent=2, ensure_ascii=False)
        b64 = base64.standard_b64encode(merged.encode("utf-8")).decode("ascii")

        # 3) Auf Host schreiben: Admin, Spine, Fallback (Spine = Port 18790/Dashboard)
        for path in [ADMIN_CONFIG_PATH, SPINE_CONFIG_PATH, FALLBACK_CONFIG]:
            dir_oc = path.rsplit("/", 1)[0]
            run(ssh, f"mkdir -p {dir_oc}")
            run(ssh, f"echo '{b64}' | base64 -d > {path} && chmod 644 {path}")
            run(ssh, f"chown -R 1000:1000 {dir_oc} 2>/dev/null || true")
            print("  Geschrieben:", path)

        # 4) Beide Container neustarten (Admin + Spine; Spine = Dashboard auf 18790)
        for name in ["openclaw-admin", "openclaw-spine"]:
            code, out, err = run(ssh, f"docker restart {name} 2>&1")
            print("  docker restart", name + ":", out or err, "exit", code)

        # 5) Verifikation: Config im Container enthaelt controlUi.dangerouslyDisableDeviceAuth
        for container, label in [("openclaw-admin", "Admin"), ("openclaw-spine", "Spine")]:
            code, out, _ = run(ssh, f"docker exec {container} cat /home/node/.openclaw/openclaw.json 2>/dev/null | grep -A1 dangerouslyDisableDeviceAuth || true")
            if "true" in (out or ""):
                print("  [OK]", label, "liest dangerouslyDisableDeviceAuth: true")
            else:
                print("  [WARN]", label, "controlUi nicht gefunden – Mount-Pfad evtl. anders")
    finally:
        ssh.close()

    print("Fertig. Dashboard mit Token-URL neu laden; device identity sollte entfallen.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
