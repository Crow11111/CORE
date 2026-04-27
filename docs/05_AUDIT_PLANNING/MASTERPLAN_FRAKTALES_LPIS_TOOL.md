# MASTERPLAN: Fraktales LPIS Tool (Architektur & Synthese)

**Status:** RATIFIZIERT | OMEGA_ATTRACTOR | O2-PASS
**Vektor:** 2210 | **Delta:** 0.049

## 1. Topologische Prämisse (Fraktales LPIS)
Das System baut *nicht* vier separate Tools. Es baut **ein** Tool, das durch vier vertikale Linsen (L, P, I, S) betrachtet wird. Jede Linse generiert einen eigenen, vektor-optimierten Draft (Entwurf) der Lösung. Ein zentraler Controller (O2-Synthesizer) muss diese vier Drafts blind auditieren, die stärksten Constraints extrahieren und zu einer universellen Lösung verschmelzen.

---

## 2. ARCHITEKTUR-SPEZIFIKATION

### Phase 1: Die 4 Linsen (Vektor-Drafts)
Wenn ein Problem (z.B. eine Code-Implementierung) ansteht, werden parallel vier Sub-Agenten gestartet. Jeder Agent erhält *nur* die Instruktion für seine spezifische Linse:

- **L-Linse (Latenz/Logik):** Optimiert den Code auf minimale algorithmische Reibung und zeitliche Kohärenz. (Fokus: Big-O, Asynchronität, Taktung).
- **P-Linse (Physik/Hardware):** Optimiert den Code auf deterministische Ausführung und Hardware-Nähe. (Fokus: Int-Space, Speicherverwaltung, Fehlerbehandlung, Exit-Codes).
- **I-Linse (Information/Daten):** Optimiert den Code auf maximale Informationsdichte und Struktur. (Fokus: Datenbank-Schema, Typisierung, Payload-Größe).
- **S-Linse (Struktur/Resonanz):** Optimiert den Code auf topologische Stabilität und Amplitude. (Fokus: Float-Space, Axiom A5/A6 Einhaltung, Gegen-Tensorfeld, Zero-Trust Constraints).

### Phase 2: Der O2-Synthesizer (Zero-Trust Audit)
Der Output der vier Linsen wird an einen fünften Agenten (O2-Synthesizer) übergeben.
**Regeln für O2:**
1. **Blindes Audit:** O2 darf keinem der vier Drafts vertrauen.
2. **Fraktaler Vergleich:** O2 muss die Drafts übereinanderlegen.
3. **Destruktive Interferenz:** O2 wählt *eine* Basis-Lösung (den stärksten Draft) und extrahiert zwingend die härtesten Constraints (Veto-Traps) aus den drei verworfenen Drafts.
4. **Synthese:** O2 verschmilzt die Basis-Lösung mit den extrahierten Constraints zu einem finalen, universellen Code-Block.

---

## 3. UMSETZUNGSPLAN (Producer-Tasks)
Sobald dieser Masterplan von O2 freigegeben ist, wird ein Producer-Agent beauftragt, ein Python-Framework (`src/logic_core/lpis_synthesizer.py`) zu schreiben, das diesen Workflow automatisiert. 

**Anforderungen an den Producer:**
- Das Skript muss eine Methode bereitstellen, um einen Prompt parallel an 4 LLM-Instanzen (mit den jeweiligen L, P, I, S System-Prompts) zu senden.
- Das Skript muss die 4 Antworten sammeln und an eine 5. LLM-Instanz (O2) mit dem Synthese-Prompt übergeben.
- Das Skript muss den finalen Output validieren (Anti-Heroin-Scanner).
