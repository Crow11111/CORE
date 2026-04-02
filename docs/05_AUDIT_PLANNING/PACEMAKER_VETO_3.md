# PACEMAKER — Orchestrator B (Hugin) Review | Iteration 3

**Quelle:** `docs/05_AUDIT_PLANNING/SPEC_PACEMAKER.md` (Iteration 3 — nach VETO 2)  
**Rolle:** Zero-Context Critic / asymmetrische Gegenkontrolle

---

## 1. NMI — PID-Ziel, Lock `600`, Nonce: manipulationssicher genug?

**Verbesserung gegenüber VETO 2:**  
Pfadwechsel weg von `/tmp` hin zu `/OMEGA_CORE/run/`, verpflichtendes Lock-File mit Modus `600` sowie Timestamp und Random-Nonce — das adressiert Ownership/„leeres Lock“-Schwäche sachlich. Die NMI-Matrix bleibt äußerlich und zyklusbasiert definiert.

**Verbleibende kritische Lücken (Spezifikationsebene):**

| Thema | Befund |
|--------|--------|
| **PID-Integrität** | Es wird nur „PID aus Datei lesen und `kill`“ gefordert. Es fehlt die **Verifikation**, dass `/proc/<pid>` (cmdline, Executable, ggf. CGroup/UID) zum intendierten OCBrain passt. Jeder Schreibzugriff auf `ocbrain.pid` (Kompromittierung, Bug, Race) kann **Fehlziel** oder **Nicht-Kill** (falsche/stale PID) erzeugen — das ist kein kryptographisches, aber ein **operatives Manipulations- und Safety-Risiko**, das die Formulierung „manipulationssicher“ überfordert. |
| **Stale PID / PID-Reuse** | Keine Forderung nach **atomarem Schreiben** (temp + rename), **fsync**, oder Alters-/Nonce-Kopplung in `ocbrain.pid`, sodass der Pacemaker nicht gegen einen wiederverwendeten OS-PID-Fehler absichert. |
| **Lock-File vs. Claim „fälschungssicher“** | Timestamp + Nonce belegen ein Ereignis, sind aber **nicht an den konkreten Homeostase-Fail gebunden** (kein Hash der Probe-Ergebnisse, keine Signatur). Mit gleichen Rechten auf `run/` ist Überschreiben/Parallel-Schreiben spezifikationsoffen. |

**Fazit zu (1):** Die gröbsten VETO-2-Punkte (Pfad, Modbits, Nonce) sind geschlossen; **„manipulationssicher genug“ im strengen Sinne (Zielprozess + Integrität der PID-Datei + semantische Bindung des Locks)** ist in der Spec **noch nicht** abgedeckt → **kritische Restlücke**.

---

## 2. Wertbeitrag (Anti-Junk) — noch leicht zu faken?

**Verbesserung:**  
Chroma: Null-Vektor via `sum(v) != 0.0` ausgeschlossen. Postgres: Länge > 50 **und** verbal „nachweisbare Varianz“, explizit kein `a`*50 — das verschärft gegen die naivste Junk-Spur aus VETO 2.

**Verbleibende kritische Lücken:**

| Thema | Befund |
|--------|--------|
| **Chroma** | Jedes Embedding mit **minimalem Nicht-Null-Rauschen** erfüllt `sum(v) != 0.0` und kann mit gültigem Timestamp als „Wert“ durchgehen — **weiterhin mechanisch fakelbar** mit geringem Aufwand (kein semantischer oder Entropie-Schwellwert über die reine Summe hinaus). |
| **Postgres „Varianz“** | Der Begriff ist **nicht operationalisiert** (z. B. Mindest-Shannon-Entropie, Anteil distinkter Zeichen, maximale Run-Länge wiederholter Zeichen). Ohne messbare Schwelle bleibt ein **Implementierungs-Schlupfloch** für schwache Validator-Logik. |

**Fazit zu (2):** Klar besser als reine Längen- oder Event-Only-Regeln; **„nicht mehr leicht zu faken“ trifft für Chroma und die unpräzise Varianz-Regel nicht zu** → **kritische Restlücke** auf Spec-Niveau.

---

## 3. Test-Doubles für alle drei Traps — strengstens verboten?

**Befund:** Abschnitt 4 enthält eine **globale, explizite Klausel**: Mocks und Test-Doubles sind für **alle drei** Fallen verboten; Tests müssen gegen echte Dateisysteme, echte Prozesse und echte bzw. lokale Test-Datenbanken laufen.

**Randnotiz (kein VETO-Trigger gegen diese Frage):** Falle 3 verlangt das **Forcieren des internen Timers** auf `0.049`. Das ist kein externes Test-Double, kann aber ohne Klärung (z. B. nur dokumentierter **Test-only Env-Hook** im Binary, kein Mock von Chroma/Postgres) zu Interpretationsstreit führen — empfehlenswert wäre eine **eine Zeile „erlaubte Test-Steuerung“** (nur nicht-mockende Injektion). Das ist eine Präzisierung, kein Widerspruch zum Verbot.

**Fazit zu (3):** Die Frage „sind Test-Doubles für alle 3 Traps strengstens verboten?“ ist mit **Ja** gemäß aktuellem Text beantwortbar → **dieser Punkt ist geschlossen**.

---

## Gesamturteil

| Kriterium | Status |
|-----------|--------|
| NMI manipulationssicher genug definiert | **Nein** (PID-/Prozessnachweis, Stale-PID, Lock-Bindung) |
| Wertbeitrag nicht mehr leicht fakelbar | **Nein** (Chroma nur Summe ≠ 0; Varianz unquantifiziert) |
| Test-Doubles alle 3 Traps verboten | **Ja** |

**Ergebnis:** Es bestehen weiterhin **spezifikationskritische Lücken** bei NMI-Zielintegrität und Anti-Junk-Operationalisierung.

---

**Endstatus:** **VETO**

**Kurz-Empfehlung für Iteration 4 (nur inhaltlich, keine Implementierung durch Hugin):**  
(a) Vor `SIGKILL`: harte `/proc`-Verifikation des OCBrain + atomares `ocbrain.pid`-Protokoll; optional Lock-Inhalt mit Fail-Fingerprint.  
(b) Chroma: zusätzlicher Schwellwert (z. B. Mindestnorm, Mindest-Entropie der quantisierten Komponenten, oder kollisionsgeprüfter Insert).  
(c) Postgres: messbare Varianz-/Entropie-Formel mit Untergrenze in der Spec.  
(d) Falle 3: erlaubte Art der Timer-Injektion explizit benennen.

---

*Orchestrator B (Hugin) — Turn beendet.*


[LEGACY_UNAUDITED]
