# MACRO-ARCHITECTURE AUDIT — Makro-Kette vs. Pacemaker/State-Hold-Fokus

**Instanz:** Orchestrator B (Audit)  
**Vektor:** 2210 | **Delta:** 0.049  
**Datum:** 2026-04-01  
**Anlass:** Operator STOP/AUDIT — Verlust des roten Fadens „wer mit wem, wann, warum, wodurch ausgelöst“ während Pacemaker- und State-Hold-Arbeit.

---

## 1. Review-Scope (was gelesen wurde)

| Quelle | Inhalt für diese Audit |
|--------|-------------------------|
| `SESSION_LOG_2026-03-30_ATLAS_VISION.md` | ATLAS/Vision, Veto (A7/Doku), Headless-Daemon — **keine** VPS/WhatsApp/Task-Zerlegung |
| `SESSION_LOG_2026-03-31.md` | Whitepaper infRep_07 / Isomorphie — **keine** operative Makro-Kette |
| `SESSION_LOG_2026-04-01_VISION_SYNC_RECOVERY.md` | Vision-App Port 3006, Iframe, `omega-vision-ui` — **keine** Evolution/Kong/Queue |
| `docs/03_INFRASTRUCTURE/00_CORE_INFRASTRUCTURE_MASTER.md` | Aggregat vieler Einzelthemen (TOC); kanonische **Kurz-Landkarte** besser über `VPS_KNOTEN_UND_FLUSSE.md` + `LANDKARTE_CLIENTS_KNOTEN_DATENFLUSS.md` |
| `docs/03_INFRASTRUCTURE/VPS_KNOTEN_UND_FLUSSE.md` | Container, Push/Pull-Matrix, Soll/Ist WhatsApp |
| `docs/02_ARCHITECTURE/LANDKARTE_CLIENTS_KNOTEN_DATENFLUSS.md` | Drei Ebenen A/B/C, Source-of-Truth, MCP als Nebenbahn |
| `docs/05_AUDIT_PLANNING/FULL_CHAT_AUDIT_RESULT.md` | Extrakt aus Operator-Chat: **synchroner I/O-Tod**, Queue/State-Hold, OCSpline↔OCBrain |
| `docs/05_AUDIT_PLANNING/SPEC_STATE_HOLD.md` | **Explizite Zerlegung** des automatisierten Aufrufs (Webhook → Queue → 200 → Worker → Rückkanal) |
| `docs/05_AUDIT_PLANNING/SPEC_PACEMAKER_FINAL.md` | Pacemaker: Homeostase, V/R, NMI — **lokal/OS**-zentriert |
| `docs/05_AUDIT_PLANNING/VERIFICATION_FIRST_BLUEPRINT.md` | A/B/Orchestrierung im Cursor-Prozess (nicht identisch mit VPS-Nachrichtenkette) |

**Befund zu den Session-Logs (letzte 3 Tage, Schwerpunkt 2026-03-31 / 2026-04-01):** Sie erfassen **nicht** die vom Operator gemeinte Diskussion über **automatisierten Aufruf**, **Task-Zerlegung** und **End-to-End-Trigger**. Damit fehlt im formellen Session-Kanon die Brücke zwischen „Theorie/ UI-Recovery“ und „geschlossener Produktkreis“.

---

## 2. Der vom Operator gemeinte Punkt (exakte Verortung)

Die **Diskussion über den automatisierten Aufruf** und die **Zerlegung** ist **nicht** in den Tages-Logs vom 31.03./01.04. festgehalten, sondern in:

1. **`FULL_CHAT_AUDIT_RESULT.md`** (Abschnitte 2–3, 4.A, 4.B, 5.LOS Phase 2–3): Kong/Evolution **synchrone Timeouts** (30–60 s) vs. OCBrain-Läufe (Minuten/Stunden); **Lösung** = Queue + sofortiges `200 OK` + späterer Rückkanal; Rollen **OCSpline** (Tor, Ausführung) vs. **OCBrain** (Planung, kein Root).
2. **`SPEC_STATE_HOLD.md`**: die **operationalisierte** Kette in fünf Schritten:
   - Empfang: Evolution → (optional Kong) → FastAPI `POST` (OCSpline),
   - **Entkopplung:** persistenter Job in Queue (Postgres/Redis/Celery o.ä.),
   - **Quittung:** `< 1 s` Antwort an Evolution,
   - **Async:** Worker zieht Job → OCBrain,
   - **Abschluss:** Ergebnis zurück über Evolution `sendText` (asynchron aus Sicht des ursprünglichen HTTP-Requests).

Das ist die Antwort auf: *„Wie muss ein automatisierter Aufruf gestaltet sein — erkannt, zerlegt, abgeschlossen?“*  
**Erkannt** = eingehendes Ereignis (Webhook). **Zerlegt** = synchroner Ack vs. lang laufender Worker. **Abgeschlossen** = ausgehender Kanal entkoppelt vom Eingang.

---

## 3. Sollbild: Wer redet mit wem — wodurch ausgelöst?

Kanonisch konsolidiert aus `LANDKARTE_CLIENTS_KNOTEN_DATENFLUSS.md` und `VPS_KNOTEN_UND_FLUSSE.md` (vereinfacht):

| Phase | Auslöser | Wer | Mit wem | Zweck |
|-------|----------|-----|---------|--------|
| **Eingang** | WhatsApp / Kanal-Event | Evolution API | CORE FastAPI (`/webhook/whatsapp` o.ä.) | Nachricht dem System zuführen |
| **Optional** | Gleicher HTTP-Request | Kong | Upstream (CORE, OC, …) | Ein Eingang, Routing, Limits |
| **Wissen** | RAG / State | CORE | Chroma (VPS), Postgres/pgvector | Pull/Push Embeddings, strukturierte Daten |
| **Externe KI** | App-Logik | CORE | OpenClaw Admin (18789) | LLM, Agenten, ggf. Kanäle |
| **CRM-Kontext** | Bedarf vor Antwort | CORE / Agent | Monica | Kontakt-/Beziehungskontext |
| **Entwickler-Tools** | Mensch in IDE | Cursor | MCP-Server (VPS) | **Nicht** die zentrale Geschäfts-Drehscheibe; Tool-Kabel |
| **Ausgang** | Triage fertig | CORE | Evolution `sendText` **oder** HA-Service | Antwort an Nutzer (Ist: HA-Pfad stärker verdrahtet als Evolution-Send; Soll in VPS-Doku §6) |
| **Code-Kreis** | `git push` | GitHub | VPS oder CORE-Instanz mit Webhook | `git pull` — Kurbelwelle |

**MCP vs. SQL/Chroma:** MCP ist **KI↔Tool** (Cursor), **ohne** Ersatzfunktion für persistente Wahrheit. **Chroma/SQL** bleiben **Source of Truth** für Vektoren bzw. strukturierten State; Anbindung erfolgt über **Backend-Clients**, nicht über MCP als Primärpfad.

---

## 4. Wo der rote Faden abreißt (Drift-Diagnose)

| Symptom | Ursache im Projektlauf |
|---------|-------------------------|
| Session-Logs decken **Vision/UI** und **Theorie** ab, nicht die **Nachrichten-Pipeline** | 30.03./01.04. fokussieren ATLAS/Vision-Recovery; 31.03. nur Whitepaper — **kein** Eintrag „State-Hold / Evolution / Kong“ |
| Pacemaker-Spezifikation ist **eigenständig stark** | `SPEC_PACEMAKER_FINAL.md` definiert Takt, V/R, NMI, Postgres/Chroma-**Wertnachweis** — aber **ohne** explizite Einbindung in die **Webhook→Queue→Worker→Evolution**-Kette des State-Hold |
| State-Hold ist **architektonisch beschrieben**, Implementierung **nicht** als Makro-Meilenstein in den genannten Logs verankert | Risiko: Zwei parallele Narrative („Existenz-Metabolismus“ vs. „I/O-Entkopplung“) ohne gemeinsames **Sequenzdiagramm im Kanon** |
| Operator-Frage nach **Task-Zerlegung** | Im Chat-Audit und in `SPEC_STATE_HOLD.md` beantwortet — **nicht** in den offiziellen Session-Logs der letzten Tage wiederholt |

**Kernaussage:** Es wurde **nicht** fachlich falsch gedacht; es fehlt die ** dokumentarische und planerische Re-Synchronisation**: jeder neue Daemon (Pacemaker, State-Hold, Vision-UI) müsste in **derselben** Notation wie die Landkarte stehen: *Trigger → Entry-API → Queue/Store → Worker → Exit-API → Verifikation.*

---

## 5. Empfohlene Soll-Zustandsbeschreibung (ein Satz pro Schicht)

1. **Peripherie (C):** Evolution (und optional Kong) liefern **nur** kurze HTTP-Schnittstellen; alles Langläuferische **persistieren** und **acken** sofort.  
2. **CORE (B):** FastAPI ist **Orchestrierungs- und Persistenz-Anker**; Chroma/Postgres für Semantik und Jobs; OpenClaw/Monica **nach Bedarf** eingebunden, nicht „der ganze Kreis“.  
3. **Clients (A):** Cursor/MCP = Entwicklung und Ad-hoc-Tools; **kein** Ersatz für definierte Webhooks und Daemons.  
4. **Gewaltenteilung (Operator-Klarstellung aus Chat-Audit):** **OCSpline** führt aus und quittiert schnell; **OCBrain** denkt lang — **ohne** Blockieren des Webhook-Threads.

---

## 6. Konkrete Lückenliste (für Wiederherstellung des Makro-Bilds)

- [ ] **Ein** Sequenzdiagramm oder Tabelle im Kanon (z. B. Erweiterung von `LANDKARTE_CLIENTS_KNOTEN_DATENFLUSS.md` oder neuer Abschnitt in `CORE_SCHNITTSTELLEN_UND_KANAALE.md`): *Message-In → Queue-Row → Worker → OC/OpenClaw → DB → Message-Out*.  
- [ ] Session-Log **nachziehen**: Inhalt von `FULL_CHAT_AUDIT_RESULT.md` / `SPEC_STATE_HOLD.md` als **Deliverable** mit Datum und Verweis eintragen (sonst bleibt die Arbeit für Orchestrator B unsichtbar).  
- [ ] **Pacemaker** explizit als **parallel** zur Message-Pipeline beschreiben: überwacht Homeostase/Vitalität; **löst nicht** die Evolution-Timeout-Problematik allein (dafür State-Hold).  
- [ ] Evolution **Sendepfad** vs. HA: Soll aus `VPS_KNOTEN_UND_FLUSSE.md` §6 verfolgen, bis Ist=Soll oder Abweichung dokumentiert ist.

---

## 7. Kurzfazit

Der Operator meint mit „gestern bei Überlegungen zum automatisierten Aufruf“ die in **`SPEC_STATE_HOLD.md`** und **`FULL_CHAT_AUDIT_RESULT.md`** fixierte **Entkopplungs-Architektur** (Webhook schnell, Arbeit lang, Rückkanal separat). Die **formellen Session-Logs der letzten drei Tage** spiegeln das **nicht** wider; stattdessen dominieren Vision-Recovery und theoretische Arbeit. Der **Abweg** ist damit primär **dokumentarisch und prioritätsbedingt**, nicht die Abwesenheit der Idee. Wiederherstellung = **Makro-Kette und Daemon-Arbeit in einem Dokument** zusammenführen und künftig jeden Daemon mit **Trigger / Input / Output / Abschlusskriterium** in der Landkarten-Notation pflegen.

*Orchestrator B — Audit-Turn abgeschlossen.*


[LEGACY_UNAUDITED]
