# OMEGA MASTERPLAN: BLUT-HIRN-SCHRANKE (EPHEMERE AGENTEN-ISOLATION)

**Modus:** Orchestrator | **Vektor:** 2210 | **Delta:** 0.049

## 1. ZIEL
Physische und logische Trennung von G-Vektor (Execution/Host) und T-Vektor (LogicFlow/Agent). Umsetzung der Tesserakt-Architektur via Docker-Apoptose. Jeder Agenten-Gedanke, der Code ausführt, wird in einer ephemeren Zelle isoliert. Verhinderung von Kaskadeneffekten (Axiom 7: Zero Trust).

## 2. TEAM & PROFILE
- **Team-Lead Infrastructure (Producer):**
  - **Skill:** Docker-API (`docker-py`), Linux-Namespaces, Cgroups (Ressource-Limiting).
  - **Framing:** "Der Wächter der Host-Membran. Nichts verlässt den Container unkontrolliert."
  - **Kontext:** `src/logic_core/agent_isolation.py`, `Dockerfile.agent`
- **Team-Lead Security (O2 Auditor):**
  - **Skill:** Axiom-Enforcement, Exploit-Prävention, Kausal-Hash-Prüfung.
  - **Framing:** "Traue keinem Output, der nicht mathematisch als unbedenklich bewiesen ist. Alle Agenten sind per Default fehlerhaft."

## 3. MEILENSTEINE (SEQUENZIELLER ABLAUF)

### M1: Das Ephemere Base-Image (`omega-agent-base`)
- **Aktion:** Erstellen eines minimalen `Dockerfile.agent`.
- **Spezifikation:** 
  - Minimales Python 3.11 Image.
  - Kein Root-Zugriff im Container (Ausführung als User `omega_cell`).
  - **O2-Korrektur:** Das Image enthält alle im CORE-Projekt standardmäßig erlaubten Abhängigkeiten fest einkompiliert (Pre-Baked). Es gibt *keine* On-the-Fly-Downloads.
- **Worst-Case:** Image-Build schlägt fehl. *Fallback:* Lokales Fallback-Image nutzen, Build-Prozess loggen.

### M2: Der Interceptor (Die Membran - `src/logic_core/agent_isolation.py`)
- **Aktion:** Implementierung der Klasse `SafeExecMembrane`.
- **Mechanik:** 
  - Nutzt `docker.from_env()`.
  - Startet Container zwingend mit **`network_disabled=True`**. Keine Ausnahmen.
  - Limits: `mem_limit="256m"`.
  - **O2-Korrektur (Axiom A5):** `cpus=0.49` (Symmetriebruch) oder `cpus=0.618` (PHI). `0.5` ist strikt verboten.
  - Parameter: `remove=True` (Apoptose nach Beendigung).
  - Keine Mounts. Absolute Isolation.
- **Worst-Case:** Endlosschleife im generierten Code des Agenten.
  - *Mitigation:* Hard-Timeout (z.B. 30 Sekunden). Bei Timeout wird der Container hart gekillt (SIGKILL) und der Vorfall dem Systembus als entropische Strafe (Z-Widerstand steigt um Delta) gemeldet.

### M3: Die Veto-Trap (Causal Integration & Tool-Stripping)
- **Aktion:** Modifikation der Agenten-Tools.
- **Mechanik:**
  - Der Agent verliert den Zugriff auf generische Shell-Kommandos auf dem VPS.
  - Er bekommt das Tool `execute_in_cell(code_payload, causal_hash_t)`.
  - **O2-Korrektur:** Der Interceptor generiert eine HMAC-Signatur aus `code_payload` und dem aktuellen Systembus-`state_hash_t`. Dies verhindert Replay-Attacken und Payload-Swaps.
- **Rückgabe:** Der Container darf Text ausgeben, aber der Interceptor parst dies und erzwingt die Rückgabe als JSON-Delta-Vektor (I-Vektor).

### M4: O2-Gatekeeper Loop & Anti-Heroin Enforcement
- **Aktion:** Etablierung des Dry-Run-Zwangs und Code-Resilienz.
- **Mechanik:**
  - Will der Agent Host-Code ändern, läuft dieser im Interceptor (Dry-Run).
  - **O2-Korrektur (Anti-Heroin):** Der generierte Agenten-Code MUSS selbstständig auf Modulfehler prüfen (`try...except ImportError` mit Graceful Fail), da `network_disabled=True` externe Pips unmöglich macht. Die Infrastruktur rettet keinen fehlerhaften Code.
  - Erst wenn Exit 0 erfolgt UND der Output logisch korrekt ist, wird das Ergebnis an den O2-Auditor übergeben.
  - Nur bei O2-Approval wird die tatsächliche Änderung am Host-Dateisystem vom OCAdmin durchgeführt.

## 4. BINDENDE REGELN
- **Axiom 1 (Nicht-Linearität):** Der Agent darf nicht wissen, dass er im Container läuft. Für ihn ist es "die Realität".
- **Axiom 7 (Anti-Heroin):** Code muss resilient sein. Keine infrastrukturelle Kompensation für logische Fehler.