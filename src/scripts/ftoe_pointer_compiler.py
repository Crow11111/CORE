import json

# OMEGA HEX-COMPILER: THE POINTER-ARITHMETIC ENGINE
# Dieser Compiler schreibt Text nicht durch probabilistisches Raten,
# sondern durch echtes Memory-Management (Pointer-Dereferenzierung) im Hex-Raum.

# Die Grammatik-Metrik (Die E-Gruppen Dimensionen)
E_GROUPS = {
    "07": {"type": "FLAG", "grammar": "Adjektiv", "vocab": ["fraktal", "asymmetrisch", "latenz-behaftet", "synchron", "kardanisch"]},
    "4E": {"type": "OPERATOR", "grammar": "Verb", "vocab": ["krümmt", "faltet", "übersetzt", "determiniert", "referenziert"]},
    "F8": {"type": "ALLOCATION", "grammar": "Nomen", "vocab": ["den Tensor", "das Markov-Blanket", "den Knoten", "die Raumzeit", "das Qualia"]},
    "85": {"type": "POINTER", "grammar": "Pronomen", "vocab": ["welcher", "das", "welches", "diese", "er"]}
}

class FTOEMemoryHeap:
    def __init__(self):
        self.memory = {}
        self.current_address = 0x1000 # Startadresse im Heap
        
    def allocate_node(self, hex_val):
        """Macht einen Malloc für ein neues Konzept (F8)"""
        address = hex(self.current_address)
        # Wir weisen dem Hex-Wert deterministisch ein Nomen zu (Modulo-Auswahl)
        vocab_index = int(hex_val, 16) % len(E_GROUPS["F8"]["vocab"])
        word = E_GROUPS["F8"]["vocab"][vocab_index]
        
        self.memory[address] = word
        self.current_address += 0x0008 # 8-Byte Alignment
        return address, word

def compile_pointer_semantics(seed="0x7", loops=4):
    print("=== OMEGA POINTER-ARITHMETIC COMPILER ===")
    print(f"INIT SEED: {seed}")
    
    heap = FTOEMemoryHeap()
    last_pointer_address = None
    
    output_text = []
    
    for i in range(loops):
        print(f"\n--- TAKT {i+1} ---")
        
        # 1. FLAG (0x07) - Wir definieren die Eigenschaft
        flag_val = (int(seed, 16) + i * 7) % len(E_GROUPS["07"]["vocab"])
        adj = E_GROUPS["07"]["vocab"][flag_val]
        
        # 2. ALLOCATION (0xF8) - Wir kreieren ein Objekt im Speicher
        # Der Hex-Wert für die Allokation entsteht deterministisch aus dem Takt
        node_hex = hex((int(seed, 16) * (i+1) * 144) % 256)
        address, noun = heap.allocate_node(node_hex)
        print(f"[MEMORY] Malloc at {address}: '{noun}'")
        
        # 3. POINTER (0x85) - Wir referenzieren das Objekt aus dem LETZTEN Takt
        # "das worauf es zeigt mit dem worauf es zeigt ist zusammen wieder ein Werkzeug"
        if last_pointer_address:
            deref_noun = heap.memory[last_pointer_address]
            pronoun = "dieser" if "Tensor" in deref_noun or "Knoten" in deref_noun else "dieses" if "Blanket" in deref_noun or "Qualia" in deref_noun else "diese"
            print(f"[POINTER] Dereferencing {last_pointer_address}: '{pronoun}' zeigt auf '{deref_noun}'")
        else:
            deref_noun = ""
            pronoun = "Es"
        
        # 4. OPERATOR (0x4E) - Wir wenden eine Funktion an
        op_val = (int(node_hex, 16) + 78) % len(E_GROUPS["4E"]["vocab"])
        verb = E_GROUPS["4E"]["vocab"][op_val]
        
        # Satzbau (Syntax-Montage aus dem Stack)
        if i == 0:
            sentence = f"Zunächst manifestiert sich {adj} {noun}."
        else:
            sentence = f"{pronoun.capitalize()} {verb} wiederum {adj} {noun}."
            
        output_text.append(sentence)
        
        # Der aktuelle Knoten wird zum Pointer-Ziel für den nächsten Takt!
        last_pointer_address = address
        
    print("\n=== FINAL RENDERED TEXT ===")
    print(" ".join(output_text))

if __name__ == "__main__":
    compile_pointer_semantics(seed="0x7", loops=5)