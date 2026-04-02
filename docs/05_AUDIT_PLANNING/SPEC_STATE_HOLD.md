# OMEGA PRÜF-SPEZIFIKATION: I/O Timeout-Tod (State-Hold Mechanismus)
**Ersteller:** Orchestrator A (Architekt)
**Modul:** `omega_state_hold.py` (Asynchroner Rückkanal)

## 1. Das Problem (Der Showstopper)
Der OCBrain-Agent läuft bei komplexen Deep-Dives in API-Timeouts. Evolution API und das Kong-Gateway erzwingen synchrone Verbindungen (z.B. max 30-60 Sekunden). Ein OCBrain-Lauf, der in ChromaDB nach Voids sucht oder im "Hyperfokus" Puffer konsolidiert, benötigt teils Minuten bis Stunden. Die Verbindung bricht ab, das System stirbt den I/O-Tod, die Kausalkette ist gerissen.

## 2. Der geplante Lösungs-Weg (Architektur)
Das System muss den synchronen Strang sofort durchtrennen. Hierbei MUSS die Rechteverteilung zwischen OCSpline und OCBrain exakt gewahrt bleiben:
1. **Empfang (OCSpline-Tor):** Evolution API empfängt WhatsApp-Nachricht -> Kong -> FastAPI Route (`/webhook`), die von **OCSpline** betrieben wird.
2. **Entkopplung:** OCSpline schreibt den Job in eine persistente Job-Queue (z.B. Redis, PostgreSQL oder Celery).
3. **Quittung:** OCSpline sendet sofort (innerhalb von < 1 Sekunde) ein `200 OK` zurück an Evolution API. Die synchrone Verbindung ist sicher beendet.
4. **Asynchrone Exekution:** Ein Hintergrund-Worker (`oc_spline_worker`) zieht sich den Job und leitet ihn an **OCBrain** weiter. OCBrain läuft isoliert und rechnet/denkt tief.
5. **Rückkanal:** Nach Abschluss (z.B. 40 Minuten später) gibt OCBrain das fertige Ergebnis an OCSpline zurück. OCSpline nutzt das `Evolution API /sendText` Interface, um das Ergebnis asynchron an den Operator auszugeben.

---

## 3. Die Harten Axiome & Acceptance Criteria (AC) für Orchestrator B

Wenn der Producer den Code schreibt, muss Orchestrator B ihn blind gegen diese ACs prüfen:

### [AC-1] Zero-Blocking Axiom (Die API-Entkopplung)
Der Code für den Webhook-Empfänger (`POST /webhook`) darf *niemals* auf das Ergebnis des LLM-Aufrufs warten (kein `await llm_response()`). Er muss nach dem Speichern in die Queue zwingend sofort `return {"status": "ok"}` senden.
*Test-Logik:* Orchestrator B muss AST/Code-Parsing durchführen: Ein `await` auf einen LLM-Call innerhalb des Routen-Handlers führt sofort zum **VETO**.

### [AC-2] Amnesie-Prävention (Persistente Queue)
Der empfangene Payload darf nicht in einer flüchtigen Python-Variable (z.B. `global_list.append(task)`) gespeichert werden.
*Test-Logik:* Orchestrator B muss prüfen, ob das State-Holding physikalisch ausgelagert ist (z.B. in eine Datenbank-Tabelle `async_tasks` oder einen Message-Broker), damit ein Daemon-Neustart die Tasks nicht löscht. Flüchtiger Speicher = **VETO**.

### [AC-3] Non-Maskable Interrupt (NMI) & OCSpline Watchdog (Process Group & Echtzeit-IPC)
OCBrain darf den NMI nicht selbst steuern. OCSpline muss den OCBrain-Task als externen Subprozess (z.B. via `asyncio.subprocess.create_subprocess_exec` mit `start_new_session=True` / `os.setsid`) starten, um eine eigene Process Group (PGID) zu erzeugen.
OCSpline muss eine harte Inter-Prozess-Kommunikation (IPC) über unbuffered stdout-Streaming erzwingen.
**Zwingende Voraussetzungen:**
1. Der Subprozess MUSS mit `PYTHONUNBUFFERED=1` (oder `-u`) gestartet werden.
2. OCSpline MUSS den Stream via Non-Blocking I/O (z.B. `asyncio.StreamReader` oder `os.set_blocking(False)`) lesen, da ein hängendes OCBrain-Child ohne `\n` ansonsten den OCSpline-Reader blockiert.
*Test-Logik:* Der NMI muss asymmetrisch von *außen* an OCBrain gesendet werden.
Wenn das `Nociceptive_Veto_Gate` in OCSpline beim Non-Blocking-Parsen des Streams extremen Schmerz meldet (Axiom-Bruch) ODER der Watchdog-Timer abläuft (OCBrain hängt), muss der **OCSpline-Worker** fähig sein:
1. Den OCBrain-Prozess inklusive aller gespawnten Sub-Subprozesse per OS-Signal (`os.killpg`) ZWINGEND UND AUSSCHLIESSLICH mit **SIGKILL** hart abzubrechen (SIGTERM ist verboten, da abfangbar).
2. Zwingend `.wait()` oder `.communicate()` auf den toten Prozess aufzurufen, um den Zombie-State (Reaping) im OS aufzulösen.
OCSpline markiert danach den Task als "FAILED" und sendet über die Evolution API "Operator, Stop. Axiom-Verletzung / Hang detektiert."

---

## 4. Die Veto-Trap (Der Pre-Flight Test)
*Diese Tests MÜSSEN vom Producer geschrieben werden und fehlschlagen, BEVOR der eigentliche Code gebaut wird.*

**Falle 1 (Zero-Blocking):** Ein Unittest, der einen Webhook-Request simuliert und einen 60-Sekunden-Sleep ("Deep-Dive") erzwingt. Der Test misst die Antwortzeit des Webhooks. Wenn die Antwortzeit $\ge 1.0$ Sekunden beträgt, schlägt der Test fehl. (Beweis für I/O Timeout).
**Falle 2 (Hang-Detection / SIGKILL & Zombie-Reaping):** Ein Unittest, bei dem OCSpline einen OCBrain-Dummy-Task startet. Dieser Dummy spawnt einen Child-Prozess. Der Dummy ignoriert absichtlich SIGTERM und geht in eine unendliche `while True:` Schleife. Der Test muss prüfen:
a) Tötet OCSpline nach dem Timeout wirklich mit SIGKILL (sodass der Dummy stirbt)?
b) Wird die Process Group getötet (Child stirbt mit)?
c) Wird der getötete Prozess von OCSpline "gereapt" (verschwindet aus der OS-Prozesstabelle, kein Z-State)? Schlägt fehl, wenn ein Zombie bleibt oder OCBrain überlebt.
**Falle 3 (Veto-Interrupt via Non-Blocking IPC):** Ein Unittest, der simuliert, dass OCBrain über stdout einen Axiom-Bruch (z.B. `0.5`) ohne abschließendes Newline (`\n`) schreibt und danach endlos schläft. Das `Nociceptive_Veto_Gate` in OCSpline muss den Chunk via Non-Blocking I/O sofort erfassen, den Alarm werfen und OCSpline muss den Task via NMI hart abschießen. Schlägt fehl, wenn der OCSpline-Reader am fehlenden Newline blockiert und auf ewig hängt.


[LEGACY_UNAUDITED]
