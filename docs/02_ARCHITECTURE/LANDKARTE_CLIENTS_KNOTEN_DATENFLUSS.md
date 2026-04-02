# Landkarte: Clients, Knoten, Datenfluss (Push / Pull / Kreis)

**Vektor:** 2210 | **Delta:** 0.049  
**Zweck:** Aus dem „Gewusel“ (Cursor, Claude Desktop, ATLAS/KDE, VPS, MCP, SSH, HA, OpenClaw, Monica, Kong, …) **eine lesbare Ordnung** machen: wer macht was, wer zieht, wer drückt, wo der Kreis **ohne Lücke** geschlossen ist.

**Detail-Tiefen:**  
- VPS-Container und Tabellen: `@docs/03_INFRASTRUCTURE/VPS_KNOTEN_UND_FLUSSE.md`  
- Tesserakt, Webhooks, Kurbelwelle: `@docs/02_ARCHITECTURE/CORE_SCHNITTSTELLEN_UND_KANAALE.md`  
- Git-Sync-Kreis: `@docs/02_ARCHITECTURE/G_CORE_CIRCLE.md`  
- MCP vs. Drehscheibe: `@AGENTS.md` (Abschnitt MCP / Skills)

---

## 1. Drei Ebenen (ein Bild im Kopf)

| Ebene | Typische Maschine / Software | Rolle in einem Satz |
|-------|------------------------------|---------------------|
| **A – KI-Clients** | Cursor, Claude Desktop, Browser, ATLAS-Plasmoid (KDE/CachyOS) | **Mensch ↔ Modell ↔ Tools**; sie **starten** Arbeit, **lesen** Repo/Logs, rufen **APIs** oder **MCP** auf. Sie sind **nicht** die Datenbank der Wahrheit. |
| **B – OMEGA / CORE-Laufzeit** | Dreadnought: FastAPI `:8000`, Daemons (`omega-*`), lokales Repo `/OMEGA_CORE` | **Geschäftslogik**: Webhooks, Takt 0, Gravitator, Chroma/PG-Clients, HA, OpenClaw-Bridge. **Hier** laufen die meisten Push/Pull-Entscheidungen in Code. |
| **C – VPS & Peripherie** | Hostinger-Docker (Chroma, OC Admin/Spine, Evolution, Postgres, Kong, Monica, MCP-Server …), Scout-HA | **Persistenz + Brücken**: Vektoren, CRM, Gateway, WhatsApp-Instanz, optional zentraler API-Eingang (Kong). **SSH** ist Admin-/Deploy-Pfad, nicht der semantische Kern des Produkts. |

**Merksatz:** Clients **denken mit** und **triggern**; Backend **führt aus**; VPS **hält Zustand** und **empfängt/sendet** nach außen.

---

## 2. Wer ist „Source of Truth“ für was?

| Domäne | Quelle der Wahrheit | Wer synchronisiert |
|--------|---------------------|-------------------|
| **Anwendungscode & Docs** | Git-Remote (z. B. GitHub) + lokaler Clone auf Dreadnought | Du/Cursor: commit/push; VPS/Webhook: pull (siehe Kurbelwelle). |
| **Vektor-State (RAG, Anker)** | ChromaDB (lokal oder VPS `chroma-uvmy`) | Backend-Ingest / Queries; nicht „das MCP-Gefühl“. |
| **Strukturierter Text / Multi-View** | PostgreSQL (+ pgvector) auf VPS (`atlas_postgres_state`) | `multi_view_client` & Co.; Backend. |
| **Smart-Home-Fakten** | Home Assistant (primär **Scout** im LAN) | Event-Bus, `ha_client`, Webhooks Richtung CORE. |
| **WhatsApp-Session / Kanal** | Evolution API (VPS) **oder** HA-Pfad (je nach Config) | Eingehend Webhook → CORE; ausgehend API/HA-Service (Ist/Soll: `VPS_KNOTEN_UND_FLUSSE.md` §6). |
| **Externe KI mit Kanälen (OC)** | OpenClaw **Admin** (Gateway), optional Spine | CORE ruft OC an; OC kann Callbacks/Webhooks spiegeln — Details: `OPENCLAW_ADMIN_ARCHITEKTUR.md`. |

Wenn zwei Stellen **dieselbe** Information halten (z. B. alter ATLAS-Chroma + `chroma-uvmy`), ist das **technische Schuld** bis zur Migration — die Landkarte sagt nur: **ein** Soll pro Domäne.

---

## 3. Die Spieler kurz benannt

| Name im Alltag | Was es wirklich ist | Typische Bindung |
|------------------|----------------------|------------------|
| **Cursor** | IDE + eingebetteter KI-Agent | Lokales Repo, Terminal, optional **MCP** → VPS-Tools, **kein** Ersatz für Backend. |
| **Claude Desktop** | Separater KI-Client (Anthropic) | Eigene MCP-Config; spricht **nicht automatisch** mit deinem FastAPI-Backend, außer du baust URL/Tools explizit. |
| **ATLAS (KDE)** | Plasmoid `atlas-omega-voice/` | HTTP zum **OMEGA-Backend** (`CORE_API_URL`), Voice/TTS — siehe `ATLAS_OMEGA_VOICE_PLASMOID.md`. |
| **MCP** | Protokoll **KI ↔ Tool-Server** | Z. B. Cursor startet Prozess/SSH zu VPS: **Tools** (Dateien, Chroma-Query), **nicht** die zentrale App-Router-Drehscheibe aller Dienste (`AGENTS.md`). |
| **SSH** | Transportschicht für Admin | `git pull` auf VPS, Docker, `verify_vps_stack`, Deploy — **kein** Ersatz für definierte HTTP-APIs im Betrieb. |
| **OpenClaw Admin / „Brain“** | OC-Gateway: LLM, RAG, WhatsApp (Baileys), Agenten | Port `18789`; CORE-Client in `openclaw_client`. |
| **Monica** | CRM | Kontext für Anrede/Beziehung; Pull bei Bedarf. |
| **Kong** | API-Gateway | Optional ein Host für viele Backend-Services; Routing statt N Ports im Kopf. |
| **HA (Scout)** | Heim-Automatisierung | Push von Events, Pull von States, ggf. WhatsApp-Rest-Pfad. |

---

## 4. Push / Pull — vereinfachte Matrix

**Pull** = ich hole Daten/Status. **Push** = ich schreibe/send aktiv.

| Von | Nach | Richtung | Inhalt (Beispiel) |
|-----|------|----------|-------------------|
| Chroma / Postgres (VPS) | CORE Backend | **Pull** | Embedding-Suche, Multi-View-Rows |
| CORE Backend | Chroma (VPS) | **Push** | Ingest, StateAnchor-Update |
| Evolution / HA | CORE | **Push** (Webhook) | Neue Nachricht, Event |
| CORE | Evolution / HA | **Push** | Antwortnachricht, Service-Call |
| GitHub | VPS oder CORE-Instanz | **Push** (Webhook) | `push` → `git pull` |
| CORE / Du | GitHub | **Push** | `git push` nach Änderung |
| OpenClaw | CORE | **Pull** (CORE fragt) / **Push** (Callback) | Chat, RAG, Spiegelung |
| Monica | CORE | **Pull** | Kontakte |
| Cursor (MCP) | VPS MCP-Server | **Pull/Push** | Tool-Ops im Workspace — **Nebenbahn** zu Produkt-APIs |
| ATLAS | CORE `:8000` | **Pull/Push** | Chat/TTS wie normale API |

Die **vollständige** Container-Tabelle steht in `VPS_KNOTEN_UND_FLUSSE.md` (Abschnitte 2–3).

---

## 5. Wo schließt sich der Kreis? („OS atmet“)

Ohne Rückkopplung **stirbt** der Prozess im Trichter (nur hinlegen, nie verifizieren).

| Kreis | Minimal-Bedingung | Prüfung |
|-------|---------------------|---------|
| **Code-Kurbelwelle** | Lokal bearbeiten → push → Webhook → pull auf Zielhost | `G_CORE_CIRCLE.md`, GitHub Payload-URL, `GIT_PULL_DIR` |
| **Nachrichten** | Eingehend Webhook erreichbar **und** ausgehend Sendepfad konfiguriert | E2E-Test Evolution oder HA-Doku |
| **Wissen** | Ingest in Chroma **und** Query aus demselben Cluster wie Soll | `verify_multiview_pg` / Integritäts-Skripte |
| **Bedienung** | ATLAS/Cursor zeigen **dieselbe** API-Basis wie laufendes Backend | `curl localhost:8000/status`, Plasmoid-URL |

**Fazit:** „Atmen“ = **geschlossene Schleife mit messbarem Echo** (HTTP 200, Log-Zeile, Test grün) — nicht die Anzahl installierter Apps.

---

## 6. Intuition vs. Plan

| Intuitiv (oft passiert) | Plan (strukturiert) |
|-------------------------|---------------------|
| Noch einen Container „weil cool“ | Eintrag in `VPS_KNOTEN_UND_FLUSSE.md`: Zweck, Port, wer pullt/pusht |
| Noch einen KI-Client | Klar: **welche URL**, **welche Secrets**, **welcher Kanal** (MCP vs. REST) |
| MCP = „die Cloud“ | MCP = **Tool-Kabel**; Datenhoheit bleibt bei DB + Backend |
| Alles über SSH | SSH für Ops; **API-Verträge** für wiederkehrende Automatisierung |

---

## 7. Nächster Schritt bei Chaos

1. **Ein** laufendes Backend (`:8000`) und **ein** definierter Chroma/PG-Zielort.  
2. `VPS_KNOTEN_UND_FLUSSE.md` mit der Realität abgleichen (`docker ps` / `verify_vps_stack`).  
3. Pro neuem Spieler: eine Zeile in Abschnitt **3** dieser Datei + Verweis in die VPS-Tabelle.  

Damit bleibt die Intuition (rückwärts sinnvoll) **ankerbar** im Kanon, ohne jedes Mal neu zu raten.


[LEGACY_UNAUDITED]
