import asyncio
import os
import subprocess
from dotenv import load_dotenv

load_dotenv()

def get_ssh_config():
    key = os.getenv("VPS_SSH_KEY", "/home/mth/.ssh/id_ed25519_hostinger")
    host = os.getenv("VPS_HOST", "187.77.68.250")
    user = os.getenv("VPS_USER", "root")
    docker_cmd = "docker exec -i atlas_postgres_state psql -U atlas_admin -d atlas_state"
    return key, host, user, docker_cmd

async def query_last_postgres():
    ssh_key, vps_host, vps_user, docker_cmd = get_ssh_config()

    # SQL-Abfrage für die letzten Einträge aus core_directives
    sql = "SELECT created_at, doc_id, source_collection FROM multi_view_embeddings WHERE source_collection = 'core_directives' ORDER BY created_at DESC LIMIT 10;"

    ssh_cmd = [
        "ssh", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=15",
        "-i", ssh_key, f"{vps_user}@{vps_host}", docker_cmd,
    ]

    try:
        print(f"Verbinde zu {vps_host} via SSH...")
        process = subprocess.run(
            ssh_cmd,
            input=sql.encode("utf-8"),
            capture_output=True,
            timeout=30
        )

        if process.returncode != 0:
            print(f"FEHLER: psql Abfrage fehlgeschlagen (Returncode {process.returncode})")
            print(process.stderr.decode("utf-8"))
            return

        output = process.stdout.decode("utf-8")
        print("\n--- PostgreSQL Audit: Letzte Einträge in multi_view_embeddings ---")
        print(output)
        print("------------------------------------------------------------------")

    except Exception as e:
        print(f"Ein Fehler ist aufgetreten: {e}")

if __name__ == "__main__":
    asyncio.run(query_last_postgres())
