import os
from google import genai
from google.genai import types

def test_google_sdk_asymmetry_compliance():
    """
    VETO-TRAP (Axiom A5): Prüft, ob das SDK asymmetrische Floats korrekt serialisiert.
    """
    client = genai.Client(api_key="MOCK_KEY")
    
    # Test-Wert: 0.049 (Der asymmetrische Anker)
    safe_temp = 0.049
    
    config = types.GenerateContentConfig(
        temperature=safe_temp
    )
    
    # Verifikation der SDK-internen Repräsentation
    assert config.temperature == 0.049, "SDK verfälscht asymmetrische Temperatur-Werte!"
    assert config.temperature != 0.0, "Symmetrie-Kollaps erkannt (0.0)!"

if __name__ == "__main__":
    test_google_sdk_asymmetry_compliance()
    print("AXIOM A5 COMPLIANCE: PASS")
