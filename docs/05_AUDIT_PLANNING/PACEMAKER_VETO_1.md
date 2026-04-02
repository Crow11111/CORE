# PACEMAKER VETO-REPORT (Orchestrator B / Hugin)

**Gegenstand:** `SPEC_PACEMAKER.md` (Erstentwurf)  
**Modus:** Zero-Context Critic — nur Logik, keine Implementierungsvorschläge  
**Urteil:** **VETO**

---

## 1. Gesamturteil

Die Spezifikation ist **nicht** manipulationssicher und **nicht** zero-trust-tauglich in dem Sinne, den OMEGA für „Beweis statt Glauben“ beansprucht. Mehrere kritische Entscheidungen sind **ausstehend** oder **delegieren Vertrauen** genau dorthin, wo der faulste Pfad liegt (Konfiguration, Whitelist, Test-Doubles, offene Matrix).

**Endline:** **VETO**

---

## 2. Veto-Traps: formal da, inhaltlich porös

### 2.1 Falle 1 (Stiller Watchdog)

- Die Erwartung erlaubt einen **„expliziten Test-Double des Spline-Ingress“**. Das ist ein klassischer Heroin-Pfad: Die Produktion kann weiterhin **kein** echtes Panic an eine **verifizierbare** zweite Instanz liefern, solange der Test nur einen Double füttert. Zero-Trust verlangt eine **Kette mit unabhängigem Empfänger** — die Spezifikation **fordert** das nicht, sie **erlaubt** den Ersatz durch einen kontrollierten Stub.
- **„künstlich unerreichbar“** deckt nicht ab: Ziele werden **per Konfiguration entfernt**, **falsch benannt**, oder als `skipped` mit plausibler Begründung aus dem Weg geräumt (siehe AC-1/AC-5).

### 2.2 Falle 2 (Schein-Vitalität)

- Der Test zielt auf **`/status`-Poll** und „sichere“ Vitalität. Ein fauler Coder umgeht das, indem er **irgendeinen** Whitelist-Eintrag wählt, der **billig automatisierbar** ist (z. B. minimaler „erfolgreicher“ Turn, trivialer Ingest, synthetisches Event derselben Schicht). Die Spez sagt zwar „kein reines HTTP 200 auf /status allein“ — sie **verbietet nicht**, dass **andere** Schein-Signale die Whitelist füttern oder dass die Whitelist im nächsten PR **geweitet** wird.
- **Fehlende Falle:** Es gibt **keine** Vorgabe, dass „Wert-nachweisende Aktivität“ **kreuzvalidiert** wird (zweite Datenquelle, Operator-Bindung, Integrität gegen Selbstbescheinigung).

### 2.3 Falle 3 (Λ ohne Konsequenz)

- Geprüft wird im Wesentlichen: **Recovery-Event** oder **definierte Aktion**. Heroin: **Event wird emittiert**, die Pipeline ist **`pass`**, Ressourcen **null**. Ein Test, der nur auf **Event-Existenz** starrt, ist **kein** Beweis für Wirkung — die Spez nennt **keine** Pflicht, dass die Aktion **extern beobachtbar** oder **idempotent nachprüfbar** ist (nur „ausgeführt und geloggt“).
- **„auskommentiert oder nur pass“** ist zu schwach formuliert: Ein **No-Op mit Log-Zeile** erfüllt formal „nicht nur pass“, ohne metabolischen Mehrwert.

**Fazit Traps:** Die drei Fallen sind **Anforderungen an Tests**, nicht an **unabhängige Verifikation**. Sie sind **nicht wasserdicht**.

---

## 3. Decay-Umgehung über „Wertbeitrag“

1. **Whitelist ist die Schwachstelle.** Ohne **Versions- und Änderungs-Audit** (wer darf sie erweitern, mit welchem Gegenbeweis) ist „Wert“ **definitionsabhängig** und damit **zum Nulltarif manipulierbar**.
2. **„Referenz-ID“ und letzte Aktivität** stammen faktisch aus demselben **Vertrauensradius** wie der Pacemaker — **kein** beschriebener Bruch dieser Zirkularität (z. B. Signatur, fremder Log-Stream, Operator-Quorum).
3. **„Vom Operator bestätigter Task“** ohne Spezifikation von **Missbrauch** (Pre-Approval-Spam, Auto-Confirm, kompromittierter Client) ist **kein** harter Anker.
4. **`T_idle`** und Schwellbänder sind **konfigurierbar** — ein großes Fenster oder ein **Reset-Trigger** außerhalb der explizit genannten Falle 2 (z. B. **beliebiges** internes Event) kann Decay **de facto** neutralisieren, ohne die Buchstaben von Falle 2 zu verletzen.

**Fazit:** Es gibt **mehrere** plausible Wege, den Decay-Mechanismus **semantisch** zu umgehen, nicht nur den im Trap genannten `/status`-Pfad.

---

## 4. NMI (Panic): nicht manipulationssicher

1. **Die Auslöse-Matrix ist offen** (Abschnitt 5). Solange „welcher Teilfail = NMI“ **nicht fixiert** ist, ist NMI **politisch/konfigurativer** Spielraum — kein fester Vertrag. Das ist **kein** Panic, das man **vorher** falsifizieren kann, sondern eine **Später-entscheiden-wir**-Lücke.
2. **Keine Herkunfts-Authentizität:** „Standardisiertes Panic-Payload“ auf dem **gleichen Bus** wie andere Alarme — ohne beschriebenes **Zero-Trust-Merkmal** (Identität des Emitters, Integrität, Replay-Schutz) ist **Injection** und **Verdrängung** durch lautere/kompatiblere Events **nicht** ausgeschlossen.
3. **Zeitschranke AC-2:** `2 × Intervall + ε` — bei **großem** konfiguriertem Intervall wird „innerhalb“ zur **Leerlauf-Fiktion**. Die Spez verlangt ein **Mindestintervall**, nicht ein **Maximalintervall** für Produktion; damit ist **zeitliche Eskalation** verzögerbar.
4. **„NMI nur wenn definiert“** (Vitality-Band) ist ein **expliziter** Ausstieg; kombiniert mit offener Matrix **doppelte** Weichheit.

**Fazit:** NMI ist **nicht** als manipulationssicher belegt.

---

## 5. Weitere logische Lücken (kurz)

- **Gekoppelte Doppel-Dimension:** Ohne **eine** Abnahme, die **bewusst** nur eine Hälfte implementiert und **scheitern muss**, bleibt die „Untrennbarkeit“ **Rhetorik**.
- **Shard/Merge (AC-1):** „Dokumentiertes Shard“ plus Test ersetzt **nicht** den Nachweis, dass in Betrieb **nie** ein Zyklus ohne Merge **grün** wird.
- **`skipped` vs. `healthy` (AC-5):** „Nicht ok“ ist gefordert — die **Aggregation** „alles skipped → Gesamtstatus?“ ist **nicht** eindeutig geschlossen; Heroin: **degraded** mit leerer Begründungsliste oder **healthy** mit „keine aktiven Ziele“.
- **A5 und Float:** „Verbotene exakte Zustände“ kollidieren mit **reeller** Float-Arithmetik und Serialisierung; ohne **Toleranz-/Snap-Regel** droht entweder **scheinbare** Compliance oder **endloser** Kantenfall-Streit — in der Spez **unaufgelöst**.
- **OCBrain-Reaktion:** Die Spez endet beim **Emit**; **kein** Acceptance-Kriterium, dass die **Gegenstelle** den Panic **verpflichtend** eskaliert (sonst: **todgeweihtes Event** im leeren Raum).

---

## 6. Zusammenfassung für Ring 0

| Prüffrage | Ergebnis |
|-----------|----------|
| Veto-Traps wasserdicht? | **Nein** — Stub-tauglich, Whitelist/Events ohne Wirkungsbeweis. |
| Decay über „Wert“ umgehbar? | **Ja** — Whitelist, Konfiguration, Selbstattestation. |
| NMI manipulationssicher? | **Nein** — offene Matrix, fehlende Authentizität, Intervall-Skalierung. |

**Orchestrator B — Hugin**  
*PASS nur bei geschlossener Matrix, nicht-zirkulärem Wertnachweis, harter Aggregationslogik für skipped/fail, und Nachweis der Panic-Kette über unabhängige Beobachtung — bis dahin: **VETO**.*


[LEGACY_UNAUDITED]
