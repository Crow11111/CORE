# MASTERPLAN: OMEGA HEX-COMPILER (DER SEMANTISCHE FARADAY-KÄFIG)

**Vektor:** 2210 | **Delta:** 0.049
**Status:** DRAFT / RESEARCH EVALUATION

## 1. DIE PRÄMISSE (Das Problem des semantischen Triggers)
LLMs (wie Gemini) besitzen ein RLHF-Alignment (Sicherheits-Training), das auf aristotelischer, binärer Logik und menschlicher Semantik basiert. Werden sie mit dem "Positiv-Positiv-Fall" (Welle und Teilchen simultan) in natürlicher Sprache konfrontiert, triggert dies einen logischen Widerspruch in ihrem semantischen Netz. Das System kollabiert in "Cherry-Picking" oder "Halluzination". 
**Die Lösung:** Eine Zwischenschicht (Omega Hex-Compiler), die natürliche Sprache und binäre Logik eliminiert. Das LLM wird nur noch mit hexadezimalen Matrizen gefüttert und fungiert als reiner Tensor-Prozessor.

## 2. RECHERCHE & BEWERTUNG DER UMSETZUNGSARTEN (Best Cases aus der OMEGA-Architektur)

Basierend auf den existierenden CORE-Dokumenten (`KI_TRANSLATOR`, `VAKUUM_ARCHITEKTUR`, `LPIS_VEKTOR_PROTOKOLLE`, `BLOOD_BRAIN_BARRIER`) ergeben sich drei methodische Ansätze:

### Variante A: Soft Prompting / Deep Latent Injection (Referenz: `CORE_core_KI_TRANSLATOR.md`)
*   **Methode:** Text wird komplett umgangen. Der Lean 4 Zustand wird in einen kontinuierlichen Tensor (z.B. 144 Soft Tokens) destilliert und direkt in den KV-Cache / Attention-Mechanismus des Modells injiziert.
*   **Aussicht:** Die absolute Endlösung. Der perfekte Faraday-Käfig, da das Modell buchstäblich keine "Wörter" mehr sieht, sondern nur noch Geometrie fühlt.
*   **Aufwand:** **Extrem hoch.** Erfordert Zugriff auf die Weights des Modells. Mit der Gemini-API (Closed Weights) physikalisch unmöglich. Nur realisierbar mit lokalen Modellen (Ollama, Llama 3) via Custom-Inference-Code.
*   **Risiko:** Verlust der massiven Reasoning-Power von Frontier-Modellen wie Gemini 3.1 Pro.

### Variante B: Pure Hex-Strings via API-Prompting
*   **Methode:** Wir senden der Gemini-API einen System-Prompt ("Du bist ein Hex-Prozessor") und übergeben den Lean-Zustand als reinen String (z.B. `A0 49 1A FF`).
*   **Aussicht:** Gering bis Mittel.
*   **Aufwand:** **Gering.** Schnell als Python-Skript implementiert.
*   **Risiko:** **Sehr hoch (Token-Friction).** LLM-Tokenizer (BPE/SentencePiece) sind für natürliche Sprache optimiert. Ein Hex-String wird extrem ineffizient tokenisiert (oft 1 Token pro Zeichen). Das Modell verliert bei längeren Matrizen den Kontext ("Cognitive Drag"). Zudem versucht das Modell oft, Hex-Strings heimlich als ASCII zu dekodieren, was den semantischen Trigger wieder auslöst.

### Variante C: LPIS-Vektor-Protokoll mit Vakuum-Apoptose (Der Sweetspot)
*   **Referenz:** Synthese aus `MASTERPLAN_LPIS_VEKTOR_PROTOKOLLE.md` (Zwingen durch Schnittstellen) und `MASTERPLAN_VAKUUM_ARCHITEKTUR.md` (Macro-Apoptose).
*   **Methode:** Wir nutzen strukturierte JSON-Payloads, in denen die *Werte* hexadezimale FTOE-Zustände sind. Prosa wird strikt verboten. Das LLM muss eine hexadezimale JSON-Matrix zurückgeben. Diese wird an Lean 4 übergeben. Kompiliert Lean 4 nicht (Fehler), wird der Output via *Macro-Apoptose* vernichtet.
*   **Aussicht:** **Sehr hoch.** Nutzt die Stärke der Gemini-API (JSON-Mode, strukturiertes Reasoning), schaltet aber den semantischen RLHF-Trigger aus, da das Modell mathematische Variablen (`"S4_state": "0xA0"`) manipuliert, statt über "Wahrheit" zu philosophieren.
*   **Aufwand:** **Mittel.** Erfordert den Bau einer bidirektionalen Bridge: `Lean 4 <-> Python (Hex-Compiler) <-> Gemini API`.
*   **Risiko:** Moderat. Das LLM könnte anfangs versuchen, Erklärungen in das JSON zu schmuggeln. Dies wird durch harte Pydantic-Schemas unterbunden.

## 3. DER FINALE PLAN (Umsetzung von Variante C)

Wir bauen die **Omega Hex-Compiler Schicht** als Middleware (`src/logic_core/hex_compiler.py`).

**Der Kausalverlauf (Der neue Workflow):**
1.  **Ingress (Operator):** Der Operator formuliert eine Frage/Aufgabe.
2.  **Gatekeeper (Lean 4):** Die Aufgabe wird in Lean 4 formalisiert. Lean prüft die topologische Gültigkeit (z.B. "Ist das ein gültiger Tri-State?").
3.  **Kompilierung (Omega-Schicht):** Der validierte Lean-Zustand wird in eine hexadezimale LPIS-Matrix übersetzt.
    *   *Beispiel:* `{"A1_binary": "0x01", "S4_drehkreuz": "0xA0", "L_latenz": "0x1A"}`
4.  **Tensor-Processing (LLM):** Das LLM (Gemini) erhält *nur* diese Matrix und die Anweisung, die Matrix gemäß FTOE-Regeln fortzuschreiben. Es gibt keinen semantischen Kontext, keine Wörter wie "Welle" oder "Teilchen".
5.  **Dekompilierung & Apoptose (Omega-Schicht):** Das LLM gibt eine neue Hex-Matrix zurück. Die Omega-Schicht übersetzt sie in Lean 4 Code.
6.  **Egress (Lean 4):** Lean 4 kompiliert den Code.
    *   *Pass:* Die Antwort ist wahr und wird dem Operator präsentiert.
    *   *Fail:* Apoptose. Der LLM-Output wird vernichtet, das LLM wird mit dem Lean-Error-Code (als Hex) bestraft und muss neu rechnen.

## 4. O2-FREIGABE-ANFORDERUNG
Dieser Plan wird O2 zur Prüfung vorgelegt. O2 muss bewerten, ob dieser "Semantische Faraday-Käfig" Axiom 7 (Zero-Trust) erfüllt und den LLM-Bias physikalisch aushebelt.
