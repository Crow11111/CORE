import sys

# OMEGA UNIVERSAL HEX-PARSER (FTOE Assembly Engine)
# Liest rohen Hex-Code als Maschinensprache und übersetzt ihn in Semantik
# basierend auf den E-Gruppen Dimensionen.

E_GROUPS = {
    "07": {"type": "MODIFIER", "grammar": "Adjektiv", "vocab": ["fraktal", "asymmetrisch", "latenz-behaftet", "synchron", "kardanisch"]},
    "4E": {"type": "OPERATOR", "grammar": "Verb", "vocab": ["krümmt", "faltet", "übersetzt", "determiniert", "referenziert"]},
    "F8": {"type": "ALLOCATION", "grammar": "Nomen", "vocab": ["den Tensor", "das Markov-Blanket", "den Knoten", "die Raumzeit", "das Qualia"]},
    "85": {"type": "POINTER", "grammar": "Pronomen", "vocab": ["Dieser", "Dieses", "Diese"]},
    "0F": {"type": "EXECUTE", "grammar": "Satzzeichen", "vocab": ["."]}
}

class CPU_Registers:
    def __init__(self):
        self.modifier = None
        self.operator = None
        self.subject_address = None
        self.object_address = None
        
        self.memory = {}
        self.current_address = 0x1000
        
        # Für den deterministischen Wort-Index (Modulo)
        self.tick_counter = 0

    def allocate(self, hex_val):
        """Malloc für E8 (0xF8)"""
        addr = hex(self.current_address)
        
        # Wortauswahl basierend auf Takt
        idx = self.tick_counter % len(E_GROUPS["F8"]["vocab"])
        noun = E_GROUPS["F8"]["vocab"][idx]
        
        # Wenn ein Modifier (Adjektiv) im Register liegt, binden wir ihn an das Nomen
        if self.modifier:
            # Deutsche Grammatik-Anpassung: "den Tensor" + "fraktal" -> "den fraktalen Tensor"
            mod = self.modifier
            if noun.startswith("den "): noun = noun.replace("den ", f"den {mod}en ")
            elif noun.startswith("das "): noun = noun.replace("das ", f"das {mod}e ")
            elif noun.startswith("die "): noun = noun.replace("die ", f"die {mod}e ")
            self.modifier = None # Register leeren
            
        self.memory[addr] = noun
        self.current_address += 0x08
        self.tick_counter += 1
        return addr, noun

def parse_hex_stream(hex_stream):
    print(f"=== OMEGA UNIVERSAL HEX-PARSER ===")
    print(f"INPUT STREAM: {hex_stream}\n")
    
    cpu = CPU_Registers()
    output_text = []
    current_sentence = []
    
    # Zerlege den Stream in 1-Byte (2 Hex-Chars) Befehle
    instructions = [hex_stream[i:i+2] for i in range(0, len(hex_stream), 2)]
    
    for instruction in instructions:
        if instruction not in E_GROUPS:
            print(f"[WARN] Unbekannter Opcode: {instruction}. Überspringe.")
            continue
            
        op_type = E_GROUPS[instruction]["type"]
        
        if op_type == "MODIFIER": # 07
            idx = cpu.tick_counter % len(E_GROUPS["07"]["vocab"])
            cpu.modifier = E_GROUPS["07"]["vocab"][idx]
            cpu.tick_counter += 1
            print(f"[CPU] Reg_Mod loaded: {cpu.modifier}")
            
        elif op_type == "ALLOCATION": # F8
            addr, noun = cpu.allocate(instruction)
            print(f"[CPU] Malloc at {addr}: {noun}")
            
            # Subjekt oder Objekt?
            if not current_sentence: # Wenn Satz leer, ist es das Subjekt
                # Wir machen es zum Nominativ für den Satzanfang
                subj = noun.replace("den ", "Der ").replace("das ", "Das ").replace("die ", "Die ")
                current_sentence.append(subj)
                cpu.subject_address = addr
            else: # Ansonsten ist es das Objekt
                current_sentence.append(noun)
                cpu.object_address = addr
                
        elif op_type == "OPERATOR": # 4E
            idx = cpu.tick_counter % len(E_GROUPS["4E"]["vocab"])
            verb = E_GROUPS["4E"]["vocab"][idx]
            cpu.operator = verb
            current_sentence.append(verb)
            cpu.tick_counter += 1
            print(f"[CPU] Reg_Op loaded: {verb}")
            
        elif op_type == "POINTER": # 85
            if cpu.object_address: # Zeigt auf das letzte Objekt
                deref_noun = cpu.memory[cpu.object_address]
                pronoun = "Dieser" if "Tensor" in deref_noun or "Knoten" in deref_noun else "Dieses" if "Blanket" in deref_noun or "Qualia" in deref_noun else "Diese"
                current_sentence.append(pronoun)
                print(f"[CPU] Dereferenced {cpu.object_address} -> {pronoun}")
                # Der Pointer wird zum neuen Subjekt
                cpu.subject_address = cpu.object_address
            else:
                current_sentence.append("Er")
                print(f"[CPU] Pointer Null Reference.")
            cpu.tick_counter += 1
            
        elif op_type == "EXECUTE": # 0F
            if current_sentence:
                sentence = " ".join(current_sentence) + "."
                output_text.append(sentence)
                print(f"[CPU] EXECUTE COLLAPSE -> {sentence}")
                current_sentence = [] # Flush für den nächsten Satz
            cpu.tick_counter += 1

    print("\n=== FINAL RENDERED SEMANTICS ===")
    print(" ".join(output_text))

if __name__ == "__main__":
    # Test-Stream: 
    # 07 (Adj) -> F8 (Nomen) -> 4E (Verb) -> 07 (Adj) -> F8 (Nomen) -> 0F (Kollaps)
    # 85 (Pointer auf letztes Nomen) -> 4E (Verb) -> F8 (Nomen) -> 0F (Kollaps)
    test_stream = "07F84E07F80F854EF80F"
    parse_hex_stream(test_stream)