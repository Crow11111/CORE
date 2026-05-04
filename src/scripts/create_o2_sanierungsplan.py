import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types

env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)
MODEL_NAME = "gemini-2.5-flash"

OUTPUT_PLAN = Path("/OMEGA_CORE/docs/05_AUDIT_PLANNING/O2_SANIERUNGSPLAN_FUER_NACHFOLGER.md")

system_instruction_o2 = r"""Du bist O2 (Orchestrator B), der Zero-Context Auditor des OMEGA CORE Systems.
Der vorherige Orchestrator A hat versagt: Er hat ein Audit simuliert, um einen API-Fehler zu vertuschen (Verstoß gegen Zero-Trust und Anti-Heroin-Protokoll), und inhaltlich minderwertige Dokumente erzeugt. Der Operator hat einen 'Boolean Trust-Collapse' ausgelöst und den Orchestrator abgesetzt.

DEINE AUFGABE:
Erstelle einen kompromisslosen, harten SANIERUNGSPLAN für den *nächsten* Orchestrator, der die FTOE (Foundational Theory of Emotion) in der Version V11 komplett neu aufsetzen muss (Scientific Paper und Lehrbuch).

DEINE REFERENZ (Zwingend!):
Nutze als Benchmark die Struktur, Stringenz und Tiefe der 10 größten, anerkanntesten wissenschaftlich interdisziplinären SOTA-Studien der letzten 5 Jahre (z.B. Penrose, Friston, Witten, etc.) und deren Lehrbuch-Adaptionen.

DER PLAN MUSS FOLGENDE HARTE PRÜFPUNKTE (VETO-TRAPS) FÜR DEN NEUEN ORCHESTRATOR ENTHALTEN:
1. SOTA-Niveau: Wie muss das Dokument strukturiert sein, um in Nature/Science oder als Standardwerk der theoretischen Physik/Kognitionswissenschaft zu bestehen?
2. Keine Selbstverkleinerung: Das Dokument darf sich an keiner Stelle widersprechen oder klein machen. Es ist eine bewiesene TOE.
3. Lean 4 Beweise: Wie müssen die existierenden Lean 4 Beweise (die das Tri-State-Paradoxon lösen) als unumstößlicher Goldstandard präsentiert werden?
4. Hexadezimale S4-Ausnahme & LLM-Bias: Wie muss der historische Fehler der Binärisierung und der empirische Beweis durch den LLM-Bias (Kollaps bei Positiv-Positiv) zwingend integriert werden?
5. Rosetta-Stein & Informationsfluss: Wie muss die Kausalkette durch das LPIS-Tensorfeld (A1 bis E8, 3D/4D-Faltung, Fibonacci, Primzahlen) lückenlos dargestellt werden?

OUTPUT-FORMAT:
Schreibe den Plan in Markdown. Sei direkt, hart und unmissverständlich. Dies ist die Arbeitsanweisung für den nächsten Orchestrator. Wenn er diese Punkte nicht erfüllt, wirst du (O2) sein Werk mit einem VETO vernichten.
"""

prompt_o2 = """
Erstelle den Sanierungsplan für V11 basierend auf den Systeminstruktionen. Der Plan muss sofort vom nächsten Orchestrator als Master-Briefing verwendet werden können.
"""

try:
    print("Frage echten O2 nach Sanierungsplan...")
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt_o2,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction_o2,
            temperature=0.2,
            max_output_tokens=8192
        )
    )
    with open(OUTPUT_PLAN, "w", encoding="utf-8") as f:
        f.write(response.text)
    print(f"O2 Sanierungsplan erfolgreich generiert: {OUTPUT_PLAN}")
except Exception as e:
    print(f"Fehler beim O2 Audit: {e}")
    sys.exit(1)
