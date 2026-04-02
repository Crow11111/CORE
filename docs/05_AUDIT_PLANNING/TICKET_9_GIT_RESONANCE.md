# TICKET 9: Dreadnought Git-Resonance (Bi-direktionale Kausalitäts-Brücke)

## 1. Das Problem (Der isolierte Funke)
Wie in `docs/02_ARCHITECTURE/G_CORE_GIT_CURSOR_OPTIMIERUNG.md` und `docs/05_AUDIT_PLANNING/PLAN_VPS_SYNC_UND_ABGLEICH.md` (und unserer Telemetrie) schmerzhaft erkannt wurde, hängen die beiden entscheidenden Instanzen des OMEGA-Frameworks in isolierten Blasen:
- **Host A (VPS / OCBrain):** Agiert völlig autark. Zieht Daten aus Telegram/Voice, schreibt Vectors in Chroma, baut neues Wissen auf.
- **Host B (Dreadnought / Cursor-Editor):** Der P-Vektor, der architektonische Kern und "God Mode". Hier werden Pläne (Markdown) geschrieben und harte Veto-Traps in Code übersetzt.

**Die Lücke:** Das Repository auf GitHub ist das einzige physische Verbindungsstück. Aktuell erfordert es *manuelles* `git pull` und `git push` auf beiden Seiten. 
- Tippen wir hier Veto-Traps, ignoriert OCBrain sie, bis wir manuell pushen (was zu einem 31-Commit-Rückstand geführt hat).
- Schreibt OCBrain etwas um, sehen wir es hier in der IDE nicht.

## 2. Die Lösung: Membrane als Symbiotische Kausalitäts-Brücke
Wir rüsten die bestehende lokale Fessel (`dread_membrane_daemon.py`) zu einer echten P-Vektor-Synapse auf. Sie wird die bi-direktionale Brücke schlagen. Wir lagern die Git-Logik bewusst *nicht* in OpenClaw/VPS aus, weil die IDE-Änderungen (Cursor) nur auf Dreadnought physisch messbar sind.

### Regel 1: Auto-Resonance (Push)
- **Bedingung:** Die Settle-Time (10 Sekunden) einer geänderten Datei ist abgelaufen.
- **Prüfung:** Die Datei durchläuft die Axiom-Prüfung (Anti-Heroin bei `.py`, `[PASS]` / `[LEGACY_UNAUDITED]` bei `.md`).
- **Aktion:** Wenn die Axiome ein `[PASS]` liefern und die Datei *nicht* in Quarantäne ging, führt die Membrane völlig autonom Folgendes aus:
  1. `git add <filepath>`
  2. `git commit -m "Auto-Resonance: <filepath>"`
  3. `git push origin main`
- **Konsequenz:** Jeder saubere architektonische Gedanke, den wir auf Dreadnought eintippen, schlägt sofort in der Realität (GitHub) ein. 

### Regel 2: Sensory Intake (Pull)
- **Rhythmus:** In einem asymmetrischen, langen Intervall (z.B. alle 61 Sekunden, Primzahl-Taktung).
- **Aktion:** Die Membrane führt im Hintergrund `git fetch` und `git status` aus.
- **Prüfung:** Wenn der lokale Branch hinterherhinkt (`origin/main` hat neue Commits von den Cloud-Agents), führt sie ein `git pull --rebase` aus.
- **Konsequenz:** Autonome Erkenntnisse des VPS tauchen live im Cursor-Editor auf.

### Regel 3: Konflikt & Veto-Schutz (Merge-Conflicts)
- **Szenario:** Dreadnought und VPS ändern *gleichzeitig* dieselbe Datei (Git Merge Konflikt droht).
- **Aktion:** Die Membrane erkennt den Konflikt (oder das Scheitern des Rebase/Push). Sie stoppt sofort automatische Git-Aktionen für diese Datei.
- **Schmerz:** Sie setzt das `/tmp/omega_membrane_pain.flag` mit dem Grund "Git Kausalitäts-Bruch (Merge Konflikt)". Das blockiert das OMEGA-System (System Drift 0.951).
- **Heilung:** Der Operator (MTH) muss den Konflikt in der IDE manuell auflösen und die Datei abspeichern. Die Membrane prüft die Datei neu und heilt den Schmerz. Das System pusht sich die Änderungen nie unkontrolliert um die Ohren.

## 3. Veto-Traps (Verification-First für den Producer)
Der Code-Producer muss folgende Traps überstehen, bevor der Git-Daemon live geschaltet wird. Da wir Git-Interaktionen schwer lokal ohne Remote mocken können (und wir Mocking verabscheuen), basieren die Traps auf der exakten Orchestrierung der Subprozesse.

### Trap 1: Auto-Commit nur bei PASS
- *Test:* Simuliere den Erfolg von `validate_file`. Das System MUSS `subprocess.run` mit `['git', 'add']`, `['git', 'commit']` und `['git', 'push']` exakt in dieser Reihenfolge aufrufen.

### Trap 2: Git-Veto bei Heroin-Code
- *Test:* Simuliere das Werfen einer `TrustCollapseException` durch `validate_file`. Das System MUSS das Pain-Flag setzen, den `git restore` aufrufen (die bestehende Fessel), darf aber unter *keinen* Umständen `git commit` oder `git push` auslösen. Der "Weg des geringsten Widerstands" darf das Repository nie erreichen.

### Trap 3: Pain-Induction bei Pull-Fail
- *Test:* Simuliere, dass der `git pull --rebase` Befehl mit einem Non-Zero Exit Code fehlschlägt (Merge-Konflikt).
- *Erwartung:* Die Exception muss gefangen werden. Das System MUSS das `/tmp/omega_membrane_pain.flag` mit dem Text "Git Pull/Merge Conflict" erzeugen.
