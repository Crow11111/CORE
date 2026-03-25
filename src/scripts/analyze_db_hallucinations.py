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

async def run_query(sql: str):
    ssh_key, vps_host, vps_user, docker_cmd = get_ssh_config()
    ssh_cmd = [
        "ssh", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=15",
        "-i", ssh_key, f"{vps_user}@{vps_host}", docker_cmd,
    ]
    process = subprocess.run(
        ssh_cmd,
        input=sql.encode("utf-8"),
        capture_output=True,
        timeout=60
    )
    if process.returncode != 0:
        return False, process.stderr.decode("utf-8")
    return True, process.stdout.decode("utf-8")

async def analyze_hallucinations():
    # 1. Gesamtanzahl
    _, out = await run_query("SELECT count(*) FROM multi_view_embeddings;")
    print(f"Gesamtanzahl Einträge: {out.strip()}")

    # 2. Suche nach KI-Mustern
    patterns = [
        "Vielen Dank",
        "Ich hoffe",
        "Zusammenfassend",
        "Zusammenfassung",
        "Helfen",
        "Fragen",
        "KI-Modell",
        "Künstliche Intelligenz",
        "Hier ist",
        "Gern geschehen"
    ]

    print("\n--- Analyse der KI-Muster ---")
    for p in patterns:
        sql = f"SELECT count(*) FROM multi_view_embeddings WHERE document ILIKE '%{p}%';"
        ok, out = await run_query(sql)
        count = out.strip().split("\n")[-2].strip() if ok else "ERROR"
        print(f"Muster '{p}': {count} Treffer")

    # 3. Stichprobe der Treffer (Top 10)
    print("\n--- Stichprobe (Top 10 Treffer mit 'Hier ist' or 'Zusammenfassung') ---")
    sql = """
    SELECT created_at, left(document, 150) as snippet, source_collection 
    FROM multi_view_embeddings 
    WHERE (document ILIKE '%Hier ist%' OR document ILIKE '%Zusammenfassung%')
      AND created_at < '2026-03-23'
    ORDER BY created_at DESC 
    LIMIT 10;
    """
    ok, out = await run_query(sql)
    print(out)

    # 4. Vergleich Legacy vs Neu
    print("\n--- Zeitliche Verteilung der gesamten DB (Wochen-Aggregation) ---")
    sql = """
    SELECT count(*), date_trunc('week', created_at) as week 
    FROM multi_view_embeddings 
    GROUP BY week ORDER BY week DESC;
    """
    ok, out = await run_query(sql)
    print(out)

if __name__ == "__main__":
    asyncio.run(analyze_hallucinations())
