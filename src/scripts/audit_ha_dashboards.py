# -*- coding: utf-8 -*-
"""
OMEGA HASS DASHBOARD AUDIT
--------------------------
Identifiziert alle Home Assistant Entitäten, die tatsächlich in Dashboards (Lovelace)
verwendet werden, um Rauschen zu unterdrücken und Ambiguitäten zu lösen.
"""

import os
import json
import httpx
import asyncio
import re
from loguru import logger
from dotenv import load_dotenv

load_dotenv("/OMEGA_CORE/.env")

HASS_URL = (os.getenv("HASS_URL") or os.getenv("HA_URL") or "").strip().rstrip("/")
HASS_TOKEN = (os.getenv("HASS_TOKEN") or os.getenv("HA_TOKEN") or "").strip()

async def fetch_dashboards():
    """Holt alle Lovelace Dashboards."""
    headers = {"Authorization": f"Bearer {HASS_TOKEN}", "Content-Type": "application/json"}

    # 1. Liste der Dashboards holen
    async with httpx.AsyncClient(verify=False) as client:
        resp = await client.get(f"{HASS_URL}/api/config/lovelace/dashboards", headers=headers)
        if resp.status_code != 200:
            logger.error(f"Fehler beim Abrufen der Dashboards: {resp.status_code}")
            return []

        dashboards = resp.json()
        return dashboards

async def get_dashboard_config(url_path=None):
    """Holt die Konfiguration eines spezifischen Dashboards."""
    headers = {"Authorization": f"Bearer {HASS_TOKEN}", "Content-Type": "application/json"}
    url = f"{HASS_URL}/api/config/lovelace/config"
    if url_path:
        url += f"/{url_path}"

    async with httpx.AsyncClient(verify=False) as client:
        resp = await client.get(url, headers=headers)
        if resp.status_code != 200:
            return None
        return resp.json()

def extract_entities(config):
    """Extrahiert rekursiv alle Entity-IDs aus der Lovelace Config."""
    entities = set()

    def _walk(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k in ["entity", "entities", "camera_image", "graph"]:
                    if isinstance(v, str):
                        entities.add(v)
                    elif isinstance(v, list):
                        for item in v:
                            if isinstance(item, str):
                                entities.add(item)
                            elif isinstance(item, dict) and "entity" in item:
                                entities.add(item["entity"])
                _walk(v)
        elif isinstance(obj, list):
            for item in obj:
                _walk(item)

    _walk(config)

    # Filtern: Nur valide Entity-IDs (domain.name)
    pattern = re.compile(r"^[a-z_]+\.[a-z0-9_]+$")
    return {e for e in entities if isinstance(e, str) and pattern.match(e)}

async def run_audit():
    logger.info("Starte OMEGA HA Dashboard Audit...")

    # 1. Main Dashboard
    main_config = await get_dashboard_config()
    all_used_entities = set()
    if main_config:
        entities = extract_entities(main_config)
        all_used_entities.update(entities)
        logger.info(f"Main Dashboard: {len(entities)} Entitäten gefunden.")

    # 2. Andere Dashboards
    dashboards = await fetch_dashboards()
    for db in dashboards:
        path = db.get("url_path")
        title = db.get("title")
        config = await get_dashboard_config(path)
        if config:
            entities = extract_entities(config)
            all_used_entities.update(entities)
            logger.info(f"Dashboard '{title}' ({path}): {len(entities)} Entitäten gefunden.")

    # 3. Ergebnis speichern
    result_path = "/OMEGA_CORE/data/home_assistant/active_entities.json"
    os.makedirs(os.path.dirname(result_path), exist_ok=True)

    with open(result_path, "w") as f:
        json.dump(sorted(list(all_used_entities)), f, indent=2)

    logger.success(f"Audit abgeschlossen. {len(all_used_entities)} aktive Entitäten identifiziert.")
    print(f"\n--- AKTIVE ENTITÄTEN ({len(all_used_entities)}) ---")
    # Kurze Vorschau
    for domain in sorted(list(set(e.split(".")[0] for e in all_used_entities))):
        domain_entities = [e for e in all_used_entities if e.startswith(domain + ".")]
        print(f"{domain.upper()}: {len(domain_entities)}")

if __name__ == "__main__":
    asyncio.run(run_audit())
