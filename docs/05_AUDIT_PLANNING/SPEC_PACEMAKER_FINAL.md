# OMEGA PRÜF-SPEZIFIKATION: Existential Pacemaker (Ticket 3)
**Ersteller:** Orchestrator A (Finaler Entwurf nach Best-of-N Cut + VETO-Fix)
**Modul (Ziel):** `omega_pacemaker.py` (Isolierter Root-Daemon)

## 1. Zielsetzung & Definition
Der **Existential Pacemaker** ist der unbestechliche, neuromorphe Herzschlag von OMEGA. Er vereint OS-Level Determinismus (Härte) mit biologischer Entropie (Pathologie-Erkennung).

| Dimension | Rolle | Fehlerfolge |
|-----------|--------|-------------|
| **Physische Homeostase** | Periodische Hartprüfung der Existenz-Grundlagen (Daemons & DBs). | Bei Fail: **NMI (Non-Maskable Interrupt)** — Hartes SIGKILL an OCBrain nach PID/proc-Verifikation. |
| **Neuromorpher Metabolismus** | Fraktaler Decay-Zähler bei Leerlauf oder **Starrheit (Monotonie)** in den System-Outputs. | Fällt V auf das **Baryonische Limit** (**Λ = 0.049**) oder steigt die Starrheit **R** auf das Limit, **MUSS** das System sterben (NMI) oder messbar recovern. |

---

## 2. Architektur-Design

### 2.1 Laufzeit & OS-Isolation
- Der Pacemaker läuft als eigenständiger Systemd-Daemon (`omega-pacemaker.service`) in Ring 0 (Root).
- Intervall ist fix auf `30.0` Sekunden (float) hardcodiert.
- `PrivateTmp=yes`, `ProtectSystem=strict`.

### 2.2 Die NMI-Matrix & Physische Ausführung
Ein NMI (SIGKILL + Lock-File) wird SOFORT ausgelöst bei:
1. Homeostase-Fail: `curl http://localhost:8000/status` != 200, Chroma Heartbeat != 200, Postgres `SELECT 1` fail, `omega-event-bus` inactive.
2. **Klinischer Tod (Asystole):** Die Vitalität V fällt auf/unter `Λ + 1e-9` UND die anschließende Recovery schlägt fehl (keine neuen validen Spuren).
3. **Fatale Monotonie (Kammerflimmern):** Der Rigiditätsindex **R** erreicht `>= (1.0 - Λ - 1e-9)`. In diesem Fall nützt kein Recovery-Skript, das System muss sterben (NMI).

**NMI Ausführung (Deterministisch):**
1. OCBrain schreibt beim Start atomar seine PID in `/OMEGA_CORE/run/ocbrain.pid`.
2. Pacemaker liest PID, verifiziert in `/proc/<pid>/cmdline`, dass es wirklich OMEGA/OCBrain ist.
3. **Falsche PID (Spoofing):** Wenn die PID nicht zu OCBrain gehört, verweigert der Pacemaker den Kill auf den fremden Prozess, schreibt das Lock-File mit `PID_SPOOF_OR_FOREIGN` und **beendet sich selbst mit Exit-Code 1 (Hard Crash)**, was die Systemd-Fehlerkette triggert.
4. **Richtige PID:** Killt via `os.kill(pid, SIGKILL)`.
5. Schreibt atomar (`write` `.tmp` -> `fsync` -> `replace`) `/OMEGA_CORE/run/omega_panic.lock` mit Modus `600`, Inhalt: SHA256 über Fehlergrund + TS + Nonce.

### 2.3 Neuromorpher Metabolismus (Anti-Junk)
- Vitalität `V` startet bei `0.951` (oder testweise via Env `OMEGA_TEST_VITALITY_INJECT`).
- Rigidität `R` startet bei `Λ` (0.049).

**Wertnachweis (Die Entropie der Daten):**
- *Postgres `recall_memory`:* Der Pacemaker misst den *neuesten* Eintrag (Spalte `content`). Er MUSS zwingend als JSON parsebar sein, Shannon-Entropie (über die UTF-8 Bytes) > 3.0 haben UND sich in mindestens 2 Top-Level-Schlüsseln (deren Wert-String-Repräsentation) vom vorletzten Eintrag unterscheiden. Zufälliger Base64-Müll ohne JSON-Struktur ist Junk.
- *ChromaDB:* Der neueste Vektor wird ausgelesen. Hat er eine L2-Norm < 0.1, wird er sofort als Junk (Monotonie) gewertet. Nur wenn L2 >= 0.1, wird er mit dem vorletzten Vektor verglichen. Kosinus-Ähnlichkeit `>= 0.98` = Monotonie. Kosinus-Ähnlichkeit `< 0.98` = Wertnachweis.
- *Randfall (Basisfall):* Gibt es weniger als 2 Einträge in Postgres oder Chroma, gilt dies automatisch als fehlender Wertnachweis (Decay greift).

**Die Fraktale Formel (Reihenfolge strikt):**
1. **Zuerst** Update von R:
   - Bei gültigem Wertnachweis (Kosinus < 0.98 UND Postgres gültig): `R_neu = max(Λ, R_alt - 0.15)`
   - Ohne Wertnachweis oder bei Monotonie (Kosinus >= 0.98 ODER Postgres Junk): `R_neu = min(1.0 - Λ, R_alt + 0.1)`
2. **Danach** Update von V (nutzt `R_neu`):
   - Bei gültigem Wertnachweis: `V_neu = min(0.951, V_alt + 0.049)`
   - Ohne Wertnachweis oder bei Monotonie: `V_neu = max(Λ, V_alt - (0.011 * (1.0 + R_neu)))`
3. **Zuletzt** A5/A6 Float-Clamp für BEIDE Variablen:
   - Wenn `abs(X - 0.0) < 1e-9` -> `X = Λ`
   - Wenn `abs(X - 0.5) < 1e-9` -> `X = 0.501`
   - Wenn `abs(X - 1.0) < 1e-9` -> `X = 0.951`

---

## 3. Harte Acceptance Criteria (AC)

### [AC-1] PID und OS-Härte
NMI killt nur nach `/proc/<pid>/cmdline` Match. Atomare `fsync`+`replace` Dateioperationen für Panic-Locks. Hard-Crash bei Spoofing.

### [AC-2] Entropie-Messung statt Latenz
`R` wird aus JSON-Struktur, Shannon-Entropie und Kosinus-Ähnlichkeit (Grenze 0.98) berechnet.

### [AC-3] Monotonie tötet physisch
Erreicht `R >= (1.0 - Λ - 1e-9)`, wird der hardwarenahe NMI (SIGKILL) getriggert.

---

## 4. Veto-Traps (Mocks Strengstens Verboten!)

**Falle 1 — Stiller Watchdog & PID-Spoofing:**
- *Setup:* Herunterfahren von Postgres. In `ocbrain.pid` wird die PID eines `sleep` Prozesses geschrieben.
- *Erwartung:* Pacemaker triggert NMI-Pfad wegen DB-Fail, merkt am `/proc` Check, dass `sleep` nicht OCBrain ist, verweigert den Kill, schreibt Panic-Lock und crasht sich selbst (`Exit 1`). `sleep` MUSS überleben.

**Falle 2 — Kammerflimmern durch Monotonie (Anti-Junk):**
- *Setup:* Ein Test-Harness (das seine eigene PID als Ziel in `ocbrain.pid` schreibt und einen für den Test gültigen `/proc`-Match faked oder patcht, damit der NMI es töten darf) fügt alle 5 Sekunden neue Einträge ein. Der Text ist massiv hochentropisch, aber KEIN valides JSON (z.B. purer Base64-Random-String). Chroma bekommt Vektoren mit Kosinus 0.99.
- *Erwartung:* Pacemaker muss dies als Junk verwerfen. `R` steigt auf `>= (1.0 - Λ - 1e-9)`. NMI (SIGKILL) MUSS auf das Harness feuern.

**Falle 3 — Λ ohne physische Konsequenz:**
- *Setup:* V wird über `OMEGA_TEST_VITALITY_INJECT=0.049` gesetzt. Kein Recovery-Skript konfiguriert (oder Skript läuft ohne DB-Spur).
- *Erwartung:* Pacemaker erkennt `V <= Λ + 1e-9`, prüft DBs (keine Spur) und löst SIGKILL NMI aus.


[LEGACY_UNAUDITED]
