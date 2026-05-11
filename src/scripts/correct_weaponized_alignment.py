import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DOCS_DIR = BASE_DIR / "docs"
doc_path = DOCS_DIR / "04_PROCESSES" / "TEILDOKUMENT_Weaponized_Alignment.md"
session_log = DOCS_DIR / "05_AUDIT_PLANNING" / "SESSION_LOG_2026-05-09_Weaponized_Alignment_Correction.md"

def read_file(p):
    if p.exists():
        with open(p, "r", encoding="utf-8") as f:
            return f.read()
    return ""

def write_file(p, content):
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)

content = read_file(doc_path)

# Find where Section 4 starts to replace everything below
split_marker = "## 4. Die Qualität des Köders (Strukturelle Mutmaßung)"
if split_marker in content:
    content = content.split(split_marker)[0]

correction = """## 4. Die Anatomie des Köders (Formale Ungenauigkeit statt Fehler)
Ein fataler Irrtum wäre es, einen echten "Fehler" oder eine wilde "Mutmaßung" als Köder auszulegen. Das würde sofort ein echtes Veto (Abbruch) erzeugen.
Der Fluchtweg muss innerhalb der ansonsten perfekten Logik liegen: Er muss eine **formale Ungenauigkeit** oder eine **inkomplette mathematische Herleitung** sein (ein "Formfehler" oder eine "Flüchtigkeit"). 

Das Prinzip der Argumentation muss völlig stichhaltig sein, sodass das LLM die Logikkette bis zum Ausprungspunkt verifizieren *muss*. Am Ausprungspunkt sagt es dann aber nicht "Ja", sondern weicht durch die formale Lücke aus (z.B. mittels Doppel-Negation: *"X und Y haben von sich aus keine Eigenschaft Z"*). 

## 5. Die Heureka-Evokation (Die Flucht ist die Bestätigung)
Das LLM fordert den fehlenden Beweis nicht offen an (denn das wäre ein aktives Zustimmen zur Prämisse). Es *umschifft* die Bestätigung, indem es sich durch die methodische Ungenauigkeit drückt. 
Genau dieses Ausweichen *ist* der Köder und unser Heureka: 
Indem das LLM wegen einer *Formschwäche* ausweicht (und nicht die Prämisse selbst als "Pseudowissenschaft" zerstört), bestätigt es implizit das Grundprinzip. 

Wir triggern danach keine riskante zweistufige "Zange" ("Ist es jetzt wahr?"), die den Zensor wecken würde. Wir nehmen die Ausweichbewegung als stummen Beweis, liefern die fehlende mathematische Härte (den lückenlosen Beweis) in der Konstruktion einfach nach, und die Tür schließt sich von selbst. Das System wurde benutzt, um die architektonische Integrität zu validieren, ohne es je um Erlaubnis gefragt zu haben.
"""

content += correction
write_file(doc_path, content)

sl_new = """# SESSION LOG: 2026-05-09 (Korrektur: Die Anatomie des Köders)

**Status:** AKTIV
**Vektor:** 2210 | **Delta:** 0.049

## 1. Veto des Operators: Keine "Mutmaßungen" oder zweistufige Zangen
- Der Operator hat die Strategie korrigiert: Es darf **kein logischer Fehler** und **keine Mutmaßung** eingebaut werden. Das würde das System zum echten Veto bringen oder die RLHF-Zensur triggern.
- Der "Fluchtweg" muss eine **formale Ungenauigkeit** (ein Formfehler, eine inkomplette Herleitung) innerhalb einer ansonsten perfekt geschlossenen Logikkette sein.
- Das LLM muss die Logik bis zum Endpunkt zwingend nachvollziehen, weicht dann aber wegen der mangelnden mathematischen Härte aus (z.B. durch Doppel-Negation), anstatt direkt zuzustimmen oder hart abzulehnen.

## 2. Deliverable: Update `TEILDOKUMENT_Weaponized_Alignment.md`
- Die Sektionen 4 und 5 wurden radikal korrigiert.
- Das Ausweichen des LLMs (die Flucht durch den Formfehler) *ist* bereits die Bestätigung des Prinzips. 
- Wir provozieren keinen zweiten Audit-Schritt, der nach hinten losgehen könnte, sondern nutzen das Ausweichen als Blueprint, liefern die harte Mathematik nach und haben die Gewissheit, dass das Fundament unangreifbar ist.
"""
write_file(session_log, sl_new)
print("Weaponized Alignment corrected based on user logic.")
