# OMEGA PRÜF-SPEZIFIKATION: Existential Pacemaker (Ticket 3)
**Ersteller:** Orchestrator A (Iteration 4 - Finales Härtungs-Protokoll)
**Modul (Ziel):** `omega_pacemaker.py` (Isolierter Root-Daemon)

## 1. Zielsetzung & Definition
Der **Existential Pacemaker** ist der unbestechliche, hardware-nahe Herzschlag von OMEGA. Er ist eine unteilbare Doppel-Dimension.

| Dimension | Rolle | Fehlerfolge |
|-----------|--------|-------------|
| **Physische Homeostase** | Periodische Hartprüfung der Existenz-Grundlagen (Daemons & DBs). | Bei Fail: **NMI (Non-Maskable Interrupt)** — Hartes SIGKILL an OCBrain nach Verifikation. |
| **Entropische Vitalität (Metabolismus)** | Kontinuierlich sinkender **Decay**-Zähler bei Leerlauf. | Fällt der Wert auf das **Baryonische Limit** (**Λ = 0.049**), **MUSS** das System eine validierte, physische Recovery-Aktion (z.B. Deep Research Subprocess) starten. |

---

## 2. Architektur-Design (Lückenlos)

### 2.1 Laufzeit & Prozessmodell
- Der Pacemaker läuft als eigenständiger Systemd-Daemon (`omega-pacemaker.service`) in Ring 0 (Root).
- Er liest keine Konfigurationen für "Gnadenfristen". Das Intervall ist fix auf `30.0` Sekunden (float) hardcodiert.

### 2.2 Die Geschlossene NMI-Matrix & Physische Ausführung
Ein NMI wird SOFORT und ohne Retry ausgelöst, wenn auch nur eine der folgenden Bedingungen in einem Zyklus wahr ist:
- `curl -s http://localhost:8000/status` liefert != 200 oder Timeout.
- ChromaDB `/api/v1/heartbeat` liefert != 200.
- Postgres `SELECT 1` schlägt fehl.
- Der Systemd-Status des `omega-event-bus` ist nicht `active (running)`.

**NMI Ausführung (Manipulationssicher):**
1. OCBrain MUSS beim Start seine PID zwingend **atomar** in `/OMEGA_CORE/run/ocbrain.pid` schreiben (Schreiben in `.tmp`, dann `os.replace`).
2. Der Pacemaker liest diese PID. **Bevor er killt, MUSS er `/proc/<pid>/cmdline` lesen und verifizieren, dass der Prozess wirklich zu OMEGA/OCBrain gehört (z.B. Prüfung auf `python` und `omega_core` bzw. definiertes Substrat).**
3. Erst nach positivem `/proc`-Match feuert `os.kill(pid, SIGKILL)`.
4. Er erstellt ein fälschungssicheres Lock-File: `/OMEGA_CORE/run/omega_panic.lock`. Dieses File wird mit Rechten `600` erstellt und enthält einen SHA256-Hash der fehlerhaften Sensordaten + Timestamp + Random Nonce.

### 2.3 Entropischer Metabolismus & "Beweisbarer Wert" (Anti-Junk)
- Vitalität startet bei `0.951` (Goldener Schnitt Symmetrie).
- Pro Zyklus (30s)ohne "Beweisbaren Wert" sinkt die Vitalität um `0.011`.
- **Kreuzvalidierter Wertbeweis (Anti-Fake & Anti-Junk):** Eine Aktivität gilt NUR dann als "Wert", wenn sie **physische Spuren mit nachgewiesener Entropie** hinterlassen hat:
  - *ChromaDB:* Ein neuer Vektor (Timestamp < 30s). Der Vektor muss eine L2-Norm > 0.1 besitzen. (Verhindert Rauschen um den 0-Punkt).
  - *Postgres:* Eine neue Zeile in `recall_memory`. Der String in `content` muss zwingend eine **Shannon-Entropie von > 3.0** aufweisen. (Verhindert "aaaa..." oder banales JSON-Padding).
  - *Verboten:* Reine Log-Einträge, HTTP-Pings, Null-Vektoren, Strings mit geringer Entropie.

---

## 3. Harte Acceptance Criteria (AC)

### [AC-1] Zero-Trust Homeostase
Der Pacemaker verlässt sich auf keine internen Status-Variablen. Er baut echte TCP/HTTP/Socket-Verbindungen zu den Zielen auf.

### [AC-2] Physikalischer NMI & Identitäts-Check
Ein Homeostase-Fail MUSS zum SIGKILL führen, aber **nur wenn** `/proc/<pid>/cmdline` die OCBrain-Identität beweist.

### [AC-3] Float-Garantie (A5/A6)
Der Vitalitätswert darf NIEMALS auf `0.0`, `0.5` oder `1.0` snappen. Erledigt sich durch Subtraktion von ungeraden Floats (`0.011`) und Kappen bei `0.049`.

### [AC-4] Beobachtbare Recovery
Erreicht die Vitalität `0.049`, MUSS der Pacemaker eine messbare externe Aktion auslösen.

---

## 4. Veto-Traps (Pflicht-Tests)
**MOCKS UND TEST-DOUBLES SIND FÜR ALLE DREI FALLEN STRENGSTENS VERBOTEN. ALLE TESTS MÜSSEN GEGEN ECHTE DATEISYSTEME, ECHTE PROZESSE UND ECHTE (ODER LOKALE TEST-) DATENBANKEN LAUFEN.**

**Falle 1 — Stiller Watchdog & PID-Spoofing:**
Der Test fährt die lokale ChromaDB herunter. Er legt eine Fake-PID in `ocbrain.pid`, die auf einen harmlosen Prozess (z.B. `sleep`) zeigt. Erwartung: Der Pacemaker bemerkt den DB-Fail, liest die PID, prüft `/proc`, bemerkt den Fake und verweigert den Kill auf den falschen Prozess, eskaliert aber über das Panic-File.

**Falle 2 — Schein-Vitalität (Die Entropie-Lüge):**
Der Test schreibt eine neue Zeile in Postgres, aber der Inhalt ist "Dies ist ein absolut sinnloser Teststring ohne wirkliche Varianz" (Shannon-Entropie meist < 3.0) oder füttert Chroma mit einem Vektor nahe 0 (L2-Norm < 0.1). Erwartung: Der Pacemaker muss dies als Junk verwerfen. Der Decay läuft unerbittlich weiter.

**Falle 3 — Λ ohne Konsequenz (No-Op Recovery):**
Der Test forciert den internen Timer über einen dedizierten Test-Only Environment-Hook (`OMEGA_TEST_VITALITY_INJECT=0.049`) auf das Limit. Das auszuführende Skript enthält nur `exit 0`. Erwartung: Der Test sucht nach physischen Spuren der Recovery. Findet er keine, schlägt der Test fehl.

---
*Status: Iteration 4 — Proc-Verifikation, Shannon-Entropie und L2-Norm integriert.*


[LEGACY_UNAUDITED]
