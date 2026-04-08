# -*- coding: utf-8 -*-
"""
Gemeinsamer Zero-Trust-Hinweis für alle Chroma-MCP-Tool-Antworten (stdio / State-Nexus).

Einheitlicher Text, damit `query_chromadb` und `query_*_semantic` dieselbe Semantik tragen.
"""

CHROMA_ZERO_TRUST_NOTICE = (
    "Chroma liefert nur Ähnlichkeits-Treffer (Vektorraum) — keine verifizierten Fakten. "
    "Pflicht: Text anhand Metadaten (repo_path/source_file) in der echten Datei prüfen; "
    "bei Zahlen/Ports zusätzlich VPS_HOST_PORT_CONTRACT / vps_public_ports / Live-Check (A7 Zero-Trust)."
)
