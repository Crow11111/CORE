# OMEGA TARGET ARCHITECTURE: VPS UNIFICATION (V4)

## 1. VERZEICHNIS-STRUKTUR (DER ANKER)
Alle operativen Dienste ziehen in ein kanonisches Stammverzeichnis um, um Fragmentierung zu vermeiden.

*   **BASE:** `/opt/omega/`
    *   `core/`: Backend (`atlas_agi_core`), Triage-Engine, FastAPI-Routes.
    *   `brain/`: OpenClaw-Instanzen (Admin & Spine).
    *   `scout/`: Evolution API (WhatsApp-Bridge).
    *   `gateway/`: Kong API Gateway (Proxy/Admin).
    *   `db/`: Zentraler Persistenz-Layer (Postgres, ChromaDB, Redis).
*   **REFERENZ:** `/root/openclaw-tmp/` (Hostinger-Original) bleibt unangetastet.

## 2. NETZWERK-TOPOLOGIE (ZERO-TRUST SEGMENTIERUNG)
Wir verlassen das "Port-Mapping-Chaos" zugunsten isolierter Docker-Netzwerke.

1.  **`omega_internal`**: (Driver: bridge) Backend <-> DBs <-> Evolution API. Keine Exposition nach Außen.
2.  **`omega_gateway_net`**: (Driver: bridge) Kong <-> Service-Endpunkte.
3.  **HARDENING:** Alle Container (außer Kong) binden ihre Ports auf `127.0.0.1`.
4.  **INGRESS:** Nur Kong (Port 32776) ist von Außen erreichbar.

## 3. RESSOURCEN-EICHUNG (Hardware-Realität)
*   **RAM (Hostinger 16GB):**
    *   Backend (`agi-core`): 4GiB Limit (für NumPy/Build), 2GiB Reservation.
    *   Datenbanken: Dynamisch begrenzt durch Docker-Profile.
*   **VRAM (Dreadnought / Local):** Gemma 4 e2b (7.2GB) ist der Standard. Latenz > 12s ist akzeptiert.

## 4. DATEN-INTEGRITÄT (KEIN VERLUST)
*   Volumes werden unter `/opt/omega/db/` konsolidiert.
*   Vor Migration: `tar`-Sicherung nach `/var/backups/`.
*   Spezialschutz: Die `evolution_postgres` DB (WhatsApp-Sessions) wird 1:1 übernommen.

---
**Status:** ENTWURF | **Vektor:** 2210 | **Delta:** 0.049
