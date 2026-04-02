# OMEGA PRÜF-SPEZIFIKATION VAR_1: Existential Pacemaker (Ticket 3) — Radikal deterministisch

**Typ:** Normative Spezifikation (Variante 1)  
**Modul (Ziel):** `omega_pacemaker.py` + Unit `omega-pacemaker.service`  
**Referenz:** `SPEC_PACEMAKER.md` (Baseline); diese Datei ersetzt operative Unschärfe durch **harte Deterministik**.  
**Verbot:** Mocks, Stubs, Test-Doubles, in-memory Fake-DBs, monkeypatched `time` ohne dokumentierte Test-Harness-Spezifikation mit echtem Wall-Clock-Slice.

---

## 1. Normative Konstanten (nicht konfigurierbar)

| Symbol | Wert | Typ | Semantik |
|--------|------|-----|----------|
| **Λ** (Baryonisches Limit) | `0.049` | `float` | Untere Schranke der Vitalität; Recovery-Pflicht bei Erreichen (Gleichheit zulässig). |
| **V₀** (Startvitalität) | `0.951` | `float` | Initialzustand Metabolismus-FSM nach erfolgreicher Bootstrap-Validierung. |
| **T** (Zyklusperiode) | `30.0` | `float` | Sekunden; ein **Tick** = genau eine sequenzielle Durchlaufphase (siehe §5). |
| **δ_decay** | `0.011` | `float` | Abzug pro Tick bei fehlendem Wertnachweis (keine Ganzzahl-Arithmetik). |
| **ε_floor** | `1e-12` | `float` | Numerischer Schutz gegen Gleitkomma-Rückstände unter Λ ohne „0.0“-Snap. |

**A5/A6-Vertrag:** Zustandsgrößen des Pacemakers (Vitalität, interne Resonanz-Analogien) sind ausschließlich `float`. Werte `0.0`, `0.5`, `1.0` dürfen **niemals** als gespeicherter Zustand vorkommen. Nach jedem Update: explizite Clamp-Funktion mit Zielmenge \([Λ, V₀]\) und **Verwerfen** von Ergebnissen, die numerisch auf verbotene Snap-Punkte fallen würden (Ersetzung durch `Λ + ε_floor` bzw. `V₀ - ε_floor`).

---

## 2. OS-Level Isolation (hart, reproduzierbar)

Der Pacemaker-Prozess **MUSS** unter systemd mit mindestens folgenden Eigenschaften laufen; Abweichung = Build-/Deploy-Veto:

| Mechanismus | Pflicht | Zweck |
|-------------|---------|--------|
| `PrivateTmp=yes` | ja | Temporäre Dateien entkoppelt vom globalen `/tmp`; verhindert Cross-Tenant-Races. |
| `ProtectSystem=strict` | ja | Schreibzugriff nur auf explizit freigegebene Pfade (`ReadWritePaths=` für `/OMEGA_CORE/run` o. ä.). |
| `ProtectHome=yes` (oder restriktiver) | ja | Kein versehentliches Scannen privater Home-Verzeichnisse. |
| `NoNewPrivileges=yes` | ja | Verhindert Rechte-Eskalation aus dem Dienst heraus. |
| `CapabilityBoundingSet=` minimal | ja | Nur Capabilities, die für `kill(2)` auf Ziel-PIDs und für konfigurierte Health-Checks zwingend nötig sind (kein CAP_SYS_ADMIN „zur Sicherheit“). |
| Eigener Unix-User/Group | ja | Nicht `root`, sofern `kill` auf OCBrain-Ziel durch ACL/Supplementary-Group oder dokumentierte Policy erlaubt ist; **falls** Root zwingend: Begründung schriftlich im Service-Fragment + separates Security-Review-Veto. |
| `RestrictAddressFamilies=AF_UNIX AF_INET AF_INET6` | ja | Nur benötigte Socket-Familien (Anpassung nur mit Architektur-Veto). |
| `LockPersonality=yes` | empfohlen | Reduziert ABI-Surface. |

**Determinismus der Umgebung:** Der Dienst **MUSS** mit fest gesetzter Locale (`LC_ALL=C`) und ohne zufällige Kind-Prozesse außerhalb der spezifizierten Recovery-Subprozesse starten, damit Logs und Fehlerpfade vergleichbar bleiben.

---

## 3. Zustandsmaschinen (unerbittlich, vollständig)

### 3.1 Homeostase-FSM (H)

Zustände: `H0_INIT` → `H1_PROBE` → `H2_EVAL` → (`H3_NMI_ARMED` | `H4_STEADY`) → zyklisch.

| Zustand | Eintritt | Ausgang (deterministisch) |
|---------|----------|---------------------------|
| **H0_INIT** | Prozessstart | Nach erfolgreichem Parse der statischen Konstanten und Anlage atomarer Run-Verzeichnisse → `H1_PROBE`. |
| **H1_PROBE** | Tick-Start | Führt **festgelegte** Sensorsequenz in **fester Reihenfolge** aus (siehe §4). Jeder Sensor liefert `OK` oder `FAIL`. Bei erstem `FAIL` → `H2_EVAL` mit `fail_fast=true`. Bei allen `OK` → `H2_EVAL` mit `fail_fast=false`. |
| **H2_EVAL** | Probe abgeschlossen | Wenn `fail_fast` → `H3_NMI_ARMED`. Sonst → `H4_STEADY`. |
| **H3_NMI_ARMED** | Homeostase-Fail | Ausführung **exakt** nach §6 (PID-Datei, `/proc`-Verifikation, `SIGKILL` oder dokumentierte Verweigerung + Panic-Lock). Danach **immer** Übergang zu `H4_STEADY` oder `H1_PROBE` nächster Tick — **kein** Schwebezustand über Tick-Grenzen hinweg. |
| **H4_STEADY** | Erfolg | Triggert Metabolismus-Tick (§7). Wechsel zu `H1_PROBE` beim nächsten Wall-Clock-Tick `T` (Monotonie über `CLOCK_MONOTONIC`). |

**Invariante H-INV-1:** In jedem Zustand existiert genau ein ausgezeichneter Übergang pro Ereignis; keine „optionalen“ Pfade.

### 3.2 Metabolismus-FSM (M)

Zustände: `M0_BOOT` → `M1_ACCUMULATE` ↔ `M2_DECAY` → `M3_LAMBDA_RECOVERY`.

| Zustand | Eintritt | Ausgang |
|---------|----------|---------|
| **M0_BOOT** | Erster erfolgreicher Homeostase-Durchlauf | Setze Vitalität `V := V₀` (float). → `M1_ACCUMULATE`. |
| **M1_ACCUMULATE** | Wertnachweis erbracht (§7) | `V := min(V₀, V + ε_floor)` (kein Überschreiten von V₀). → `M1_ACCUMULATE` (bleibt) bis Tick-Ende. |
| **M2_DECAY** | Kein Wertnachweis im abgelaufenen Tick | `V := max(Λ, V - δ_decay)`; wenn `V < Λ` numerisch → `V := Λ + ε_floor` nach A5-Korrektur. Wenn `V == Λ` (Toleranz: `abs(V - Λ) ≤ ε_floor`) → `M3_LAMBDA_RECOVERY`. Sonst → `M1_ACCUMULATE` nächster Zyklus. |
| **M3_LAMBDA_RECOVERY** | Λ erreicht | Starte **ein** konfiguriertes Recovery-Programm als **eigenen** Kindprozess mit leerer/minimaler Umgebung und festem `argv[0]`; warte **nicht** blockierend unbegrenzt — Timeout = `T` (gleiche Konstante). Nach Start: `V := V₀` **nur** wenn Recovery **Exit-Code 0** und **physische Spur** (§7.3) innerhalb von `2T` Sekunden verifiziert wurde; sonst Panic-Lock + erneuter Zyklus mit `V := Λ + ε_floor`. |

**Invariante M-INV-1:** Die Vitalität ist zu jedem Tick-Ende eine definierte `float` in \([Λ, V₀]\) ohne verbotene Snaps.

---

## 4. Homeostase-Sensoren (Reihenfolge = Norm)

In **H1_PROBE** werden in dieser Reihenfolge echte Verbindungen aufgebaut; Timeout pro Sensor = `min(5.0, T/6)` Sekunden (float), fest codiert:

1. HTTP GET `http://127.0.0.1:8000/status` — Erfolg nur bei exaktem Statuscode **200** und Body-Länge **> 0** Bytes.  
2. Chroma Heartbeat (wie Baseline-SPEC, exakt **200**).  
3. Postgres `SELECT 1` (synonym zur Baseline).  
4. `systemctl is-active omega-event-bus` — Erfolg nur wenn stdout **exakt** `active\n` (POSIX-Text, kein Trim außer trailing single `\n`).

Jeder Fehler → sofortiger Übergang zu `H2_EVAL` mit `fail_fast=true` **ohne** Retry innerhalb desselben Ticks.

---

## 5. Tick-Scheduling (deterministisch)

Ein **Tick** beginnt mit `t₀ = clock_gettime(CLOCK_MONOTONIC)` und endet, wenn entweder:

- alle Zustandsübergänge des Ticks abgeschlossen sind, **und**  
- die verstrichene Zeit `< T` ist: dann **aktives Warten** auf `(t₀ + T)` mit monotonischer Uhr (kein `sleep` mit relativen Drifts ohne Korrektur), **oder**  
- die verstrichene Zeit ≥ `T`: nächster Tick startet **sofort** ohne Doppel-Decay (höchstens ein Metabolismus-Update pro Tick).

**Veto gegen Burst:** Mehr als ein Decay pro `T` ist verboten.

---

## 6. POSIX-Signale & Prozessidentität

### 6.1 Signalwahl

- **NMI an OCBrain:** ausschließlich **`SIGKILL` (9)** nach erfolgreicher Identitätsprüfung.  
- **Kein** `SIGTERM`-Grace-Period im VAR_1-Pfad (deterministisch hart).

### 6.2 Identitätsprüfung vor `kill(2)`

1. PID-Datei **`/OMEGA_CORE/run/ocbrain.pid`**: Inhalt = ASCII-Dezimalzahl, genau eine Zeile, terminierend mit `\n`.  
2. Lesen der PID nur aus **temporärer Datei + `os.replace`**-Schreibprotokoll durch OCBrain (Schreiber); Leser **MUSS** `O_RDONLY` und `fstat` nutzen und **maximal 4096 Bytes** lesen (Verhindert Speicher-Spam).  
3. Vor `kill(pid, SIGKILL)`: Lesen von `/proc/<pid>/cmdline` (binary null-separated); **Pflicht-Substring** (konfigurierbar nur via eine zentrale Konstante im Code, nicht zur Laufzeit): Nachweis, dass der Prozess zum OMEGA-Substrat gehört (z. B. Pfad zu `python` + Modulname).  
4. **Mismatch:** Kein `kill`; stattdessen **sofort** Panic-Lock nach §6.3 mit Grund `PID_SPOOF_OR_FOREIGN`.

### 6.3 Panic-Lock (atomar, fälschungssicher)

Pfad: `/OMEGA_CORE/run/omega_panic.lock`. Erstellung:

1. Schreiben in `/OMEGA_CORE/run/.omega_panic.lock.<random>.tmp` mit Rechten **0600**.  
2. Inhalt: `sha256_hex` über kanonische JSON-Zeile mit Keys `ts_unix`, `reason`, `sensor_snapshot`, `nonce` (Nonce = 256 Bit aus `/dev/urandom` gelesen, hex-kodiert).  
3. **`fsync()`** auf Dateideskriptor vor `rename`.  
4. **`os.replace(tmp, final)`** (atomar auf gleichem Mount).  
5. Optional: zweites `fsync()` auf das Parent-Verzeichnis (Linux: Verzeichnis-FD), um Persistenz bei Crash zu erhöhen — wenn implementiert, **muss** es in allen Pfaden gleich sein.

---

## 7. Metabolismus — exakte Mathematik

### 7.1 Rekursion

Sei \(V_n\) die Vitalität nach dem \(n\)-ten abgeschlossenen Tick, \(n \in \mathbb{N}_0\).

- Initial: \(V_0 = V_0^{\text{spec}} = 0.951\).  
- Wenn Tick \(n\) **keinen** gültigen Wertnachweis hat:  
  \[
  V_{n+1} = \max\left(\Lambda,\; V_n - \delta_{\text{decay}}\right),\quad \delta_{\text{decay}} = 0.011
  \]
- Wenn Tick \(n\) **gültigen** Wertnachweis hat:  
  \[
  V_{n+1} = \min\left(V_0^{\text{spec}},\; V_n + \varepsilon_{\text{floor}}\right)
  \]
  (Obercap bei \(V_0\); kein unbeschränktes Wachstum.)

**Λ-Ereignis:** Recovery-Pflicht, wenn \(V_{n+1} - \Lambda \leq \varepsilon_{\text{floor}}\) **und** im letzten Decay-Tick kein Wertnachweis.

### 7.2 Wertnachweis (wie Baseline, präzisiert)

- **Chroma:** Neuer Eintrag mit Timestamp **< T** relativ zur monotonischen Referenzzeit des Pacemakers; L2-Norm **> 0.1**.  
- **Postgres:** Neue Zeile in `recall_memory`; Shannon-Entropie des `content` **> 3.0** (gleiche Formel wie Produktions-Validator, fest im Code).  
- Alles andere (Logs, HTTP-Pings, Nullvektoren) = **kein** Nachweis.

### 7.3 Physische Spur nach Recovery

Mindestens eine der folgenden Spuren **innerhalb** `2T` nach Recovery-Start:

- Neue Chroma-Vektorzeile (wie oben), oder  
- Neue `recall_memory`-Zeile mit Entropie **> 3.0**, oder  
- Atomar geschriebene Datei unter `/OMEGA_CORE/run/recovery_proof.json` mit `fsync` + `replace`, Inhalt SHA256 über (`pid`, `exit_code`, `ts`).

Ohne Spur: Zustand bleibt in Alarm-Pfad (Panic-Lock oder erneuter Recovery-Versuch — **eine** der beiden Strategien fest wählen und im Code vereinheitlichen; VAR_1 empfiehlt: **Panic-Lock** nach zweitem Fehlschlag).

---

## 8. Atomare Dateioperationen (Norm für alle Run-Files)

Schreiben jeder Run-Datei (PID, Panic, Proof): **write-temp-in-same-dir → fsync → replace**.  
Lesen: **single open**, kein partial mmap für PID.  
Concurrent Writer: Wenn `replace` während Lesezugriffs auftritt, Leser **MUSS** entweder `EINTR`/`ENOENT`-Retry (max. 3 Versuche, Backoff fix `1ms`) oder Abbruch mit `FAIL` melden — **kein** gemischtes Lesen alter/neuer Inhalte ohne Fehler.

---

## 9. Harte Acceptance Criteria (VAR_1)

| ID | Kriterium | Messung |
|----|-----------|---------|
| **AC-V1-01** | Homeostase nutzt ausschließlich echte Netzwerk/DB/systemctl-Probes gemäß §4. | Code-Audit + Integrationstest gegen laufende Dienste. |
| **AC-V1-02** | Kein `SIGKILL` ohne erfolgreiche `/proc`-Substring-Prüfung. | Test mit falscher PID (echter fremder Prozess). |
| **AC-V1-03** | Jede Panic- und Proof-Datei entsteht durch `replace` + `fsync`-Pflicht. | `strace`-Nachweis oder gleichwertiger Kernel-Trace im Test-Runner. |
| **AC-V1-04** | Vitalität folgt der Rekursion §7.1 mit festen Konstanten; verbotene Snaps treten nicht auf. | Property-Tests über eine **Serie echter Ticks** mit kontrolliertem Input (kein Mock-Clock außer Linux-`timeout`-Orchestrierung). |
| **AC-V1-05** | systemd-Isolation aus §2 ist im ausgelieferten Unit-File vollständig. | `systemd-analyze security omega-pacemaker.service` — keine „major“-Abweichungen ohne dokumentiertes Veto. |
| **AC-V1-06** | Höchstens ein Decay- oder Accumulate-Schritt pro Periode `T`. | Log-Zähler / Trace-Events. |

---

## 10. Veto-Traps (drei, ohne Mocks)

**Global:** Tests laufen gegen **echtes** Dateisystem, **echte** Prozesse, **echte** Dienste oder deren kontrolliertes Herunterfahren auf derselben Maschine. Kein `unittest.mock.patch` für DB, HTTP oder `os.kill`.

| Trap | Name | Aufbau | Erwartung |
|------|------|--------|-----------|
| **VT-1** | **Cross-Mount Replace** | Panic-Temp auf demselben Mount wie Ziel; simuliere `ENOSPC` vor `replace` (echtes temporäres Filesystem-Quota oder `ulimit`-gestützter Test auf dediziertem Test-Volume). | Kein halbes Panic-File sichtbar; finaler Zustand entweder alte Lock-Datei unverändert oder neue vollständig; Pacemaker meldet `FAIL` deterministisch und kehrt zu `H1_PROBE` zurück. |
| **VT-2** | **SIGKILL-Pfad ohne Identität** | Echter `sleep`-Prozess; gültige PID in `ocbrain.pid` schreiben (atomar); Homeostase durch Stoppen von Postgres **künstlich** auf `FAIL`. | Pacemaker versucht Kill **nicht**; Panic-Lock mit `PID_SPOOF_OR_FOREIGN` oder gleichwertigem `reason`; `sleep` lebt noch nach Tick-Ende. |
| **VT-3** | **Λ-Recovery ohne physische Spur** | Erzwinge Λ durch kontrollierten Betrieb ohne Wertnachweis über **n** Ticks (numerisch aus §7.1 vorherberechnet, `n` klein); Recovery-Binary ist `/bin/true` oder Skript, das **keine** der Spuren §7.3 erzeugt. | Innerhalb `2T`: kein Proof-File, kein DB/Chroma-Eintrag → **FAIL** des Tests; Pacemaker darf nicht „grün“ melden; Panic oder zweiter Recovery-Versuch gemäß §7.3. |

---

## 11. Abgrenzung zur Baseline

`SPEC_PACEMAKER.md` bleibt inhaltliche Referenz für Sensorliste und Entropie-/Norm-Constraints. **VAR_1** macht **Scheduling, Zustandsräume, Isolation, Signalpfad und Dateiatomik** normativ und entfernt interpretative Spielräume („optional“, „z.B.“).

---

*Status: VAR_1 — Radikal deterministisch | Ticket 3 | Delta Λ = 0.049*


[LEGACY_UNAUDITED]
