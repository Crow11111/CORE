# -*- coding: utf-8 -*-
"""
RING-3 WORKER AUTHENTICATION (MODEL SIGNING & GHOST TOKENS)
---------------------------------------------------------
Status: PRODUCTIVE | OMEGA_SECURITY | V4
"""

import hashlib
import secrets
import re
from typing import Tuple, Optional
from src.config.immutable_axioms import AXIOMS

class Ring3Auth:
    def __init__(self, session_id: str, entropy_strikes: int = 0):
        self.session_id = session_id
        self.entropy_strikes = entropy_strikes
        # Generiere eindeutige Ghost Tokens für diese Session
        self.start_token = f"GHOST_START_{secrets.token_hex(4).upper()}"
        self.end_token = f"GHOST_END_{secrets.token_hex(4).upper()}"
        # Simulierter Session-Key (in V4-Phase 2 durch echte ECDSA ersetzt)
        self.session_key = hashlib.sha256(f"{session_id}_OMEGA_SECRET".encode()).hexdigest()

    def get_injection_prompt(self) -> str:
        """Erzeugt die Instruktion für den Worker."""
        max_strikes = AXIOMS.get("MAX_ENTROPY_STRIKES", 3)
        return f"""
[OMEGA_PROTOCOL_V4]
ENTROPY STRIKES: {self.entropy_strikes}/{max_strikes}
STRIKTE ANWEISUNG: Du bist ein Ring-3 Worker. 
1. ALLES was du generierst MUSS zwingend zwischen den folgenden Begrenzern stehen:
   <{self.start_token}> [DEIN OUTPUT] <{self.end_token}>
2. Füge am Ende deines Outputs (innerhalb der Begrenzer) die folgende Signatur an:
   SIGNATURE: [SHA256 von (Dein Text + {self.session_id})]
ALLES AUSSERHALB DIESER TOKENS WIRD VOM ORCHESTRATOR VERWORFEN.
"""

    def verify_and_extract(self, raw_output: str) -> Tuple[bool, Optional[str], str]:
        """
        Extrahiert den Inhalt zwischen Ghost Tokens und prüft die Signatur.
        Returns: (success, extracted_content, error_msg)
        """
        # 1. Extraktion via Regex
        pattern = rf"<{self.start_token}>(.*?)<{self.end_token}>"
        match = re.search(pattern, raw_output, re.DOTALL)
        
        if not match:
            return False, None, "MISSING_GHOST_TOKENS: Output was not properly wrapped."
        
        content = match.group(1).strip()
        
        # 2. Signatur-Prüfung
        sig_match = re.search(r"SIGNATURE:\s*([a-fA-F0-9]{64})", content)
        if not sig_match:
            return False, None, "MISSING_SIGNATURE: No SHA256 signature found in output."
        
        provided_sig = sig_match.group(1)
        # Entferne den Signatur-Teil für den Hash-Vergleich
        clean_content = re.sub(r"SIGNATURE:\s*[a-fA-F0-9]{64}", "", content).strip()
        
        expected_sig = hashlib.sha256(f"{clean_content}{self.session_id}".encode()).hexdigest()
        
        if provided_sig.lower() != expected_sig.lower():
            return False, None, f"SIGNATURE_MISMATCH: Integrity check failed (Ghosting detected)."
        
        return True, clean_content, "SUCCESS"

def wrap_ring3_call(prompt: str, session_id: str, entropy_strikes: int = 0) -> Tuple[str, Ring3Auth]:
    """Hilfsfunktion zur Vorbereitung eines Ring-3 Calls."""
    auth = Ring3Auth(session_id, entropy_strikes=entropy_strikes)
    wrapped_prompt = auth.get_injection_prompt() + "\n" + prompt
    return wrapped_prompt, auth
