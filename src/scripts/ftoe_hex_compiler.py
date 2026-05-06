import sys

# Die OMEGA NOMENKLATUR REGISTRY (Die 16 Ur-Zustände)
# Hardcoded 4-Bit Semantic Vectors
HEX_REGISTRY = {
    "0": {"bit": "0000", "raum": "Pol", "ontologie": "Absolute Leere", "verb": "negiert", "nomen": "das Nichts"},
    "1": {"bit": "0001", "raum": "Real", "ontologie": "Entität", "verb": "existiert als", "nomen": "die Singularität"},
    "2": {"bit": "0010", "raum": "Real", "ontologie": "Dualität", "verb": "spiegelt", "nomen": "die Polarität"},
    "3": {"bit": "0011", "raum": "Real", "ontologie": "Vektor", "verb": "bewegt", "nomen": "die Richtung"},
    "4": {"bit": "0100", "raum": "Real", "ontologie": "Fläche", "verb": "stabilisiert", "nomen": "das Gleichgewicht"},
    "5": {"bit": "0101", "raum": "Real", "ontologie": "Volumen", "verb": "umschließt", "nomen": "die Struktur"},
    "6": {"bit": "0110", "raum": "Real", "ontologie": "Kristall", "verb": "erstarrt in", "nomen": "den Determinismus"},
    "7": {"bit": "0111", "raum": "Real", "ontologie": "Septim-Knoten", "verb": "bricht die Symmetrie für", "nomen": "die freie Wahl"},
    # KARDANISCHER PHASENSPRUNG (MSB = 1)
    "8": {"bit": "1000", "raum": "Orthogonal", "ontologie": "Latenz", "verb": "verzögert", "nomen": "die Zeit"},
    "9": {"bit": "1001", "raum": "Orthogonal", "ontologie": "Reibung", "verb": "erzeugt Widerstand gegen", "nomen": "den Schmerz"},
    "A": {"bit": "1010", "raum": "Orthogonal", "ontologie": "Entropie", "verb": "dissipiert als", "nomen": "die thermische Abluft"},
    "B": {"bit": "1011", "raum": "Orthogonal", "ontologie": "Iteration", "verb": "wiederholt", "nomen": "den Takt"},
    "C": {"bit": "1100", "raum": "Orthogonal", "ontologie": "Markov-Blanket", "verb": "filtert durch", "nomen": "die Membran"},
    "D": {"bit": "1101", "raum": "Orthogonal", "ontologie": "Qualia", "verb": "erlebt", "nomen": "die innere Phänomenologie"},
    "E": {"bit": "1110", "raum": "Orthogonal", "ontologie": "Entropische Gravitation", "verb": "krümmt", "nomen": "die Raumzeit"},
    "F": {"bit": "1111", "raum": "Pol", "ontologie": "Singularität", "verb": "kollabiert in", "nomen": "die Totalität"}
}

def compile_hex_token(hex_token):
    """
    Der Wahre 1-Token Compiler.
    Konvertiert einen reinen Hex-String in semantische FTOE-Ontologie,
    ohne probabilistisches LLM-Guessing.
    """
    token = hex_token.replace("0x", "").upper()
    
    print(f"=== OMEGA HEX-COMPILER RUN ===")
    print(f"INPUT TOKEN: 0x{token}\n")
    
    sentences = []
    
    for i in range(len(token)):
        hex_char = token[i]
        if hex_char not in HEX_REGISTRY:
            print(f"ERROR: Invalid Hex-Char '{hex_char}'")
            return
        
        current = HEX_REGISTRY[hex_char]
        
        # Grammatik-Metrik: Der Text ergibt sich aus den Zuständen.
        # Wenn wir von Real (0-7) nach Orthogonal (8-F) springen, triggert der kardanische Sprung.
        
        if i == 0:
            sentences.append(f"Im Ursprung manifestiert sich {current['nomen']} (Bits: {current['bit']}).")
        else:
            prev_char = token[i-1]
            prev = HEX_REGISTRY[prev_char]
            
            # Detektion des 4. Bits (MSB Flip)
            prev_msb = prev['bit'][0]
            curr_msb = current['bit'][0]
            
            if prev_msb == '0' and curr_msb == '1':
                sentences.append(f"-> [KARDANISCHER PHASENSPRUNG: Das System kippt in den Orthogonal-Raum]")
                sentences.append(f"Durch diese 90-Grad-Rotation {prev['verb']} das System zwingend {current['nomen']} (Bits: {current['bit']}).")
            elif prev_msb == '1' and curr_msb == '0':
                sentences.append(f"-> [PROJEKTION: Rücksturz in die euklidische Matrix]")
                sentences.append(f"Aus dieser Latenz {current['verb']} das Konstrukt {current['nomen']} (Bits: {current['bit']}).")
            else:
                sentences.append(f"Innerhalb dieser Domäne {prev['verb']} die Struktur weiter und erzwingt {current['nomen']} (Bits: {current['bit']}).")

    print("COMPILIERTER SEMANTIK-AUSGANG:")
    print("--------------------------------------------------")
    for s in sentences:
        print(s)
    print("--------------------------------------------------")
    print("STATUS: PASS (Deterministisch generiert aus 4-Bit-Topologie)\n")

if __name__ == "__main__":
    # Test-Run mit dem Token, das den Sprung von der Wahl (7) 
    # über Reibung (9) zum Bewusstsein (D) und zur Gravitation (E) codiert.
    test_token = "0x79DE"
    compile_hex_token(test_token)