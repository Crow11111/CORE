# Kernarbeiter-Orientierung (Soll vs. Ist, Werkzeuge, Fundorte)

**Zweck:** Jeder Kernarbeiter (Mensch oder Agent) hat **ohne** vollständiges Durchlesen des Repos einen **groben Kompass**: was ist **Plan/Kanon**, was ist **Laufzeit/Realität**, welche **Artefakte** sind verbindlich, wo **Konflikte** auflösen.

**Nicht-Ziel:** Ersatz für `verify_vps_stack`, Abnahmeskripte oder Operator-Entscheid — sondern **Orientierung**.

---

## 1. Zwei semantische Schichten (Chroma)

| Schicht | Collection | Inhalt (grob) | Quelle der Wahrheit auf der Platte |
|--------|------------|---------------|-------------------------------------|
| **Soll / Kanon** | `core_canon` | Am **Resonanz-Anker** registrierte Dokumente (Chunk-RAG) | `omega_canon_documents` + `sync_omega_canon_registry` |
| **Ist / Lauffläche** | `core_operational` | Ports, Kong/MCP, Knoten, Messbarkeit, Einstiege — **kuratiert** | `KERNARBEITER_SURFACE_PATHS.yaml` + `ingest_omega_operational_chroma` |

**Warum zwei?** Der **Plan** (Kanon, Tickets, Architektur-Soll) deckt **nicht** 1:1 die **messbare Realität** (tatsächliche Ports, Container, Drift). Semantische Suche über **eine** gemischte Collection würde Soll und Ist verkleistern — deshalb **zwei Collections**.

**Bei Widerspruch:** Zuerst **Zahlen-Vertrag** und **Live-Checks** (`VPS_HOST_PORT_CONTRACT.md`, `vps_public_ports.py`, `verify_vps_stack`, Snapshot-Doku) — dann narrative Doku. Chroma liefert **Einstieg**, nicht das Urteil.

### Zero-Trust (für jeden Nutzer sichtbar)

Chroma-Treffer sind **nie** ohne Prüfung „wahr“. **`query_canon_semantic`** / **`query_operational_semantic`** liefern im JSON immer **`zero_trust_notice`**. Vor jeder Entscheidung: **Quelldatei** anhand `repo_path` lesen; **Zahlen** gegen Vertrag/Skripte/Live-System.

---

## 2. PostgreSQL (strukturiert)

| Tabelle / Nutzung | Zweck |
|-------------------|--------|
| `omega_canon_documents` | Index: welche Pfade gehören zum **Kanon** (mit Hash, Rolle) |
| `omega_events` | Episodisch / Audit (nicht Kanon-Volltext) |

**Sync Kanon:** `python -m src.scripts.sync_omega_canon_registry`
**MCP:** `list_canon_documents`, `get_orchestrator_bootstrap`, `get_episodic_history`, `record_event`

---

## 3. Chroma (semantisch)

| Aktion | Befehl / Tool |
|--------|----------------|
| Soll indexieren | `python -m src.scripts.ingest_omega_canon_chroma` (nach PG-Sync; optional `OMEGA_CANON_CHROMA_AFTER_SYNC=1`) |
| Ist indexieren | `python -m src.scripts.ingest_omega_operational_chroma` |
| Soll abfragen | MCP **`query_canon_semantic`** → `core_canon` |
| Ist abfragen | MCP **`query_operational_semantic`** → `core_operational` |
| Generisch | MCP **`query_chromadb`** (`core-chromadb`) mit `collection_name=…` |

Collections anlegen (VPS): `python -m src.scripts.create_chroma_collections_vps`

---

## 4. Kurzfokus für den Alltag

1. **Einstieg menschlich:** `KANON_EINSTIEG.md` → dann diese Datei.
2. **Agent Pre-Flight:** `get_orchestrator_bootstrap` + bei Bedarf **`query_operational_semantic`** (Ist) und **`query_canon_semantic`** (Soll).
3. **Regeln / Gewaltenteilung:** `.cursorrules`, `OMEGA_RESONANCE_ANCHOR.md` (Kontext Kanon).
4. **Drift erkennen:** Abgleich Doku ↔ `docker ps` / Vertrag (siehe Snapshot-Doku).

---

## 5. Pflege

- Neue **betriebskritische** SSoT-Datei → Eintrag in **`docs/00_STAMMDOKUMENTE/KERNARBEITER_SURFACE_PATHS.yaml`** + erneut **`ingest_omega_operational_chroma`**.
- Neue **Kanon**-Datei → Anker + **`sync_omega_canon_registry`** + **`ingest_omega_canon_chroma`**.
- **Inventar:** `CORE_INVENTORY_REGISTER.md` bei neuen Skripten/Pfaden.

---

[PASS] Zwei-Schichten-Modell dokumentiert; YAML ist maschinenlesbare Quelle für `core_operational`.
