# WhatsApp Closed-Loop (OC Admin Integration)

**Vektor:** 2210 (CORE) | 2201 (CORE)
**Resonance:** 0221 | Delta: 0.049
**Status:** IMPLEMENTIERT (Vollkreis geschlossen)

## 1. Übersicht
Die WhatsApp-Anbindung über die Evolution API wurde von einer instabilen Einweg-Kommunikation zu einem robusten **Push-and-Pull-Vollkreis** refactored. OC Brain (VPS) fungiert dabei als "Admin" und kann autonom Nachrichten an den Operator (WhatsApp) senden (Push), während Anfragen vom Operator (@oc ...) verifiziert an OC Brain geleitet werden (Pull).

## 2. Die 5-Phase Engine im WhatsApp-Loop

### PULL-Szenario (WhatsApp -> OC Brain)
1. **TAKT 1 (Ansaugen):** `whatsapp_webhook.py` empfängt Nachricht mit `@oc`. Erzeugung einer eindeutigen `TraceID` (z. B. `WA-E3B077`).
2. **TAKT 2 (Verdichten):** Normalisierung durch `EntryAdapter`, Prüfung durch `Takt 0 Gate`.
3. **TAKT 3 (Arbeiten):** Weiterleitung an OC Brain via `openclaw_client.py`. OC Brain verarbeitet die Anfrage.
4. **TAKT 4 (Ausstoßen):** OC Brain Antwort wird von `whatsapp_webhook.py` übernommen und via `EvolutionClient` an WhatsApp gesendet. Die `TraceID` wird im Log mitgeführt.

### PUSH-Szenario (OC Brain -> WhatsApp)
1. **TAKT 1 (Ansaugen):** OC Brain sendet eine `rat_submission` oder einen Event-Push an den CORE-Webhook `POST /api/oc/webhook`.
2. **TAKT 2 (Verdichten):** CORE validiert die Einreichung und weist (falls nicht vorhanden) eine `TraceID` (z. B. `TEST-PUSH-4B26`) zu.
3. **TAKT 3 (Arbeiten):** CORE erkennt den Push-Bedarf (Typ `rat_submission` oder Topic `WhatsApp-Push`) und initiiere den Versand.
4. **TAKT 4 (Ausstoßen):** Versand via `EvolutionClient` an den Operator (`WHATSAPP_TARGET_ID`).

## 3. Verifikation (Test Harness)
Die Funktionalität wird durch `src/scripts/test_whatsapp_closed_loop.py` bewiesen.
Der Test-Harness simuliert beide Kanäle (Pull & Push) und verifiziert die korrekte Log-Ausgabe der Takt-Schritte (1-4).

## 4. Komponenten & Endpunkte

| Komponente | Rolle | Pfad |
|------------|-------|------|
| **EvolutionClient** | Physischer I/O (Takt 4) | `src/network/evolution_client.py` |
| **WhatsApp Webhook** | Pull-Einstieg (Takt 1) | `src/api/routes/whatsapp_webhook.py` |
| **OC Channel** | Push-Einstieg (Takt 1) | `src/api/routes/oc_channel.py` |
| **Test Harness** | Loop-Verifikation | `src/scripts/test_whatsapp_closed_loop.py` |

## 5. Axiom-Konformität (A5/A6)
Alle numerischen Felder in den Payloads (z. B. `audio_seconds`) werden durch die `resonance_membrane.py` gescannt, um sicherzustellen, dass keine boolschen Werte oder verbotene Symmetrien (0.0, 0.5, 1.0) in die Resonanz-Domäne gelangen.
