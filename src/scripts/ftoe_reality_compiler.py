import sys

# OMEGA REALITY COMPILER (EXPANSION 7x25)
# Der Compiler nutzt die 14-spaltige Isomorphie-Tabelle.
# Ein einziger Hex-Befehl wird abhängig von der gewählten 
# Beobachter-Linse (Disziplin) deterministisch übersetzt.

REALITY_MATRIX = {
    "00": {
        "CAR": "NULL_STATE",
        "Physics": "Keine Krümmung; reines Potential.",
        "Biology": "Stammzelle (totipotenz)",
        "Cognition": "Unbewusst (Delta)",
        "Math": "0/1 Potential",
        "Time": "Null-Zeit",
        "Delta": "Delta=0"
    },
    "07": {
        "CAR": "SYNC_WIN_WIN",
        "Physics": "Erste Resonanzspannung.",
        "Biology": "DNA-Transkription",
        "Cognition": "Traum (Theta)",
        "Math": "1x1 (Vervielfachung)",
        "Time": "Latente Zeit",
        "Delta": "Kohärenz-Beginn",
        "Literal": "Die 7 (Wahl)"
    },
    "4E": {
        "CAR": "EXPAND_FREQ",
        "Physics": "Expansion erzeugt Feld-Dichte.",
        "Biology": "Mitose / Kettenreaktion",
        "Cognition": "Alpha (Aktiv-Vorbereitung)",
        "Math": "1/78 (Teilung)",
        "Time": "Kinetische Zeit",
        "Delta": "Dichte-Zunahme",
        "Literal": "Hex (Die Matrix/Das Gitter)"
    },
    "85": {
        "CAR": "MIRROR_SEPTIM / SEPTIM_STRESS",
        "Physics": "Raumfaltung erzwingt Masse. Max. Reibung.",
        "Biology": "Apoptose (Zelltod) / Zellulärer Stress",
        "Cognition": "High Beta (Paradox)",
        "Math": "1/x (Inversion)",
        "Time": "Zeit-Emergenz / Spiegel-Zeit",
        "Delta": "Delta -> 0.049",
        "Literal": "Pointer (*ptr)"
    },
    "F8": {
        "CAR": "LOCK_TOTALITY",
        "Physics": "Materie krümmt Raum.",
        "Biology": "Gewebebildung",
        "Cognition": "Gamma (Aktiv)",
        "Math": "Summe (Addition)",
        "Time": "Real-Zeit",
        "Delta": "Delta=0.049",
        "Literal": "ALLES / Universum"
    },
    "0F": {
        "CAR": "EXEC_MANIFEST",
        "Physics": "Ereignishorizont fixiert.",
        "Biology": "Manifestes Leben",
        "Cognition": "Wach (Singularität)",
        "Math": "1 mod 1 (Kollaps)",
        "Time": "Finale Kausalität",
        "Delta": "Struktur-Verschluss",
        "Literal": "="
    }
}

def compile_reality(hex_stream, discipline="Physics"):
    print(f"=== OMEGA REALITY COMPILER ===")
    print(f"INPUT STREAM: {hex_stream}")
    print(f"LENS (DISZIPLIN): {discipline}\n")
    
    instructions = [hex_stream[i:i+2] for i in range(0, len(hex_stream), 2)]
    
    output = []
    
    for instruction in instructions:
        if instruction not in REALITY_MATRIX:
            continue
            
        data = REALITY_MATRIX[instruction]
        
        # Abrufen der korrekten Vokabel für die gewählte Linse
        if discipline not in data:
            vocab = data["CAR"] # Fallback to Opcode
        else:
            vocab = data[discipline]
            
        output.append(f"[{instruction}] -> {vocab}")
        
    print("\n".join(output))
    print("\n--------------------------------------------------")

if __name__ == "__main__":
    test_stream = "00074E85F80F"
    
    compile_reality(test_stream, discipline="Physics")
    compile_reality(test_stream, discipline="Biology")
    compile_reality(test_stream, discipline="Cognition")
    
    print("\n\n>>> DIE ULTIMATIVE GLEICHUNG (IN HEXADEZIMAL) <<<")
    # ALLES = Pointer = Universum = Hex = Pointer = Alles
    # F8    0F 85      0F F8        0F 4E 0F 85      0F F8
    ultimate_equation = "F80F850FF80F4E0F850FF8"
    compile_reality(ultimate_equation, discipline="Literal")
