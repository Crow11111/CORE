# ============================================================
# CORE – Strang B: Ollama auf VPS (Hostinger) installieren
# ============================================================
"""
Installiert Ollama auf dem OpenClaw-Admin-VPS (OPENCLAW_ADMIN_VPS_HOST).
- Install: curl -fsSL https://ollama.com/install.sh | sh
- Service: systemctl enable/start ollama, Port 11434
- Modell: ollama pull qwen2.5:7b (ressourcenschonend)
- Prüfung: curl http://localhost:11434/api/tags

Nutzung:
    python -m src.scripts.install_ollama_vps
    python -m src.scripts.install_ollama_vps --dry-run
    python -m src.scripts.install_ollama_vps --open-firewall   # Port 11434 von außen (optional)
"""
from __future__ import annotations
import argparse
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
import paramiko
from dotenv import load_dotenv

load_dotenv("c:/CORE/.env")

def _env(key: str, default: str = "") -> str:
    v = (os.getenv(key) or default).strip().strip('"').strip("'")
    return v

HOST = _env("OPENCLAW_ADMIN_VPS_HOST") or _env("VPS_HOST")
PORT = int(os.getenv("OPENCLAW_ADMIN_VPS_SSH_PORT") or os.getenv("VPS_SSH_PORT", "22"))
USER = _env("OPENCLAW_ADMIN_VPS_USER") or "root"
PASSWORD = _env("OPENCLAW_ADMIN_VPS_PASSWORD") or _env("VPS_PASSWORD")
KEY = _env("OPENCLAW_ADMIN_VPS_SSH_KEY") or _env("VPS_SSH_KEY")

OLLAMA_PORT = 11434
OLLAMA_MODEL = "qwen2.5:7b"  # ressourcenschonend; Alternative: mistral:7b-instruct
INSTALL_URL = "https://ollama.com/install.sh"  # offiziell; ollama.ai ggf. Redirect


def connect_ssh():
    if not HOST:
        print("FEHLER: OPENCLAW_ADMIN_VPS_HOST oder VPS_HOST in .env fehlt.")
        return None
    print(f"\n[SSH] {USER}@{HOST}:{PORT} ...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        if KEY and os.path.isfile(KEY):
            ssh.connect(HOST, port=PORT, username=USER, key_filename=KEY, timeout=15)
        else:
            ssh.connect(HOST, port=PORT, username=USER, password=PASSWORD or None, timeout=15)
        print("  OK")
        return ssh
    except Exception as e:
        print(f"  FEHLER: {e}")
        return None


def run(ssh, cmd, check=True, timeout_sec=60, long_running=False):
    """Führt Befehl aus. long_running=True: liest stdout/stderr in Loop bis Ende."""
    chan = ssh.get_transport().open_session()
    chan.settimeout(max(30, min(timeout_sec, 120)) if not long_running else 30)
    chan.exec_command(cmd)
    out = []
    err = []
    if long_running:
        while not chan.exit_status_ready():
            try:
                if chan.recv_ready():
                    out.append(chan.recv(65536).decode("utf-8", errors="replace"))
                if chan.recv_stderr_ready():
                    err.append(chan.recv_stderr(65536).decode("utf-8", errors="replace"))
            except (OSError, paramiko.SSHException):
                pass
            time.sleep(0.25)
    while chan.recv_ready():
        out.append(chan.recv(65536).decode("utf-8", errors="replace"))
    while chan.recv_stderr_ready():
        err.append(chan.recv_stderr(65536).decode("utf-8", errors="replace"))
    code = chan.recv_exit_status()
    stdout = "".join(out)
    stderr = "".join(err)
    if code != 0 and check:
        print(f"  exit={code} stderr: {(stderr or stdout)[:300]}")
    return code, stdout, stderr


def main():
    ap = argparse.ArgumentParser(description="Ollama auf VPS installieren (Strang B)")
    ap.add_argument("--dry-run", action="store_true", help="Kein SSH, nur Konfig ausgeben")
    ap.add_argument("--open-firewall", action="store_true", help="Port 11434 in ufw freigeben (optional)")
    args = ap.parse_args()

    report = {
        "installation_durchgefuehrt": False,
        "ollama_status": None,
        "api_tags_output": None,
        "modell": OLLAMA_MODEL,
        "port_11434_erreichbar": None,
        "fehler": None,
        "installationspfad": None,
        "service_status": None,
        "pull_exit_code": None,
        "pull_stderr": None,
    }

    if args.dry_run:
        print(f"DRY-RUN: Host={HOST}, User={USER}, Modell={OLLAMA_MODEL}, Port={OLLAMA_PORT}")
        print("  Install: curl -fsSL " + INSTALL_URL + " | sh")
        return 0

    if not HOST:
        report["fehler"] = "OPENCLAW_ADMIN_VPS_HOST/VPS_HOST fehlt in .env"
        print_report(report)
        return 1

    ssh = connect_ssh()
    if not ssh:
        report["fehler"] = "SSH-Verbindung fehlgeschlagen"
        print_report(report)
        return 1

    try:
        # 1) Prüfen ob Ollama bereits installiert
        code, out, _ = run(ssh, "which ollama 2>/dev/null && ollama --version 2>/dev/null || true", check=False)
        _, path_out, _ = run(ssh, "which ollama 2>/dev/null || echo ''", check=False)
        if path_out and path_out.strip():
            report["installationspfad"] = path_out.strip().split("\n")[0]
        if code == 0 and "ollama" in out:
            print("[Ollama] Bereits installiert:", out.strip()[:80])
        else:
            print("[Ollama] Installiere mit install.sh ...")
            code, out, err = run(
                ssh,
                f"curl -fsSL {INSTALL_URL} | sh",
                check=False,
                timeout_sec=120,
            )
            if code != 0:
                report["fehler"] = f"Install-Skript exit={code}: {(err or out)[:500]}"
                print_report(report)
                return 1
            report["installation_durchgefuehrt"] = True
            _, path_out, _ = run(ssh, "which ollama 2>/dev/null || echo ''", check=False)
            if path_out and path_out.strip():
                report["installationspfad"] = path_out.strip().split("\n")[0]

        # 2) Service starten (ollama.service wird vom Install-Skript angelegt)
        run(ssh, "systemctl enable ollama 2>/dev/null; systemctl start ollama 2>/dev/null; true", check=False)
        run(ssh, "sleep 2; systemctl is-active ollama 2>/dev/null || true", check=False)
        # Falls kein systemd oder Service fehlt: Ollama im Hintergrund starten
        run(ssh, "pgrep -x ollama >/dev/null || (nohup ollama serve >> /var/log/ollama.log 2>&1 &); sleep 4", check=False)
        _, svc_out, _ = run(ssh, "systemctl is-active ollama 2>/dev/null || echo 'no-systemd'", check=False)
        report["service_status"] = (svc_out or "").strip() or "unknown"

        # 3) Modell pullen (lange Laufzeit)
        print(f"[Ollama] Pull {OLLAMA_MODEL} (kann mehrere Minuten dauern) ...")
        code, out, err = run(ssh, f"ollama pull {OLLAMA_MODEL}", check=False, long_running=True)
        report["pull_exit_code"] = code
        report["pull_stderr"] = (err or out or "")[:500] if (err or out) else None
        if code != 0:
            report["fehler"] = f"ollama pull exit={code}: {(err or out)[:400]}"
            # Trotzdem api/tags prüfen (evtl. anderes Modell schon da)
        else:
            report["installation_durchgefuehrt"] = True

        # 4) Server anstoßen (ollama list startet ggf. Server), warten, dann api/tags
        run(ssh, "ollama list 2>/dev/null; systemctl start ollama 2>/dev/null; sleep 3; pgrep -x ollama >/dev/null || (nohup ollama serve >> /var/log/ollama.log 2>&1 & sleep 5)", check=False)
        code, out, err = run(ssh, f"curl -s --connect-timeout 10 http://127.0.0.1:{OLLAMA_PORT}/api/tags", check=False, timeout_sec=20)
        raw = (out or err or "").strip()
        report["api_tags_output"] = raw[:2000] if raw else "(leer)"
        if code == 0 and raw and ("models" in raw or "error" in raw.lower()):
            report["ollama_status"] = "ok"
            report["port_11434_erreichbar"] = "localhost"
        else:
            # Diagnose: ollama list, systemctl status, Port
            _, list_out, _ = run(ssh, "ollama list 2>&1 || true", check=False)
            _, st_out, _ = run(ssh, "systemctl is-active ollama 2>/dev/null || echo 'no-systemd'", check=False)
            report["api_tags_output"] = (report["api_tags_output"] or "") + "\n--- ollama list ---\n" + (list_out or "")[:500] + "\n--- systemctl --- " + (st_out or "").strip()
            report["ollama_status"] = "fehler"
            if not report["fehler"]:
                report["fehler"] = f"api/tags: exit={code}, body leer oder ungültig (curl empty?). ollama list/Service siehe api_tags_output."

        # 5) Firewall: 11434 nur lokal (Standard). Optional --open-firewall für gezieltes Öffnen.
        if args.open_firewall:
            run(ssh, f"ufw allow {OLLAMA_PORT}/tcp 2>/dev/null; ufw status 2>/dev/null | head -20", check=False)
            report["port_11434_erreichbar"] = "localhost und von außen (ufw)"
        elif report["port_11434_erreichbar"] is None:
            report["port_11434_erreichbar"] = "nur localhost (11434 nicht in ufw)"

    finally:
        ssh.close()

    print_report(report)
    return 0 if report["ollama_status"] == "ok" else 1


def print_report(report):
    print("\n" + "=" * 60)
    print("STRANG B – KURZBERICHT OLLAMA VPS")
    print("=" * 60)
    print("Installation durchgeführt:", report["installation_durchgefuehrt"])
    print("Ollama-Status:", report["ollama_status"])
    print("Modell:", report["modell"])
    print("Port 11434 erreichbar:", report["port_11434_erreichbar"])
    if report.get("installationspfad"):
        print("Installationspfad:", report["installationspfad"])
    if report.get("service_status"):
        print("Service-Status:", report["service_status"])
    if report["api_tags_output"]:
        print("api/tags (Auszug):")
        print(report["api_tags_output"][:800])
    if report.get("pull_exit_code") is not None:
        print("ollama pull exit:", report["pull_exit_code"])
    if report.get("pull_stderr"):
        print("ollama pull stderr (Auszug):", report["pull_stderr"][:400])
    if report["fehler"]:
        print("Fehler:", report["fehler"])
    print("=" * 60)
    print("\nFür OpenClaw-Provider (System-Architect): baseUrl=http://localhost:11434, Modell=", report["modell"])


if __name__ == "__main__":
    sys.exit(main())
