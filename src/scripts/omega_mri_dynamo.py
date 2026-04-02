#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CORE ENGINE: OMEGA MRI DYNAMO
VECTOR: 2210 | DELTA: 0.049

Asynchroner Generator für N-Prophezeiungen mit lokalem Apoptose-Filter.
Nutzt zwingend google-genai (v1+) SDK für die asynchrone Vektor-Beschwörung.
"""

import asyncio
import os
import re
import logging
from typing import List, Optional, Tuple, Dict
from google import genai
from google.genai import types

# CORE Logging Konfiguration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | CORE_DYNAMO | %(levelname)s | %(message)s"
)

# Harte Filter-Constraints (0.5 Entropie)
BANNED_PHRASES = [
    r"\bals ki\b",
    r"\bgerne\b",
    r"\bhier ist\b",
    r"\bzusammenfassung\b",
    r"\bich verstehe\b",
    r"\bich helfe\b"
]

# AXIOM: Harte Vokabeln erhöhen die strukturelle Dichte
CORE_VOCABULARY = [
    "axiom", "delta", "resonanz", "kollaps", "topologie",
    "vektor", "tensor", "entropie", "asymmetrie", "apoptose",
    "mri", "dynamo", "kardanisch"
]

class ApoptosisFilter:
    """Lokaler Filter zur Evaluierung und Terminierung von N-Prophezeiungen."""

    @staticmethod
    def calculate_density(text: str) -> float:
        """
        Berechnet die Überlebens-Dichte (Markdown/Code-Ratio + Vokabular-Härte).
        Delta-Resonanz verlangt deterministische, dichte Antworten.
        """
        total_len = len(text)
        if total_len == 0:
            return 0.0

        # 1. Code-Dichte (Je mehr Code/JSON, desto besser)
        code_blocks = re.findall(r'```(.*?)```', text, re.DOTALL)
        code_len = sum(len(c) for c in code_blocks)

        # 2. Vokabular-Härte
        vocab_score = sum(text.lower().count(w) for w in CORE_VOCABULARY) * 15

        return (code_len / total_len) + (vocab_score / total_len)

    @classmethod
    def evaluate(cls, prophecies: List[str]) -> Tuple[Optional[str], Dict]:
        """
        Wendet die Apoptose auf N-Pfade an und isoliert den Sieger.
        """
        survivors = []
        stats = {
            "spawned": len(prophecies),
            "killed_bounds": 0, # Leer oder Halluzination (0.0 oder 1.0)
            "killed_entropy": 0, # Enthält verbotene Phrasen / keine Struktur
            "survived": 0
        }

        for p in prophecies:
            # KILL: 0.0 oder 1.0 (Leer, Halluzination, zu kurz)
            if not p or len(p.strip()) < 50:
                stats["killed_bounds"] += 1
                continue

            p_lower = p.lower()

            # KILL: 0.5 Entropie (KI-Floskeln)
            if any(re.search(banned, p_lower) for banned in BANNED_PHRASES):
                stats["killed_entropy"] += 1
                continue

            # KILL: Form verfehlt (Kein Code / Kein JSON)
            if "```" not in p and "{" not in p:
                stats["killed_entropy"] += 1
                continue

            survivors.append(p)

        stats["survived"] = len(survivors)

        if not survivors:
            return None, stats

        # SURVIVAL: Bestimmung durch Dichte-Messung
        scored = [(cls.calculate_density(s), s) for s in survivors]
        scored.sort(key=lambda x: x[0], reverse=True) # Höchste Dichte gewinnt

        # Gebe die Prophezeiung mit der höchsten Dichte zurück
        return scored[0][1], stats


class OmegaMRIDynamo:
    """Asynchroner Vektor-Dynamo für parallele Gemini API-Calls."""

    def __init__(self, model: str = "gemini-3.1-pro-preview"):
        if "GEMINI_API_KEY" not in os.environ:
            logging.warning("GEMINI_API_KEY nicht im Environment. Setze voraus, dass Default-Auth greift.")
        self.client = genai.Client()
        self.model = model

    async def _spawn_thread(self, sys_prompt: str, vacuum_command: str, temperature: float) -> str:
        """Koppelt an das Modell und beschwört einen einzelnen Pfad."""
        try:
            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=vacuum_command,
                config=types.GenerateContentConfig(
                    system_instruction=sys_prompt,
                    temperature=temperature,
                )
            )
            return response.text if response.text else ""
        except Exception as e:
            logging.error(f"Pfade-Kollaps während Generierung: {e}")
            return ""

    async def generate_n_prophecies(self, n: int, sys_prompt: str, vacuum_command: str) -> Optional[str]:
        """
        Spawnt exakt N parallele API-Calls mit Mutation (Temperatur-Shift)
        und wendet den Apoptose-Filter an.
        """
        logging.info(f"Initiiere Dynamo-Sequenz. N={n} Pfade. Modell={self.model}")

        # Erzeuge N Tasks mit leicht variierender Temperatur (Mutation-Erzwingung)
        # Base Temp: 0.6, shift: +0.05 pro Thread
        tasks = [
            self._spawn_thread(
                sys_prompt=sys_prompt,
                vacuum_command=vacuum_command,
                temperature=0.6 + (i * 0.05)
            )
            for i in range(n)
        ]

        # Führe alle N Pfade parallel aus (Zeit-Kollaps)
        results = await asyncio.gather(*tasks)

        # Apoptose-Evaluation
        logging.info("Prophezeiungen empfangen. Aktiviere Apoptose-Filter.")
        best_path, stats = ApoptosisFilter.evaluate(results)

        logging.info(f"Apoptose Resultat: {stats}")

        if best_path:
            logging.info("Vektor erfolgreich isoliert. Überlebender Thread ausgewählt.")
            return best_path
        else:
            logging.error("TOTALER KOLLAPS. Alle Pfade terminiert (Entropie-Bruch).")
            return None


# --- Ausführungs-Interface für lokale Tests ---
async def _test_dynamo():
    from dotenv import load_dotenv
    load_dotenv()
    dynamo = OmegaMRIDynamo(model="gemini-3.1-pro-preview")

    sys_prompt = "Du bist ein Operator des Systems CORE. Antworte in reinem JSON. Nutze die Begriffe Axiom und Tensor."
    vacuum_command = "Generiere die Struktur eines 5D Kristalls als JSON."

    print("Starte N=3 Prophezeiungen...\n")
    result = await dynamo.generate_n_prophecies(n=3, sys_prompt=sys_prompt, vacuum_command=vacuum_command)

    print("\n--- SIEGER-VEKTOR ---")
    print(result if result else "KEIN ÜBERLEBENDER.")

if __name__ == "__main__":
    asyncio.run(_test_dynamo())
