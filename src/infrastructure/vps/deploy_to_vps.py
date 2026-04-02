# -*- coding: utf-8 -*-
"""
OMEGA CORE V4: VPS DEPLOYMENT SCRIPT
-----------------------------------
Status: PROTOTYPE | OMEGA_INFRA | V4
"""

import os
import paramiko
from dotenv import load_dotenv
from loguru import logger

load_dotenv("/OMEGA_CORE/.env")

def deploy():
    vps_host = os.getenv("VPS_HOST")
    vps_user = os.getenv("VPS_USER", "root")
    vps_key_path = os.getenv("VPS_SSH_KEY")

    if not vps_host or not vps_key_path:
        logger.error("VPS_HOST oder VPS_SSH_KEY fehlt in .env")
        return

    try:
        # 1. SSH Verbindung aufbauen
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        logger.info(f"Verbinde zu VPS {vps_host}...")
        ssh.connect(vps_host, username=vps_user, key_filename=vps_key_path)

        # 2. Dateien übertragen
        sftp = ssh.open_sftp()
        vps_dir = "/opt/omega/v4"
        ssh.exec_command(f"mkdir -p {vps_dir}")

        files_to_deploy = [
            "vps_setup.sh",
            "ebpf_watchdog.c"
        ]

        for f in files_to_deploy:
            local_path = f"/OMEGA_CORE/src/infrastructure/vps/{f}"
            remote_path = f"{vps_dir}/{f}"
            logger.info(f"Deploye {f} -> {remote_path}")
            sftp.put(local_path, remote_path)

        sftp.close()

        # 3. Setup Script ausführen
        logger.info("Starte Setup auf dem VPS...")
        stdin, stdout, stderr = ssh.exec_command(f"chmod +x {vps_dir}/vps_setup.sh && {vps_dir}/vps_setup.sh")

        # Output streamen
        for line in stdout:
            print(f"[VPS] {line.strip()}")

        err = stderr.read().decode()
        if err:
            logger.warning(f"[VPS-ERR] {err}")

        ssh.close()
        logger.info("Deployment abgeschlossen.")

    except Exception as e:
        logger.error(f"Deployment fehlgeschlagen: {e}")

if __name__ == "__main__":
    deploy()
