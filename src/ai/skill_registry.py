# -*- coding: utf-8 -*-
"""
SKILL REGISTRY: DEFERRED TOOL LOADING (V4)
------------------------------------------
Status: PROTOTYPE | OMEGA_SKILLS | V4
"""

import json
from typing import List, Dict, Any, Optional
from loguru import logger
from src.db.multi_view_client import search_multi_view, ingest_document

class SkillRegistry:
    def __init__(self):
        self.collection = "core_skills"

    async def register_skill(self, name: str, description: str, definition: dict):
        """Registriert ein Tool/Skill in der Archival Memory (ChromaDB)."""
        metadata = {
            "skill_name": name,
            "definition": json.dumps(definition),
            "is_skill": True
        }
        # Wir nutzen die Archival Memory für die Skill-Suche
        await ingest_document(
            document=f"Skill: {name}\nDescription: {description}",
            doc_id=f"skill_{name}",
            source_collection=self.collection,
            metadata=metadata
        )
        logger.info(f"[SKILL-REGISTRY] Skill registriert: {name}")

    async def get_relevant_skills(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Findet die relevantesten Skills für eine Query via semantischer Suche."""
        results = await search_multi_view(
            query=query,
            limit=limit,
            source_collection=self.collection,
            include_ai=True # Skills können vom System generiert sein
        )

        skills = []
        for res in results:
            meta = res.get("metadata")
            if isinstance(meta, str):
                try:
                    meta = json.loads(meta)
                except:
                    continue

            if meta and meta.get("skill_name"):
                skills.append({
                    "name": meta["skill_name"],
                    "definition": json.loads(meta["definition"]) if isinstance(meta["definition"], str) else meta["definition"],
                    "similarity": res.get("similarity", 0.0)
                })
        return skills

# Singleton
skill_registry = SkillRegistry()

# --- INITIAL SKILLS (BEISPIELE) ---
async def seed_initial_skills():
    """Initialisiert das System mit Standard-Skills."""
    # HA Control
    await skill_registry.register_skill(
        "ha_control",
        "Steuert Smart Home Geräte (Licht, Schalter, Szenen) in Home Assistant.",
        {
            "name": "ha_control",
            "parameters": {
                "type": "object",
                "properties": {
                    "entity_id": {"type": "string", "description": "Die HA Entity ID (z.B. light.bad)"},
                    "action": {"type": "string", "enum": ["turn_on", "turn_off", "toggle"]}
                },
                "required": ["entity_id", "action"]
            }
        }
    )
    # File System
    await skill_registry.register_skill(
        "file_system",
        "Liest oder schreibt Dateien im lokalen Dateisystem (OMEGA_CORE).",
        {
            "name": "file_system",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Relativer Pfad zur Datei"},
                    "operation": {"type": "string", "enum": ["read", "write", "delete"]},
                    "content": {"type": "string", "description": "Inhalt (nur bei write)"}
                },
                "required": ["path", "operation"]
            }
        }
    )
