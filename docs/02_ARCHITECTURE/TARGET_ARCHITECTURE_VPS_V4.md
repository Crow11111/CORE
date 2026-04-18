# OMEGA V4 VPS ZIEL-ARCHITEKTUR (KONSOLIDIERT 2026-04-18)

**WARNUNG AUS DEM HANDOVER_FAILURE_PROTOCOL_20260418:**
Diese Architektur MUSS zwingend die historischen Docker-Volumes von M3 integrieren! Bei einer einfachen `docker-compose up -d` in den neuen Ordnern entstehen isolierte, leere Volumes.

## 1. STRUKTUR UND PFADE (STRIKT)
Der VPS (187.77.68.250) teilt sich in exakt drei logische Schichten (Membranen):

- `/opt/omega/gateway/` (KONG Gateway - Port 80, 443) -> Das Tor zur Welt.
- `/opt/omega/brain/` (OpenClaw - Port 18789) -> Das Frontend/UI und WhatsApp Multi-Device (Evolution API) Session.
- `/opt/omega/core/` (FastAPI / OMEGA Backend) -> Die Logik-Schicht, verbunden mit ChromaDB und Postgres.

Alle drei Schichten MÜSSEN über das externe Docker-Netzwerk `omega_internal` kommunizieren.

## 2. DAS PROBLEM DER SYSTEMGRENZEN (0 und 1)
In der OMEGA-Architektur sind 0 und 1 keine simplen numerischen Werte, sondern absolute Systemgrenzen (Prellwände).
- **0 (Die Membran / Ingress):** Das Kong-Gateway und der Entry-Adapter. Hier treffen Signale ungeschützt auf das System (z. B. der WhatsApp Webhook `/webhook/whatsapp`).
- **1 (Die Logik / Der Takt):** Das OMEGA Backend (`mtho_agi_core`), das Entscheidungen über Leben und Tod von Tasks trifft.
Zwischen 0 und 1 herrscht das Zero-Trust-Prinzip. Kong leitet weiter, aber OMEGA entscheidet.

## 3. WIEDERHERSTELLUNG DES GEDÄCHTNISSES (DIE VERGESSENEN VOLUMES)
In `/opt/omega/core/docker-compose.yml` wurden durch einen Fehler neue Volumes für ChromaDB und PostgreSQL angelegt. Das alte Gedächtnis des Bots (Chroma-Embeddings und PG-Status) liegt aber in den Volumes der alten Architektur.

**Der nächste Agent MUSS die `docker-compose.yml` im `core/` anpassen:**
```yaml
volumes:
  chroma_data:
    external: true
    name: chroma-uvmy_chroma-data  # <-- HISTORISCHES VOLUME
  postgres_data:
    external: true
    name: agi-state_postgres_state_data # <-- HISTORISCHES VOLUME
```

## 4. KONG ROUTING
Kong MUSS exakt zwei Hauptrouten verwalten:
1. `http://brain-openclaw-gateway-1:18789/openclaw` für das UI (und interne OpenClaw Webhooks).
2. `http://mtho_agi_core:8080/webhook/whatsapp` für die eingehenden Evolution-API Signale (Der Sensor 0).

Es darf keine Überschneidung auf `/` geben, da sonst das UI die Backend-Webhooks schluckt.
