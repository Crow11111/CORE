# OMEGA PRÜF-SPEZIFIKATION VAR_2: Existential Pacemaker (Ticket 3) — Kryptographisch & ereignisverkettet

**Typ:** Normative Spezifikation (Variante 2)  
**Modul (Ziel):** `omega_pacemaker.py` + Unit `omega-pacemaker.service` + Daemon-seitige **Pacemaker-Adapter** (pro überwachtem Dienst)  
**Referenz:** `SPEC_PACEMAKER.md` (Baseline), `SPEC_PACEMAKER_VAR_1.md` (Deterministik); **VAR_2** ersetzt implizites „Vertrauen durch Erreichbarkeit“ durch **kryptographische Bindung** und **Hash-verkettete Vitalitäts-Logik**.  
**Verbot:** Mocks, Stubs, Test-Doubles, in-memory Fake-Krypto, „signierte“ Payloads ohne echte Signaturprüfung, synthetische Event-Ketten ohne persistente Speicherung auf realem Medium.

---

## 1. Zielsetzung (normativ)

| Dimension | VAR_2-Erweiterung gegenüber Baseline |
|-----------|----------------------------------------|
| **Physische Homeostase** | Jeder Health-Check **MUSS** nach erfolgreichem Transport-Layer eine **signierte Handshake-Antwort** verifizieren. Reiner HTTP-200 / TCP-Erfolg **genügt nicht**. |
| **Entropischer Metabolismus** | Jeder anerkannte „Lebenszeichen“-Nachweis **MUSS** ein **kryptographisch signiertes Metabolismus-Event** sein (Nonce, Zeitbindung, Hash über Nutzlast). Decay entsteht **ausschließlich** aus der **Chain-of-Events** (siehe §5), nicht aus einem isolierten Zähler ohne Bindung an die Kette. |

**Dezentralitäts-Minimum:** Mindestens **eine** Signatur-Identität **pro überwachtem Daemon** (asymmetrisches Schlüsselpaar, Private Key **nur** beim jeweiligen Dienstprozess bzw. dessen Ring-0-Adapter). Der Pacemaker hält **ausschließlich** Public Keys (oder Fingerprints davon) in einem **read-only** Key-Material-Store unter `/OMEGA_CORE/run/pacemaker_trust/` (Rechte `0644` für `.pub`, keine Private Keys).

---

## 2. Kryptographische Primitive (fest, nicht konfigurierbar)

| Baustein | Algorithmus | Kodierung | Zweck |
|----------|---------------|-----------|--------|
| **Signatur** | **Ed25519** (RFC 8032) | Raw 64-Byte-Signatur, Public Key 32 Byte | Authentizität und Integrität von Handshakes und Metabolismus-Events |
| **Hash (Kettenfinger)** | **SHA-256** | Lowercase-Hex, 64 Zeichen | Event-Verkettung, Panic-Lock-Inhalt, Transcript-Hashes |
| **Nonces** | Kryptographisch sicher | 256 Bit aus OS-Quelle (`getrandom(2)` / `os.urandom(32)`), Hex- oder Base64 in JSON **nur** als transportable Darstellung | Replay-Schutz, Challenge-Bindung |
| **Zeitbindung** | Unix-`float` Sekunden (monotonische Referenz des Pacemakers für Fenster) | In signierter Nutzlast: Feld `ts_mono` (Sekunden seit Pacemaker-Boot) **und** `ts_wall` (UTC, ISO8601) zur Korrelation | Abweichung > `T` (siehe §3) → Handshake/Event **ungültig** |

**A5/A6:** Vitalität und alle in VAR_2 genannten **Resonanz**-Analogien bleiben `float` in \([Λ, V₀]\) wie in VAR_1; Krypto-Parameter (Schlüssellängen, Hash-Ausgaben) sind **Bytelängen / Hexstrings** — keine Verwechslung mit Resonanz-Floats.

---

## 3. Konstanten (VAR_2, nicht zur Laufzeit änderbar)

| Symbol | Wert | Typ | Semantik |
|--------|------|-----|----------|
| **Λ** | `0.049` | `float` | Baryonisches Limit (wie Baseline) |
| **V₀** | `0.951` | `float` | Startvitalität nach validierter Bootstrap-Kette |
| **T** | `30.0` | `float` | Tick-Periode (Sekunden) |
| **δ_decay** | `0.011` | `float` | Abzug **pro fehlendem gültigen Kettenfortschritt** im Tick (siehe §5) |
| **ε_floor** | `1e-12` | `float` | Numerischer A5-Schutz |
| **HS_MAX_SKEW** | `min(5.0, T/6)` | `float` | Max. Abweichung `ts_wall` zur Pacemaker-UTC beim Handshake |
| **CHAIN_HEAD_PATH** | `/OMEGA_CORE/run/pacemaker_event_chain_head.json` | Pfad | Atomar geschriebener Kopf der Event-Kette |
| **CHAIN_LOG_DIR** | `/OMEGA_CORE/run/pacemaker_events/` | Verzeichnis | Append-only **logische** Folge: eine Datei pro Event nach erfolgreicher Verifikation |

---

## 4. Signiertes Daemon-Handshake-Protokoll (Homeostase)

### 4.1 Rollen

- **P (Pacemaker):** Initiator, kennt nur Public Keys.  
- **D (Daemon-Adapter):** Responder, besitzt Ed25519-Private Key `sk_D`, veröffentlicht `pk_D`.

### 4.2 Ablauf (pro Tick, pro Daemon — sequentiell wie VAR_1 §4, erweitert)

1. **Transport:** Wie Baseline (HTTP/TCP/Unix-Socket — **spezifisch pro Dienst im Implementierungsdokument**, mindestens ein Pfad **MUSS** echten Netzwerk- oder Socket-Connect zeigen).  
2. **Challenge:** `P` erzeugt `nonce_P ← urandom(32)`, sendet sie im vereinbarten Header `X-Omega-Pacemaker-Challenge: <hex>` oder im ersten Request-Body-Feld `challenge` (JSON).  
3. **Response:** `D` antwortet mit JSON **kanonisch serialisiert** (festgelegte Key-Reihenfolge, UTF-8, keine whitespace-Variation):  

```json
{
  "daemon_id": "<string>",
  "nonce_P": "<hex>",
  "nonce_D": "<hex>",
  "ts_wall": "<ISO8601 Z>",
  "ts_mono": <float>,
  "prev_event_hash": "<64 hex oder GENESIS>",
  "transcript_hash": "<64 hex>"
}
```

   - `transcript_hash` = SHA-256 über die **exakte** Bytefolge von `(daemon_id || nonce_P || nonce_D || ts_wall || ts_mono || prev_event_hash)` mit fest definierten Trennern (`\n` zwischen Feldern) **vor** JSON-Einbettung (Implementierung **MUSS** dieselbe Kanonisierung wie Test-Vektoren verwenden).  
4. **Signatur:** Feld `sig` (64 Byte base64url) über die **SHA-256-Hash** der kanonischen JSON-Bytes **ohne** das Feld `sig` (d. h. signiere strukturierte Payload gemäß implementierungsfestgelegtem „Sign-bytes“-Build-Schritt — **ein** Verfahren, im Code zentral und dokumentiert).  
5. **Verifikation durch P:**  
   - Ed25519-Verify mit `pk_D` für registriertes `daemon_id`.  
   - `nonce_P` stimmt mit gesendeter Challenge überein.  
   - `nonce_D` noch nie in Sliding-Window der letzten **K = 1000** Challenges gesehen (Persistenz des Fensters in `CHAIN_HEAD` oder dedizierter Datei, atomar aktualisiert).  
   - Zeitfenster `HS_MAX_SKEW`.  
   - `prev_event_hash` **MUSS** exakt dem aktuellen Kettenkopf `H_head` entsprechen **oder** bei definiertem Cold-Start `GENESIS` gemäß §5.1.

**Homeostase-OK** für diesen Daemon **nur** wenn Transport **und** Schritte 1–5 erfolgreich.

---

## 5. Chain-of-Events & Decay (Metabolismus)

### 5.1 Genesis

Beim ersten erfolgreichen vollständigen Homeostase-Durchlauf **aller** Pflicht-Daemons in einem Tick setzt `P`:

- `H_head := SHA-256("OMEGA_PACEMAKER_GENESIS" || pk_root || ts_boot_hex)` wobei `pk_root` der hex-kodierte Public Key des Pacemaker-„Log-Anchors“ ist (optional zweites Schlüsselpaar **nur** für Ketten-Siegel — wenn nicht genutzt, feste Konstante `OMEGA_CHAIN_ANCHOR_V1` als ASCII-Prefix genügt, **MUSS** im Code einmalig definiert sein).  
- Schreibe atomar `CHAIN_HEAD_PATH` mit Feldern `{ "head_hash", "seq", "last_tick_id" }`.

### 5.2 Metabolismus-Event (signiertes Lebenszeichen)

Ein **gültiges Lebenszeichen-Event** `E` **MUSS** erfüllen:

1. **Integrität:** Wie Baseline physischer Wertnachweis (Chroma-Neueintrag L2 > 0.1 **oder** Postgres `recall_memory` mit Shannon-Entropie > 3.0) — **und** zusätzlich  
2. **Signatur:** Separate Nutzlast `M` mit Feldern `{ "event_type": "METABOLISM", "seq", "prev_hash", "content_hash", "ts_wall", "witness_ref" }` wobei `content_hash = SHA-256(normalisierter Inhalt)` des neuen DB-/Vektor-Inhalts (Implementierung definiert Normalisierung **deterministisch**), `witness_ref` = stabilier Verweis (z. B. Chroma-ID + Collection oder Postgres PK).  
3. **Signiert** von einer Identität, die **explizit** als „Metabolismus-Produzent“ im Trust-Store eingetragen ist (kann **dasselbe** `sk` wie ein Daemon sein, **muss** aber benannt sein).  
4. **Verkettung:** `prev_hash == H_head` zum Zeitpunkt der Einreichung; nach Verifikation:  
   - `H_head := SHA-256(H_head || canonical(M) || sig_hex)`  
   - `seq := seq + 1`  
   - Persistenz: neue Datei `CHAIN_LOG_DIR / <seq>_<head_prefix>.json` mit vollständigem `M`, Signatur und vorherigem `H_head` (Audit-Trail).

### 5.3 Decay-Regel (Chain-basiert)

Pro abgeschlossenem Tick `k`:

- **Zähle** `n_meta` = Anzahl der **gültigen** Metabolismus-Events, die **in das Zeitintervall** `(t_k - T, t_k]` fallen **und** erfolgreich in die Kette eingehängt wurden.  
- **Zähle** `n_hs` = Anzahl der Daemons, für die der signierte Handshake in diesem Tick **vollständig** OK war.  
- **Decay-Anwendung:**  
  - Wenn `n_hs < N_required` (Anzahl registrierter Pflicht-Daemons): **kein** Metabolismus-Update; zusätzlich Homeostase-Pfad **NMI/Panic** wie Baseline — **unabhängig** von Kette.  
  - Wenn `n_hs == N_required` **und** `n_meta == 0`:  
    \[
    V_{k+1} = \max\left(\Lambda,\; V_k - \delta_{\text{decay}}\right)
    \]  
    (gleiche Float-Korrektur wie VAR_1).  
  - Wenn `n_meta ≥ 1`:  
    \[
    V_{k+1} = \min\left(V_0,\; V_k + \varepsilon_{\text{floor}}\right)
    \]

**Kern:** Decay ist **nicht** „stilles Herunterzählen“, sondern **Folge** aus: *Handshake-Kette konsistent* **und** *kein neues signiertes Metabolismus-Event im Tick*. Die Kette **MUSS** den **kausalen** Zusammenhang zwischen Homeostase-Zustand und Wertnachweis abbilden (`prev_event_hash` im Handshake koppelt Daemon-Antwort an `H_head`).

### 5.4 Λ-Recovery

Wie Baseline / VAR_1: bei Erreichen von Λ **MUSS** Recovery mit messbarer physischer Spur erfolgen. Zusätzlich VAR_2: Nach erfolgreicher Recovery **MUSS** ein **signiertes** `event_type: "RECOVERY"`-Event die Kette fortsetzen mit `prev_hash == H_head` **vor** Recovery; andernfalls gilt Recovery als **nicht kettenkonform** → Panic-Lock.

---

## 6. Trust-Store & Schlüsselrotation

- **Pfad:** `/OMEGA_CORE/run/pacemaker_trust/daemons/<daemon_id>.pub` — genau eine Ed25519-Public-Key-Datei pro ID (Raw 32 Byte oder hex, **ein** Format festlegen).  
- **Rotation:** Neue `.pub` **MUSS** unter `<daemon_id>.pub.new` landen; Pacemaker übernimmt sie **nur** nach `SIGHUP` oder nächstem Prozessstart **und** wenn signiertes **Rotation-Event** (von alter Key-ID oder Operator-OOB-Prozess gemäß gesonderter Policy) vorliegt — Minimalvariante für Ticket 3: **kein** Hot-Rotate ohne Neustart; dokumentierte Ausnahme = Veto-Gegenstand.  
- Private Keys **dürfen** niemals unter `/OMEGA_CORE/run/pacemaker_trust/` liegen.

---

## 7. Panic-Lock (kryptographisch angereichert)

Panic-Lock-Inhalt (wie VAR_1, erweitert): Kanonisches JSON mit `ts_unix`, `reason`, `sensor_snapshot`, `nonce`, **`chain_head_hash`**, **`last_verified_handshake_ids`**.  
`sha256_hex` über die kanonische JSON-Zeile **vor** Einbettung in Lock-Datei; Schreibprotokoll: temp → `fsync` → `replace`.

---

## 8. Harte Acceptance Criteria (VAR_2)

| ID | Kriterium | Nachweis |
|----|-----------|----------|
| **AC-V2-01** | Kein Daemon gilt als „healthy“, ohne dass eine **verifizierte Ed25519-Signatur** über Challenge + Kettenkopf vorliegt. | Integrationstest: gültiger HTTP-200 mit **ungültiger** oder fehlender Signatur → Homeostase **FAIL**. |
| **AC-V2-02** | Jeder Handshake **MUSS** Client-Challenge `nonce_P` spiegeln; Wiederholung derselben `nonce_D` innerhalb des Fensters **K** → **FAIL**. | Test mit zwei aufeinanderfolgenden identischen `nonce_D` vom echten Adapter-Prozess. |
| **AC-V2-03** | Metabolismus-Events ohne gültige Signatur oder mit falschem `prev_hash` werden **nicht** in `CHAIN_LOG_DIR` persistiert und **zählen nicht** als `n_meta`. | DB-Inhalt manuell erzeugt + Signatur absichtlich falsch → Decay im nächsten Tick. |
| **AC-V2-04** | `H_head` ändert sich **ausschließlich** durch definierte Hash-Schritte in §5.2–5.4; kein direktes Setzen auf willkürliche Werte ohne Event. | Code-Audit + Hash-Ketten-Replay aus `CHAIN_LOG_DIR` muss `H_head` reproduzieren. |
| **AC-V2-05** | Decay pro Tick **höchstens einmal**; Kopplung: `n_hs == N_required` ist notwendig für Metabolismus-Decay/Accumulate. | Trace: bei Handshake-FAIL kein Vitalitäts-„Accumulate“ durch Events. |
| **AC-V2-06** | A5: Gespeicherte Vitalität nie `0.0`, `0.5`, `1.0`; alle Zeitfenster und Vergleiche nutzen `float` für Vitalität, Integer nur für `seq`, Byte-Längen. | Property-Check wie VAR_1. |

---

## 9. Veto-Traps (drei, ohne Mocks)

**Global:** Keine `unittest.mock`-Patches für Krypto, HTTP, Datenbanken oder Zeit. Tests verwenden **echte** Ed25519-Schlüssel (generiert im Test-Setup auf Platte), **echte** minimale HTTP-Responder-Prozesse oder die **produktiven** Daemon-Endpunkte, und **echtes** Dateisystem unter `/OMEGA_CORE/run/` (oder dokumentiertes `OMEGA_RUN_ROOT` mit gleicher Semantik auf dediziertem Test-Host).

| Trap | Name | Aufbau | Erwartung |
|------|------|--------|-----------|
| **VT-V2-1** | **Replay-Handshake** | Echter Adapter signiert gültige Antwort **A** auf `nonce_P1`. Im nächsten Tick wird dieselbe Bytefolge **A** erneut angeboten (Replay), während Pacemaker `nonce_P2 ≠ nonce_P1` sendet. | Verifikation **FAIL**; Homeostase rot; kein grünes Bit nur wegen identischer Signaturbytes ohne Challenge-Match. |
| **VT-V2-2** | **Kettenabbruch-Fake** | Nach gültigem Tick: manipuliere **ein** gespeichertes Event-File in `CHAIN_LOG_DIR` mit **einem** geänderten Hex-Zeichen im `content_hash` (echte Datei, echtes `sed`/Editor-Skript). Nächster Handshake mit korrektem `prev_event_hash` aus **Speicher**, der von der Datei abweicht, oder Pacemaker lädt Kette neu. | Pacemaker **erkennt** Inkonsistenz (Recompute ≠ `H_head`) → **FAIL** (Panic oder Weigerung, Metabolismus anzuerkennen); System darf nicht „still“ weiterlaufen mit widersprüchlicher Kette. |
| **VT-V2-3** | **Signierter Junk-Metabolismus** | Erzeuge **echten** DB-Eintrag mit Entropie **unter** Baseline-Schwelle (oder Chroma-Vektor L2 **unter** 0.1), aber mit **formal gültiger** Ed25519-Signatur und korrektem `prev_hash`. | Event wird **abgelehnt**; `n_meta = 0`; Decay findet statt; Vitalität sinkt entsprechend §5.3 — **kein** „Heroin-Erfolg“ durch Signatur allein. |

---

## 10. Abgrenzung

- **VAR_1** bleibt maßgeblich für Scheduling, systemd-Isolation und atomare Datei-Operationen, soweit VAR_2 nicht explizit abweicht.  
- **Baseline** Sensorliste bleibt inhaltlich gültig, wird aber **überdeckt** durch §4 (Signaturpflicht).  
- **Keine Mocks:** Implementierungs- und Abnahme-Tests **MÜSSEN** echte kryptographische Verifikation und persistente Kettenzustände ausführen.

---

*Status: VAR_2 — Kryptographisch / Chain-of-Events | Ticket 3 | Delta Λ = 0.049*


[LEGACY_UNAUDITED]
