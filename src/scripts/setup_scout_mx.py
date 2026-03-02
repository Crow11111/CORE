"""
Scout-MX-Kamera einbinden: setzt SCOUT_MX_SNAPSHOT_URL in .env.
Verwendet HASS_URL/HA_URL, HASS_TOKEN/HA_TOKEN; Entity-ID per --entity oder SCOUT_MX_ENTITY_ID.
Siehe set_scout_mx_snapshot_url für die Implementierung.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.scripts.set_scout_mx_snapshot_url import main

if __name__ == "__main__":
    main()
