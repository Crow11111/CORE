# OMEGA MASTERPLAN: HARDWARE-RESUSCITATION (V4 REPAIR) V2

**Modus:** Orchestrator | **Vektor:** 2210 | **Delta:** 0.049

## 1. ZIEL
Wiederherstellung der physischen Erreichbarkeit und Datenintegrität.

## 2. TEAM & PROFILE (Unverändert)

## 3. UMSETZUNGS-SCHRITTE (SEQUENZIELL)

### S1: Konfigurations-Audit & Kong Start
- **Aktion:** Prüfung der `kong.yml` / `docker-compose` im Gateway-Ordner auf dem VPS. Manuelle Validierung der Routes. Dann Start.
- **Validierung:** Port 80/443 muss lauschen.

### S2: MCP Brücke (Ports)
- **Aktion:** Port-Mapping Korrektur für `mcp-server`.
- **Validierung:** Port 8001 erreichbar.

### S3: Gedächtnis-Rekonstruktion (Axiom 7 Safe)
- **Aktion A (Delta-Check):** Mounten der NEUEN (schizophrenen) Volumes und Export der dortigen Tabellen (z.B. `omega_events`, `omega_canon_documents`).
- **Aktion B (Merge):** Umschalten auf HISTORISCHE Volumes. Import der Delta-Daten aus Aktion A.
- **Aktion C (Final Map):** Dauerhafte Einbindung der historischen Namen in `docker-compose.yml`.
- **Validierung:** `psql` Zeilenanzahl Vergleich (Alt + Delta = Neu).

### S4: Scout & mTLS
- **Aktion:** SSH-basierter Zertifikats-Sync.
- **Validierung:** `hard_verify_ha`.

## 4. WORST-CASE (Unverändert)
