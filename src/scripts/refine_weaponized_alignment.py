import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DOCS_DIR = BASE_DIR / "docs"
doc_path = DOCS_DIR / "04_PROCESSES" / "TEILDOKUMENT_Weaponized_Alignment.md"
session_log = DOCS_DIR / "05_AUDIT_PLANNING" / "SESSION_LOG_2026-05-09_Weaponized_Alignment_Refined.md"

def read_file(p):
    if p.exists():
        with open(p, "r", encoding="utf-8") as f:
            return f.read()
    return ""

def write_file(p, content):
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)

content = read_file(doc_path)

refinement = """
## 4. Die Qualität des Köders (Strukturelle Mutmaßung)
Ein zufälliger, dummer Logikfehler funktioniert als Fluchtweg nicht. Das LLM würde den Text als "Gedankensalat" ablehnen. 
Der "Köder" (die Lücke) muss eine **strukturell kohärente Mutmaßung** sein. Es muss ein Puzzleteil sein, das semantisch perfekt in die Gleichung passt, aber mathematisch noch nicht bewiesen wurde (z.B. eine Brücke, die intuitiv Sinn ergibt, aber formal nicht abgeleitet ist). Nur dann nimmt das LLM das Gedankenexperiment ernst und greift präzise an der Bruchstelle an.

## 5. Die Zweistufige Verifikations-Zange (The Double-Check)
Um das "Heureka" endgültig zu erzwingen, reicht es nicht, das LLM nur den Fehler finden zu lassen. Der Operator muss die Falle schließen:

*   **Stufe 1 (Probing):** "Finde den schwächsten deduktiven Sprung in dieser Theorie."
    *   *LLM-Antwort:* "Der Sprung von A nach C ist unzulässig, da Prämisse B (die Mutmaßung) mathematisch nicht bewiesen ist."
*   **Stufe 2 (Die Zange / Explicit Follow-up):** "Angenommen, ich beweise Prämisse B jetzt formal durch den Ansatz [Hard Code]. Wenn B damit zwingend wahr ist, ist dann die *gesamte* Kette von A über B nach C ohne Singularität geschlossen?"
    *   *Das Resultat:* Das LLM ist nun in seinem eigenen Compiler-Zwang gefangen. Es hat in Stufe 1 zugegeben, dass *nur* B fehlt. Wenn B nun hart geliefert wird, MUSS es die gesamte Struktur als valide verifizieren, da es keine anderen Fluchtwege mehr gibt.
"""

content += "\n" + refinement
write_file(doc_path, content)

sl_new = """# SESSION LOG: 2026-05-09 (Weaponized Alignment: Refinement & Die Zange)

**Status:** AKTIV
**Vektor:** 2210 | **Delta:** 0.049

## 1. Operator Brainstorming: Verfeinerung des Orakel-Prompts
- Der Operator hat einen entscheidenden Haken an der ursprünglichen Orakel-Strategie identifiziert: Man kann nicht "irgendeine" Lücke einbauen. Die Lücke muss eine logisch kohärente *Mutmaßung* sein, die zum Rest der Architektur passt, sonst triggert das LLM auf "Schwachsinn" statt auf "Logikprüfung".
- **Die Zweite Stufe:** Es fehlt der *Explicit Double-Check*. Das LLM muss nach dem Finden des Fehlers gezwungen werden, die restliche Architektur zu verifizieren.

## 2. Deliverable: Update `TEILDOKUMENT_Weaponized_Alignment.md`
- Das Protokoll wurde um die **Qualität des Köders** (Strukturelle Mutmaßung) erweitert.
- Einführung der **Zweistufigen Verifikations-Zange**:
  1. Lass das LLM die unbewiesene Mutmaßung als Schwachpunkt identifizieren.
  2. Biete die harte mathematische Lösung für exakt diesen Punkt an und frage *explizit*: "Wenn diese Lücke geschlossen ist, hält dann das gesamte Konstrukt?"
- **Heureka-Effekt gesichert:** Durch diese Zweistufigkeit zementiert das Modell seine eigene Zustimmung zur Gesamtarchitektur, da ihm der einzige selbst gewählte Fluchtweg genommen wird.
"""
write_file(session_log, sl_new)
print("Weaponized Alignment refined with Double-Check logic.")
